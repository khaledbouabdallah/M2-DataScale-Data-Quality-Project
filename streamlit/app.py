import streamlit as st
import psycopg2
import pandas as pd
import os

# Database connection parameters
DB_CONFIG = {
    'host': os.getenv('POSTGRES_HOST', 'localhost'),
    'port': os.getenv('POSTGRES_PORT', '5432'),
    'database': os.getenv('POSTGRES_DB', 'airflow'),
    'user': os.getenv('POSTGRES_USER', 'airflow'),
    'password': os.getenv('POSTGRES_PASSWORD', 'airflow')
}

@st.cache_resource
def get_connection():
    """Create database connection"""
    return psycopg2.connect(**DB_CONFIG)

def load_metrics():
    """Load quality metrics from database"""
    conn = get_connection()
    query = """
        SELECT 
            table_name,
            column_name,
            metric_type,
            metric_value,
            source,
            timestamp
        FROM data_quality.metrics
        ORDER BY timestamp DESC
    """
    return pd.read_sql(query, conn)

def load_issues():
    """Load quality issues from database"""
    conn = get_connection()
    query = """
        SELECT 
            table_name,
            issue_type,
            severity,
            COUNT(*) as count
        FROM data_quality.issues
        GROUP BY table_name, issue_type, severity
        ORDER BY count DESC
    """
    return pd.read_sql(query, conn)

# Streamlit UI
st.set_page_config(page_title="Data Quality Dashboard", layout="wide")

st.title("📊 Data Quality Dashboard")
st.markdown("Energy Consumption Data - Quality Metrics")

# Sidebar
st.sidebar.header("Filters")
selected_source = st.sidebar.multiselect(
    "Select Source",
    options=["Paris", "Evry", "All"],
    default=["All"]
)

# Main content
tab1, tab2, tab3 = st.tabs(["📈 Metrics Overview", "⚠️ Issues", "📋 Raw Data"])

with tab1:
    st.header("Quality Metrics")
    
    try:
        df_metrics = load_metrics()
        
        if df_metrics.empty:
            st.info("No metrics available yet. Run the ETL pipeline first.")
        else:
            # Display metrics summary
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Total Metrics Collected", len(df_metrics))
            
            with col2:
                latest_metric = df_metrics.iloc[0]['timestamp']
                st.metric("Last Updated", latest_metric.strftime("%Y-%m-%d %H:%M"))
            
            with col3:
                unique_tables = df_metrics['table_name'].nunique()
                st.metric("Tables Monitored", unique_tables)
            
            # Metrics by table
            st.subheader("Metrics by Table")
            st.dataframe(df_metrics, use_container_width=True)
            
    except Exception as e:
        st.error(f"Error loading metrics: {e}")

with tab2:
    st.header("Quality Issues")
    
    try:
        df_issues = load_issues()
        
        if df_issues.empty:
            st.success("No quality issues detected!")
        else:
            st.dataframe(df_issues, use_container_width=True)
            
    except Exception as e:
        st.error(f"Error loading issues: {e}")

with tab3:
    st.header("Raw Metrics Data")
    
    try:
        df_metrics = load_metrics()
        st.dataframe(df_metrics, use_container_width=True)
        
        # Download button
        csv = df_metrics.to_csv(index=False)
        st.download_button(
            label="Download Metrics CSV",
            data=csv,
            file_name="quality_metrics.csv",
            mime="text/csv"
        )
        
    except Exception as e:
        st.error(f"Error: {e}")

# Footer
st.markdown("---")
st.markdown("**M2 DataScale 2025/2026**")