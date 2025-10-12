"""ETL Pipeline using TaskFlow API (Airflow 2.0+)"""
from airflow.decorators import dag, task, task_group
from datetime import datetime
import pandas as pd

from src.config.settings import (
    POPULATION_EVRY_FILE, 
    POPULATION_PARIS_FILE, 
    CONSOMMATION_EVRY_FILE, 
    CONSOMMATION_PARIS_FILE, 
    CSP_FILE, 
    IRIS_FILE,
    setup_logging
)
from src.extract.sources import read_csv_with_schema
from src.config.schemas import (
    POPULATION_SCHEMA,
    CONSOMMATION_SCHEMA,
    CSP_SCHEMA,
    IRIS_SCHEMA
)
from src.transform.unions import union_population_sources, union_consommation_sources
from src.transform.normalize import (
    normalize_population_addresses,
    normalize_consommation_addresses,
    normalize_iris_streets_postalcodes
)
from src.transform.consumption_by_csp import build_consommation_csp
from src.transform.consumption_by_iris import build_consommation_iris
from src.load.targets import (
    save_consommation_csp,
    save_consommation_iris_paris,
    save_consommation_iris_evry
)

logger = setup_logging(__name__)


@dag(
    dag_id='etl_pipeline',
    start_date=datetime(2025, 1, 1),
    schedule_interval=None,
    catchup=False,
    description='ETL Pipeline for Energy Consumption Data',
    tags=['etl', 'energy', 'taskflow'],
    doc_md="""
    # Energy Consumption ETL Pipeline
    
    ## Architecture
    Union-first approach: merge Paris + Evry sources early, transform once.
    
    ## Stages
    1. **Extract**: Read all sources (Population, Consommation, References)
    2. **Transform**: Union, normalize, join, aggregate
    3. **Load**: Save target tables to CSV
    
    ## Targets
    - `Consommation_CSP`: Consumption by socio-professional category
    - `Consommation_IRIS_Paris`: Consumption by geographic zone (Paris)
    - `Consommation_IRIS_Evry`: Consumption by geographic zone (Evry)
    """
)
def etl_pipeline():
    
    # ============================================
    # EXTRACT LAYER (TaskGroup for organization)
    # ============================================
    
    @task_group(group_id='extract')
    def extract_sources():
        """Extract all data sources (parallel execution)"""
        
        @task
        def extract_population_sources() -> dict:
            """Extract Population from Paris and Evry"""
            logger.info("Extracting population sources")
            
            df_paris = read_csv_with_schema(POPULATION_PARIS_FILE, POPULATION_SCHEMA)
            df_evry = read_csv_with_schema(POPULATION_EVRY_FILE, POPULATION_SCHEMA)
            
            logger.info("Extracted population sources", extra={
                'paris_rows': len(df_paris),
                'evry_rows': len(df_evry)
            })
            
            return {
                'paris': df_paris.to_dict('records'),
                'evry': df_evry.to_dict('records')
            }
        
        @task
        def extract_consommation_sources() -> dict:
            """Extract Consommation from Paris and Evry"""
            logger.info("Extracting consommation sources")
            
            df_paris = read_csv_with_schema(CONSOMMATION_PARIS_FILE, CONSOMMATION_SCHEMA)
            df_evry = read_csv_with_schema(CONSOMMATION_EVRY_FILE, CONSOMMATION_SCHEMA)
            
            logger.info("Extracted consommation sources", extra={
                'paris_rows': len(df_paris),
                'evry_rows': len(df_evry)
            })
            
            return {
                'paris': df_paris.to_dict('records'),
                'evry': df_evry.to_dict('records')
            }
        
        @task
        def extract_csp_reference() -> list[dict]:
            """Extract CSP reference data"""
            logger.info("Extracting CSP reference")
            
            df = read_csv_with_schema(CSP_FILE, CSP_SCHEMA)
            
            logger.info("Extracted CSP reference", extra={'rows': len(df)})
            
            return df.to_dict('records')
        
        @task
        def extract_iris_reference() -> list[dict]:
            """Extract IRIS reference data"""
            logger.info("Extracting IRIS reference")
            
            df = read_csv_with_schema(IRIS_FILE, IRIS_SCHEMA)
            
            logger.info("Extracted IRIS reference", extra={'rows': len(df)})
            
            return df.to_dict('records')
        
        # ✅ Return individual tasks, not a dict
        return {
            'population': extract_population_sources(),
            'consommation': extract_consommation_sources(),
            'csp': extract_csp_reference(),
            'iris': extract_iris_reference()
        }
    
    # ============================================
    # TRANSFORM LAYER (TaskGroup for organization)
    # ============================================
    
    @task_group(group_id='transform')
    def transform_data(population: dict, consommation: dict, csp: dict, iris: dict):
        """Transform: union, normalize, join, aggregate"""

        @task
        def union(population: dict, consommation: dict) -> dict:
            logger.info("Starting staging: union")
            # Reconstruct DataFrames
            pop_paris = pd.DataFrame(population['paris'])
            pop_evry = pd.DataFrame(population['evry'])
            cons_paris = pd.DataFrame(consommation['paris'])
            cons_evry = pd.DataFrame(consommation['evry'])
            
            # Union
            logger.info("Unioning sources")
            population_df = union_population_sources(pop_paris, pop_evry)
            consommation_df = union_consommation_sources(cons_paris, cons_evry)
                        
            # Log the row counts as separate messages to ensure visibility
            logger.info(f"Union complete - Population rows: {len(population_df)}")
            logger.info(f"Union complete - Consommation rows: {len(consommation_df)}")
            
            return {
                'population': population_df.to_dict('records'),
                'consommation': consommation_df.to_dict('records')
            }
            

        @task
        def normalize_addresses(population: dict, consommation: dict, iris: dict) -> dict:
            """normalize addresses"""
            logger.info("Starting staging: normalize addresses")

            population_df = pd.DataFrame(population)
            consommation_df = pd.DataFrame(consommation)
            iris_df = pd.DataFrame(iris)

            # Normalize addresses
            population_df = normalize_population_addresses(population_df)
            consommation_df = normalize_consommation_addresses(consommation_df)
            iris_df = normalize_iris_streets_postalcodes(iris_df)

            logger.info("Staging complete")
            logger.info(f"Normalized addresses - Population rows: {len(population_df)}")
            logger.info(f"Normalized addresses - Consumption rows: {len(consommation_df)}")
            logger.info(f"Normalized addresses - IRIS rows: {len(iris_df)}")
            
            return {
                'population': population_df.to_dict('records'),
                'consommation': consommation_df.to_dict('records'),
                'iris': iris_df.to_dict('records')
            }

        @task
        def build_csp_target(population: dict, consommation: dict, csp: dict) -> list[dict]:
            """Build Consommation_CSP target"""
            logger.info("Building Consommation_CSP target")

            population = pd.DataFrame(population)
            consommation = pd.DataFrame(consommation)
            csp_df = pd.DataFrame(csp)
            
            target = build_consommation_csp(population, consommation, csp_df)
            
            logger.info("Consommation_CSP complete")
            
            return target.to_dict('records')
        
        @task
        def build_iris_targets(consommation: dict, iris: dict) -> dict:
            """Build Consommation_IRIS targets"""
            logger.info("Building Consommation_IRIS targets")

            consommation = pd.DataFrame(consommation)
            iris_df = pd.DataFrame(iris)
            
            targets = build_consommation_iris(consommation, iris_df)
            
            logger.info("Consommation_IRIS complete", extra={
                'paris_rows': len(targets['paris']),
                'evry_rows': len(targets['evry'])
            })
            
            return {
                'paris': targets['paris'].to_dict('records'),
                'evry': targets['evry'].to_dict('records')
            }
        
        # ✅ Explicit dependencies within the group
        staged = union(population, consommation)
        staged = normalize_addresses(staged['population'], staged['consommation'], iris)
        target_csp = build_csp_target(staged['population'], staged['consommation'], csp)
        targets_iris = build_iris_targets(staged['consommation'], staged['iris'])
        
        return {
            'csp': target_csp,
            'iris': targets_iris
        }
    
    # ============================================
    # LOAD LAYER (TaskGroup for organization)
    # ============================================
    
    @task_group(group_id='load')
    def load_targets(target_csp: dict, targets_iris: dict):
        """Save all target tables (parallel execution)"""
        
        @task
        def load_csp_target(target: dict):
            """Save Consommation_CSP"""
            logger.info("Saving Consommation_CSP")
            
            df = pd.DataFrame(target)
            path = save_consommation_csp(df)
            
            logger.info("Saved Consommation_CSP", extra={'path': str(path)})
        
        @task
        def load_iris_targets(targets: dict):
            """Save Consommation_IRIS targets"""
            logger.info("Saving Consommation_IRIS targets")
            
            df_paris = pd.DataFrame(targets['paris'])
            df_evry = pd.DataFrame(targets['evry'])
            
            path_paris = save_consommation_iris_paris(df_paris)
            path_evry = save_consommation_iris_evry(df_evry)
            
            logger.info("Saved Consommation_IRIS targets", extra={
                'paris_path': str(path_paris),
                'evry_path': str(path_evry)
            })
        
        # ✅ Both can run in parallel (no dependencies between them)
        load_csp_target(target_csp)
        load_iris_targets(targets_iris)
    
    # ============================================
    # PIPELINE DEFINITION (Correct Dependencies)
    # ============================================
    
    # Extract all sources (returns dict of individual task results)
    sources = extract_sources()
    
    # Transform with explicit parameters (Airflow tracks dependencies correctly)
    targets = transform_data(
        population=sources['population'],
        consommation=sources['consommation'],
        csp=sources['csp'],
        iris=sources['iris']
    )
    
    # Load targets (parallel)
    load_targets(
        target_csp=targets['csp'],
        targets_iris=targets['iris']
    )


# Instantiate the DAG
dag_instance = etl_pipeline()