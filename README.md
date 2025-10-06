# Data Quality Evaluation & Improvement for Energy Consumption Data

ETL pipeline project for evaluating and improving data quality of energy consumption datasets from Paris and Evry.

**Course:** M2 DataScale | **Year:** 2025/2026 | **Instructor:** Zoubida Kedad

## Team Members
- Khaled Bouabdallah
- [Student 2]
- [Student 3]

---

## Project Overview

Build an ETL pipeline that:
- Integrates energy consumption data from multiple heterogeneous sources
- Evaluates data quality across multiple dimensions
- Implements automated data cleaning and improvement processes
- Generates target tables for statistical analysis (IRIS zones and socio-professional categories)

## Data Sources

| Source | Description | Tables |
|--------|-------------|--------|
| **S1** | Paris dataset | Population, Consommation |
| **S2** | Evry dataset | Population, Consommation |
| **S3** | Socio-professional categories | CSP (ID, Description, Salary stats) |
| **S4** | Geographic zones | IRIS (Street/City → Zone mapping) |

## Target Schema

```
Consommation_IRIS_Paris (ID_IRIS, Conso_moyenne_annuelle)
Consommation_IRIS_Evry (ID_IRIS, Conso_moyenne_annuelle)
Consommation_CSP (ID_CSP, Conso_moyenne_annuelle, Salaire_Moyen)
```

## Quality Dimensions Evaluated

- **Completeness:** Missing values detection
- **Conformity:** Format and encoding validation
- **Consistency:** Reference data alignment
- **Uniqueness:** Duplicate detection and elimination
- **Validity:** Outlier identification

---

## Tech Stack

- **ETL:** Apache Airflow
- **Data Processing:** Python (Pandas/Polars)
- **Quality Validation:** Great Expectations / Custom checks
- **Metrics Storage:** PostgreSQL/DuckDB
- **Dashboard:** Streamlit (optional)
- **Version Control:** Git

---

## Repository Structure

```
.
├── assets/
│   └── images/          # Diagrams and logos
├── docs/
│   └── report.md        # Detailed project report
├── dags/                # Airflow DAG definitions
├── src/
│   ├── extract/         # Data extraction modules
│   ├── transform/       # Transformation logic
│   ├── quality/         # Quality check functions
│   └── load/            # Target table loading
├── config/              # Configuration files
├── tests/               # Unit and integration tests
├── notebooks/           # Data profiling notebooks
└── README.md
```

---

## Quick Start

### Prerequisites
```bash
Python 3.9+
Apache Airflow 2.7+
PostgreSQL (or DuckDB)
```

### Installation
```bash
# Clone repository
git clone <repo-url>
cd data-quality-project

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Initialize Airflow
airflow db init
airflow users create --username admin --password admin --firstname Admin --lastname User --role Admin --email admin@example.com
```

### Running the Pipeline
```bash
# Start Airflow webserver and scheduler
airflow webserver --port 8080
airflow scheduler

# Trigger DAG via UI or CLI
airflow dags trigger energy_consumption_etl
```

---

## Pipeline Architecture

```
Extract → Quality Check (sources) → Transform & Clean → Quality Check (targets) → Load → Store Metrics
```

**Key Design Decision:** Union-first approach
- Merge Paris/Evry sources early
- Apply transformations once
- Filter by source at the end

See [detailed mapping diagram](./docs/report.md#1-data-mapping--transformation-strategy)

---

## Data Quality Workflow

1. **Source Profiling:** Analyze raw data for patterns and issues
2. **Validation:** Apply quality rules at table and column level
3. **Cleaning:** Automated fixes (normalization, deduplication, imputation)
4. **Verification:** Re-check quality post-transformation
5. **Reporting:** Store metrics with timestamps for trend analysis

---

## Current Status

- [x] Schema mapping and transformation design
- [x] Quality dimensions definition
- [x] Tool selection and justification
- [ ] Data receipt and profiling
- [ ] ETL pipeline implementation
- [ ] Quality improvement automation
- [ ] Dashboard development
- [ ] Final testing and validation

**Next Milestone:** Data profiling (upon dataset receipt)

---

## Key Challenges

**Address Matching:** Three different address formats must be reconciled
- Population: free text addresses
- Consommation: structured (street number, name, postal code)
- IRIS: requires numeric IDs

**Solution approach:** Standardization → lookup/geocoding → join

See [full risk assessment](./docs/report.md#4-risk-assessment)

---

## Documentation

- **[Project Report](./docs/report.md)** - Comprehensive analysis, assumptions, and decisions
- **[Data Mapping Diagram](./assets/images/mapping%20data%20quality%20project.drawio.png)** - Visual pipeline architecture

---

## Contributing

1. Create feature branch: `git checkout -b feature/your-feature`
2. Commit changes: `git commit -m "Add feature"`
3. Push branch: `git push origin feature/your-feature`
4. Open Pull Request

---

## License

Academic project for M2 DataScale course - Université de Versailles

---

## Contact

For questions, contact team members or instructor Zoubida Kedad.