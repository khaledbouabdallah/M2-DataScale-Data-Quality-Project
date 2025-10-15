import pandas as pd
from typing import Dict
from src.config.settings import setup_logging

logger = setup_logging(__name__)


def join_consommation_with_iris(consommation_df: pd.DataFrame, iris_df: pd.DataFrame) -> pd.DataFrame:
    """
    Join Consommation with IRIS reference to add ID_IRIS.
    
    INNER JOIN on consommation.ID_IRIS == iris.ID_IRIS
    """
    
    # inner join on Nom_Rue = ID_Rue and Code_Postal = ID_Ville
    result = consommation_df.merge(
        iris_df[['ID_Iris', 'ID_Rue', 'ID_Ville']],
        left_on=['Nom_Rue', 'Code_Postal'],
        right_on=['ID_Rue', 'ID_Ville'],
        how='inner'
    )
    
    # save df to csv for debugging
    logger.info(f"Joined consommation with iris: {len(result)} rows")
    return result


def aggregate_consumption_by_iris(merged_df: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregate consumption by IRIS.
    
    GROUP BY ID_Iris
    - AVG(NB_KW_Jour * 365) as Conso_moyenne_annuelle
    """
    agg_df = merged_df.groupby('ID_Iris', as_index=False).agg(
        Conso_moyenne_annuelle=pd.NamedAgg(column='NB_KW_Jour', aggfunc=lambda x: (x * 365).sum()),
        Source=pd.NamedAgg(column='Source', aggfunc='first')
    )
    
    return agg_df

def build_consommation_iris(consommation_df: pd.DataFrame, iris_df: pd.DataFrame) -> Dict[str, pd.DataFrame]:
    """
    Build Consommation by IRIS dataset.
    Steps:
    1. Join consommation with iris to get ID_Iris
    2. Aggregate consumption by IRIS
    
    Returns dict with keys 'paris' and 'evry'
    """
    # Join consommation with iris
    merged_df = join_consommation_with_iris(consommation_df, iris_df)
    
    # Aggregate by IRIS
    result_df = aggregate_consumption_by_iris(merged_df)
    
    paris_df = result_df[result_df['Source'] == 'Paris']
    evry_df = result_df[result_df['Source'] == 'Evry']
    
    logger.info(f"Built consommation by IRIS - Paris rows: {len(paris_df)}, Evry rows: {len(evry_df)}")
    
    return {
        'paris': paris_df,
        'evry': evry_df
    }