#!/usr/bin/env python3
"""Add sample data for Indian Boutique"""

import os
import sys
sys.path.append('.')

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from adapters.database.entities import Base, CategoryEntity, ProductEntity
from domain.models import ProductStatus
import uuid
from datetime import datetime

# Database connection
DATABASE_URL = "postgresql://admin:password@localhost:5433/admin_api"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def add_sample_data():
    db = SessionLocal()
    try:
        # Create categories
        categories = [
            {"name": "Sarees", "description": "Traditional Indian sarees in silk, cotton, and designer fabrics"},
            {"name": "Lehengas", "description": "Bridal and party lehengas with intricate embroidery"},
            {"name": "Salwar Suits", "description": "Comfortable and elegant salwar kameez sets"},
            {"name": "Kurtis", "description": "Modern and traditional kurtis for everyday wear"},
            {"name": "Blouses", "description": "Designer blouses to pair with sarees and lehengas"}
        ]
        
        category_ids = {}
        for cat_data in categories:
            category = CategoryEntity(
                id=str(uuid.uuid4()),
                name=cat_data["name"],
                description=cat_data["description"]
            )
            db.add(category)
            category_ids[cat_data["name"]] = category.id
        
        db.commit()
        
        # Create products
        products = [
            {
                "title": "Banarasi Silk Saree",
                "description": "Handwoven Banarasi silk saree with gold zari work",
                "sku_id": "BSS001",
                "material": "Pure Silk",
                "pattern": "Traditional Zari",
                "color_primary": "#8B0000",
                "colors": [
                    {"name": "Deep Red", "code": "#8B0000"},
                    {"name": "Royal Blue", "code": "#4169E1"},
                    {"name": "Emerald Green", "code": "#50C878"}
                ],
                "width_estimate_cm": 550,
                "scale": "6 meters",
                "special_features": ["Handwoven", "Gold Zari", "Pure Silk", "Traditional"],
                "image_urls": {
                    "main": "banarasi_red_main.jpg",
                    "detail": "banarasi_red_detail.jpg",
                    "model": "banarasi_red_model.jpg"
                },
                "category": "Sarees"
            },
            {
                "title": "Designer Bridal Lehenga",
                "description": "Heavy embroidered bridal lehenga with dupatta",
                "sku_id": "DBL001",
                "material": "Velvet",
                "pattern": "Heavy Embroidery",
                "color_primary": "#DC143C",
                "colors": [
                    {"name": "Bridal Red", "code": "#DC143C"},
                    {"name": "Royal Maroon", "code": "#800000"},
                    {"name": "Pink Rose", "code": "#FF69B4"}
                ],
                "width_estimate_cm": 400,
                "scale": "Full Length",
                "special_features": ["Bridal Wear", "Heavy Work", "Designer", "Dupatta Included"],
                "image_urls": {
                    "main": "bridal_lehenga_main.jpg",
                    "back": "bridal_lehenga_back.jpg",
                    "detail": "bridal_lehenga_detail.jpg"
                },
                "category": "Lehengas"
            },
            {
                "title": "Anarkali Salwar Suit",
                "description": "Flowing Anarkali suit with churidar and dupatta",
                "sku_id": "ASS001",
                "material": "Georgette",
                "pattern": "Floral Print",
                "color_primary": "#FF1493",
                "colors": [
                    {"name": "Magenta", "code": "#FF1493"},
                    {"name": "Turquoise", "code": "#40E0D0"},
                    {"name": "Orange", "code": "#FF8C00"}
                ],
                "width_estimate_cm": 200,
                "scale": "Medium",
                "special_features": ["Flowy", "Comfortable", "Party Wear", "Dupatta"],
                "image_urls": {
                    "main": "anarkali_magenta_main.jpg",
                    "side": "anarkali_magenta_side.jpg"
                },
                "category": "Salwar Suits"
            },
            {
                "title": "Cotton Block Print Kurti",
                "description": "Comfortable cotton kurti with traditional block prints",
                "sku_id": "CBK001",
                "material": "Cotton",
                "pattern": "Block Print",
                "color_primary": "#4682B4",
                "colors": [
                    {"name": "Steel Blue", "code": "#4682B4"},
                    {"name": "Mustard Yellow", "code": "#FFDB58"},
                    {"name": "Mint Green", "code": "#98FB98"}
                ],
                "width_estimate_cm": 100,
                "scale": "Regular",
                "special_features": ["Breathable", "Daily Wear", "Hand Block Print", "Comfortable"],
                "image_urls": {
                    "main": "cotton_kurti_blue.jpg",
                    "pattern": "cotton_kurti_pattern.jpg"
                },
                "category": "Kurtis"
            },
            {
                "title": "Designer Silk Blouse",
                "description": "Embroidered silk blouse for sarees and lehengas",
                "sku_id": "DSB001",
                "material": "Silk",
                "pattern": "Embroidered",
                "color_primary": "#FFD700",
                "colors": [
                    {"name": "Golden", "code": "#FFD700"},
                    {"name": "Silver", "code": "#C0C0C0"},
                    {"name": "Rose Gold", "code": "#E8B4B8"}
                ],
                "width_estimate_cm": 50,
                "scale": "Blouse",
                "special_features": ["Designer", "Embroidered", "Silk", "Versatile"],
                "image_urls": {
                    "main": "silk_blouse_gold.jpg",
                    "back": "silk_blouse_back.jpg"
                },
                "category": "Blouses"
            }
        ]
        
        for prod_data in products:
            product = ProductEntity(
                id=str(uuid.uuid4()),
                title=prod_data["title"],
                description=prod_data["description"],
                sku_id=prod_data["sku_id"],
                material=prod_data["material"],
                pattern=prod_data["pattern"],
                color_primary=prod_data["color_primary"],
                colors=prod_data["colors"],
                width_estimate_cm=prod_data["width_estimate_cm"],
                scale=prod_data["scale"],
                special_features=prod_data["special_features"],
                image_urls=prod_data["image_urls"],
                created_by="admin",
                status="PUBLISHED",
                enabled=True,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            db.add(product)
        
        db.commit()
        print("✅ Sample data added successfully!")
        print(f"✅ Added {len(categories)} categories")
        print(f"✅ Added {len(products)} products")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    add_sample_data()
