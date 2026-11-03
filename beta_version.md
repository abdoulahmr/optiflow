### System Architecture & Overview

**OptiFlow** is a Point of Sale (POS) and Enterprise Resource Planning (ERP) application engineered for optometry practices, optical shops, and eyewear retailers operating in French-speaking regions with local currency support in Algerian Dinar (DA).

The system unifies patient clinical records, optical prescription calculators, custom lens matrix pricing, multi-category inventory management, supplier ledgers, order checkout workflows, thermal ticket printing, and system configuration into a single dashboard.

---

### Comprehensive Module Breakdown

```
                             ┌──────────────────────────────────────┐
                             │           OptiFlow            │
                             └──────────────────┬───────────────────┘
                                                │
         ┌───────────────────┬──────────────────┼───────────────────┬───────────────────┐
         │                   │                  │                   │                   │
┌────────┴─────────┐ ┌───────┴────────┐ ┌───────┴────────┐ ┌────────┴─────────┐ ┌────────┴─────────┐
│ Patient EHR &    │ │ Optical Lens   │ │ Inventory &    │ │ Supplier Ledger │ │ POS Checkout &  │
│ Prescriptions    │ │ Price Matrix   │ │ Product Stock  │ │ & Accounting    │ │ Thermal Receipts│
└──────────────────┘ └────────────────┘ └────────────────┘ └─────────────────┘ └─────────────────┘

```

#### 1. Patient EHR & Optical Prescriptions (`Clients` / `Fiche Client`)

* **Personal & Clinical Profile:** Captures patient identity including Last Name (*Nom*), First Name (*Prénom*), Date of Birth, auto-calculated Age, Gender, Phone Number, and Residential Address.


* **Pupillary Distance (PD) Tracking:** Dedicated inputs for **PD OD** (Right Eye), **PD OG** (Left Eye), and an auto-calculated **PD Total**.


* **Spectacle Refraction Grid (`Correction Optique`):**
* Separate calculation arrays for **VL** (*Vision de Loin* / Distance) and **VP** (*Vision de Près* / Near).


* Parameters recorded for Right Eye (OD) and Left Eye (OG): **SPH** (Sphere), **CYL** (Cylinder), **AXE** (Axis), **Prisme** (Prism), **Base**, **ADD** (Addition), and Exam Date.




* **Contact Lens Fitting Module (`Lentilles de Contact`):**
* Toggle switch to activate fitting parameters alongside fitting date tracking.


* Refraction metrics per eye: Lens Type (e.g., *Lentille Souple*), SPH, CYL, AXE, **Diamètre** (Diameter), and **Rayon BC** (Base Curve).


* Additional metadata for Brand (*Marque*), Lens Color, and free-text clinical observations (*Note / Observations*).




* **Prescription History Tabs:** Direct navigation to historical spectacle corrections (*Historique - Corrections Précédentes*) and previous contact lens fittings (*Historique Lentilles*).



#### 2. Optical Lens Price Matrix & Stock (`Matrice des Prix des Verres` & `Verres`)

* **Multi-Tabbed Grid Matrix:** Tabbed views for **Verre Transparent**, **Verre Photochromique**, and **Verres Spéciale**.


* **Grid Mapping Schema:**
* **Y-Axis:** Optical Power Groups ($G_2, G_4, G_6, G_8, G_{10}, G_{2/2}, G_{2/4}, \dots, G_{2/10}$).


* **X-Axis:** Treatment combinations (**HC Hard Coat**, **HMC Multi-Coat**, **Blue Block**) across Refractive Indices (**1.56**, **1.61**, **1.67**, **1.74**).




* **Pricing & Data Exchange:** Toggles between **Prix de Vente** (Retail Price) and **Prix d'Achat** (Cost Price), with built-in **Import Data** and **Export Excel** controls.


* **Automated Prescription Naming:** Entering optical parameters (SPH, CYL, Treatment, Index) automatically assigns the optical group ($G_2$) and generates standard product strings (e.g., *Transparent HMC 1.56 Mid-Index G2 (Sph: 0.00 Cyl: 0.00)*).


* **Lens Filter & Search Engine:** Dedicated inventory view filtering lenses by SPH, CYL, Treatment, Type, and Refraction Index.



#### 3. General Inventory & Stock Management (`Stock` & `Gestion du Produit`)

* **Multi-Category Support:** Handles non-lens inventory including Frames (*Montures*), Contact Lenses (*Lentilles*), Cleaning Solutions (*Produits de nettoyage*), and Accessories.


* **Automated Barcode System:** Generates unique numeric barcodes (e.g., `1000001`) for scanning and label printing.


* **Dynamic Pricing Calculation:** Evaluates retail price based on cost price (*Prix Achat*) and a customizable markup multiplier ($k$ / *Coefficient*).


* **Perishability & Low Stock Alerts:** Optional expiration toggle that initiates system notifications **3 months prior** to expiry, alongside customizable minimum stock threshold limits (*Seuil*).


* **Inventory KPI Dashboard:** Live status cards monitoring Total References, Total Purchase Stock Value, Low Stock Count (*Stock Faible*), Out of Stock Count (*Rupture de Stock*), and Expiring Items (*Péremption Proche*).



#### 4. Supplier Ledger & Accounts Payable (`Fournisseurs`)

* **Supplier Profiles (`Fiche Fournisseur`):** Registers business details, point of contact, and category tags (e.g., *Montures*).


* **Fiscal & Financial Compliance:** Tracks formal tax identification fields including **RC**, **NIF**, **NIS**, **ART**, **CCP**, and **Bank RIB**.


* **Integrated Financial Ledger (`Historique des Transactions`):** Directly records supplier invoices (*Facture*) and payment receipts (*Versement*), calculating live balance due (*Solde Global Dû*).



#### 5. POS Checkout & Thermal Receipts (`Nouvelle Prescription` & `Finalisation`)

* **Point of Sale Interface:** Combines lens prescriptions, frame selections, and additional services into a unified cart summary (`Récapitulatif`).


* **Split Vision Calculation:** Calculates equipment costs independently for Distance Vision (VL) and Near Vision (VP).


* **Order Settlement Modal (`Règlement`):**
* Displays Total Payable, Deposit Received (*Versement / Montant Reçu*), and Remaining Balance (*Reste à Payer*).


* State tracking toggles between **En cours** (Processing) and **Livré** (Delivered).


* Supports multiple payment channels: Cash (*Espèces*), Card (*CIB*), or Check (*Chèque*).




* **80mm Thermal Receipt Generator:**
* Itemized receipt containing store details, patient information, timestamp, and unique Client ID (*ID Client*).


* Breakdown of right/left eye lenses, frames, and cords/accessories with subtotal, discount (*Remise*), amount paid, and balance due.


* System-generated barcode for order retrieval and bilingual store policy notes in French and Arabic.





#### 6. System Settings & Controls (`Paramètres`)

* **System Settings:** Admin controls divided into Store Profile (*Établissement*), User Roles & Access (*Utilisateurs*), Default Pricing Grids (*Tarifs par Défaut*), and Data Backups (*Sauvegarde*).


* **Header & Security Bar:** Live alerts for trial/license duration (*4 jours restants*), notification panel, and role-based privilege displays (*admin / Administrateur*).