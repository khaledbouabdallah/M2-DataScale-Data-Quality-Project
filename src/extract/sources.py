"""Data extraction functions"""
import pandas as pd
from pathlib import Path
from src.config.schemas import TableSchema, validate_required_columns
from src.config.settings import setup_logging


from src.config.schemas import POPULATION_SCHEMA, CONSOMMATION_SCHEMA, CSP_SCHEMA, IRIS_SCHEMA

logger = setup_logging(__name__)


def read_csv_with_schema(filepath: str | Path, schema: TableSchema) -> pd.DataFrame:
    """
    Generic CSV reader with schema validation.
    
    Args:
        filepath: Path to CSV file
        schema: TableSchema defining expected structure
        
    Returns:
        DataFrame with validated schema
        
    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If required columns are missing
        
    Example:
        >>> from src.config.schemas import POPULATION_SCHEMA
        >>> df = read_csv_with_schema("data/population.csv", POPULATION_SCHEMA)
    """
    path = Path(filepath)
    
    logger.info(f"Reading {schema.name} from {path}")
    
    if not path.exists():
        logger.error(f"File not found: {filepath}")
        raise FileNotFoundError(f"CSV file not found: {filepath}")
    
    # Read with correct dtypes from schema
    df = pd.read_csv(path, dtype=schema.dtypes)
    logger.debug(f"Read {len(df)} rows, {len(df.columns)} columns")
    
    # Validate required columns exist
    try:
        validate_required_columns(df.columns.tolist(), schema)
        logger.info(f"✅ Successfully loaded {len(df)} rows from {path.name}")
    except ValueError as e:
        logger.error(f"Schema validation failed: {e}")
        raise
    
    return df


def read_population_csv(filepath: str | Path) -> pd.DataFrame:
    """Read population CSV with predefined schema"""
    return read_csv_with_schema(filepath, POPULATION_SCHEMA)

def read_consommation_csv(filepath: str | Path) -> pd.DataFrame:
    """Read consommation CSV with predefined schema"""
    return read_csv_with_schema(filepath, CONSOMMATION_SCHEMA)

def read_csp_csv(filepath: str | Path) -> pd.DataFrame:
    """Read CSP CSV with predefined schema"""
    return read_csv_with_schema(filepath, CSP_SCHEMA)

def read_iris_csv(filepath: str | Path) -> pd.DataFrame:
    """Read IRIS CSV with predefined schema"""
    return read_csv_with_schema(filepath, IRIS_SCHEMA)