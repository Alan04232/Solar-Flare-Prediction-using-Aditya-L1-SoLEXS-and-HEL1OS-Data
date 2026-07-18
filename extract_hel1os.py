"""
===========================================================
HEL1OS Data Extraction Module
Author : Alan S
Project : Solar Flare Prediction using Aditya-L1
===========================================================

This module extracts every useful parameter from HEL1OS
FITS files and converts them into machine-learning-ready CSVs.

Supported Files
---------------
evt.fits
lc.fits
pi.fits

Outputs
-------
HEL1OS_EVENTS.csv
HEL1OS_LIGHTCURVES.csv
HEL1OS_SPECTRA.csv
===========================================================
"""

import os
import logging
from pathlib import Path
from typing import List

import numpy as np
import pandas as pd

from astropy.io import fits
from astropy.time import Time


# --------------------------------------------------------
# Logging
# --------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

logger = logging.getLogger(__name__)


# --------------------------------------------------------
# HEL1OS Extractor
# --------------------------------------------------------

class HEL1OSExtractor:

    def __init__(self,
                 root_folder: str,
                 output_folder: str):

        self.root = Path(root_folder)
        self.output = Path(output_folder)

        self.output.mkdir(parents=True, exist_ok=True)

        self.events = []
        self.lightcurves = []
        self.spectra = []

    # --------------------------------------------------------

    def run(self):

        logger.info("=" * 60)
        logger.info("HEL1OS Extraction Started")
        logger.info("=" * 60)

        self.scan_directory()

        self.save_results()

        logger.info("Finished.")

    # --------------------------------------------------------

    def scan_directory(self):

        logger.info("Scanning Folder")

        for root, dirs, files in os.walk(self.root):

            for file in files:

                file_lower = file.lower()

                filepath = os.path.join(root, file)

                try:

                    if file_lower == "evt.fits":

                        logger.info(f"EVENT FILE : {filepath}")

                        self.extract_event_file(filepath)

                    elif file_lower.endswith(".lc"):

                        logger.info(f"LIGHT CURVE : {filepath}")

                        self.extract_lightcurve(filepath)

                    elif file_lower.endswith(".fits") and "lc" in file_lower:

                        logger.info(f"LIGHT CURVE : {filepath}")

                        self.extract_lightcurve(filepath)

                    elif file_lower.endswith(".pi"):

                        logger.info(f"SPECTRUM : {filepath}")

                        self.extract_spectrum(filepath)

                    elif file_lower.endswith(".fits") and "pi" in file_lower:

                        logger.info(f"SPECTRUM : {filepath}")

                        self.extract_spectrum(filepath)

                except Exception as e:

                    logger.error(e)

    # --------------------------------------------------------

    def extract_event_file(self, filepath):

        with fits.open(filepath) as hdul:

            for hdu in hdul:

                if hdu.data is None:
                    continue

                if not hasattr(hdu, "columns"):
                    continue

                cols = hdu.columns.names

                useful = [

                    "TIME",
                    "MJD",
                    "ISOT",
                    "ENER",
                    "DET_ID",
                    "PIX_ID",
                    "PHA",
                    "PI",
                    "GRADE"

                ]

                df = pd.DataFrame()

                for col in useful:

                    if col in cols:

                        df[col] = hdu.data[col]

                if len(df) == 0:
                    continue

                # ------------------------
                # Metadata
                # ------------------------

                header = hdu.header

                df["OBSERVATION"] = os.path.basename(
                    os.path.dirname(filepath)
                )

                df["SOURCE_FILE"] = filepath

                df["HDU_NAME"] = hdu.name

                df["TELESCOP"] = header.get("TELESCOP", "")

                df["INSTRUME"] = header.get("INSTRUME", "")

                df["OBJECT"] = header.get("OBJECT", "")

                df["DATE_OBS"] = header.get("DATE-OBS", "")

                df["DATE_END"] = header.get("DATE-END", "")

                df["EXPOSURE"] = header.get("EXPOSURE", np.nan)

                df["TSTART"] = header.get("TSTART", np.nan)

                df["TSTOP"] = header.get("TSTOP", np.nan)

                df["RA_OBJ"] = header.get("RA_OBJ", np.nan)

                df["DEC_OBJ"] = header.get("DEC_OBJ", np.nan)

                self.events.append(df)

    # --------------------------------------------------------

    def extract_lightcurve(self, filepath):

        with fits.open(filepath) as hdul:

            for hdu in hdul:

                if hdu.data is None:
                    continue

                if not hasattr(hdu, "columns"):
                    continue

                cols = hdu.columns.names

                if "MJD" not in cols:
                    continue

                df = pd.DataFrame()

                df["TIME"] = Time(
                    hdu.data["MJD"],
                    format="mjd"
                ).to_datetime()

                if "CTR" in cols:
                    df["COUNT_RATE"] = hdu.data["CTR"]

                if "STAT_ERR" in cols:
                    df["STAT_ERR"] = hdu.data["STAT_ERR"]

                if "MJD" in cols:
                    df["MJD"] = hdu.data["MJD"]

                header = hdu.header

                df["ENERGY_RANGE"] = header.get(
                    "EXTNAME",
                    ""
                )

                df["SOURCE_FILE"] = filepath

                df["OBSERVATION"] = os.path.basename(
                    os.path.dirname(filepath)
                )

                self.lightcurves.append(df)

    # --------------------------------------------------------

    def extract_spectrum(self, filepath):

        with fits.open(filepath) as hdul:

            for hdu in hdul:

                if hdu.data is None:
                    continue

                if not hasattr(hdu, "columns"):
                    continue

                cols = hdu.columns.names

                if "CHANNEL" not in cols:
                    continue

                df = pd.DataFrame()

                df["CHANNEL"] = hdu.data["CHANNEL"]

                if "COUNTS" in cols:
                    df["COUNTS"] = hdu.data["COUNTS"]

                if "STAT_ERR" in cols:
                    df["STAT_ERR"] = hdu.data["STAT_ERR"]

                if "QUALITY" in cols:
                    df["QUALITY"] = hdu.data["QUALITY"]

                if "GROUPING" in cols:
                    df["GROUPING"] = hdu.data["GROUPING"]

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
                  # --------------------------------------------------------
    # Validate Data
    # --------------------------------------------------------

    def validate_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:

        if len(df) == 0:
            return df

        # Remove duplicate rows
        df = df.drop_duplicates()

        # Remove completely empty rows
        df = df.dropna(how="all")

        # Remove duplicate timestamps if available
        if "TIME" in df.columns:
            df = df.drop_duplicates(subset=["TIME"])

        # Convert numeric columns
        numeric_cols = [
            "ENER",
            "PHA",
            "PI",
            "COUNT_RATE",
            "COUNTS",
            "STAT_ERR",
            "MJD"
        ]

        for col in numeric_cols:

            if col in df.columns:

                df[col] = pd.to_numeric(
                    df[col],
                    errors="coerce"
                )

        return df

    # --------------------------------------------------------
    # Merge Detector Outputs
    # --------------------------------------------------------

    def merge_lightcurves(self):

        if len(self.lightcurves) == 0:

            logger.warning("No Light Curves Found")

            return pd.DataFrame()

        logger.info("Merging Light Curves")

        merged = pd.concat(
            self.lightcurves,
            ignore_index=True
        )

        merged = self.validate_dataframe(merged)

        merged = merged.sort_values("TIME")

        return merged

    # --------------------------------------------------------

    def merge_events(self):

        if len(self.events) == 0:

            logger.warning("No Event Files Found")

            return pd.DataFrame()

        logger.info("Merging Event Files")

        merged = pd.concat(
            self.events,
            ignore_index=True
        )

        merged = self.validate_dataframe(merged)

        return merged

    # --------------------------------------------------------

    def merge_spectra(self):

        if len(self.spectra) == 0:

            logger.warning("No Spectra Found")

            return pd.DataFrame()

        logger.info("Merging Spectra")

        merged = pd.concat(
            self.spectra,
            ignore_index=True
        )

        merged = self.validate_dataframe(merged)

        return merged

    # --------------------------------------------------------
    # Summary Statistics
    # --------------------------------------------------------

    def statistics(self):

        logger.info("=" * 60)
        logger.info("SUMMARY")
        logger.info("=" * 60)

        logger.info(f"Event Tables      : {len(self.events)}")
        logger.info(f"Light Curves      : {len(self.lightcurves)}")
        logger.info(f"Spectra           : {len(self.spectra)}")

        if len(self.events):

            rows = sum(len(i) for i in self.events)

            logger.info(f"Total Event Rows  : {rows}")

        if len(self.lightcurves):

            rows = sum(len(i) for i in self.lightcurves)

            logger.info(f"Total LC Rows     : {rows}")

        if len(self.spectra):

            rows = sum(len(i) for i in self.spectra)

            logger.info(f"Total Spec Rows   : {rows}")

    # --------------------------------------------------------
    # Save CSV Files
    # --------------------------------------------------------

    def save_results(self):

        logger.info("Saving CSV Files")

        events = self.merge_events()

        lightcurves = self.merge_lightcurves()

        spectra = self.merge_spectra()

        if len(events):

            outfile = self.output / "HEL1OS_EVENTS.csv"

            events.to_csv(outfile, index=False)

            logger.info(f"Saved {outfile}")

        if len(lightcurves):

            outfile = self.output / "HEL1OS_LIGHTCURVES.csv"

            lightcurves.to_csv(outfile, index=False)

            logger.info(f"Saved {outfile}")

        if len(spectra):

            outfile = self.output / "HEL1OS_SPECTRA.csv"

            spectra.to_csv(outfile, index=False)

            logger.info(f"Saved {outfile}")

        self.statistics()
# --------------------------------------------------------
# Main
# --------------------------------------------------------

def main():

    ROOT_FOLDER = r"D:\Downloads\New folder"

    OUTPUT_FOLDER = r"D:\Downloads\New folder\Processed"

    extractor = HEL1OSExtractor(

        root_folder=ROOT_FOLDER,

        output_folder=OUTPUT_FOLDER

    )

    extractor.run()


if __name__ == "__main__":

    main()
