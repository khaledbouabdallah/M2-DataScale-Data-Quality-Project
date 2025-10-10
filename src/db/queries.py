"""Database query utilities for quality metrics"""
from datetime import datetime
from sqlalchemy import text
from .connection import get_engine

def save_quality_metric(table_name: str, column_name: str, metric_type: str, 
                       metric_value: float, source: str = None):
    """Save a quality metric to the database"""
    engine = get_engine()
    
    query = text("""
        INSERT INTO data_quality.metrics 
        (table_name, column_name, metric_type, metric_value, source, timestamp)
        VALUES (:table_name, :column_name, :metric_type, :metric_value, :source, :timestamp)
    """)
    
    with engine.begin() as conn:  # Changed from connect() to begin()
        conn.execute(query, {
            'table_name': table_name,
            'column_name': column_name,
            'metric_type': metric_type,
            'metric_value': metric_value,
            'source': source,
            'timestamp': datetime.now()
        })

def save_quality_issue(table_name: str, row_id: str, issue_type: str,
                      issue_description: str, severity: str = 'medium',
                      source: str = None):
    """Save a quality issue to the database"""
    engine = get_engine()
    
    query = text("""
        INSERT INTO data_quality.issues 
        (table_name, row_id, issue_type, issue_description, severity, source, timestamp)
        VALUES (:table_name, :row_id, :issue_type, :issue_description, :severity, :source, :timestamp)
    """)
    
    with engine.begin() as conn:  # Changed from connect() to begin()
        conn.execute(query, {
            'table_name': table_name,
            'row_id': row_id,
            'issue_type': issue_type,
            'issue_description': issue_description,
            'severity': severity,
            'source': source,
            'timestamp': datetime.now()
        })

def get_latest_metrics(table_name: str = None, limit: int = 100):
    """Retrieve latest quality metrics"""
    engine = get_engine()
    
    if table_name:
        query = text("""
            SELECT * FROM data_quality.metrics 
            WHERE table_name = :table_name
            ORDER BY timestamp DESC 
            LIMIT :limit
        """)
        params = {'table_name': table_name, 'limit': limit}
    else:
        query = text("""
            SELECT * FROM data_quality.metrics 
            ORDER BY timestamp DESC 
            LIMIT :limit
        """)
        params = {'limit': limit}
    
    with engine.connect() as conn:
        result = conn.execute(query, params)
        return result.fetchall()