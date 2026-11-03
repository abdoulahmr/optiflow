-- ==========================================
-- 1. PATIENTS & EHR (Fiche Client)
-- ==========================================
CREATE TABLE IF NOT EXISTS patients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nom TEXT NOT NULL,
    prenom TEXT NOT NULL,
    date_of_birth TEXT,
    age INTEGER,
    gender TEXT,
    phone TEXT,
    address TEXT,
    pd_od REAL,
    pd_og REAL,
    pd_total REAL,
    created_at TEXT DEFAULT (datetime('now', 'localtime'))
);

CREATE TABLE IF NOT EXISTS prescriptions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id INTEGER NOT NULL,
    exam_date TEXT,
    vl_sph_od REAL, vl_cyl_od REAL, vl_axe_od REAL, vl_prisme_od REAL, vl_base_od REAL, vl_add_od REAL,
    vl_sph_og REAL, vl_cyl_og REAL, vl_axe_og REAL, vl_prisme_og REAL, vl_base_og REAL, vl_add_og REAL,
    vp_sph_od REAL, vp_cyl_od REAL, vp_axe_od REAL, vp_prisme_od REAL, vp_base_od REAL, vp_add_od REAL,
    vp_sph_og REAL, vp_cyl_og REAL, vp_axe_og REAL, vp_prisme_og REAL, vp_base_og REAL, vp_add_og REAL,
    FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS contact_lenses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id INTEGER NOT NULL,
    fitting_date TEXT,
    type TEXT,
    marque TEXT, color TEXT, observations TEXT,
    od_sph REAL, od_cyl REAL, od_axe REAL, od_diametre REAL, od_rayon_bc REAL,
    og_sph REAL, og_cyl REAL, og_axe REAL, og_diametre REAL, og_rayon_bc REAL,
    FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE
);

-- ==========================================
-- 2. LENS MATRIX & STOCK (Verres)
-- ==========================================
CREATE TABLE IF NOT EXISTS lenses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    type TEXT NOT NULL,
    treatment TEXT NOT NULL,
    optical_group TEXT NOT NULL,
    retail_price REAL,
    cost_price REAL,
    stock_qty INTEGER DEFAULT 0
);

-- ==========================================
-- 2b. LENS STOCK ENTRIES (per SPH/CYL)
-- ==========================================
CREATE TABLE IF NOT EXISTS lens_stock_entries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    lens_id INTEGER NOT NULL,
    sph REAL NOT NULL,
    cyl REAL NOT NULL,
    quantity INTEGER NOT NULL DEFAULT 0,
    FOREIGN KEY (lens_id) REFERENCES lenses(id) ON DELETE CASCADE,
    UNIQUE(lens_id, sph, cyl)  -- Prevents duplicate SPH/CYL rows for same lens
);

-- ==========================================
-- 3. GENERAL INVENTORY (Gestion du Stock)
-- ==========================================
CREATE TABLE IF NOT EXISTS inventory (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    barcode TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    category TEXT NOT NULL,
    cost_price REAL NOT NULL,
    retail_price REAL NOT NULL,
    coefficient REAL,
    stock_qty INTEGER DEFAULT 0,
    seuil INTEGER DEFAULT 5,
    expiration_date TEXT,
    created_at TEXT DEFAULT (datetime('now', 'localtime'))
);

-- ==========================================
-- 4. SUPPLIERS (Fournisseurs)
-- ==========================================
CREATE TABLE IF NOT EXISTS suppliers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    contact_person TEXT,
    phone TEXT,
    email TEXT,
    address TEXT,
    category_tag TEXT,
    rc TEXT, nif TEXT, nis TEXT, art TEXT, ccp TEXT, bank_rib TEXT,
    balance_due REAL DEFAULT 0.0,
    created_at TEXT DEFAULT (datetime('now', 'localtime'))
);

CREATE TABLE IF NOT EXISTS supplier_transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    supplier_id INTEGER NOT NULL,
    transaction_type TEXT NOT NULL,
    amount REAL NOT NULL,
    date TEXT DEFAULT (datetime('now', 'localtime')),
    note TEXT,
    FOREIGN KEY (supplier_id) REFERENCES suppliers(id) ON DELETE CASCADE
);

-- ==========================================
-- 5. POS CHECKOUT (Nouvelle Prescription & Finalisation)
-- ==========================================
CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id INTEGER NOT NULL,
    client_id_text TEXT,
    total_payable REAL NOT NULL,
    deposit_received REAL DEFAULT 0.0,
    remaining_balance REAL NOT NULL,
    status TEXT DEFAULT 'En cours',
    payment_method TEXT,
    created_at TEXT DEFAULT (datetime('now', 'localtime')),
    FOREIGN KEY (patient_id) REFERENCES patients(id)
);

CREATE TABLE IF NOT EXISTS order_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER NOT NULL,
    item_type TEXT NOT NULL,
    description TEXT,
    price REAL NOT NULL,
    discount REAL DEFAULT 0.0,
    cost_price REAL DEFAULT 0.0,
    FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE
);

-- ==========================================
-- 6. SYSTEM SETTINGS (Paramètres)
-- ==========================================
CREATE TABLE IF NOT EXISTS settings (
    key TEXT PRIMARY KEY,
    value TEXT
);

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    role TEXT NOT NULL
);

-- ==========================================
-- 7. BUSINESS CHARGES (Dépenses)
-- ==========================================
CREATE TABLE IF NOT EXISTS charges (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT DEFAULT (datetime('now', 'localtime')),
    description TEXT NOT NULL,
    category TEXT,
    amount REAL NOT NULL
);

-- ==========================================
-- 8. FINANCIAL SNAPSHOTS (Clôtures)
-- ==========================================
CREATE TABLE IF NOT EXISTS financial_snapshots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    period_type TEXT NOT NULL, -- 'monthly' or 'annual'
    period_value TEXT NOT NULL, -- e.g., '2024-10' or '2024'
    revenue REAL,
    realized_profit REAL,
    total_charges REAL,
    net_profit REAL,
    stock_value REAL,
    total_debt REAL,
    date_saved TEXT DEFAULT (datetime('now', 'localtime')),
    UNIQUE(period_type, period_value) -- Prevents duplicate snapshots for the same period
);

INSERT OR IGNORE INTO settings (key, value) VALUES ('store_name', 'Store');
INSERT OR IGNORE INTO settings (key, value) VALUES ('store_phone', '05 50 50 50 50');
INSERT OR IGNORE INTO settings (key, value) VALUES ('store_address', '12 Rue Centrale, Alger');
INSERT OR IGNORE INTO settings (key, value) VALUES ('is_activated', 'False');