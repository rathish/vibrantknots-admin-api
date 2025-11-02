from domain.base.entity import AggregateRoot
from domain.product.value_objects import ProductId, Money
from domain.partner.value_objects import PartnerId
from typing import Optional
import uuid


class StockRecord(AggregateRoot):
    def __init__(
        self,
        stock_id: str,
        product_id: ProductId,
        partner_id: PartnerId,
        partner_sku: str,
        quantity_available: int = 0,
        quantity_reserved: int = 0,
        reorder_level: int = 10,
        wholesale_price: Money = None,
        retail_price: Money = None
    ):
        super().__init__(stock_id)
        self.stock_id = stock_id
        self.product_id = product_id
        self.partner_id = partner_id
        self.partner_sku = partner_sku
        self.quantity_available = quantity_available
        self.quantity_reserved = quantity_reserved
        self.reorder_level = reorder_level
        self.wholesale_price = wholesale_price or Money(0.0)
        self.retail_price = retail_price or Money(0.0)
    
    def update_stock(self, available: int, reserved: int = None):
        self.quantity_available = available
        if reserved is not None:
            self.quantity_reserved = reserved
    
    def update_pricing(self, wholesale: Money, retail: Money):
        self.wholesale_price = wholesale
        self.retail_price = retail
    
    @property
    def total_stock(self):
        return self.quantity_available + self.quantity_reserved
