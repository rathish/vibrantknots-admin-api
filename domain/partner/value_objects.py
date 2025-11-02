from domain.base.value_object import ValueObject
import uuid


class PartnerId(ValueObject):
    def __init__(self, value: str):
        if not value:
            raise ValueError("PartnerId cannot be empty")
        self.value = value
    
    @classmethod
    def generate(cls):
        return cls(str(uuid.uuid4()))


class PartnerCode(ValueObject):
    def __init__(self, value: str):
        if not value or len(value.strip()) == 0:
            raise ValueError("Partner code cannot be empty")
        if len(value) > 50:
            raise ValueError("Partner code too long")
        self.value = value.strip().upper()
