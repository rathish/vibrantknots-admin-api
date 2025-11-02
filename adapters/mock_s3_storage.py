import os
import uuid
from typing import Dict
from domain.models import ImageUpload
from domain.ports import StoragePort

class MockS3StorageAdapter(StoragePort):
    def __init__(self, bucket_name: str, region: str = "us-east-1"):
        self.bucket_name = bucket_name
        self.region = region
        self.base_path = "/tmp/mock_s3"
        os.makedirs(self.base_path, exist_ok=True)
    
    def store_image(self, image: ImageUpload) -> str:
        """Store image locally and return mock S3 key"""
        key = f"images/{uuid.uuid4()}.jpg"
        file_path = os.path.join(self.base_path, key.replace('/', '_'))
        
        # Save file locally
        with open(file_path, 'wb') as f:
            image.content.seek(0)
            f.write(image.content.read())
        
        return key
    
    def get_image_url(self, key: str) -> str:
        """Return mock S3 URL"""
        return f"https://{self.bucket_name}.s3.{self.region}.amazonaws.com/{key}"
    
    def store_product_images(self, images: Dict[str, ImageUpload]) -> Dict[str, str]:
        """Store multiple images and return mock URLs"""
        image_urls = {}
        for img_type, image in images.items():
            key = f"products/{img_type}/{uuid.uuid4()}.jpg"
            file_path = os.path.join(self.base_path, key.replace('/', '_'))
            
            # Save file locally
            with open(file_path, 'wb') as f:
                image.content.seek(0)
                f.write(image.content.read())
            
            image_urls[img_type] = f"https://{self.bucket_name}.s3.{self.region}.amazonaws.com/{key}"
        
        return image_urls
