from abc import ABC, abstractmethod
from typing import List, Optional
from domain.category.entities import Category
from domain.category.value_objects import CategoryId


class CategoryRepository(ABC):
    @abstractmethod
    def save(self, category: Category) -> Category:
        pass
    
    @abstractmethod
    def find_by_id(self, category_id: CategoryId) -> Optional[Category]:
        pass
    
    @abstractmethod
    def find_all(self) -> List[Category]:
        pass
    
    @abstractmethod
    def delete(self, category_id: CategoryId) -> bool:
        pass
