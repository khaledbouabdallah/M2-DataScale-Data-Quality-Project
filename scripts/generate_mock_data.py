"""Generate mock CSV data for all sources"""
import csv
import random
from pathlib import Path

# Mock data constants
FIRST_NAMES = ["Jean", "Marie", "Pierre", "Sophie", "Luc", "Claire", "Thomas", "Emma", "Nicolas", "Julie"]
LAST_NAMES = ["Martin", "Bernard", "Dubois", "Thomas", "Robert", "Richard", "Petit", "Durand", "Leroy", "Moreau"]

STREETS_PARIS = [
    "Rue de Rivoli",
    "Avenue des Champs-Élysées", 
    "Rue Victor Hugo",
    "Boulevard Haussmann",
    "Rue de la Paix"
]

STREETS_EVRY = [
    "Avenue des Champs-Élysées",  # Some overlap
    "Rue Victor Hugo",
    "Boulevard Haussmann",
    "Rue de la République",
    "Avenue du Lac"
]

POSTAL_CODES_PARIS = ["75001", "75002"]
POSTAL_CODES_EVRY = ["91000", "91080"]

CSP_CODES = ["1", "2", "3", "4", "5", "6"]

# CSP Reference Data (Source S3)
CSP_REFERENCE = [
    {"ID_CSP": "1", "Desc": "Agriculteurs exploitants", "Salaire_Moyen": 25000, "Salaire_Min": 18000, "Salaire_Max": 35000},
    {"ID_CSP": "2", "Desc": "Artisans, commerçants", "Salaire_Moyen": 32000, "Salaire_Min": 22000, "Salaire_Max": 50000},
    {"ID_CSP": "3", "Desc": "Cadres et professions intellectuelles", "Salaire_Moyen": 55000, "Salaire_Min": 40000, "Salaire_Max": 100000},
    {"ID_CSP": "4", "Desc": "Professions intermédiaires", "Salaire_Moyen": 38000, "Salaire_Min": 28000, "Salaire_Max": 50000},
    {"ID_CSP": "5", "Desc": "Employés", "Salaire_Moyen": 28000, "Salaire_Min": 20000, "Salaire_Max": 38000},
    {"ID_CSP": "6", "Desc": "Ouvriers", "Salaire_Moyen": 26000, "Salaire_Min": 19000, "Salaire_Max": 35000},
]


def generate_iris_reference(output_path: Path):
    """
    Generate IRIS reference CSV (Source S4).
    Maps street names and postal codes to IRIS zones.
    """
    output_path.parent.mkdir(exist_ok=True)
    
    iris_data = []
    iris_counter = 1
    
    # Paris IRIS zones
    for postal_code in POSTAL_CODES_PARIS:
        for street in STREETS_PARIS:
            iris_data.append({
                "ID_Rue": street.lower(),  # Normalized street name
                "ID_Ville": postal_code,
                "ID_Iris": f"751{postal_code[-2:]}{iris_counter:04d}"
            })
            iris_counter += 1
    
    # Evry IRIS zones
    iris_counter = 1
    for postal_code in POSTAL_CODES_EVRY:
        for street in STREETS_EVRY:
            iris_data.append({
                "ID_Rue": street.lower(),  # Normalized street name
                "ID_Ville": postal_code,
                "ID_Iris": f"910{postal_code[-2:]}{iris_counter:04d}"
            })
            iris_counter += 1
    
    # Write CSV
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=["ID_Rue", "ID_Ville", "ID_Iris"])
        writer.writeheader()
        writer.writerows(iris_data)
    
    print(f"✅ Generated {output_path} with {len(iris_data)} IRIS zones")


def generate_csp_reference(output_path: Path):
    """Generate CSP reference CSV (Source S3)"""
    output_path.parent.mkdir(exist_ok=True)
    
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=["ID_CSP", "Desc", "Salaire_Moyen", "Salaire_Min", "Salaire_Max"])
        writer.writeheader()
        writer.writerows(CSP_REFERENCE)
    
    print(f"✅ Generated {output_path} with {len(CSP_REFERENCE)} CSP categories")


def generate_population_csv(output_path: Path, city: str, num_rows: int = 50, add_quality_issues: bool = True):
    """
    Generate Population CSV for Paris or Evry (Source S1/S2).
    
    Quality issues included:
    - 10% missing Nom
    - 5% missing CSP
    - 3% invalid CSP (code 99)
    - 8% missing Adresse
    """
    output_path.parent.mkdir(exist_ok=True)
    
    streets = STREETS_PARIS if city == "Paris" else STREETS_EVRY
    postal_codes = POSTAL_CODES_PARIS if city == "Paris" else POSTAL_CODES_EVRY
    
    prefix = "P" if city == "Paris" else "E"
    
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["ID", "Nom", "Prenom", "Adresse", "CSP"])
        
        for i in range(1, num_rows + 1):
            # Generate address
            street_num = random.randint(1, 200)
            street_name = random.choice(streets)
            postal_code = random.choice(postal_codes)
            address = f"{street_num} {street_name}, {postal_code}"
            
            # Add quality issues
            if add_quality_issues:
                # 10% missing Nom
                nom = "" if random.random() < 0.1 else random.choice(LAST_NAMES)
                
                # 5% missing CSP
                if random.random() < 0.05:
                    csp = ""
                # 3% invalid CSP (not in reference)
                elif random.random() < 0.03:
                    csp = "99"  # Invalid code
                else:
                    csp = random.choice(CSP_CODES)
                
                # 8% missing Adresse
                if random.random() < 0.08:
                    address = ""
                
                prenom = random.choice(FIRST_NAMES)
            else:
                nom = random.choice(LAST_NAMES)
                prenom = random.choice(FIRST_NAMES)
                csp = random.choice(CSP_CODES)
            
            writer.writerow([
                f"{prefix}{i:04d}",  # P0001 or E0001
                nom,
                prenom,
                address,
                csp
            ])
    
    print(f"✅ Generated {output_path} with {num_rows} rows ({city})")


def generate_consommation_csv(output_path: Path, city: str, num_rows: int = 50, add_quality_issues: bool = True):
    """
    Generate Consommation CSV for Paris or Evry (Source S1/S2).
    
    Quality issues included:
    - 5% missing Nom_Rue
    - 3% invalid Code_Postal format
    - Consumption values: 5-50 kWh/day
    """
    output_path.parent.mkdir(exist_ok=True)
    
    streets = STREETS_PARIS if city == "Paris" else STREETS_EVRY
    postal_codes = POSTAL_CODES_PARIS if city == "Paris" else POSTAL_CODES_EVRY
    
    prefix = "A" if city == "Paris" else "B"
    
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["ID_Adr", "N", "Nom_Rue", "Code_Postal", "NB_KW_Jour"])
        
        for i in range(1, num_rows + 1):
            street_num = random.randint(1, 200)
            street_name = random.choice(streets)
            postal_code = random.choice(postal_codes)
            
            # Consumption: 5-50 kWh per day (realistic household)
            consumption = round(random.uniform(5, 50), 2)
            
            # Add quality issues
            if add_quality_issues:
                # 5% missing Nom_Rue
                if random.random() < 0.05:
                    street_name = ""
                
                # 3% invalid postal code format
                if random.random() < 0.03:
                    postal_code = "999"  # Invalid format
            
            writer.writerow([
                f"{prefix}{i:04d}",  # A0001 or B0001
                street_num,
                street_name,
                postal_code,
                consumption
            ])
    
    print(f"✅ Generated {output_path} with {num_rows} rows ({city})")


def main():
    """Generate all mock data files"""
    mock_dir = Path("data/mock")
    mock_dir.mkdir(parents=True, exist_ok=True)
    
    print("🎲 Generating mock data for ETL pipeline...\n")
    
    # Source S1 - Paris
    print("📍 Source S1 - Paris")
    generate_population_csv(mock_dir / "population_paris.csv", city="Paris", num_rows=50)
    generate_consommation_csv(mock_dir / "consommation_paris.csv", city="Paris", num_rows=50)
    
    # Source S2 - Evry
    print("\n📍 Source S2 - Evry")
    generate_population_csv(mock_dir / "population_evry.csv", city="Evry", num_rows=50)
    generate_consommation_csv(mock_dir / "consommation_evry.csv", city="Evry", num_rows=50)
    
    # Source S3 - CSP Reference
    print("\n📚 Source S3 - CSP Reference")
    generate_csp_reference(mock_dir / "csp_reference.csv")
    
    # Source S4 - IRIS Reference
    print("\n📚 Source S4 - IRIS Reference")
    generate_iris_reference(mock_dir / "iris_reference.csv")
    
    print("\n" + "="*60)
    print("🎉 Mock data generation complete!")
    print("="*60)
    print("\n📁 Generated files in data/mock/:")
    print("  - population_paris.csv (50 rows)")
    print("  - population_evry.csv (50 rows)")
    print("  - consommation_paris.csv (50 rows)")
    print("  - consommation_evry.csv (50 rows)")
    print("  - csp_reference.csv (6 CSP categories)")
    print("  - iris_reference.csv (IRIS zones)")
    print("\n⚠️  Quality issues included for testing:")
    print("  - Missing values (Nom, CSP, Adresse, Nom_Rue)")
    print("  - Invalid CSP codes (99)")
    print("  - Invalid postal codes (999)")
    print("\n🚀 Ready to test ETL pipeline!")


if __name__ == "__main__":
    main()