from abc import ABC, abstractmethod
from typing import List, Optional
from .models import ImageUpload, ProcessingJob, ProductAnalysisJob, Category, Product

class StoragePort(ABC):
    @abstractmethod
    def store_image(self, image: ImageUpload) -> str:
        pass

class QueuePort(ABC):
    @abstractmethod
    def queue_job(self, job: ProcessingJob) -> None:
        pass

class ProductAnalysisQueuePort(ABC):
    @abstractmethod
    def queue_analysis(self, job: ProductAnalysisJob) -> None:
        pass

class CategoryRepositoryPort(ABC):
    @abstractmethod
    def create(self, category: Category) -> Category:
        pass
    
    @abstractmethod
    def get_by_id(self, category_id: str) -> Optional[Category]:
        pass
    
    @abstractmethod
    def get_all(self) -> List[Category]:
        pass
    
    @abstractmethod
    def update(self, category: Category) -> Category:
        pass
    
    @abstractmethod
    def delete(self, category_id: str) -> bool:
        pass

class ProductRepositoryPort(ABC):
    @abstractmethod
    def create(self, product: Product) -> Product:
        pass
    
    @abstractmethod
    def get_by_id(self, product_id: str) -> Optional[Product]:
        pass
    
    @abstractmethod
    def get_all(self) -> List[Product]:
        pass
    
    @abstractmethod
    def update(self, product: Product) -> Product:
        pass
    
    @abstractmethod
    def delete(self, product_id: str) -> bool:
        pass
