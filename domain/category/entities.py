from domain.base.entity import AggregateRoot
from domain.category.value_objects import CategoryId, CategoryName
from typing import Optional


class Category(AggregateRoot):
    def __init__(
        self,
        category_id: CategoryId,
        name: CategoryName,
        description: Optional[str] = None
    ):
        super().__init__(category_id.value)
        self.category_id = category_id
        self.name = name
        self.description = description
    
    def update_name(self, new_name: CategoryName):
        self.name = new_name
    
    def update_description(self, description: str):
        self.description = description
