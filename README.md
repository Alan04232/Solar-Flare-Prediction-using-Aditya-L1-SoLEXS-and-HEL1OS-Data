# Solar Flare Prediction using Aditya-L1 SoLEXS and HEL1OS Data

## Overview

This project aims to develop a Machine Learning-based solar flare prediction system using X-ray observations from the **Aditya-L1** mission. The system combines data from the **Solar Low Energy X-ray Spectrometer (SoLEXS)** and the **High Energy L1 Orbiting X-ray Spectrometer (HEL1OS)** to detect patterns that precede solar flare events.

Solar flares are sudden releases of magnetic energy from the Sun that can affect satellites, GPS systems, radio communications, power grids, and astronauts. By analyzing both soft and hard X-ray emissions, this project attempts to identify precursor signatures of flare activity and classify future flare occurrences.

The project includes data extraction from FITS files, preprocessing, feature engineering, machine learning model development, evaluation, and visualization.

---

## Project Objectives

- Extract scientific data from Aditya-L1 SoLEXS and HEL1OS FITS files.
- Convert raw observation data into structured datasets.
- Synchronize soft and hard X-ray observations.
- Generate statistical and temporal features.
- Train Machine Learning models for flare prediction.
- Evaluate prediction accuracy using standard metrics.
- Visualize flare activity and prediction results.

---

## About Aditya-L1

Aditya-L1 is India's first dedicated solar observatory positioned around the Sun-Earth L1 Lagrange point. It continuously observes the Sun using multiple scientific payloads for studying solar physics and space weather. :contentReference[oaicite:0]{index=0}

This project primarily utilizes two payloads:

### SoLEXS (Solar Low Energy X-ray Spectrometer)

- Measures Soft X-rays
- Energy Range: **2–22 keV**
- Detects thermal emissions from the solar corona
- High temporal and spectral resolution
- Suitable for monitoring gradual flare evolution and coronal heating :contentReference[oaicite:1]{index=1}

### HEL1OS (High Energy L1 Orbiting X-ray Spectrometer)

- Measures Hard X-rays
- Energy Range: **10–150 keV**
- Captures energetic electrons during the impulsive phase of solar flares
- Useful for studying flare initiation and particle acceleration :contentReference[oaicite:2]{index=2}

---

## Why Combine Both Instruments?

Solar flares produce emissions across a wide X-ray spectrum.

| Instrument | Observes | Information |
|------------|-----------|-------------|
| SoLEXS | Soft X-rays | Thermal plasma, flare evolution |
| HEL1OS | Hard X-rays | Non-thermal energetic electrons |

Using both datasets provides a more complete description of flare development than either instrument alone. :contentReference[oaicite:3]{index=3}

---

# Project Workflow

```
          Aditya-L1 Data Archive
                    │
        ┌───────────┴───────────┐
        │                       │
     SoLEXS FITS           HEL1OS FITS
        │                       │
        └───────────┬───────────┘
                    │
            FITS Data Extraction
                    │
            Data Cleaning
                    │
         Timestamp Synchronization
                    │
          Feature Engineering
                    │
          Dataset Construction
                    │
        Machine Learning Model
                    │
      Solar Flare Prediction
                    │
        Evaluation & Visualization
```

---

# Dataset

The project uses scientific FITS files obtained from the Aditya-L1 mission archive.

Examples include

### SoLEXS

- Light Curve
- Spectrum
- Event Files

### HEL1OS

- CdTe Light Curves
- CZT Light Curves
- Event Files

Extracted parameters include

- Observation Time
- Modified Julian Date (MJD)
- Photon Counts
- Count Rate
- Energy
- Detector ID
- Statistical Error
- Energy Channel

---

# Data Processing Pipeline

## 1. FITS File Extraction

Libraries used:

- Astropy
- NumPy
- Pandas

Operations:

- Read FITS headers
- Extract HDUs
- Parse observation tables
- Convert to CSV

---

## 2. Data Cleaning

- Remove missing values
- Remove corrupted observations
- Handle duplicate timestamps
- Normalize timestamps
- Merge detector outputs

---

## 3. Feature Engineering

Example features:

- Mean Count Rate
- Maximum Count Rate
- Standard Deviation
- Moving Average
- Rolling Variance
- Photon Count
- Energy Distribution
- Time Difference
- Count Rate Gradient

Additional temporal features:

- Previous N-minute average
- Flare rise rate
- Background intensity
- Peak intensity

---

## 4. Label Generation

Solar activity can be categorized into

- No Flare
- A-Class
- B-Class
- C-Class
- M-Class
- X-Class

Labels are generated using flare catalogs or threshold-based methods depending on dataset availability.

---

# Machine Learning Models

Possible algorithms include

- Random Forest
- XGBoost
- Gradient Boosting
- Support Vector Machine
- LSTM Neural Network
- GRU
- Transformer Time-Series Models

Current implementation primarily uses:

- Random Forest Classifier

---

# Model Evaluation

Metrics used

- Accuracy
- Precision
- Recall
- F1 Score
- ROC-AUC
- Confusion Matrix

Regression metrics (if predicting flare intensity)

- RMSE
- MAE

---

# Project Structure

```
Solar-Flare-Prediction/
│
├── data/
│   ├── raw/
│   ├── processed/
│   └── labels/
│
├── notebooks/
│
├── src/
│   ├── preprocessing.py
│   ├── feature_engineering.py
│   ├── train.py
│   ├── predict.py
│   └── visualization.py
│
├── models/
│   └── random_forest.pkl
│
├── figures/
│
├── results/
│
├── requirements.txt
│
└── README.md
```

---

# Technologies Used

Programming

- Python 3.x

Libraries

- Astropy
- NumPy
- Pandas
- Matplotlib
- Scikit-learn
- Joblib
- SciPy

Data Format

- FITS
- CSV

Development Environment

- VS Code
- Jupyter Notebook

---

# Installation

Clone the repository

```bash
git clone https://github.com/username/Solar-Flare-Prediction.git
```

Move into project directory

```bash
cd Solar-Flare-Prediction
```

Install dependencies

```bash
pip install -r requirements.txt
```

---

# Example Workflow

1. Download SoLEXS and HEL1OS FITS files.
2. Extract observation tables.
3. Convert FITS to CSV.
4. Merge both datasets using timestamps.
5. Generate features.
6. Train Machine Learning model.
7. Predict future flare activity.
8. Evaluate results.

---

# Future Improvements

- Deep Learning using LSTM and Transformers
- Real-time prediction pipeline
- Integration with GOES flare catalogs
- Space weather alert system
- Interactive web dashboard
- Real-time Aditya-L1 data ingestion
- Multi-payload fusion (SUIT, VELC, SoLEXS, HEL1OS)

---

# Applications

- Space Weather Forecasting
- Satellite Protection
- GPS Reliability
- Power Grid Monitoring
- Radio Communication
- Aviation Safety
- Scientific Research
- Solar Physics

---

# References

1. ISRO Aditya-L1 Mission
2. SoLEXS Instrument Documentation
3. HEL1OS Instrument Documentation
4. Astropy Documentation
5. Scikit-learn Documentation

---

# Author

**Alan S**

Electronics and Communication Engineering

Project: **Solar Flare Prediction using Aditya-L1 SoLEXS and HEL1OS Data**

---

## License

This project is intended for educational and research purposes.
