# models/contact_lens_model.py
from database.db_manager import db

class ContactLensModel:
    @staticmethod
    def save_lenses(patient_id, data, fitting_date):
        # Clear existing record to keep it simple (1 active fitting per patient)
        db.execute_query("DELETE FROM contact_lenses WHERE patient_id = ?", (patient_id,))
        
        query = """
            INSERT INTO contact_lenses (
                patient_id, fitting_date, type, marque, color, observations,
                od_sph, od_cyl, od_axe, od_diametre, od_rayon_bc,
                og_sph, og_cyl, og_axe, og_diametre, og_rayon_bc
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        params = (
            patient_id, fitting_date, 
            data['type'], data['marque'], data['color'], data['observations'],
            data['od_sph'], data['od_cyl'], data['od_axe'], data['od_diametre'], data['od_rayon_bc'],
            data['og_sph'], data['og_cyl'], data['og_axe'], data['og_diametre'], data['og_rayon_bc']
        )
        return db.execute_query(query, params)

    @staticmethod
    def get_lenses(patient_id):
        return db.fetch_one("SELECT * FROM contact_lenses WHERE patient_id = ?", (patient_id,))