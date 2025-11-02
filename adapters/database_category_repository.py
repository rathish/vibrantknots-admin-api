from typing import List, Optional
from sqlalchemy.orm import Session
from domain.category.repositories import CategoryRepository
from domain.category.entities import Category
from domain.category.value_objects import CategoryId, CategoryName
from .database.entities import CategoryEntity


class DatabaseCategoryRepository(CategoryRepository):
    def __init__(self, db: Session):
        self.db = db
    
    def save(self, category: Category) -> Category:
        entity = self.db.query(CategoryEntity).filter(CategoryEntity.id == category.id).first()
        if entity:
            # Update existing
            entity.name = category.name.value
            entity.description = category.description
        else:
            # Create new
            entity = CategoryEntity(
                id=category.id,
                name=category.name.value, 
                description=category.description
            )
            self.db.add(entity)
        
        self.db.commit()
        self.db.refresh(entity)
        return self._entity_to_domain(entity)
    
    def find_by_id(self, category_id: CategoryId) -> Optional[Category]:
        entity = self.db.query(CategoryEntity).filter(CategoryEntity.id == category_id.value).first()
        if not entity:
            return None
        return self._entity_to_domain(entity)
    
    def find_all(self) -> List[Category]:
        entities = self.db.query(CategoryEntity).all()
        return [self._entity_to_domain(e) for e in entities]
    
    def get_all(self) -> List[dict]:
        entities = self.db.query(CategoryEntity).all()
        return [{"id": str(e.id), "name": e.name, "description": e.description} for e in entities]
    
    def get_all_categories(self) -> List[dict]:
        return self.get_all()
    
    def delete(self, category_id: CategoryId) -> bool:
        entity = self.db.query(CategoryEntity).filter(CategoryEntity.id == category_id.value).first()
        if not entity:
            return False
        self.db.delete(entity)
        self.db.commit()
        return True
    
    def _entity_to_domain(self, entity: CategoryEntity) -> Category:
        return Category(
            category_id=CategoryId(str(entity.id)),
            name=CategoryName(entity.name),
            description=entity.description
        )

    def get_by_id(self, category_id: str) -> Optional[dict]:
        entity = self.db.query(CategoryEntity).filter(CategoryEntity.id == category_id).first()
        if not entity:
            return None
        return {"id": str(entity.id), "name": entity.name, "description": entity.description}
    
    def create(self, name: str, description: str = None) -> dict:
        entity = CategoryEntity(name=name, description=description)
        self.db.add(entity)
        self.db.commit()
        self.db.refresh(entity)
        return {"id": str(entity.id), "name": entity.name, "description": entity.description}
    
    def update(self, category_id: str, name: str = None, description: str = None) -> Optional[dict]:
        entity = self.db.query(CategoryEntity).filter(CategoryEntity.id == category_id).first()
        if not entity:
            return None
        if name:
            entity.name = name
        if description:
            entity.description = description
        self.db.commit()
        return {"id": str(entity.id), "name": entity.name, "description": entity.description}
