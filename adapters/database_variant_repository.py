from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import text
from domain.product.entities import ProductVariant
from domain.product.repositories import VariantRepository
from domain.product.value_objects import ProductId
import uuid
from datetime import datetime


class DatabaseVariantRepository(VariantRepository):
    def __init__(self, db: Session):
        self.db = db
    
    def save(self, variant: ProductVariant) -> ProductVariant:
        """Save or update a variant"""
        if hasattr(variant, 'variant_id') and variant.variant_id:
            # Update existing variant
            self.db.execute(
                text("""
                    UPDATE product_variants 
                    SET variant_name = :variant_name,
                        color_code = :color_code,
                        color_name = :color_name,
                        sku_suffix = :sku_suffix,
                        updated_time = NOW()
                    WHERE id = :variant_id
                """),
                {
                    "variant_id": variant.variant_id,
                    "variant_name": variant.color_name,
                    "color_code": variant.color_code,
                    "color_name": variant.color_name,
                    "sku_suffix": variant.sku_suffix
                }
            )
        else:
            # Create new variant
            variant_id = str(uuid.uuid4())
            variant.variant_id = variant_id
            
            self.db.execute(
                text("""
                    INSERT INTO product_variants (id, product_id, variant_name, color_code, color_name, 
                                                sku_suffix, range_details, additional_images, is_active, created_by)
                    VALUES (:id, :product_id, :variant_name, :color_code, :color_name, 
                            :sku_suffix, '{}', '{}', true, 'system')
                """),
                {
                    "id": variant_id,
                    "product_id": variant.product_id.value,
                    "variant_name": variant.color_name,
                    "color_code": variant.color_code,
                    "color_name": variant.color_name,
                    "sku_suffix": variant.sku_suffix
                }
            )
            
            # Add stock records if provided
            for stock_record in variant.stock_records:
                stock_id = str(uuid.uuid4())
                self.db.execute(
                    text("""
                        INSERT INTO stock (id, product_id, variant_id, partner_id, quantity_available, 
                                         quantity_reserved, reorder_level, reorder_quantity,
                                         retail_price, wholesale_price, currency, last_updated)
                        VALUES (:id, :product_id, :variant_id, :partner_id, :quantity_available,
                                :quantity_reserved, :reorder_level, :reorder_quantity,
                                :retail_price, :wholesale_price, :currency, NOW())
                    """),
                    {
                        "id": stock_id,
                        "product_id": variant.product_id.value,
                        "variant_id": variant_id,
                        "partner_id": stock_record.get("partner_id"),
                        "quantity_available": stock_record.get("available_quantity", 0),
                        "quantity_reserved": stock_record.get("reserved_quantity", 0),
                        "reorder_level": stock_record.get("reorder_level", 10),
                        "reorder_quantity": stock_record.get("reorder_quantity", 50),
                        "retail_price": stock_record.get("retail_price", 0.0),
                        "wholesale_price": stock_record.get("wholesale_price", 0.0),
                        "currency": stock_record.get("currency", "INR")
                    }
                )
        
        self.db.commit()
        return variant
    
    def find_by_id(self, variant_id: str) -> Optional[ProductVariant]:
        """Find variant by ID with stock records"""
        result = self.db.execute(
            text("""
                SELECT v.id, v.product_id, v.variant_name, v.color_code, v.color_name, v.sku_suffix,
                       s.id as stock_id, s.partner_id, s.quantity_available, s.quantity_reserved,
                       s.retail_price, s.wholesale_price, s.currency
                FROM product_variants v
                LEFT JOIN stock s ON v.id = s.variant_id
                WHERE v.id = :variant_id
            """),
            {"variant_id": variant_id}
        )
        
        rows = result.fetchall()
        if not rows:
            return None
        
        first_row = rows[0]
        stock_records = []
        
        for row in rows:
            if row.stock_id:
                stock_records.append({
                    "partner_id": str(row.partner_id),
                    "available_quantity": row.quantity_available,
                    "reserved_quantity": row.quantity_reserved,
                    "retail_price": float(row.retail_price) if row.retail_price else 0.0,
                    "wholesale_price": float(row.wholesale_price) if row.wholesale_price else 0.0,
                    "currency": row.currency
                })
        
        return ProductVariant(
            variant_id=str(first_row.id),
            product_id=ProductId(str(first_row.product_id)),
            color_name=first_row.color_name,
            color_code=first_row.color_code,
            sku_suffix=first_row.sku_suffix,
            stock_records=stock_records
        )
    
    def find_by_product_id(self, product_id: ProductId) -> List[ProductVariant]:
        """Find all variants for a product with stock records"""
        result = self.db.execute(
            text("""
                SELECT v.id, v.product_id, v.variant_name, v.color_code, v.color_name, v.sku_suffix,
                       s.id as stock_id, s.partner_id, s.quantity_available, s.quantity_reserved,
                       s.retail_price, s.wholesale_price, s.currency
                FROM product_variants v
                LEFT JOIN stock s ON v.id = s.variant_id
                WHERE v.product_id = :product_id
                ORDER BY v.created_time, s.partner_id
            """),
            {"product_id": product_id.value}
        )
        
        variants_dict = {}
        for row in result:
            variant_id = str(row.id)
            if variant_id not in variants_dict:
                variants_dict[variant_id] = {
                    "variant_id": variant_id,
                    "product_id": ProductId(str(row.product_id)),
                    "color_name": row.color_name,
                    "color_code": row.color_code,
                    "sku_suffix": row.sku_suffix,
                    "stock_records": []
                }
            
            if row.stock_id:
                variants_dict[variant_id]["stock_records"].append({
                    "partner_id": str(row.partner_id),
                    "available_quantity": row.quantity_available,
                    "reserved_quantity": row.quantity_reserved,
                    "retail_price": float(row.retail_price) if row.retail_price else 0.0,
                    "wholesale_price": float(row.wholesale_price) if row.wholesale_price else 0.0,
                    "currency": row.currency
                })
        
        variants = []
        for variant_data in variants_dict.values():
            variants.append(ProductVariant(
                variant_id=variant_data["variant_id"],
                product_id=variant_data["product_id"],
                color_name=variant_data["color_name"],
                color_code=variant_data["color_code"],
                sku_suffix=variant_data["sku_suffix"],
                stock_records=variant_data["stock_records"]
            ))
        
        return variants
    
    def delete(self, variant_id: str) -> bool:
        """Delete variant and its stock records"""
        # Delete stock records first
        self.db.execute(
            text("DELETE FROM stock WHERE variant_id = :variant_id"),
            {"variant_id": variant_id}
        )
        
        # Delete variant
        result = self.db.execute(
            text("DELETE FROM product_variants WHERE id = :variant_id"),
            {"variant_id": variant_id}
        )
        
        self.db.commit()
        return result.rowcount > 0
    
    def add_stock_record(self, variant_id: str, stock_data: dict) -> str:
        """Add stock record to variant"""
        stock_id = str(uuid.uuid4())
        
        # Get product_id for the variant
        result = self.db.execute(
            text("SELECT product_id FROM product_variants WHERE id = :variant_id"),
            {"variant_id": variant_id}
        )
        row = result.fetchone()
        if not row:
            raise ValueError("Variant not found")
        
        self.db.execute(
            text("""
                INSERT INTO stock (id, product_id, variant_id, partner_id, quantity_available, 
                                 quantity_reserved, reorder_level, reorder_quantity,
                                 retail_price, wholesale_price, currency, last_updated)
                VALUES (:id, :product_id, :variant_id, :partner_id, :quantity_available,
                        :quantity_reserved, :reorder_level, :reorder_quantity,
                        :retail_price, :wholesale_price, :currency, NOW())
            """),
            {
                "id": stock_id,
                "product_id": str(row.product_id),
                "variant_id": variant_id,
                "partner_id": stock_data.get("partner_id"),
                "quantity_available": stock_data.get("available_quantity", 0),
                "quantity_reserved": stock_data.get("reserved_quantity", 0),
                "reorder_level": stock_data.get("reorder_level", 10),
                "reorder_quantity": stock_data.get("reorder_quantity", 50),
                "retail_price": stock_data.get("retail_price", 0.0),
                "wholesale_price": stock_data.get("wholesale_price", 0.0),
                "currency": stock_data.get("currency", "INR")
            }
        )
        
        self.db.commit()
        return stock_id
