"""Generate Consommation_CSP target table"""
import pandas as pd
from src.config.settings import setup_logging

logger = setup_logging(__name__)


def join_population_with_csp(population_df: pd.DataFrame, csp_df: pd.DataFrame) -> pd.DataFrame:
    """
    Join Population with CSP reference to add Salaire_Moyen.
    
    INNER JOIN on population.CSP == csp.ID_CSP
    """
    logger.info(f"Joining {len(population_df)} population records with CSP reference")
    
    result = population_df.merge(
        csp_df[['ID_CSP', 'Salaire_Moyen']],
        left_on='CSP',
        right_on='ID_CSP',
        how='inner'
    )
    
    dropped = len(population_df) - len(result)
    if dropped > 0:
        logger.warning(f"Dropped {dropped} records with invalid CSP codes")
    
    logger.info(f"✅ Enriched {len(result)} records with salary data")
    return result


def join_population_with_consumption(population_df: pd.DataFrame, 
                                     consommation_df: pd.DataFrame) -> pd.DataFrame:
    """
    Join Population with Consommation on normalized address.
    
    INNER JOIN on Adresse
    """
    logger.info(f"Joining population with consumption data on address")
    
    result = population_df.merge(
        consommation_df[['Adresse', 'NB_KW_Jour']],
        on='Adresse',
        how='inner'
    )
    
    dropped = len(population_df) - len(result)
    if dropped > 0:
        logger.warning(f"Dropped {dropped} records without matching address")
    
    logger.info(f"✅ Matched {len(result)} records")
    return result


def aggregate_consumption_by_csp(merged_df: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregate consumption by CSP category.
    
    GROUP BY CSP
    - AVG(NB_KW_Jour * 365) as Conso_moyenne_annuelle
    - MAX(Salaire_Moyen) as Salaire_Moyen (same for all in group)
    """
    logger.info("Aggregating consumption by CSP category")
    
    result = merged_df.groupby('CSP').agg({
        'NB_KW_Jour': lambda x: (x * 365).mean(),  # Annual average
        'Salaire_Moyen': 'max'  # Reference value (same for all)
    }).reset_index()
    
    result.columns = ['ID_CSP', 'Conso_moyenne_annuelle', 'Salaire_Moyen']
    
    logger.info(f"✅ Generated Consommation_CSP with {len(result)} categories")
    return result


def build_consommation_csp(population_df: pd.DataFrame,
                           consommation_df: pd.DataFrame,
                           csp_df: pd.DataFrame) -> pd.DataFrame:
    """
    Main function to build Consommation_CSP target table.
    
    Pipeline:
    1. Enrich population with CSP salary data
    2. Join population with consumption on address
    3. Aggregate by CSP category
    
    Returns:
        DataFrame with columns: ID_CSP, Conso_moyenne_annuelle, Salaire_Moyen
    """
    logger.info("Building Consommation_CSP target table")
    
    # Step 1: Enrich with CSP
    population_enriched = join_population_with_csp(population_df, csp_df)
    
    # Step 2: Join with consumption
    merged = join_population_with_consumption(population_enriched, consommation_df)
    
    # Step 3: Aggregate
    target = aggregate_consumption_by_csp(merged)
    
    logger.info(f"✅ Consommation_CSP complete: {len(target)} rows")
    return target