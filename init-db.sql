-- Create separate schema for data quality metrics
CREATE SCHEMA IF NOT EXISTS data_quality;

-- Grant permissions to airflow user
GRANT ALL PRIVILEGES ON SCHEMA data_quality TO airflow;

-- Example table for quality metrics (modify as needed)
CREATE TABLE IF NOT EXISTS data_quality.metrics (
    id SERIAL PRIMARY KEY,
    table_name VARCHAR(100) NOT NULL,
    column_name VARCHAR(100),
    metric_type VARCHAR(50) NOT NULL,
    metric_value NUMERIC,
    source VARCHAR(50),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_metrics_table ON data_quality.metrics(table_name);
CREATE INDEX idx_metrics_timestamp ON data_quality.metrics(timestamp);

-- Example table for quality issues
CREATE TABLE IF NOT EXISTS data_quality.issues (
    id SERIAL PRIMARY KEY,
    table_name VARCHAR(100) NOT NULL,
    row_id VARCHAR(100),
    issue_type VARCHAR(50) NOT NULL,
    issue_description TEXT,
    severity VARCHAR(20),
    source VARCHAR(50),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_issues_table ON data_quality.issues(table_name);
CREATE INDEX idx_issues_severity ON data_quality.issues(severity);