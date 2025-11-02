from abc import ABC
from typing import Any


class Entity(ABC):
    """Base class for domain entities."""
    
    def __init__(self, id: Any = None):
        self._id = id
    
    @property
    def id(self) -> Any:
        return self._id
    
    def __eq__(self, other):
        if not isinstance(other, Entity):
            return False
        return self._id == other._id
    
    def __hash__(self):
        return hash(self._id)


class AggregateRoot(Entity):
    """Base class for domain aggregates."""
    
    def __init__(self, id: Any = None):
        super().__init__(id)
        self._domain_events = []
    
    def add_domain_event(self, event):
        self._domain_events.append(event)
    
    def clear_domain_events(self):
        self._domain_events.clear()
    
    @property
    def domain_events(self):
        return self._domain_events.copy()
