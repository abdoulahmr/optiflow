# models/lens_model.py
from database.db_manager import db
import math

class LensModel:
    @staticmethod
    def initialize_matrix():
        """Clears old format and generates the exact new groups and columns."""
        # PERFORMANCE FIX: If the table already has lenses, skip the heavy loop entirely
        count = db.fetch_one("SELECT COUNT(*) as count FROM lenses")['count']
        if count > 0:
            # Check if old schema exists and force rebuild
            old_schema = db.fetch_one("SELECT sql FROM sqlite_master WHERE type='table' AND name='lenses'")
            if old_schema and 'refractive_index' in old_schema['sql']:
                db.execute_query("DROP TABLE lenses")
                db.execute_query("""
                    CREATE TABLE lenses (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        type TEXT NOT NULL,
                        treatment TEXT NOT NULL,
                        optical_group TEXT NOT NULL,
                        retail_price REAL,
                        cost_price REAL,
                        stock_qty INTEGER DEFAULT 0
                    )
                """)
            else:
                return # Database is already updated, exit immediately!
            
        # The list of 17 groups requested
        groups = [
            "G2", "G4", "G6", "G8", "G10", "G12", "G14",
            "G2/2", "G2/4", "G2/6", "G2/8", "G2/10", "G2/12", "G2/14",
            "G6/2", "G6/4", "G6/6"
        ]
        
        # The 30 columns requested
        columns = [
            "HMC 1.5", "HMC 1.6", "HMC 1.67", "HMC 1.74",
            "BB 1.5", "BB 1.6", "BB 1.67", "BB 1.74",
            "PROFILO MC", "PROFILO BB", "PC MC", "PC BB",
            "TRANS HC", "TRANS MC", "TRANS BB",
            "YAL 1.5", "YAL 1.6", "YAL 1.67", "YALLA 1.67", "YAL 1.74",
            "YAL BB 1.6", "YAL BB 1.67", "YAL TRAN MC", "YAL TRAN B",
            "CRISTAL/AZUR 1.5 MC", "CRISTAL/AZUR 1.5 BB", "DRIVE 1.5",
            "TOP MC", "YOUNG ASPH 1.74", "ZEISS"
        ]
        
        types = ["Transparent", "Photochromique", "Speciale"]
        
        try:
            existing = db.fetch_all("SELECT type, optical_group, treatment FROM lenses")
            existing_set = {(row['type'], row['optical_group'], row['treatment']) for row in existing}
            
            to_insert = []
            for t in types:
                for g in groups:
                    for c in columns:
                        if (t, g, c) not in existing_set:
                            to_insert.append((t, c, g, 0.0, 0.0, 0)) # type, treatment, group, retail, cost, stock
            
            if to_insert:
                cursor = db.conn.cursor()
                cursor.executemany(
                    "INSERT INTO lenses (type, treatment, optical_group, retail_price, cost_price, stock_qty) VALUES (?, ?, ?, ?, ?, ?)",
                    to_insert
                )
                db.conn.commit()
        except Exception as e:
            print(f"Error initializing matrix: {e}")

    @staticmethod
    def get_all_groups():
        """Fetches distinct optical groups for the matrix UI."""
        result = db.fetch_all("SELECT DISTINCT optical_group FROM lenses ORDER BY optical_group ASC")
        return [row['optical_group'] for row in result]

    @staticmethod
    def get_all_treatments():
        """Fetches distinct treatments for the matrix UI columns."""
        result = db.fetch_all("SELECT DISTINCT treatment FROM lenses ORDER BY treatment ASC")
        return [row['treatment'] for row in result]

    @staticmethod
    def add_group(group_name):
        """Adds a new group and generates all missing rows for it."""
        group_name = group_name.strip()
        if not group_name: return False
        
        treatments = LensModel.get_all_treatments()
        types = ["Transparent", "Photochromique", "Speciale"]
        
        to_insert = []
        for t in types:
            for tr in treatments:
                exists = db.fetch_one("SELECT id FROM lenses WHERE type=? AND optical_group=? AND treatment=?", (t, group_name, tr))
                if not exists:
                    to_insert.append((t, tr, group_name, 0.0, 0.0, 0))
                    
        if to_insert:
            cursor = db.conn.cursor()
            cursor.executemany(
                "INSERT INTO lenses (type, treatment, optical_group, retail_price, cost_price, stock_qty) VALUES (?, ?, ?, ?, ?, ?)",
                to_insert
            )
            db.conn.commit()
        return True

    @staticmethod
    def add_treatment(treatment_name):
        """Adds a new column (treatment) and generates all missing rows for it."""
        treatment_name = treatment_name.strip()
        if not treatment_name: return False
        
        groups = LensModel.get_all_groups()
        types = ["Transparent", "Photochromique", "Speciale"]
        
        to_insert = []
        for t in types:
            for g in groups:
                exists = db.fetch_one("SELECT id FROM lenses WHERE type=? AND optical_group=? AND treatment=?", (t, g, treatment_name))
                if not exists:
                    to_insert.append((t, treatment_name, g, 0.0, 0.0, 0))
                    
        if to_insert:
            cursor = db.conn.cursor()
            cursor.executemany(
                "INSERT INTO lenses (type, treatment, optical_group, retail_price, cost_price, stock_qty) VALUES (?, ?, ?, ?, ?, ?)",
                to_insert
            )
            db.conn.commit()
        return True

    @staticmethod
    def delete_group(group_name):
        db.execute_query("DELETE FROM lenses WHERE optical_group = ?", (group_name,))
        
    @staticmethod
    def update_group(old_name, new_name):
        new_name = new_name.strip()
        if not new_name or new_name == old_name: return False
        db.execute_query("UPDATE lenses SET optical_group = ? WHERE optical_group = ?", (new_name, old_name))
        return True

    @staticmethod
    def delete_treatment(treatment_name):
        db.execute_query("DELETE FROM lenses WHERE treatment = ?", (treatment_name,))
        
    @staticmethod
    def update_treatment(old_name, new_name):
        new_name = new_name.strip()
        if not new_name or new_name == old_name: return False
        db.execute_query("UPDATE lenses SET treatment = ? WHERE treatment = ?", (new_name, old_name))
        return True

    @staticmethod
    def get_lenses(lens_type):
        query = "SELECT * FROM lenses WHERE type = ?"
        raw_data = db.fetch_all(query, (lens_type,))
        
        exact_order = [
            "G2", "G4", "G6", "G8", "G10", "G12", "G14",
            "G2/2", "G2/4", "G2/6", "G2/8", "G2/10", "G2/12", "G2/14",
            "G6/2", "G6/4", "G6/6"
        ]
        
        raw_data.sort(key=lambda x: exact_order.index(x['optical_group']) if x['optical_group'] in exact_order else 999)
        return raw_data

    @staticmethod
    def save_matrix_batch(data_list):
        """Saves prices only — stock is now managed via LensStockModel."""
        try:
            cursor = db.conn.cursor()
            for item in data_list:
                if item['type'] == 'retail':
                    cursor.execute("UPDATE lenses SET retail_price = ? WHERE id = ?", 
                                   (item['price'], item['id']))
                else:
                    cursor.execute("UPDATE lenses SET cost_price = ? WHERE id = ?", 
                                   (item['price'], item['id']))
            db.conn.commit()
        except Exception as e:
            print(f"Error saving matrix: {e}")

    @staticmethod
    def sell_lens(lens_id, quantity_sold=1):
        """Decreases lens stock when a sale is finalized in the POS."""
        db.execute_query("UPDATE lenses SET stock_qty = stock_qty - ? WHERE id = ?", (quantity_sold, lens_id))

    @staticmethod
    def calculate_lens_group(sph, cyl):
        """Determines the optical group based on SPH and CYL values.
        
        Convention:
        - SPH ±[0-1.75] → group 2
        - SPH ±[2-3.75] → group 4
        - SPH ±[4-5.75] → group 6
        - SPH ±[6-7.75] → group 8
        - SPH ±[8-9.75] → group 10
        - etc.
        
        - If CYL = 0 → no suffix (just "G2", "G4", etc.)
        - If CYL ≠ 0 → append "/{cyl_group}" using same logic
        
        Examples:
        - SPH +1.50, CYL 0      → "G2"
        - SPH +1.50, CYL +0.50  → "G2/2"
        - SPH -2.75, CYL 0      → "G4"
        - SPH -4.50, CYL -1.25  → "G6/2"
        - SPH +5.00, CYL +7.50  → "G6/8"
        - SPH +3.25, CYL -2.75  → "G4/4"
        """
        def get_group_number(value):
            """Returns 2, 4, 6, 8, 10, ... based on absolute value.
            - 0-1.75 → 2
            - 2-3.75 → 4
            - 4-5.75 → 6
            - etc.
            """
            abs_val = abs(value)
            return 2 * math.ceil((abs_val + 0.25) / 2)
        
        sph_group = get_group_number(sph)
        
        if abs(cyl) < 0.01:  # CYL is effectively 0
            return f"G{sph_group}"
        
        cyl_group = get_group_number(cyl)
        return f"G{sph_group}/{cyl_group}"

    @staticmethod
    def find_lens_by_group_treatment_type(group, treatment, lens_type):
        """Finds a lens by its group, treatment, and type."""
        return db.fetch_one(
            "SELECT * FROM lenses WHERE optical_group=? AND treatment=? AND type=?",
            (group, treatment, lens_type)
        )

    @staticmethod
    def get_group_ranges(group_name):
        """Parses a group name and returns the SPH/CYL ranges.
        Returns: (sph_min, sph_max, cyl_min, cyl_max)
        """
        import re
        match = re.match(r'G(\d+)(?:/(\d+))?', group_name)
        if not match:
            return (0, 0, 0, 0)
        
        sph_num = int(match.group(1))
        cyl_num = int(match.group(2)) if match.group(2) else 0
        
        sph_min = max(0, sph_num - 2)
        sph_max = sph_min + 1.75
        cyl_min = max(0, cyl_num - 2)
        cyl_max = cyl_min + 1.75 if cyl_num > 0 else 0
        
        return (sph_min, sph_max, cyl_min, cyl_max)
    
    @staticmethod
    def get_valid_values_for_group(group_name):
        """Returns valid SPH and CYL values for a group, strictly within the range.
        
        Returns: (list_of_sph_values, list_of_cyl_values)
        Each item is a tuple: (actual_value, display_text)
        
        Sort order (descending):
        For G2 (range 0-1.75):
          +1.75, +1.50, ..., +0.25, 0.00, -0.25, ..., -1.75
        
        For G4 (range 2-3.75):  
          +3.75, +3.50, ..., +2.00, -2.00, -2.25, ..., -3.75  (NO 0.00!)
        
        For G6/8 SPH (range 4-5.75):
          +5.75, +5.50, ..., +4.00, -4.00, -4.25, ..., -5.75
        """
        sph_min, sph_max, cyl_min, cyl_max = LensModel.get_group_ranges(group_name)
        
        def generate_values(v_min, v_max):
            """Generate (value, display) tuples strictly within [v_min, v_max]."""
            values = []
            # Lowest positive value to include (skip 0 here, add separately if needed)
            min_positive = max(v_min, 0.25)
            
            # Positive values from v_max down to min_positive (descending)
            v = v_max
            while v >= min_positive - 0.001:
                values.append((round(v, 2), f"+{v:.2f}"))
                v -= 0.25
            
            # Add 0.00 ONLY if 0 is within the range
            if v_min == 0:
                values.append((0.0, "0.00"))
            
            # Negative values from -min_positive down to -v_max (descending)
            v = -min_positive
            while v >= -v_max - 0.001:
                values.append((round(v, 2), f"{v:.2f}"))
                v -= 0.25
            
            return values
        
        sph_values = generate_values(sph_min, sph_max)
        
        cyl_values = []
        if cyl_max == 0:
            cyl_values = [(0.0, "0.00")]
        else:
            cyl_values = generate_values(cyl_min, cyl_max)
        
        return (sph_values, cyl_values)