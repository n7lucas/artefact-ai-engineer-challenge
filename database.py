import os
import re
import json
import sqlite3
import pandas as pd
from config import settings

def clean_phone(phone_str: str) -> str:
    """Remove non-numerical characters."""
    if not isinstance(phone_str, str):
        return ""
    return re.sub(r"\D", "", phone_str)

def parse_spec_field(specs_json: str, field_name: str) -> str:
    """Extract specific fields from specs JSON."""
    try:
        data = json.loads(specs_json)
        return str(data.get(field_name, ""))
    except Exception:
        return ""

def init_database(db_path: str = settings.db_path) -> sqlite3.Connection:
    """Load all CSV files from Emporio da Musica, apply the necessary processing, and persist them to the database.."""
    conn = sqlite3.connect(db_path)
    
   
    csv_mapping = {
        "categories": "desafio_tecnico_ai_eng - categories.csv",
        "products": "desafio_tecnico_ai_eng - products.csv",
        "customers": "desafio_tecnico_ai_eng - customers.csv",
        "orders": "desafio_tecnico_ai_eng - orders.csv",
        "order_items": "desafio_tecnico_ai_eng - order_items.csv",
        "promotions": "desafio_tecnico_ai_eng - promotions.csv"
    }

    for table_name, csv_file in csv_mapping.items():
        if not os.path.exists("data\\" +  csv_file):
            print(f"⚠️ Aviso: Arquivo {csv_file} não encontrado na raiz.")
            continue
            
        df = pd.read_csv("data\\" + csv_file)
        
        # Treatment 1: Cleaning of Phone Numbers in the Customers table
        if table_name == "customers" and "phone" in df.columns:
            df["phone_clean"] = df["phone"].apply(clean_phone)
            
        # Treatment 2: Denormalization of the JSON from the Products table
        if table_name == "products" and "specs" in df.columns:
            df["spec_strings"] = df["specs"].apply(lambda s: parse_spec_field(s, "strings"))
            df["spec_electronics"] = df["specs"].apply(lambda s: parse_spec_field(s, "electronics"))
            df["spec_color"] = df["specs"].apply(lambda s: parse_spec_field(s, "color"))

        df.to_sql(table_name, conn, if_exists="replace", index=False)
        print(f"✅ Tabela '{table_name}' ingestada ({len(df)} registros).")

    # Treatment 3: Relational VIEW for the automatic calculation of active discounts
    conn.execute("""
    CREATE VIEW IF NOT EXISTS v_active_promotions AS
    SELECT 
        p.product_id,
        p.name AS product_name,
        p.price_brl AS original_price,
        pm.discount_percent,
        ROUND(p.price_brl * (1 - pm.discount_percent / 100.0), 2) AS promotional_price,
        pm.description AS promotion_description
    FROM products p
    JOIN promotions pm ON p.product_id = pm.product_id
    WHERE pm.is_active = 1;
    """)
    conn.commit()
    print("✅ VIEW 'v_active_promotions' criada com sucesso.")
    return conn