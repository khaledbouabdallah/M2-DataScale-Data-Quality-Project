"""Generate mock CSV data for testing the ETL pipeline"""
import csv
import random
from pathlib import Path

# Mock data
FIRST_NAMES = ["Jean", "Marie", "Pierre", "Sophie", "Luc", "Claire", "Thomas", "Emma", "Nicolas", "Julie"]
LAST_NAMES = ["Martin", "Bernard", "Dubois", "Thomas", "Robert", "Richard", "Petit", "Durand", "Leroy", "Moreau"]
STREETS = ["Rue de Rivoli", "Avenue des Champs-Élysées", "Rue Victor Hugo", "Boulevard Haussmann", "Rue de la Paix"]
CITIES = [("Paris", "75001"), ("Paris", "75002"), ("Evry", "91000")]
CSP_CODES = ["1", "2", "3", "4", "5", "6"]  # Reference to CSP table

def generate_population_csv(filename: str, num_rows: int = 100, add_quality_issues: bool = True):
    """Generate mock Population CSV with intentional quality issues"""
    
    output_path = Path("data") / filename
    output_path.parent.mkdir(exist_ok=True)
    
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["ID", "Nom", "Prenom", "Adresse", "CSP", "Source"])
        
        for i in range(1, num_rows + 1):
            # Determine source based on city
            city, postal_code = random.choice(CITIES)
            source = "Paris" if city == "Paris" else "Evry"
            
            # Generate address
            street_num = random.randint(1, 200)
            street_name = random.choice(STREETS)
            address = f"{street_num} {street_name}, {postal_code}"
            
            # Add quality issues randomly
            if add_quality_issues:
                # 10% missing names
                if random.random() < 0.1:
                    nom = ""
                else:
                    nom = random.choice(LAST_NAMES)
                
                # 5% missing CSP
                if random.random() < 0.05:
                    csp = ""
                # 3% invalid CSP (not in reference)
                elif random.random() < 0.03:
                    csp = "99"  # Invalid code
                else:
                    csp = random.choice(CSP_CODES)
                
                # 8% missing address
                if random.random() < 0.08:
                    address = ""
                
                prenom = random.choice(FIRST_NAMES)
                
            else:
                nom = random.choice(LAST_NAMES)
                prenom = random.choice(FIRST_NAMES)
                csp = random.choice(CSP_CODES)
            
            writer.writerow([
                f"P{i:04d}",
                nom,
                prenom,
                address,
                csp,
                source
            ])
    
    print(f"✅ Generated {output_path} with {num_rows} rows")
    return output_path

if __name__ == "__main__":
    # Generate test data
    generate_population_csv("population_test.csv", num_rows=100, add_quality_issues=True)
    print("\n🎉 Mock data generation complete!")
    print("📁 File location: data/population_test.csv")