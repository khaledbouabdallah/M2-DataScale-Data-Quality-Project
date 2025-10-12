"""CSV schema definitions for source and target tables"""
from typing import Dict, List
from dataclasses import dataclass

@dataclass
class TableSchema:
    """Schema definition for a table"""
    name: str
    columns: List[str]
    dtypes: Dict[str, str]
    required_columns: List[str]
    primary_key: str

# Source S1 & S2 - Population (Paris & Evry)
POPULATION_SCHEMA = TableSchema(
    name="Population",
    columns=["ID", "Nom", "Prenom", "Adresse", "CSP"],
    dtypes={
        "ID": "string",
        "Nom": "string",
        "Prenom": "string", 
        "Adresse": "string",
        "CSP": "string"  # String to handle missing values
    },
    required_columns=["ID"],
    primary_key="ID"
)

# Source S1 & S2 - Consommation (Paris & Evry)
CONSOMMATION_SCHEMA = TableSchema(
    name="Consommation",
    columns=["ID_Adr", "N", "Nom_Rue", "Code_Postal", "NB_KW_Jour"],
    dtypes={
        "ID_Adr": "string",
        "N": "string",
        "Nom_Rue": "string",
        "Code_Postal": "string",
        "NB_KW_Jour": "float64"
    },
    required_columns=["ID_Adr", "N", "Nom_Rue", "Code_Postal", "NB_KW_Jour"],
    primary_key="ID_Adr"
)

# Source S3 - CSP Reference
CSP_SCHEMA = TableSchema(
    name="CSP",
    columns=["ID_CSP", "Desc", "Salaire_Moyen", "Salaire_Min", "Salaire_Max"],
    dtypes={
        "ID_CSP": "string",
        "Desc": "string",
        "Salaire_Moyen": "float64",
        "Salaire_Min": "float64",
        "Salaire_Max": "float64"
    },
    required_columns=["ID_CSP", "Salaire_Moyen"],
    primary_key="ID_CSP"
)

# Source S4 - IRIS Reference
IRIS_SCHEMA = TableSchema(
    name="IRIS",
    columns=["ID_Rue", "ID_Ville", "ID_Iris"],
    dtypes={
        "ID_Rue": "string",  # Street name as text (teacher's assumption)
        "ID_Ville": "string",  # Postal code as text
        "ID_Iris": "string"
    },
    required_columns=["ID_Rue", "ID_Ville", "ID_Iris"],
    primary_key=["ID_Rue", "ID_Ville"]  # Composite key
)

# Target - Consommation_CSP
CONSOMMATION_CSP_SCHEMA = TableSchema(
    name="Consommation_CSP",
    columns=["ID_CSP", "Conso_moyenne_annuelle", "Salaire_Moyen"],
    dtypes={
        "ID_CSP": "string",
        "Conso_moyenne_annuelle": "float64",
        "Salaire_Moyen": "float64"
    },
    required_columns=["ID_CSP", "Conso_moyenne_annuelle", "Salaire_Moyen"],
    primary_key="ID_CSP"
)

# Target - Consommation_IRIS (Paris & Evry)
CONSOMMATION_IRIS_SCHEMA = TableSchema(
    name="Consommation_IRIS",
    columns=["ID_IRIS", "Conso_moyenne_annuelle"],
    dtypes={
        "ID_IRIS": "string",
        "Conso_moyenne_annuelle": "float64"
    },
    required_columns=["ID_IRIS", "Conso_moyenne_annuelle"],
    primary_key="ID_IRIS"
)

# Intermediate - Population enriched with Source
POPULATION_UNION_SCHEMA = TableSchema(
    name="Population_Union",
    columns=["ID_Source", "Nom", "Prenom", "Adresse", "CSP", "Source"],
    dtypes={
        "ID_Source": "string",
        "Nom": "string",
        "Prenom": "string",
        "Adresse": "string",
        "CSP": "string",
        "Source": "string"
    },
    required_columns=["ID_Source", "Source"],
    primary_key="ID_Source"
)

# Intermediate - Consommation enriched with Source
CONSOMMATION_UNION_SCHEMA = TableSchema(
    name="Consommation_Union",
    columns=["ID_Adr_Source", "N", "Nom_Rue", "Code_Postal", "NB_KW_Jour", "Source"],
    dtypes={
        "ID_Adr_Source": "string",
        "N": "string",
        "Nom_Rue": "string",
        "Code_Postal": "string",
        "NB_KW_Jour": "float64",
        "Source": "string"
    },
    required_columns=["ID_Adr_Source", "NB_KW_Jour", "Source"],
    primary_key="ID_Adr_Source"
)

# Schema registry for easy access
SCHEMAS = {
    "population": POPULATION_SCHEMA,
    "consommation": CONSOMMATION_SCHEMA,
    "csp": CSP_SCHEMA,
    "iris": IRIS_SCHEMA,
    "consommation_csp": CONSOMMATION_CSP_SCHEMA,
    "consommation_iris": CONSOMMATION_IRIS_SCHEMA,
    "population_union": POPULATION_UNION_SCHEMA,
    "consommation_union": CONSOMMATION_UNION_SCHEMA,
}


def get_schema(name: str) -> TableSchema:
    """Get schema by name"""
    if name not in SCHEMAS:
        raise ValueError(f"Unknown schema: {name}. Available: {list(SCHEMAS.keys())}")
    return SCHEMAS[name]


def validate_columns(df_columns: List[str], schema: TableSchema) -> Dict[str, List[str]]:
    """
    Validate dataframe columns against schema.
    
    Returns dict with:
        - 'missing': columns in schema but not in dataframe
        - 'extra': columns in dataframe but not in schema
    """
    df_cols = set(df_columns)
    schema_cols = set(schema.columns)
    
    return {
        "missing": list(schema_cols - df_cols),
        "extra": list(df_cols - schema_cols)
    }
    

def validate_required_columns(df_columns: List[str], schema: TableSchema) -> None:
    """
    Validate required columns exist in dataframe.
    Raises ValueError if any required columns are missing.
    """
    validation = validate_columns(df_columns, schema)
    if validation["missing"]:
        missing = validation["missing"]
        raise ValueError(
            f"Missing required columns in {schema.name}: {missing}"
        )