from domain.base.value_object import ValueObject
import uuid


class CategoryId(ValueObject):
    def __init__(self, value: str):
        if not value:
            raise ValueError("CategoryId cannot be empty")
        self.value = value
    
    @classmethod
    def generate(cls):
        return cls(str(uuid.uuid4()))


class CategoryName(ValueObject):
    def __init__(self, value: str):
        if not value or len(value.strip()) == 0:
            raise ValueError("Category name cannot be empty")
        if len(value) > 100:
            raise ValueError("Category name too long")
        self.value = value.strip()
