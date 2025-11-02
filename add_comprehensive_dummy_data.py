#!/usr/bin/env python3

import uuid
import random
from datetime import datetime
import psycopg2
import os

# Database connection
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://admin:password@localhost:5432/admin_api")

def get_db_connection():
    return psycopg2.connect(DATABASE_URL)

def add_dummy_data():
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        # Get existing products and partners
        cur.execute("SELECT id FROM products LIMIT 5")
        products = [row[0] for row in cur.fetchall()]
        
        cur.execute("SELECT id FROM partners LIMIT 3")
        partners = [row[0] for row in cur.fetchall()]
        
        if not products:
            print("No products found. Please create products first.")
            return
            
        if not partners:
            print("No partners found. Please create partners first.")
            return
        
        # Colors and variants data
        colors = [
            {"code": "#FF0000", "name": "Red"},
            {"code": "#00FF00", "name": "Green"},
            {"code": "#0000FF", "name": "Blue"},
            {"code": "#FFFF00", "name": "Yellow"},
            {"code": "#FF00FF", "name": "Magenta"},
            {"code": "#00FFFF", "name": "Cyan"},
            {"code": "#FFA500", "name": "Orange"},
            {"code": "#800080", "name": "Purple"}
        ]
        
        variant_count = 0
        stock_count = 0
        price_count = 0
        
        # Create variants for each product
        for product_id in products:
            # Create 2-3 variants per product
            num_variants = random.randint(2, 3)
            selected_colors = random.sample(colors, num_variants)
            
            for i, color in enumerate(selected_colors):
                variant_id = str(uuid.uuid4())
                
                # Insert variant
                cur.execute("""
                    INSERT INTO product_variants (id, product_id, variant_name, color_code, color_name, 
                                                range_details, sku_suffix, additional_images, is_active, created_by)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    variant_id,
                    product_id,
                    f"{color['name']} Variant",
                    color['code'],
                    color['name'],
                    '{}',
                    f"-{color['name'].upper()[:3]}",
                    '{}',
                    True,
                    'system'
                ))
                variant_count += 1
                
                # Create stock records for each partner
                for partner_id in partners:
                    stock_id = str(uuid.uuid4())
                    quantity = random.randint(50, 200)
                    wholesale_price = round(random.uniform(15.0, 30.0), 2)
                    retail_price = round(wholesale_price * 1.4, 2)
                    
                    cur.execute("""
                        INSERT INTO stock (id, product_id, variant_id, partner_id, partner_sku, 
                                         quantity_available, quantity_reserved, reorder_level, 
                                         wholesale_price, retail_price, currency)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (
                        stock_id,
                        product_id,
                        variant_id,
                        partner_id,
                        f"SKU-{variant_id[:8]}-{partner_id[:8]}",
                        quantity,
                        random.randint(0, 10),
                        random.randint(10, 25),
                        wholesale_price,
                        retail_price,
                        'INR'
                    ))
                    stock_count += 1
            
            # Create price record for the product
            cur.execute("""
                INSERT INTO price_tables (id, product_id, wholesale_price, retail_price, currency, created_by, version)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (product_id) DO UPDATE SET
                    wholesale_price = EXCLUDED.wholesale_price,
                    retail_price = EXCLUDED.retail_price,
                    modified_time = NOW(),
                    version = price_tables.version + 1
            """, (
                str(uuid.uuid4()),
                product_id,
                round(random.uniform(20.0, 35.0), 2),
                round(random.uniform(28.0, 50.0), 2),
                'INR',
                'system',
                1
            ))
            price_count += 1
        
        conn.commit()
        print(f"✅ Successfully added:")
        print(f"   - {variant_count} variants")
        print(f"   - {stock_count} stock records")
        print(f"   - {price_count} price records")
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Error: {e}")
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    add_dummy_data()
