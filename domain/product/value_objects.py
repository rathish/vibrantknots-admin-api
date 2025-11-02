from domain.base.value_object import ValueObject
from typing import Optional
import uuid


class ProductId(ValueObject):
    def __init__(self, value: str):
        if not value:
            raise ValueError("ProductId cannot be empty")
        self.value = value
    
    @classmethod
    def generate(cls):
        return cls(str(uuid.uuid4()))


class Money(ValueObject):
    def __init__(self, amount: float, currency: str = "INR"):
        if amount < 0:
            raise ValueError("Amount cannot be negative")
        self.amount = amount
        self.currency = currency


class ProductTitle(ValueObject):
    def __init__(self, value: str):
        if not value or len(value.strip()) == 0:
            raise ValueError("Product title cannot be empty")
        if len(value) > 200:
            raise ValueError("Product title too long")
        self.value = value.strip()


class SKU(ValueObject):
    def __init__(self, value: str):
        if not value:
            raise ValueError("SKU cannot be empty")
        self.value = value.upper()
