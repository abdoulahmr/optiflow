# models/prescription_model.py
from database.db_manager import db

class PrescriptionModel:
    @staticmethod
    def save_prescription(patient_id, vl_data, vp_data, exam_date):
        """Saves or updates a prescription for a patient."""
        # First, delete existing prescription for this patient to keep it simple 
        # (In a full system, we'd keep history, but for the current active prescription we upsert)
        db.execute_query("DELETE FROM prescriptions WHERE patient_id = ?", (patient_id,))
        
        query = """
            INSERT INTO prescriptions (
                patient_id, exam_date,
                vl_sph_od, vl_cyl_od, vl_axe_od, vl_add_od,
                vl_sph_og, vl_cyl_og, vl_axe_og, vl_add_og,
                vp_sph_od, vp_cyl_od, vp_axe_od, vp_add_od,
                vp_sph_og, vp_cyl_og, vp_axe_og, vp_add_og
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        params = (
            patient_id, exam_date,
            vl_data['sph_od'], vl_data['cyl_od'], vl_data['axe_od'], vl_data['add_od'],
            vl_data['sph_og'], vl_data['cyl_og'], vl_data['axe_og'], vl_data['add_og'],
            vp_data['sph_od'], vp_data['cyl_od'], vp_data['axe_od'], vp_data['add_od'],
            vp_data['sph_og'], vp_data['cyl_og'], vp_data['axe_og'], vp_data['add_og']
        )
        return db.execute_query(query, params)

    @staticmethod
    def get_prescription(patient_id):
        query = "SELECT * FROM prescriptions WHERE patient_id = ?"
        return db.fetch_one(query, (patient_id,))

#