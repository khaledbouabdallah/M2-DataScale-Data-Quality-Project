"""Address and string normalization functions"""
import pandas as pd
import re

def _normalize_string(text: str) -> str:
    """
    Normalize a string for matching:
    - Strip whitespace
    - Convert to lowercase
    - Remove extra spaces
    """
    if pd.isna(text):
        return ""
    
    text = str(text).strip().lower()
    text = re.sub(r'\s+', ' ', text)  # Replace multiple spaces with single space
    return text


def _create_full_address(row: pd.Series) -> str | None:
    """
    Create standardized full address from components.
    
    Input: row with columns N, Nom_Rue, Code_Postal
    Output: "12 rue victor hugo, 75001"
    
    Returns None if any component is missing.
    """
    if pd.isna(row.get('N')) or pd.isna(row.get('Nom_Rue')) or pd.isna(row.get('Code_Postal')):
        return None
    
    n = str(row['N']).strip()
    rue = _normalize_string(row['Nom_Rue'])
    postal = str(row['Code_Postal']).strip()
    
    return f"{n} {rue}, {postal}"


def _normalize_population_address(address: str) -> str | None:
    """
    Normalize Population.Adresse field to match Consommation format.
    
    Input: "12 Rue Victor Hugo, 75001"
    Output: "12 rue victor hugo, 75001"
    """
    if pd.isna(address):
        return None
    
    # Split by comma to get street and postal code
    parts = address.split(',')
    if len(parts) != 2:
        return None  # Invalid format
    
    street = _normalize_string(parts[0])
    postal = parts[1].strip()
    
    return f"{street}, {postal}"


def normalize_consommation_addresses(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add normalized 'Adresse' column to Consommation dataframe.
    
    Input: DataFrame with columns N, Nom_Rue, Code_Postal
    Output: DataFrame with additional 'Adresse' column
    """
    df = df.copy()
    df['Code_Postal'] = df['Code_Postal'].apply(_normalize_string)
    df['Nom_Rue'] = df['Nom_Rue'].apply(_normalize_string)
    df['Adresse'] = df.apply(_create_full_address, axis=1)
    return df


def normalize_population_addresses(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normalize existing 'Adresse' column in Population dataframe.
    
    Input: DataFrame with 'Adresse' column
    Output: DataFrame with normalized 'Adresse' column
    """
    df = df.copy()
    df['Adresse'] = df['Adresse'].apply(_normalize_population_address)
    return df

def normalize_iris_streets_postalcodes(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normalize 'ID_Rue' in IRIS dataframe for matching.

    Input: DataFrame with 'ID_Rue' column
    Output: DataFrame with normalized 'ID_Rue' column
    """

    df = df.copy()
    df['ID_Rue'] = df['ID_Rue'].apply(_normalize_string)
    df['ID_Ville'] = df['ID_Ville'].apply(_normalize_string)
    return df