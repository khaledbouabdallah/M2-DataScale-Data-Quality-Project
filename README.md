# Data Quality Project - Energy Consumption ETL

**M2 DataScale 2025/2026** | Zoubida Kedad

**Team:** Khaled Bouabdallah, [Student 2], [Student 3]

---

## Goal

Build an ETL pipeline to integrate and clean energy consumption data from Paris and Evry, generating quality reports and target tables for analysis.

**Sources:** Population + Consommation (Paris & Evry), CSP reference data, IRIS geographic zones

**Targets:** 
- `Consommation_IRIS_Paris/Evry` (consumption by geographic zone)
- `Consommation_CSP` (consumption by socio-professional category)

---

## Tech Stack

- **ETL:** Apache Airflow
- **Processing:** Python (Pandas)
- **Quality:** Great Expectations
- **Storage:** PostgreSQL
- **Dashboard:** Streamlit (if time permits)

---

## Repository Structure


___incoming___

---

## Setup


___incoming___

---

## Pipeline Overview

```
Extract → Quality Check → Clean & Transform → Quality Check → Load → Metrics
```

---

## Current Status

- [x] Mapping & design
- [ ] Data profiling (waiting for dataset)
- [ ] Pipeline implementation
- [ ] Quality automation
- [ ] Final report

**See [docs/report.md](./docs/report.md) for detailed analysis.**
