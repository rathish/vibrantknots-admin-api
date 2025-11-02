from typing import List, Optional, Dict
from uuid import uuid4
from domain.ports import CategoryRepositoryPort
from domain.models import Category

class MemoryCategoryRepository(CategoryRepositoryPort):
    def __init__(self):
        self._categories: Dict[str, Category] = {}
    
    def create(self, category: Category) -> Category:
        category_id = str(uuid4())
        new_category = Category(id=category_id, name=category.name, description=category.description)
        self._categories[category_id] = new_category
        return new_category
    
    def get_by_id(self, category_id: str) -> Optional[Category]:
        return self._categories.get(category_id)
    
    def get_all(self) -> List[Category]:
        return list(self._categories.values())
    
    def update(self, category: Category) -> Category:
        self._categories[category.id] = category
        return category
    
    def delete(self, category_id: str) -> bool:
        if category_id in self._categories:
            del self._categories[category_id]
            return True
        return False
