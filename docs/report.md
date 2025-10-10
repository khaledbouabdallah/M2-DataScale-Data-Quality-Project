![logo](../assets/images/uni_logo.jpeg)

# Project Report: Data Quality Evaluation & Improvement for Energy Consumption Data

**Academic Year:** 2025/2026  
**Course:** M2 DataScale  
**Instructor:** Zoubida Kedad

**Team Members:**
- Khaled Bouabdallah
- [Student 2]
- [Student 3]

---

## 1. Data Mapping & Transformation Strategy

![Data Mapping Diagram](../assets/images/mapping_data_quality_project.png)

### 1.1 Architectural Decision

**Approach:** Union-first, transform-once, filter-last

**Pipeline flow:**
1. Union S1 (Paris) + S2 (Evry) source tables early in the pipeline
2. Add `Source` column ('Paris' or 'Evry') for lineage traceability
3. Apply all transformations on merged dataset
4. Filter by `Source` at the final stage to generate separate `Consommation_IRIS_Paris` and `Consommation_IRIS_Evry` target tables

**Rationale:**
- Eliminates duplicate transformation logic for Paris and Evry data
- Improves maintainability - changes apply to both sources automatically
- Simplifies quality metric comparison between sources

**Key schema modifications:**
- `ID_Adr` → `ID_Adr_Source` (composite key: prevents ID collisions post-union)
- `ID` → `ID_Source` (same rationale)

---

## 2. Critical Assumptions & Data Dependencies

### 2.1 Address Normalization & Matching

**Challenge:** Three different address representations must be joined:

| Source | Format | Example |
|--------|--------|---------|
| Population | Free text | "12 Rue Victor Hugo, 75001" |
| Consommation | Structured fields | N=12, Nom_Rue="Rue Victor Hugo", Code_Postal=75001 |
| IRIS | Requires IDs | ID_Rue=456, ID_Ville=75, ID_Iris=751012301 |

**Primary preprocessing workload:** Consommation table
- Normalize `Nom_Rue` (trim whitespace, lowercase, remove accents, standardize abbreviations)
- Validate `Code_Postal` format
- Construct standardized full address

**Secondary preprocessing:** Population table
- Parse `Adresse` field to extract components (street number, name, postal code)
- Apply same normalization rules

**Critical assumption:** IRIS table provides a lookup mechanism `(Nom_Rue, Code_Postal) → (ID_Rue, ID_Ville, ID_Iris)`

**Risk if assumption fails:**
- Fallback to fuzzy string matching (high computational cost, lower accuracy)
- Potential need for external geocoding API (adds dependency, latency, costs)
- Manual mapping table creation (non-scalable)

---

### 2.2 Join Strategy & Cardinality

**Population ↔ CSP:**
- **Join type:** INNER JOIN
- **Decision:** Discard Population records with CSP codes not in reference table
- **Alternative considered:** LEFT JOIN + assign "Unknown" CSP category (rejected due to complexity in handling missing salary data)

**Population ↔ Consommation:**
- **Cardinality unknown:** 1:1 or 1:many?
  - If one address has multiple residents → aggregation must account for this
  - If one address has one consumption meter → simpler aggregation
- **Current assumption:** 1:1 (one address = one consumption record)
- **Validation needed:** Inspect data for duplicate addresses in either table

**Consommation ↔ IRIS:**
- **Assumed:** Many-to-one (multiple addresses within one IRIS zone)

---

### 2.3 Aggregation Logic Clarification

**Target table:** `Consommation_CSP (ID_CSP, Conso_moyenne_annuelle, Salaire_Moyen)`

**Important clarification:** `CSP.Salaire_Moyen` is NOT averaged during GROUP BY

**Explanation:**
- `CSP.Salaire_Moyen` is a pre-calculated reference metric for the entire profession
- After `GROUP BY ID_CSP`, all records have identical `Salaire_Moyen` values from CSP lookup
- Simply carry through using MAX/MIN/FIRST (all equivalent)

**Correct aggregation:**
```sql
SELECT 
    p.CSP as ID_CSP,
    AVG(c.NB_KW_Jour * 365) as Conso_moyenne_annuelle,
    MAX(csp.Salaire_Moyen) as Salaire_Moyen
FROM Population p
JOIN Consommation c ON <address_match>
JOIN CSP csp ON p.CSP = csp.ID_CSP
GROUP BY p.CSP
```

---

## 3. Data Quality Evaluation Strategy

### 3.1 Quality Dimensions

| Dimension | Definition | Measurement |
|-----------|------------|-------------|
| **Completeness** | Presence of required values | % non-NULL per column |
| **Conformity** | Adherence to format rules | % matching expected patterns |
| **Consistency** | Alignment with reference data | % valid foreign keys |
| **Uniqueness** | Absence of duplicates | Count of duplicate IDs |
| **Validity** | Values within expected ranges | % outliers detected |

### 3.2 Measurement Points

**Source-level metrics (before transformation):**
- Individual table and column granularity
- Separate tracking for S1 (Paris) vs S2 (Evry)
- Metrics stored with timestamp for trend analysis

**Target-level metrics (after transformation):**
- Same quality dimensions applied to output tables
- Row count reconciliation (input vs output)
- Aggregation validation through spot-checking

**Lineage tracking:**
- Maintain `Source` column in intermediate tables
- Enable traceability from target records back to source

### 3.3 Quality Thresholds (To Be Defined)

Post data profiling, establish:
- Completeness thresholds (e.g., ≥95% for critical fields)
- Acceptable outlier percentages
- Duplicate handling rules
- NULL value strategies per column

---

## 4. Risk Assessment

### 🔴 Blocking Issues

**Address normalization & IRIS mapping:**
- Implementation strategy undefined until actual data formats are known
- Critical dependency on IRIS table structure

### 🟡 Medium Risks

**Cardinality unknowns:**
- Population ↔ Consommation relationship affects aggregation correctness
- May require algorithm adjustments post-profiling

**Reference data mismatches:**
- CSP codes in Population may not exist in CSP reference table
- Potential data loss with INNER JOIN strategy

**ID collision:**
- `ID_Adr_Source` composite key strategy may be insufficient depending on actual ID formats

### 🟢 Low Risks

**Stable elements:**
- Schema mapping is straightforward once address issue resolved
- Aggregation logic is simple (AVG, GROUP BY)
- Union strategy is well-defined

---

## 5. Technical Stack

### 5.1 ETL Platform

**Selected:** Apache Airflow

**Justification:**
- Python-native (leverages team programming expertise)
- Programmatic control for complex quality validation logic
- Industry-standard tool with strong community support
- Flexible orchestration for branching workflows

### 5.2 Supporting Tools

| Component | Tool | Purpose |
|-----------|------|---------|
| Data Quality Validation | Great Expectations / Custom Pandas | Rule definition and automated checks |
| Metrics Storage | PostgreSQL or DuckDB | Time-series quality metrics |
| Visualization | Streamlit | Interactive dashboard (if time permits) |
| Schema Mapping | draw.io | Visual documentation |

---

## 6. Implementation Roadmap

### Phase 1: Data Discovery (Upon data receipt)
1. Data profiling: inspect formats, distributions, missing values
2. Validate/revise address matching assumptions
3. Determine actual cardinalities between tables
4. Identify quality issues in raw data

### Phase 2: Pipeline Development
1. Implement source extraction with quality checks
2. Develop address normalization logic
3. Build transformation workflows with error handling
4. Create target table generation processes
5. Implement metrics collection and storage

### Phase 3: Quality Improvement
1. Define quality thresholds based on profiling results
2. Implement data cleaning rules
3. Add branching logic for quality failures
4. Version control transformation rules

### Phase 4: Validation & Documentation
1. End-to-end testing with full dataset
2. Quality metrics analysis and reporting
3. Dashboard development (if time allows)
4. Final documentation and presentation preparation

---

## 7. Open Questions

**Awaiting data to resolve:**
1. Actual format of address fields in all tables
2. Structure of IRIS lookup mechanism
3. ID uniqueness across Paris/Evry sources
4. Distribution of NULL values and outliers
5. Presence of duplicate records

**To discuss with instructor:**
1. Acceptable data loss threshold for quality filtering
2. Handling strategy for unmatched addresses
3. Expected granularity of quality reporting

---

**Document Status:** Initial mapping and planning phase  
**Last Updated:** [06/10/2025]  
**Next Review:** Upon data receipt