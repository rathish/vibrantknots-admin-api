#!/usr/bin/env python3
"""
Add dummy data for variants, stock and pricing
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def add_dummy_data():
    """Add comprehensive dummy data for variants, stock and pricing"""
    
    # Create categories
    categories = [
        {"name": "Cotton Fabrics", "description": "Premium cotton materials"},
        {"name": "Silk Fabrics", "description": "Luxury silk materials"},
        {"name": "Linen Fabrics", "description": "Natural linen materials"}
    ]
    
    category_ids = []
    print("Creating categories...")
    for cat in categories:
        response = requests.post(f"{BASE_URL}/categories", json=cat)
        if response.status_code == 200:
            category_ids.append(response.json()["id"])
            print(f"  ✓ {cat['name']}")
    
    # Create partners
    partners = [
        {"name": "Mumbai Textiles", "code": "MUM-TEX"},
        {"name": "Delhi Fabrics", "code": "DEL-FAB"},
        {"name": "Bangalore Weavers", "code": "BLR-WEV"}
    ]
    
    partner_ids = []
    print("\nCreating partners...")
    for partner in partners:
        response = requests.post(f"{BASE_URL}/partners", json=partner)
        if response.status_code == 200:
            partner_ids.append(response.json()["id"])
            print(f"  ✓ {partner['name']}")
    
    # Create products with variants
    products_data = [
        {
            "title": "Premium Cotton Collection",
            "sku_id": "COT-001",
            "description": "High-quality cotton fabric collection",
            "material": "Cotton",
            "pattern": "Solid",
            "variants": [
                {"color_name": "Crimson Red", "color_code": "#DC143C", "sku_suffix": "CRM"},
                {"color_name": "Navy Blue", "color_code": "#000080", "sku_suffix": "NVY"},
                {"color_name": "Forest Green", "color_code": "#228B22", "sku_suffix": "FOR"},
                {"color_name": "Golden Yellow", "color_code": "#FFD700", "sku_suffix": "GLD"}
            ]
        },
        {
            "title": "Luxury Silk Series",
            "sku_id": "SLK-001", 
            "description": "Premium silk fabric series",
            "material": "Silk",
            "pattern": "Textured",
            "variants": [
                {"color_name": "Royal Purple", "color_code": "#663399", "sku_suffix": "RPL"},
                {"color_name": "Emerald Green", "color_code": "#50C878", "sku_suffix": "EMR"},
                {"color_name": "Champagne Gold", "color_code": "#F7E7CE", "sku_suffix": "CHM"}
            ]
        },
        {
            "title": "Natural Linen Range",
            "sku_id": "LIN-001",
            "description": "Organic linen fabric range", 
            "material": "Linen",
            "pattern": "Woven",
            "variants": [
                {"color_name": "Ivory White", "color_code": "#FFFFF0", "sku_suffix": "IVY"},
                {"color_name": "Beige Tan", "color_code": "#F5F5DC", "sku_suffix": "BGE"},
                {"color_name": "Charcoal Gray", "color_code": "#36454F", "sku_suffix": "CHR"}
            ]
        }
    ]
    
    print("\nCreating products with variants and stock...")
    
    for i, product_data in enumerate(products_data):
        # Create product
        product_payload = {
            "title": product_data["title"],
            "sku_id": product_data["sku_id"],
            "description": product_data["description"],
            "material": product_data["material"],
            "pattern": product_data["pattern"],
            "category_id": category_ids[i % len(category_ids)]
        }
        
        response = requests.post(f"{BASE_URL}/products", json=product_payload)
        if response.status_code != 200:
            print(f"  ✗ Failed to create {product_data['title']}")
            continue
            
        product = response.json()
        product_id = product["id"]
        print(f"\n  ✓ Product: {product_data['title']} ({product_id})")
        
        # Create variants for this product
        for j, variant_data in enumerate(product_data["variants"]):
            variant_payload = {
                "variant_name": variant_data["color_name"],
                "color_name": variant_data["color_name"],
                "color_code": variant_data["color_code"],
                "sku_suffix": variant_data["sku_suffix"],
                "is_active": True
            }
            
            response = requests.post(f"{BASE_URL}/api/v1/products/{product_id}/variants", json=variant_payload)
            if response.status_code != 200:
                print(f"    ✗ Failed to create variant {variant_data['color_name']}")
                continue
                
            variant = response.json()
            variant_id = variant["id"]
            print(f"    ✓ Variant: {variant_data['color_name']} ({variant_id})")
            
            # Add stock records for each partner
            for k, partner_id in enumerate(partner_ids):
                base_quantity = 100 + (j * 50) + (k * 25)
                base_retail = 25.99 + (i * 10) + (j * 5)
                base_wholesale = base_retail * 0.75
                
                stock_payload = {
                    "partner_id": partner_id,
                    "available_quantity": base_quantity,
                    "retail_price": round(base_retail, 2),
                    "wholesale_price": round(base_wholesale, 2),
                    "currency": "INR"
                }
                
                response = requests.post(f"{BASE_URL}/api/v1/products/{product_id}/variants/{variant_id}/stock", json=stock_payload)
                if response.status_code == 200:
                    print(f"      ✓ Stock: Partner {k+1} - {base_quantity} units @ ₹{base_retail}")
                else:
                    print(f"      ✗ Failed to add stock for Partner {k+1}")
    
    print(f"\n🎉 Dummy data creation complete!")
    print(f"\nSummary:")
    print(f"  • {len(categories)} Categories created")
    print(f"  • {len(partners)} Partners created") 
    print(f"  • {len(products_data)} Products created")
    print(f"  • {sum(len(p['variants']) for p in products_data)} Variants created")
    print(f"  • {sum(len(p['variants']) for p in products_data) * len(partners)} Stock records created")
    
    # Show sample data
    print(f"\n📊 Sample Data Overview:")
    for i, product_data in enumerate(products_data):
        print(f"\n{product_data['title']}:")
        for variant in product_data['variants']:
            print(f"  • {variant['color_name']} ({variant['color_code']}) - SKU: {product_data['sku_id']}-{variant['sku_suffix']}")

if __name__ == "__main__":
    add_dummy_data()
