from abc import ABC
from typing import Any


class ValueObject(ABC):
    """Base class for value objects."""
    
    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__
    
    def __hash__(self):
        return hash(tuple(sorted(self.__dict__.items())))
    
    def __repr__(self):
        attrs = ', '.join(f'{k}={v}' for k, v in self.__dict__.items())
        return f'{self.__class__.__name__}({attrs})'
