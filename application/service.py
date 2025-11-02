from domain.models import ImageUpload, ProcessingJob
from domain.ports import StoragePort, QueuePort

class Service:
    """Base service class for compatibility"""
    pass

class ImageProcessingService:
    def __init__(self, storage: StoragePort, queue: QueuePort):
        self.storage = storage
        self.queue = queue
    
    def upload_and_queue(self, image: ImageUpload) -> str:
        image_key = self.storage.store_image(image)
        job = ProcessingJob(image_key=image_key, filename=image.filename)
        self.queue.queue_job(job)
        return image_key
