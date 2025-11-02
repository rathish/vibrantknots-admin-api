import os
import uuid
from domain.models import ImageUpload

class MockRawImageStorageAdapter:
    def __init__(self, bucket_name: str = "test", region: str = "us-east-1"):
        self.bucket_name = bucket_name
        self.region = region
        self.base_path = "/tmp/mock_raw_images"
        os.makedirs(self.base_path, exist_ok=True)
    
    def store_raw_image(self, image: ImageUpload) -> str:
        """Store raw image in unprocessed bucket"""
        key = f"raw/{uuid.uuid4()}.jpg"
        file_path = os.path.join(self.base_path, key.replace('/', '_'))
        
        # Save file locally
        with open(file_path, 'wb') as f:
            image.content.seek(0)
            f.write(image.content.read())
        
        return key
    
    def get_raw_image_url(self, key: str) -> str:
        """Return mock S3 URL for raw image"""
        return f"https://{self.bucket_name}.s3.{self.region}.amazonaws.com/{key}"

class MockRawStorageAdapter(MockRawImageStorageAdapter):
    """Alias for compatibility"""
    pass
