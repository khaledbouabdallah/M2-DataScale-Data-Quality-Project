![logo](../assets/images/uni_logo.jpeg)

# Data Quality Project: Energy Consumption ETL

**M2 DataScale 2025/2026** | Zoubida Kedad  
**Team:** Khaled Bouabdallah, [Student 2], [Student 3]  
**Last Updated:** 2025-10-11

---

## 1. Architecture Decision: Union-First Approach

**Strategy:** Merge sources early, transform once, split outputs late.

**Pipeline:**
```
S1 (Paris) + S2 (Evry) → Union → Transform → Split → Targets
```

**Why union-first:**
- Single codebase (no duplicate logic for Paris/Evry)
- Guaranteed consistency across sources
- Easy source comparison via `Source` column
- Scales to new cities without code changes

**Implementation details:**
- Add `Source` column ('Paris' or 'Evry') during union
- Use composite keys: `ID` → `ID_Source`, `ID_Adr` → `ID_Adr_Source`
- Filter by `Source` only at final stage for separate target tables

---

## 2. Data Mapping

![Mapping Diagram](../assets/images/mapping_data_quality_project.png)

### Flow Summary

**Path 1: Consommation_CSP**
```
Population (S1+S2) → Join CSP → Enrich with Salaire_Moyen
   ↓
Consommation (S1+S2) → Create full address
   ↓
Join on Address → Group by CSP → AVG(consumption), MAX(salary)
```

**Path 2: Consommation_IRIS (Paris/Evry)**
```
Consommation (S1+S2) → Create full address
   ↓
Join IRIS (ID_Rue==Nom_Rue, ID_Ville==Code_Postal)
   ↓
Group by ID_IRIS → SUM(consumption)
   ↓
Split by Source → Paris target, Evry target
```

---

## 3. Critical Assumptions

| Component | Assumption | Risk if Wrong | Mitigation |
|-----------|------------|---------------|------------|
| **IRIS Join** | `ID_Rue` = street name (text), `ID_Ville` = postal code (text) | Need lookup table | Teacher confirmed this assumption |
| **Address Match** | Population format matches Consommation concatenation | Join fails | String normalization (trim, lowercase) |
| **Cardinality** | 1:1 relationship between address and consumption | Wrong aggregation | Validate during profiling |
| **CSP Codes** | All Population.CSP exist in CSP reference table | Data loss from INNER JOIN | Track dropped records |

---

## 4. Transformation Rules

### Address Normalization
```python
# Consommation side
Adresse = f"{N} {Nom_Rue}, {Code_Postal}"

# Both sides
Adresse = Adresse.strip().lower()
Nom_Rue = Nom_Rue.strip().lower()
Code_Postal = Code_Postal.strip()
```

### Aggregations
```sql
-- Consommation_CSP
GROUP BY CSP
  AVG(NB_KW_Jour * 365) as Conso_moyenne_annuelle
  MAX(Salaire_Moyen) as Salaire_Moyen  -- Reference value, not averaged

-- Consommation_IRIS
GROUP BY ID_IRIS  
  SUM(NB_KW_Jour * 365) as Conso_moyenne_annuelle  -- Total zone consumption
```

### Join Strategy
All joins are **INNER** (discard non-matching records):
- Population ⋈ CSP: Drop invalid CSP codes
- Population ⋈ Consommation: Drop unmatched addresses  
- Consommation ⋈ IRIS: Drop addresses outside IRIS zones

---


## 5. Tech Stack

| Component | Tool | Purpose |
|-----------|------|---------|
| Orchestration | Apache Airflow | Workflow scheduling |
| Processing | Python + Pandas | Data transformation |
| Quality Checks | Custom scripts | Validation logic |
| Storage | PostgreSQL | Metrics database |
| Visualization | Streamlit | Dashboard (optional) |

---

## 6. Known Risks

| Risk | Severity | Status |
|------|----------|--------|
| Address format mismatch between sources | 🔴 High | Awaiting real data |
| String matching for IRIS join (no fuzzy logic) | 🟡 Medium | Normalization implemented |
| Data loss from INNER JOINs | 🟡 Medium | Will quantify after profiling |
| ID collisions between Paris/Evry | 🟢 Low | Composite keys prevent this |


## 7. Open Questions

**Awaiting real data:**
1. Actual address format in Population table
2. Presence of street name variations requiring fuzzy matching
3. Distribution of NULL values
4. Duplicate address frequency (affects cardinality assumption)