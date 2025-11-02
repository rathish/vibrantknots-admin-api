from typing import List, Optional
from domain.models import Category
from domain.ports import CategoryRepositoryPort

class CategoryService:
    def __init__(self, repository: CategoryRepositoryPort):
        self.repository = repository
    
    def create_category(self, name: str, description: Optional[str] = None) -> Category:
        category = Category(id=None, name=name, description=description)
        return self.repository.create(category)
    
    def get_category(self, category_id: str) -> Optional[Category]:
        return self.repository.get_by_id(category_id)
    
    def get_all_categories(self) -> List[dict]:
        return self.repository.get_all_categories()
    
    def update_category(self, category_id: str, name: str, description: Optional[str] = None) -> Optional[Category]:
        existing = self.repository.get_by_id(category_id)
        if not existing:
            return None
        
        updated = Category(id=category_id, name=name, description=description)
        return self.repository.update(updated)
    
    def delete_category(self, category_id: str) -> bool:
        return self.repository.delete(category_id)
