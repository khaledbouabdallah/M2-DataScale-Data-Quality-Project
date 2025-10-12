"""Application configuration and settings"""
from pathlib import Path
import os
import logging

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent.parent
DATA_DIR = PROJECT_ROOT / "data"
MOCK_DATA_DIR = DATA_DIR / "mock"
RAW_DATA_DIR = DATA_DIR / "raw"
OUTPUT_DIR = DATA_DIR / "output"
LOGS_DIR = PROJECT_ROOT / "logs"

# Create directories if they don't exist
for directory in [MOCK_DATA_DIR, RAW_DATA_DIR, OUTPUT_DIR, LOGS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# Environment variable to switch between mock and real data
USE_MOCK_DATA = os.getenv('USE_MOCK_DATA', 'true').lower() == 'true'
DATA_SOURCE_DIR = MOCK_DATA_DIR if USE_MOCK_DATA else RAW_DATA_DIR

# Data files - Paris (Source S1)
POPULATION_PARIS_FILE = DATA_SOURCE_DIR / "population_paris.csv"
CONSOMMATION_PARIS_FILE = DATA_SOURCE_DIR / "consommation_paris.csv"

# Data files - Evry (Source S2)
POPULATION_EVRY_FILE = DATA_SOURCE_DIR / "population_evry.csv"
CONSOMMATION_EVRY_FILE = DATA_SOURCE_DIR / "consommation_evry.csv"

# Reference files (Source S3, S4)
CSP_FILE = DATA_SOURCE_DIR / "csp_reference.csv"
IRIS_FILE = DATA_SOURCE_DIR / "iris_reference.csv"

# Target table names
TARGET_TABLES = {
    'csp': 'Consommation_CSP',
    'iris_paris': 'Consommation_IRIS_Paris',
    'iris_evry': 'Consommation_IRIS_Evry',
}

# Logging configuration
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
LOG_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'


def setup_logging(name: str = __name__) -> logging.Logger:
    """
    Setup logger with consistent formatting.
    
    Args:
        name: Logger name (usually __name__ of the module)
        
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    
    # Avoid adding handlers multiple times
    if logger.hasHandlers():
        return logger
    
    logger.setLevel(LOG_LEVEL)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(LOG_LEVEL)
    console_formatter = logging.Formatter(LOG_FORMAT, LOG_DATE_FORMAT)
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    return logger