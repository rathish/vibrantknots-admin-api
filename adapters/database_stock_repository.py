from typing import List, Optional
from sqlalchemy.orm import Session
from domain.stock.entities import StockRecord
from domain.product.value_objects import ProductId, Money
from domain.partner.value_objects import PartnerId
from adapters.database.entities import Base
from sqlalchemy import Column, String, Integer, Numeric, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
import uuid


class StockRecordEntity(Base):
    __tablename__ = "stock"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_id = Column(UUID(as_uuid=True), ForeignKey('products.id'), nullable=False)
    partner_id = Column(UUID(as_uuid=True), ForeignKey('partners.id'), nullable=False)
    partner_sku = Column(String(100))
    quantity_available = Column(Integer, default=0)
    quantity_reserved = Column(Integer, default=0)
    reorder_level = Column(Integer, default=10)
    wholesale_price = Column(Numeric(10, 2), default=0.00)
    retail_price = Column(Numeric(10, 2), default=0.00)
    currency = Column(String(3), default='INR')


class DatabaseStockRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def save(self, stock_record: StockRecord) -> StockRecord:
        entity = self.db.query(StockRecordEntity).filter(StockRecordEntity.id == stock_record.stock_id).first()
        if entity:
            # Update existing
            entity.quantity_available = stock_record.quantity_available
            entity.quantity_reserved = stock_record.quantity_reserved
            entity.reorder_level = stock_record.reorder_level
            entity.wholesale_price = stock_record.wholesale_price.amount
            entity.retail_price = stock_record.retail_price.amount
            entity.currency = stock_record.wholesale_price.currency
        else:
            # Create new
            entity = StockRecordEntity(
                id=stock_record.stock_id,
                product_id=stock_record.product_id.value,
                partner_id=stock_record.partner_id.value,
                partner_sku=stock_record.partner_sku,
                quantity_available=stock_record.quantity_available,
                quantity_reserved=stock_record.quantity_reserved,
                reorder_level=stock_record.reorder_level,
                wholesale_price=stock_record.wholesale_price.amount,
                retail_price=stock_record.retail_price.amount,
                currency=stock_record.wholesale_price.currency
            )
            self.db.add(entity)
        
        self.db.commit()
        self.db.refresh(entity)
        return self._entity_to_domain(entity)
    
    def find_by_product(self, product_id: ProductId) -> List[StockRecord]:
        entities = self.db.query(StockRecordEntity).filter(StockRecordEntity.product_id == product_id.value).all()
        return [self._entity_to_domain(e) for e in entities]
    
    def find_by_product_and_partner(self, product_id: ProductId, partner_id: PartnerId) -> Optional[StockRecord]:
        entity = self.db.query(StockRecordEntity).filter(
            StockRecordEntity.product_id == product_id.value,
            StockRecordEntity.partner_id == partner_id.value
        ).first()
        if not entity:
            return None
        return self._entity_to_domain(entity)
    
    def _entity_to_domain(self, entity: StockRecordEntity) -> StockRecord:
        return StockRecord(
            stock_id=str(entity.id),
            product_id=ProductId(str(entity.product_id)),
            partner_id=PartnerId(str(entity.partner_id)),
            partner_sku=entity.partner_sku,
            quantity_available=entity.quantity_available,
            quantity_reserved=entity.quantity_reserved,
            reorder_level=entity.reorder_level,
            wholesale_price=Money(float(entity.wholesale_price), entity.currency),
            retail_price=Money(float(entity.retail_price), entity.currency)
        )
