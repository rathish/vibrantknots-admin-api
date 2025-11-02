import json
from domain.models import ProcessingJob, ProductAnalysisJob
from domain.ports import QueuePort, ProductAnalysisQueuePort

class MockSQSQueueAdapter(QueuePort):
    def __init__(self, queue_url: str):
        self.queue_url = queue_url
        self.messages = []
    
    def queue_job(self, job: ProcessingJob):
        """Mock message sending - just log it"""
        message = {
            "image_key": job.image_key,
            "filename": job.filename
        }
        self.messages.append(message)
        print(f"Mock SQS: Queued processing job for {job.filename}")

class MockSQSAnalysisQueueAdapter(ProductAnalysisQueuePort):
    def __init__(self, queue_url: str):
        self.queue_url = queue_url
        self.messages = []
    
    def queue_analysis(self, job: ProductAnalysisJob):
        """Mock analysis queue - just log it"""
        message = {
            "product_id": job.product_id,
            "sku_id": job.sku_id,
            "image_urls": job.image_urls,
            "analysis_type": job.analysis_type
        }
        self.messages.append(message)
        print(f"Mock SQS: Queued analysis job for product {job.product_id}")
