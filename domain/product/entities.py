from domain.base.entity import AggregateRoot, Entity
from domain.product.value_objects import ProductId, ProductTitle, SKU, Money
from typing import Optional, List, Dict
from datetime import datetime
from enum import Enum


class ProductStatus(Enum):
    DRAFT = "DRAFT"
    PUBLISHED = "PUBLISHED"


class ProductVariant(Entity):
    def __init__(
        self,
        variant_id: str,
        product_id: ProductId,
        color_name: str,
        color_code: str,
        sku_suffix: str,
        stock_records: Optional[List[Dict]] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None
    ):
        super().__init__(variant_id)
        self.variant_id = variant_id
        self.product_id = product_id
        self.color_name = color_name
        self.color_code = color_code
        self.sku_suffix = sku_suffix
        self.stock_records = stock_records or []
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()
    
    def add_stock_record(self, partner_id: str, available_quantity: int, retail_price: float, wholesale_price: float, currency: str = "INR"):
        """Add a stock record for a specific partner"""
        stock_record = {
            "partner_id": partner_id,
            "available_quantity": available_quantity,
            "retail_price": retail_price,
            "wholesale_price": wholesale_price,
            "currency": currency,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        self.stock_records.append(stock_record)
        self.updated_at = datetime.utcnow()
    
    def update_stock_record(self, partner_id: str, **kwargs):
        """Update stock record for a specific partner"""
        for record in self.stock_records:
            if record["partner_id"] == partner_id:
                record.update(kwargs)
                record["updated_at"] = datetime.utcnow()
                self.updated_at = datetime.utcnow()
                break
    
    def get_stock_for_partner(self, partner_id: str) -> Optional[Dict]:
        """Get stock record for a specific partner"""
        for record in self.stock_records:
            if record["partner_id"] == partner_id:
                return record
        return None


class Product(AggregateRoot):
    def __init__(
        self,
        product_id: ProductId,
        title: ProductTitle,
        sku: SKU,
        category_id: Optional[str] = None,
        description: Optional[str] = None,
        material: Optional[str] = None,
        pattern: Optional[str] = None,
        color_primary: Optional[str] = None,
        colors: Optional[List[str]] = None,
        width_estimate_cm: Optional[float] = None,
        scale: Optional[str] = None,
        special_features: Optional[List[str]] = None,
        image_urls: Optional[Dict[str, str]] = None,
        variants: Optional[List[ProductVariant]] = None,
        created_by: str = "system",
        status: ProductStatus = ProductStatus.DRAFT,
        enabled: bool = True,
        discontinuation_reason: Optional[str] = None,
        discontinuation_date: Optional[datetime] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None
    ):
        super().__init__(product_id.value)
        self.product_id = product_id
        self.title = title
        self.sku = sku
        self.category_id = category_id
        self.description = description
        self.material = material
        self.pattern = pattern
        self.color_primary = color_primary
        self.colors = colors or []
        self.width_estimate_cm = width_estimate_cm
        self.scale = scale
        self.special_features = special_features or []
        self.image_urls = image_urls or {}
        self.variants = variants or []
        self.created_by = created_by
        self.status = status
        self.enabled = enabled
        self.discontinuation_reason = discontinuation_reason
        self.discontinuation_date = discontinuation_date
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()
    
    def add_variant(self, variant: ProductVariant):
        """Add a new variant to the product"""
        self.variants.append(variant)
        self.updated_at = datetime.utcnow()
    
    def remove_variant(self, variant_id: str):
        """Remove a variant from the product"""
        self.variants = [v for v in self.variants if v.variant_id != variant_id]
        self.updated_at = datetime.utcnow()
    
    def get_variant(self, variant_id: str) -> Optional[ProductVariant]:
        """Get a specific variant by ID"""
        for variant in self.variants:
            if variant.variant_id == variant_id:
                return variant
        return None
    
    def get_total_stock_for_partner(self, partner_id: str) -> int:
        """Get total available stock across all variants for a partner"""
        total = 0
        for variant in self.variants:
            stock_record = variant.get_stock_for_partner(partner_id)
            if stock_record:
                total += stock_record.get("available_quantity", 0)
        return total
    
    def update_title(self, new_title: ProductTitle):
        self.title = new_title
        self.updated_at = datetime.utcnow()
    
    def publish(self):
        if self.status == ProductStatus.DRAFT:
            self.status = ProductStatus.PUBLISHED
            self.updated_at = datetime.utcnow()
    
    def disable(self):
        self.enabled = False
        self.updated_at = datetime.utcnow()
    
    def discontinue(self, reason: str):
        self.discontinuation_reason = reason
        self.discontinuation_date = datetime.utcnow()
        self.enabled = False
        self.updated_at = datetime.utcnow()
