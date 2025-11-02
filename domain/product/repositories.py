from abc import ABC, abstractmethod
from typing import List, Optional
from domain.product.entities import Product, ProductVariant
from domain.product.value_objects import ProductId


class ProductRepository(ABC):
    @abstractmethod
    def save(self, product: Product) -> Product:
        pass
    
    @abstractmethod
    def find_by_id(self, product_id: ProductId) -> Optional[Product]:
        pass
    
    @abstractmethod
    def find_all(self) -> List[Product]:
        pass
    
    @abstractmethod
    def delete(self, product_id: ProductId) -> bool:
        pass


class VariantRepository(ABC):
    @abstractmethod
    def save(self, variant: ProductVariant) -> ProductVariant:
        pass
    
    @abstractmethod
    def find_by_id(self, variant_id: str) -> Optional[ProductVariant]:
        pass
    
    @abstractmethod
    def find_by_product_id(self, product_id: ProductId) -> List[ProductVariant]:
        pass
    
    @abstractmethod
    def delete(self, variant_id: str) -> bool:
        pass
