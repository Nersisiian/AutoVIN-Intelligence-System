import pandas as pd
from sklearn.preprocessing import LabelEncoder
import re

def extract_features(vin: str) -> dict:
    """Extract WMI, VDS, VIS, Year, Manufacturer from VIN."""
    vin = vin.upper().strip()
    if len(vin) != 17:
        raise ValueError("VIN must be 17 characters")
    wmi = vin[:3]
    vds = vin[3:8]
    vis = vin[9:]
    year_char = vin[9]
    year_map = {
        'A': 2010, 'B': 2011, 'C': 2012, 'D': 2013, 'E': 2014,
        'F': 2015, 'G': 2016, 'H': 2017, 'J': 2018, 'K': 2019,
        'L': 2020, 'M': 2021, 'N': 2022, 'P': 2023, 'R': 2024,
        'S': 2025, 'T': 2026, 'V': 2027, 'W': 2028, 'X': 2029,
        'Y': 2030, '1': 2031, '2': 2032, '3': 2033, '4': 2034,
        '5': 2035, '6': 2036, '7': 2037, '8': 2038, '9': 2039,
    }
    year = year_map.get(year_char, 0)
    return {
        "wmi": wmi,
        "vds": vds,
        "vis": vis,
        "year": year,
        "manufacturer": wmi,
    }

def load_training_data(filepath: str = "data/vin_dataset.csv"):
    df = pd.read_csv(filepath)
    features = []
    targets_trim = []
    targets_engine = []
    targets_transmission = []
    targets_class = []
    for _, row in df.iterrows():
        try:
            feat = extract_features(row['vin'])
            features.append(feat)
            targets_trim.append(row.get('trim', 'Unknown'))
            targets_engine.append(row.get('engine', 'Unknown'))
            targets_transmission.append(row.get('transmission', 'Unknown'))
            targets_class.append(row.get('vehicle_class', 'Unknown'))
        except:
            continue
    return pd.DataFrame(features), targets_trim, targets_engine, targets_transmission, targets_class