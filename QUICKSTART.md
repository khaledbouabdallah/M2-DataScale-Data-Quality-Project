# Quick Start Guide - Simple Workflow

## Setup Steps


### 2. Setup Environment

```bash
# Copy environment template
cp .env.example .env

# Set your user ID (Linux/Mac)
echo "AIRFLOW_UID=$(id -u)" >> .env

# Windows: manually set AIRFLOW_UID=50000 in .env
```

### 3. Install Dependencies

```bash
# Install main project dependencies
uv sync

# Generate mock data
uv run python scripts/generate_mock_data.py
```

You should see:
```
✅ Generated data/population_test.csv with 100 rows
🎉 Mock data generation complete!
```

### 4. Start Docker Services

```bash
# Initialize Airflow database (first time only)
docker compose up airflow-init

# Start all services
docker compose up -d

# Check logs
docker compose logs -f
```

Wait for all services to be healthy (~30 seconds).

### 5. Access Services

Open in your browser:
- **Airflow UI**: http://localhost:8080 (user: `airflow`, pass: `airflow`)
- **Streamlit Dashboard**: http://localhost:8501

---

## Running the Simple Workflow

### Via Airflow UI

1. Go to http://localhost:8080
2. Login (airflow/airflow)
3. Find DAG: `simple_quality_workflow`
4. Click ▶️ (Play button) to trigger
5. Watch tasks turn green: Extract → Validate → Report
6. Click on task to see logs

### Via CLI

```bash
# Trigger DAG
docker compose exec airflow-webserver airflow dags trigger simple_quality_workflow

# Watch logs
docker compose logs -f airflow-scheduler
```

---

## What the Workflow Does

```
1. Extract Data
   ↓ Reads data/population_test.csv (100 rows)
   
2. Validate Data
   ↓ Checks:
     - Completeness (% non-NULL per column)
     - Format conformity (ID pattern, CSP pattern)
     - Duplicates
   ↓ Saves metrics to PostgreSQL
   
3. Report Results
   ↓ Prints summary
```

---

## Viewing Results

### In Streamlit Dashboard

Go to http://localhost:8501:
- **Metrics Overview**: See completeness percentages
- **Issues**: View detected quality problems
- **Raw Data**: Download metrics CSV

### In Database

```bash
# Connect to PostgreSQL
docker compose exec postgres psql -U airflow

# Query metrics
SELECT * FROM data_quality.metrics ORDER BY timestamp DESC LIMIT 10;

# Query issues
SELECT * FROM data_quality.issues ORDER BY timestamp DESC LIMIT 10;

# Exit
\q
```

---

## Expected Results

After running the workflow, you should see:

**Completeness Metrics:**
- ID: ~100%
- Nom: ~90% (10% intentionally missing)
- Prenom: 100%
- Adresse: ~92% (8% intentionally missing)
- CSP: ~95% (5% intentionally missing)
- Source: 100%

**Format Issues:**
- ~3% invalid CSP codes (value "99" instead of 1-6)
- ID format: 100% conform (P0001 pattern)

**Duplicates:**
- 0 duplicates (clean mock data)

---

## Troubleshooting

### DAG Not Showing Up

```bash
# Check if file exists
ls -la dags/simple_workflow.py

# Restart scheduler
docker compose restart airflow-scheduler

# Wait 30 seconds and refresh UI
```

### Import Errors in DAG

```bash
# Check Python path in container
docker compose exec airflow-webserver python -c "import sys; print(sys.path)"

# Check if src is accessible
docker compose exec airflow-webserver ls -la /opt/airflow/src
```

### No Metrics in Database

```bash
# Check if tables exist
docker compose exec postgres psql -U airflow -c "\dt data_quality.*"

# Check table contents
docker compose exec postgres psql -U airflow -c "SELECT COUNT(*) FROM data_quality.metrics;"
```

### Streamlit Can't Connect

```bash
# Check if postgres is running
docker compose ps postgres

# Test connection from streamlit container
docker compose exec streamlit python -c "import psycopg2; conn = psycopg2.connect(host='postgres', user='airflow', password='airflow', database='airflow'); print('OK')"
```

---

## Next Steps

Once the simple workflow works:

1. **Add more data sources**: Create Consommation CSV
2. **Add transformations**: Join, aggregate, normalize
3. **Add more quality checks**: Outliers, reference data validation
4. **Enhance dashboard**: Add charts, filters, trends
5. **Schedule DAG**: Change `schedule_interval` to run automatically

---

## Clean Up

```bash
# Stop all services
docker compose down

# Remove volumes (deletes all data)
docker compose down -v

# Remove generated mock data
rm data/population_test.csv
```