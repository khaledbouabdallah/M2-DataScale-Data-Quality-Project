"""Simple ETL workflow: Read CSV → Validate → Save Metrics"""
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import sys
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.extract.sources import read_population_csv
from src.quality.checks import run_quality_checks

# Default arguments
default_args = {
    'owner': 'datascale',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# DAG definition
dag = DAG(
    'simple_quality_workflow',
    default_args=default_args,
    description='Simple workflow to test quality checks on Population CSV',
    schedule_interval=None,  # Manual trigger only
    catchup=False,
    tags=['quality', 'test']
)

def extract_data(**context):
    """Task 1: Extract data from CSV"""
    print("📥 Starting data extraction...")
    
    # Read CSV file
    df = read_population_csv('/opt/airflow/data/population_test.csv')
    
    print(f"📊 Extracted {len(df)} rows with {len(df.columns)} columns")
    print(f"Columns: {list(df.columns)}")
    
    # Push data to XCom for next task
    context['ti'].xcom_push(key='dataframe_shape', value=df.shape)
    context['ti'].xcom_push(key='csv_path', value='/opt/airflow/data/population_test.csv')
    
    return "extraction_complete"

def validate_data(**context):
    """Task 2: Run quality checks"""
    print("🔍 Starting data validation...")
    
    # Pull data path from previous task
    csv_path = context['ti'].xcom_pull(task_ids='extract_data', key='csv_path')
    
    # Read data again (in production, you'd pass the actual dataframe)
    df = read_population_csv(csv_path)
    
    # Run quality checks
    results = run_quality_checks(df, table_name='Population', source='Test')
    
    # Summary
    print("\n" + "="*50)
    print("📈 QUALITY CHECK SUMMARY")
    print("="*50)
    print(f"Total rows: {len(df)}")
    print(f"Completeness checks: {len(results['completeness'])} columns")
    print(f"Format checks: {len(results['conformity'])} columns")
    print(f"Duplicates found: {results['duplicates']}")
    print("="*50)
    
    return "validation_complete"

def report_results(**context):
    """Task 3: Print summary"""
    print("\n" + "🎉"*20)
    print("✅ ETL WORKFLOW COMPLETED SUCCESSFULLY")
    print("🎉"*20)
    print("\n📊 Check Streamlit dashboard at http://localhost:8501")
    print("🔍 Check Airflow UI at http://localhost:8080")
    
    return "workflow_complete"

# Define tasks
task_extract = PythonOperator(
    task_id='extract_data',
    python_callable=extract_data,
    dag=dag,
)

task_validate = PythonOperator(
    task_id='validate_data',
    python_callable=validate_data,
    dag=dag,
)

task_report = PythonOperator(
    task_id='report_results',
    python_callable=report_results,
    dag=dag,
)

# Set task dependencies
task_extract >> task_validate >> task_report