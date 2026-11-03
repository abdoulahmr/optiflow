# models/patient_model.py
from database.db_manager import db
from datetime import datetime

class PatientModel:
    @staticmethod
    def calculate_age(dob_str):
        """Calculates age from YYYY-MM-DD string"""
        if not dob_str: return None
        try:
            dob = datetime.strptime(dob_str, "%Y-%m-%d")
            today = datetime.today()
            return today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
        except ValueError:
            return None

    @staticmethod
    def add_patient(data):
        # Auto-calculate age before inserting
        data['age'] = PatientModel.calculate_age(data.get('date_of_birth'))
        query = """
            INSERT INTO patients (nom, prenom, date_of_birth, age, gender, phone, address)
            VALUES (:nom, :prenom, :date_of_birth, :age, :gender, :phone, :address)
        """
        return db.execute_query(query, data)

    @staticmethod
    def get_all_patients(search_term=""):
        query = """
            SELECT p.*, 
                   (SELECT exam_date FROM prescriptions WHERE patient_id = p.id ORDER BY exam_date DESC LIMIT 1) as last_exam,
                   (SELECT vl_sph_od FROM prescriptions WHERE patient_id = p.id ORDER BY exam_date DESC LIMIT 1) as vl_sph_od,
                   (SELECT vl_cyl_od FROM prescriptions WHERE patient_id = p.id ORDER BY exam_date DESC LIMIT 1) as vl_cyl_od,
                   (SELECT vl_sph_og FROM prescriptions WHERE patient_id = p.id ORDER BY exam_date DESC LIMIT 1) as vl_sph_og,
                   (SELECT vl_cyl_og FROM prescriptions WHERE patient_id = p.id ORDER BY exam_date DESC LIMIT 1) as vl_cyl_og
            FROM patients p
        """
        params = {}
        if search_term:
            # Search in patient info OR in their prescription history
            query += """
                WHERE p.nom LIKE :search OR p.prenom LIKE :search OR p.phone LIKE :search
                OR p.id IN (SELECT patient_id FROM prescriptions WHERE exam_date LIKE :search)
            """
            params['search'] = f"%{search_term}%"
            
        query += " ORDER BY p.nom ASC"
        return db.fetch_all(query, params)

    @staticmethod
    def get_patient(patient_id):
        query = "SELECT * FROM patients WHERE id = ?"
        return db.fetch_one(query, (patient_id,))

    @staticmethod
    def get_patient_orders(patient_id):
        """Returns all orders for a patient, with items count."""
        query = """
            SELECT o.id, o.created_at, o.client_id_text, o.total_payable, 
                   o.deposit_received, o.remaining_balance, o.status, o.payment_method,
                   (SELECT COUNT(*) FROM order_items WHERE order_id = o.id) as items_count
            FROM orders o
            WHERE o.patient_id = ?
            ORDER BY o.created_at DESC
        """
        return db.fetch_all(query, (patient_id,))

    @staticmethod
    def get_all_prescriptions(patient_id):
        """Returns all prescriptions for a patient ordered by date."""
        query = """
            SELECT exam_date, 
                   vl_sph_od, vl_cyl_od, vl_axe_od, vl_add_od,
                   vl_sph_og, vl_cyl_og, vl_axe_og, vl_add_og,
                   vp_sph_od, vp_cyl_od, vp_axe_od, vp_add_od,
                   vp_sph_og, vp_cyl_og, vp_axe_og, vp_add_og
            FROM prescriptions
            WHERE patient_id = ?
            ORDER BY exam_date DESC
        """
        return db.fetch_all(query, (patient_id,))

    @staticmethod
    def get_all_contact_lenses(patient_id):
        """Returns all contact lens fittings for a patient."""
        query = """
            SELECT fitting_date, type, marque, color,
                   od_sph, od_cyl, od_axe, od_diametre, od_rayon_bc,
                   og_sph, og_cyl, og_axe, og_diametre, og_rayon_bc,
                   observations
            FROM contact_lenses
            WHERE patient_id = ?
            ORDER BY fitting_date DESC
        """
        return db.fetch_all(query, (patient_id,))