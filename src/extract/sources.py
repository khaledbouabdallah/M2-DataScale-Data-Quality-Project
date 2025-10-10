"""Data extraction functions"""
import pandas as pd
from pathlib import Path

def read_population_csv(filepath: str) -> pd.DataFrame:
    """Read Population CSV file"""
    path = Path(filepath)
    
    if not path.exists():
        raise FileNotFoundError(f"CSV file not found: {filepath}")
    
    df = pd.read_csv(path, dtype=str)  # Read all as string initially
    
    print(f"✅ Loaded {len(df)} rows from {filepath}")
    return df

def read_consommation_csv(filepath: str) -> pd.DataFrame:
    """Read Consommation CSV file"""
    path = Path(filepath)
    
    if not path.exists():
        raise FileNotFoundError(f"CSV file not found: {filepath}")
    
    df = pd.read_csv(path, dtype=str)
    
    print(f"✅ Loaded {len(df)} rows from {filepath}")
    return df