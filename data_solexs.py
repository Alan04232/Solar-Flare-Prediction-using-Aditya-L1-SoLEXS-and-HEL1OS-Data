"""
===========================================================
SoLEXS Data Extraction Module
Author : Alan S
Project : Solar Flare Prediction using Aditya-L1
===========================================================

Supported Files
---------------
*.lc
*.pi
*.gti
*.fits

Outputs
-------
SOLEXS_LIGHTCURVES.csv
SOLEXS_SPECTRA.csv
SOLEXS_GTI.csv
===========================================================
"""

import os
import logging
from pathlib import Path

import numpy as np
import pandas as pd

from astropy.io import fits
from astropy.time import Time


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

logger = logging.getLogger(__name__)


class SoLEXSExtractor:

    def __init__(self,
                 root_folder,
                 output_folder):

        self.root = Path(root_folder)

        self.output = Path(output_folder)

        self.output.mkdir(parents=True,
                          exist_ok=True)

        self.lightcurves = []

        self.spectra = []

        self.gti = []

    # -----------------------------------------------------

    def run(self):

        logger.info("=" * 60)

        logger.info("Starting SoLEXS Extraction")

        logger.info("=" * 60)

        self.scan()

        self.save_results()

    # -----------------------------------------------------

    def scan(self):

        for root, dirs, files in os.walk(self.root):

            for file in files:

                filepath = os.path.join(root, file)

                lower = file.lower()

                try:

                    if lower.endswith(".lc"):

                        logger.info(f"LC : {filepath}")

                        self.extract_lightcurve(filepath)

                    elif lower.endswith(".pi"):

                        logger.info(f"PI : {filepath}")

                        self.extract_spectrum(filepath)

                    elif lower.endswith(".gti"):

                        logger.info(f"GTI : {filepath}")

                        self.extract_gti(filepath)

                    elif lower.endswith(".fits"):

                        self.extract_generic(filepath)

                except Exception as e:

                    logger.error(e)

    # -----------------------------------------------------

    def extract_generic(self,
                        filepath):

        with fits.open(filepath) as hdul:

            for hdu in hdul:

                if hdu.data is None:
                    continue

                if not hasattr(hdu,
                               "columns"):
                    continue

                ext = hdu.header.get(
                    "EXTNAME",
                    ""
                ).upper()

                if "LC" in ext:

                    self.extract_lightcurve(filepath)

                    return

                elif "PI" in ext:

                    self.extract_spectrum(filepath)

                    return

                elif "GTI" in ext:

                    self.extract_gti(filepath)

                    return

    # -----------------------------------------------------

    def extract_lightcurve(self,
                           filepath):

        with fits.open(filepath) as hdul:

            for hdu in hdul:

                if hdu.data is None:
                    continue

                if not hasattr(hdu,
                               "columns"):
                    continue

                cols = hdu.columns.names

                if "TIME" not in cols and "MJD" not in cols:
                    continue

                df = pd.DataFrame()

                if "TIME" in cols:

                    df["TIME"] = hdu.data["TIME"]

                if "MJD" in cols:

                    df["MJD"] = hdu.data["MJD"]

                    df["UTC"] = Time(
                        hdu.data["MJD"],
                        format="mjd"
                    ).to_datetime()

                if "COUNTS" in cols:

                    df["COUNTS"] = hdu.data["COUNTS"]

                if "CTR" in cols:

                    df["COUNT_RATE"] = hdu.data["CTR"]

                if "STAT_ERR" in cols:

                    df["STAT_ERR"] = hdu.data["STAT_ERR"]

                header = hdu.header

                df["OBSERVATION"] = os.path.basename(
                    os.path.dirname(filepath)
                )

                df["SOURCE_FILE"] = filepath

                df["EXPOSURE"] = header.get(
                    "EXPOSURE",
                    np.nan
                )

                df["EXTNAME"] = header.get(
                    "EXTNAME",
                    ""
                )

                self.lightcurves.append(df)

    # -----------------------------------------------------

    def extract_spectrum(self,
                         filepath):

        with fits.open(filepath) as hdul:

            for hdu in hdul:

                if hdu.data is None:
                    continue

                if not hasattr(hdu,
                               "columns"):
                    continue

                cols = hdu.columns.names

                if "CHANNEL" not in cols:
                    continue

                df = pd.DataFrame()

                df["CHANNEL"] = hdu.data["CHANNEL"]

                if "COUNTS" in cols:

                    df["COUNTS"] = hdu.data["COUNTS"]

                if "RATE" in cols:

                    df["RATE"] = hdu.data["RATE"]

                if "STAT_ERR" in cols:

                    df["STAT_ERR"] = hdu.data["STAT_ERR"]

                header = hdu.header

                df["OBSERVATION"] = os.path.basename(
                    os.path.dirname(filepath)
                )

                df["SOURCE_FILE"] = filepath

                df["EXPOSURE"] = header.get(
                    "EXPOSURE",
                    np.nan
                )

                self.spectra.append(df)
                  # -----------------------------------------------------
    # Extract GTI
    # -----------------------------------------------------

    def extract_gti(self, filepath):

        with fits.open(filepath) as hdul:

            for hdu in hdul:

                if hdu.data is None:
                    continue

                if not hasattr(hdu, "columns"):
                    continue

                cols = hdu.columns.names

                if "START" not in cols:
                    continue

                df = pd.DataFrame()

                df["START"] = hdu.data["START"]

                if "STOP" in cols:
                    df["STOP"] = hdu.data["STOP"]

                if "TIMEZERO" in cols:
                    df["TIMEZERO"] = hdu.data["TIMEZERO"]

                if "ONTIME" in cols:
                    df["ONTIME"] = hdu.data["ONTIME"]

                if "LIVETIME" in cols:
                    df["LIVETIME"] = hdu.data["LIVETIME"]

                header = hdu.header

                df["OBSERVATION"] = os.path.basename(
                    os.path.dirname(filepath)
                )

                df["SOURCE_FILE"] = filepath

                df["SDD"] = header.get(
                    "DETNAM",
                    header.get("INSTRUME", "")
                )

                self.gti.append(df)

    # -----------------------------------------------------
    # Validation
    # -----------------------------------------------------

    def validate(self, df):

        if len(df) == 0:
            return df

        df = df.drop_duplicates()

        df = df.dropna(how="all")

        numeric = [

            "COUNTS",
            "COUNT_RATE",
            "RATE",
            "STAT_ERR",
            "CHANNEL",
            "MJD"

        ]

        for col in numeric:

            if col in df.columns:

                df[col] = pd.to_numeric(
                    df[col],
                    errors="coerce"
                )

        return df

    # -----------------------------------------------------
    # Merge
    # -----------------------------------------------------

    def merge_lightcurves(self):

        if len(self.lightcurves) == 0:
            return pd.DataFrame()

        df = pd.concat(
            self.lightcurves,
            ignore_index=True
        )

        df = self.validate(df)

        if "UTC" in df.columns:

            df = df.sort_values("UTC")

        return df

    # -----------------------------------------------------

    def merge_spectra(self):

        if len(self.spectra) == 0:
            return pd.DataFrame()

        df = pd.concat(
            self.spectra,
            ignore_index=True
        )

        return self.validate(df)

    # -----------------------------------------------------

    def merge_gti(self):

        if len(self.gti) == 0:
            return pd.DataFrame()

        df = pd.concat(
            self.gti,
            ignore_index=True
        )

        return self.validate(df)

    # -----------------------------------------------------
    # Statistics
    # -----------------------------------------------------

    def statistics(self):

        logger.info("=" * 60)

        logger.info("SOLEXS SUMMARY")

        logger.info("=" * 60)

        logger.info(
            f"Light Curves : {len(self.lightcurves)}"
        )

        logger.info(
            f"Spectra      : {len(self.spectra)}"
        )

        logger.info(
            f"GTI Tables   : {len(self.gti)}"
        )

    # -----------------------------------------------------
    # Save Results
    # -----------------------------------------------------

    def save_results(self):

        lc = self.merge_lightcurves()

        sp = self.merge_spectra()

        gt = self.merge_gti()

        if len(lc):

            outfile = self.output / "SOLEXS_LIGHTCURVES.csv"

            lc.to_csv(outfile,
                      index=False)

            logger.info(
                f"Saved {outfile}"
            )

        if len(sp):

            outfile = self.output / "SOLEXS_SPECTRA.csv"

            sp.to_csv(outfile,
                      index=False)

            logger.info(
                f"Saved {outfile}"
            )

        if len(gt):

            outfile = self.output / "SOLEXS_GTI.csv"

            gt.to_csv(outfile,
                      index=False)

            logger.info(
                f"Saved {outfile}"
            )

        self.statistics()
# -----------------------------------------------------
# Main
# -----------------------------------------------------

def main():

    ROOT = r"D:\Downloads\New folder"

    OUTPUT = r"D:\Downloads\New folder\Processed"

    extractor = SoLEXSExtractor(

        root_folder=ROOT,

        output_folder=OUTPUT

    )

    extractor.run()


if __name__ == "__main__":

    main()
