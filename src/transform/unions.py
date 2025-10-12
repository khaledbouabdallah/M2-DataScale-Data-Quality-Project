import pandas as pd
from src.config.settings import setup_logging

logger = setup_logging(__name__)


def union_population_sources(df_paris: pd.DataFrame, df_evry: pd.DataFrame) -> pd.DataFrame:
    """
    Union Population data from Paris and Evry with Source column (id also need to be prefixed).
    """
    df_paris['Source'] = 'Paris'
    df_evry['Source'] = 'Evry'
    df_paris['ID'] = 'Paris_' + df_paris['ID'].astype(str)
    df_evry['ID'] = 'Evry_' + df_evry['ID'].astype(str)

    df = pd.concat([df_paris, df_evry], ignore_index=True)
    df['ID_Source'] = df['ID']
    df.drop(columns=['ID'], inplace=True)
    
    return df


def union_consommation_sources(df_paris: pd.DataFrame, df_evry: pd.DataFrame) -> pd.DataFrame:
    """
    Union Consommation data from Paris and Evry with Source column (id also need to be prefixed).
    """
    df_paris['Source'] = 'Paris'
    df_evry['Source'] = 'Evry'
    df_paris['ID_Adr'] = 'Paris_' + df_paris['ID_Adr'].astype(str)
    df_evry['ID_Adr'] = 'Evry_' + df_evry['ID_Adr'].astype(str)
    df = pd.concat([df_paris, df_evry], ignore_index=True)
    df['ID_Source'] = df['ID_Adr']
    df.drop(columns=['ID_Adr'], inplace=True)
    return df
