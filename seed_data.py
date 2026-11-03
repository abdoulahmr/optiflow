# seed_data.py
import random
from datetime import datetime, timedelta
from database.db_manager import db
from models.lens_model import LensModel

def clear_data():
    """Clears existing data to avoid duplicates when re-running the script."""
    tables = ["order_items", "orders", "supplier_transactions", "suppliers", 
              "contact_lenses", "prescriptions", "patients", "inventory", "lenses"]
    
    # Disable foreign keys temporarily to clear tables smoothly
    db.execute_query("PRAGMA foreign_keys = OFF;")
    for table in tables:
        db.execute_query(f"DELETE FROM {table};")
        # Reset auto-increment counters
        db.execute_query(f"DELETE FROM sqlite_sequence WHERE name='{table}';")
    db.execute_query("PRAGMA foreign_keys = ON;")
    print("Existing data cleared.")

def seed_patients_and_prescriptions():
    first_names = ["Ahmed", "Yacine", "Fatima", "Amina", "Karim", "Sofiane", "Nadia", "Samira", "Riad", "Lina", "Mehdi", "Sarah"]
    last_names = ["Benali", "Khelifi", "Boumediene", "Zerrouki", "Hamdi", "Belkacem", "Saidi", "Mansouri", "Cherif", "Boudjelal"]
    
    for i in range(15):
        nom = random.choice(last_names)
        prenom = random.choice(first_names)
        dob = (datetime.now() - timedelta(days=random.randint(5000, 25000))).strftime("%Y-%m-%d")
        phone = f"0{random.choice([5,6,7])}{random.randint(10000000, 99999999)}"
        
        # Calculate age
        age = datetime.now().year - datetime.strptime(dob, "%Y-%m-%d").year
        
        patient_id = db.execute_query(
            "INSERT INTO patients (nom, prenom, date_of_birth, age, gender, phone, address, pd_od, pd_og, pd_total) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (nom, prenom, dob, age, random.choice(["Homme", "Femme"]), phone, "Alger, Algerie", round(random.uniform(30, 35), 1), round(random.uniform(30, 35), 1), round(random.uniform(60, 70), 1))
        )
        
        # Add prescription for half the patients
        if i % 2 == 0 and patient_id:
            exam_date = datetime.now().strftime("%Y-%m-%d")
            db.execute_query("""
                INSERT INTO prescriptions (
                    patient_id, exam_date, vl_sph_od, vl_cyl_od, vl_axe_od, vl_add_od,
                    vl_sph_og, vl_cyl_og, vl_axe_og, vl_add_og
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                patient_id, exam_date, round(random.uniform(-3, 3), 2), round(random.uniform(-2, 2), 2), random.randint(0, 180), round(random.uniform(0.5, 2.5), 2),
                round(random.uniform(-3, 3), 2), round(random.uniform(-2, 2), 2), random.randint(0, 180), round(random.uniform(0.5, 2.5), 2)
            ))
            
    print("Patients and prescriptions seeded.")

def seed_inventory():
    frame_brands = ["Ray-Ban", "Oakley", "Persol", "Prada", "Gucci", "Burberry", "Tom Ford", "Emporio Armani"]
    frame_colors = ["Noir", "Tortue", "Argent", "Doré", "Bleu"]
    solutions = ["Opti-Free Puremoist 300ml", "Renu Multiplus 360ml", "Bausch Sensitive Eyes 120ml"]
    accessories = ["Chiffon Microfibre", "Etui Rigide", "Cordon Optique", "Spray Nettoyant 60ml"]
    contact_lenses = [
        "Acuvue Oasys 1-Day", "Acuvue Oasys 2-Weeks", "Dailies AquaComfort Plus", 
        "Air Optix Aqua", "Biofinity", "PureVision 2", "SofLens Daily Disposable"
    ]
    
    # Frames
    for i in range(20):
        name = f"Monture {random.choice(frame_brands)} {random.choice(frame_colors)}"
        cost = round(random.uniform(2500, 12000), 2)
        retail = round(cost * round(random.uniform(1.8, 2.5), 2), 2)
        db.execute_query(
            "INSERT INTO inventory (barcode, name, category, cost_price, retail_price, stock_qty, seuil) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (f"1{random.randint(100000, 899999)}", name, "Montures", cost, retail, random.randint(2, 15), 5)
        )
        
    # Contact Lenses
    for cl in contact_lenses:
        cost = round(random.uniform(1800, 4500), 2)
        retail = round(cost * 1.8, 2)
        db.execute_query(
            "INSERT INTO inventory (barcode, name, category, cost_price, retail_price, stock_qty, seuil) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (f"1{random.randint(100000, 899999)}", cl, "Lentilles", cost, retail, random.randint(10, 30), 5)
        )
        
    # Solutions
    for sol in solutions:
        cost = round(random.uniform(800, 1500), 2)
        retail = round(cost * 1.8, 2)
        db.execute_query(
            "INSERT INTO inventory (barcode, name, category, cost_price, retail_price, stock_qty, seuil) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (f"1{random.randint(100000, 899999)}", sol, "Produits de nettoyage", cost, retail, random.randint(10, 30), 5)
        )
        
    # Accessories
    for acc in accessories:
        cost = round(random.uniform(100, 500), 2)
        retail = round(cost * 2.0, 2)
        db.execute_query(
            "INSERT INTO inventory (barcode, name, category, cost_price, retail_price, stock_qty, seuil) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (f"1{random.randint(100000, 899999)}", acc, "Accessoires", cost, retail, random.randint(5, 25), 3)
        )
        
    print("Inventory seeded (with Contact Lenses).")
    
def seed_suppliers():
    suppliers = [
        {"name": "Essilor Algeria", "category_tag": "Verres", "phone": "021 55 66 77", "rc": "16/00-1234567"},
        {"name": "Luxottica Maghreb", "category_tag": "Montures", "phone": "021 77 88 99", "rc": "16/00-7654321"},
        {"name": "Alcon Vision Care", "category_tag": "Lentilles", "phone": "021 22 33 44", "rc": "16/00-9876543"}
    ]
    
    for sup in suppliers:
        supplier_id = db.execute_query(
            "INSERT INTO suppliers (name, contact_person, phone, category_tag, rc, nif, nis, balance_due) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (sup["name"], "Representant", sup["phone"], sup["category_tag"], sup["rc"], "000000000000000", "000000000000000", 0.0)
        )
        
        if supplier_id:
            # Add 3 random transactions per supplier
            for _ in range(3):
                t_type = random.choice(["Facture", "Versement"])
                amount = round(random.uniform(15000, 80000), 2)
                db.execute_query(
                    "INSERT INTO supplier_transactions (supplier_id, transaction_type, amount, note) VALUES (?, ?, ?, ?)",
                    (supplier_id, t_type, amount, "Transaction de test")
                )
                # Update balance
                current_bal = db.fetch_one("SELECT balance_due FROM suppliers WHERE id=?", (supplier_id,))['balance_due']
                new_bal = current_bal + amount if t_type == "Facture" else current_bal - amount
                db.execute_query("UPDATE suppliers SET balance_due=? WHERE id=?", (new_bal, supplier_id))
                
    print("Suppliers and transactions seeded.")

def seed_lens_prices():
    """Sets random realistic prices and stock for the lens matrix."""
    lenses = db.fetch_all("SELECT * FROM lenses")
    for lens in lenses:
        base_price = 2500
        treatment = lens['treatment']
        
        # Adjust price based on column name
        if "1.6" in treatment: base_price = 3500
        if "1.67" in treatment: base_price = 5500
        if "1.74" in treatment: base_price = 8000
        if "BB" in treatment: base_price += 1000
        if "PROFILO" in treatment: base_price += 2000
        if "ZEISS" in treatment: base_price = 12000
        if "YAL" in treatment: base_price += 500
        if "TRANS" in treatment: base_price += 1500
        if "CRISTAL" in treatment or "AZUR" in treatment: base_price += 800
        
        retail = round(base_price + random.uniform(-200, 500), 2)
        cost = round(retail / 1.6, 2)
        stock = random.randint(0, 20)  # Generate random stock quantity
        
        db.execute_query("UPDATE lenses SET retail_price=?, cost_price=?, stock_qty=? WHERE id=?", (retail, cost, stock, lens['id']))
        
    print("Lens prices and stock seeded.")
    
if __name__ == "__main__":
    print("Starting database seeding...")
    
    # 1. Clear old data first
    clear_data()
    
    # 2. Initialize the lens matrix (Creates the 1530 rows)
    LensModel.initialize_matrix()
    
    # 3. Seed the rest of the data
    seed_patients_and_prescriptions()
    seed_inventory()
    seed_suppliers()
    seed_lens_prices()
    
    print("\n✅ Dummy data generated successfully! You can now launch the app.")