from sqlalchemy.orm import Session
from domain.product.entities import Product, ProductStatus
from domain.product.repositories import ProductRepository
from domain.product.value_objects import ProductId, ProductTitle, SKU
from adapters.database.entities import ProductEntity
import uuid
from datetime import datetime
from typing import Optional, List


class DatabaseProductRepository(ProductRepository):
    def __init__(self, db: Session):
        self.db = db
    
    def save(self, product: Product) -> Product:
        entity = self.db.query(ProductEntity).filter(ProductEntity.id == product.id).first()
        if entity:
            # Update existing
            self._domain_to_entity(product, entity)
            entity.updated_at = datetime.utcnow()
        else:
            # Create new
            entity = ProductEntity(
                id=product.id,
                title=product.title.value,
                description=product.description,
                sku_id=product.sku.value,
                material=product.material,
                pattern=product.pattern,
                color_primary=product.color_primary,
                colors=product.colors,
                width_estimate_cm=product.width_estimate_cm,
                scale=product.scale,
                special_features=product.special_features,
                image_urls=product.image_urls,
                created_by=product.created_by,
                category_id=product.category_id,
                status=product.status.value,
                enabled=product.enabled,
                discontinuation_reason=product.discontinuation_reason,
                discontinuation_date=product.discontinuation_date,
                created_at=product.created_at,
                updated_at=product.updated_at
            )
            self.db.add(entity)
        
        self.db.commit()
        self.db.refresh(entity)
        return self._entity_to_domain(entity)
    
    def find_by_id(self, product_id: ProductId) -> Optional[Product]:
        entity = self.db.query(ProductEntity).filter(ProductEntity.id == product_id.value).first()
        if entity:
            return self._entity_to_domain(entity)
        return None
    
    def find_all(self) -> List[Product]:
        entities = self.db.query(ProductEntity).all()
        return [self._entity_to_domain(entity) for entity in entities]
    
    def get_all(self) -> List[dict]:
        entities = self.db.query(ProductEntity).all()
        return [{"id": str(e.id), "title": e.title, "description": e.description,
                "status": e.status, "category_id": str(e.category_id) if e.category_id else None,
                "created_at": e.created_at, "updated_at": e.updated_at} for e in entities]
    
    def get_all_products(self) -> List[dict]:
        return self.get_all()
    
    def delete(self, product_id: ProductId) -> bool:
        try:
            # Delete related records first to avoid foreign key constraints
            from sqlalchemy import text
            self.db.execute(text("DELETE FROM price_tables WHERE product_id = :product_id"), {"product_id": product_id.value})
            self.db.execute(text("DELETE FROM stock WHERE product_id = :product_id"), {"product_id": product_id.value})
            self.db.execute(text("DELETE FROM product_variants WHERE product_id = :product_id"), {"product_id": product_id.value})
            
            # Now delete the product
            entity = self.db.query(ProductEntity).filter(ProductEntity.id == product_id.value).first()
            if entity:
                self.db.delete(entity)
                self.db.commit()
                return True
            return False
        except Exception as e:
            self.db.rollback()
            raise e
    
    def _entity_to_domain(self, entity: ProductEntity) -> Product:
        # Handle status conversion - convert lowercase to uppercase
        status_value = entity.status
        if isinstance(status_value, str):
            status_value = status_value.upper()
        else:
            status_value = "DRAFT"
        
        return Product(
            product_id=ProductId(str(entity.id)),
            title=ProductTitle(entity.title),
            sku=SKU(entity.sku_id or "DEFAULT"),
            category_id=str(entity.category_id) if entity.category_id else None,
            description=entity.description,
            material=entity.material,
            pattern=entity.pattern,
            color_primary=entity.color_primary,
            colors=entity.colors or [],
            width_estimate_cm=entity.width_estimate_cm,
            scale=entity.scale,
            special_features=entity.special_features or [],
            image_urls=entity.image_urls or {},
            created_by=entity.created_by,
            status=ProductStatus(status_value),
            enabled=entity.enabled,
            discontinuation_reason=entity.discontinuation_reason,
            discontinuation_date=entity.discontinuation_date,
            created_at=entity.created_at,
            updated_at=entity.updated_at
        )
    
    def _domain_to_entity(self, product: Product, entity: ProductEntity):
        entity.title = product.title.value
        entity.description = product.description
        entity.sku_id = product.sku.value
        entity.material = product.material
        entity.pattern = product.pattern
        entity.color_primary = product.color_primary
        entity.colors = product.colors
        entity.width_estimate_cm = product.width_estimate_cm
        entity.scale = product.scale
        entity.special_features = product.special_features
        entity.image_urls = product.image_urls
        entity.created_by = product.created_by
        entity.category_id = product.category_id
        entity.status = product.status.value
        entity.enabled = product.enabled
        entity.discontinuation_reason = product.discontinuation_reason
        entity.discontinuation_date = product.discontinuation_date

    def get_by_id(self, product_id: str) -> Optional[dict]:
        entity = self.db.query(ProductEntity).filter(ProductEntity.id == product_id).first()
        if not entity:
            return None
        return {"id": str(entity.id), "title": entity.title, "description": entity.description,
                "status": entity.status, "category_id": str(entity.category_id) if entity.category_id else None,
                "created_at": entity.created_at, "updated_at": entity.updated_at}
    
    def create(self, title: str, description: str = None, category_id: str = None, status: str = "draft") -> dict:
        entity = ProductEntity(title=title, description=description, category_id=category_id, status=status)
        self.db.add(entity)
        self.db.commit()
        self.db.refresh(entity)
        return {"id": str(entity.id), "title": entity.title, "description": entity.description,
                "status": entity.status, "category_id": str(entity.category_id) if entity.category_id else None,
                "created_at": entity.created_at, "updated_at": entity.updated_at}
    
    def update(self, product_id: str, **kwargs) -> Optional[dict]:
        entity = self.db.query(ProductEntity).filter(ProductEntity.id == product_id).first()
        if not entity:
            return None
        for key, value in kwargs.items():
            if hasattr(entity, key):
                setattr(entity, key, value)
        self.db.commit()
        return {"id": str(entity.id), "title": entity.title, "description": entity.description,
                "status": entity.status, "category_id": str(entity.category_id) if entity.category_id else None,
                "created_at": entity.created_at, "updated_at": entity.updated_at}
    
    def delete_variant(self, variant_id: str) -> bool:
        return True
    
    def _to_domain(self, entity) -> dict:
        return {"id": str(entity.id), "title": entity.title}
