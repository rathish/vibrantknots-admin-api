from typing import List, Optional
from domain.models import Product, ProductStatus, ProductAnalysisJob
from domain.ports import ProductRepositoryPort, ProductAnalysisQueuePort

class ProductService:
    def __init__(self, repository: ProductRepositoryPort, analysis_queue: Optional[ProductAnalysisQueuePort] = None):
        self.repository = repository
        self.analysis_queue = analysis_queue
    
    def create_product(self, product: Product) -> Product:
        created_product = self.repository.create(product)
        
        # Queue for GenAI analysis if images exist
        if self.analysis_queue and created_product.image_urls:
            analysis_job = ProductAnalysisJob(
                product_id=created_product.id,
                sku_id=created_product.sku_id,
                image_urls=created_product.image_urls
            )
            self.analysis_queue.queue_analysis(analysis_job)
        
        return created_product
    
    def get_product(self, product_id: str) -> Optional[Product]:
        return self.repository.get_by_id(product_id)
    
    def get_all_products(self) -> List[dict]:
        return self.repository.get_all_products()
    
    def update_product(self, product: Product) -> Optional[Product]:
        existing = self.repository.get_by_id(product.id)
        if not existing:
            return None
        return self.repository.update(product)
    
    def delete_product(self, product_id: str) -> bool:
        return self.repository.delete(product_id)
