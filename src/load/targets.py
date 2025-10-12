import pandas as pd
from pathlib import Path
from src.config.settings import OUTPUT_DIR, setup_logging, TARGET_FILES

logger = setup_logging(__name__)


def save_to_csv(df: pd.DataFrame, filename: str) -> Path:
    """
    Save DataFrame to CSV in output directory.
    
    Args:
        df (pd.DataFrame): The DataFrame to save.
        filename (str): The name of the output CSV file.
    """
    output_path = OUTPUT_DIR / filename
    df.to_csv(output_path, index=False)
    return output_path


def save_consommation_csp(df: pd.DataFrame) -> Path:
    """Save consommation by CSP to CSV"""
    logger.info("Saving consommation by CSP")
    return save_to_csv(df, TARGET_FILES['csp'])


def save_consommation_iris_paris(df: pd.DataFrame) -> Path:
    """Save consommation by IRIS (Paris) to CSV"""
    logger.info("Saving consommation by IRIS (Paris)")
    return save_to_csv(df, TARGET_FILES['iris_paris'])


def save_consommation_iris_evry(df: pd.DataFrame) -> Path:
    """Save consommation by IRIS (Evry) to CSV"""
    logger.info("Saving consommation by IRIS (Evry)")
    return save_to_csv(df, TARGET_FILES['iris_evry'])