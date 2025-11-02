import boto3
from uuid import uuid4
from typing import Dict
from domain.ports import StoragePort
from domain.models import ImageUpload

class S3StorageAdapter(StoragePort):
    def __init__(self, bucket_name: str, region: str = "us-east-1"):
        self.s3 = boto3.client('s3')
        self.bucket_name = bucket_name
        self.region = region
    
    def store_image(self, image: ImageUpload) -> str:
        key = f"images/{uuid4()}-{image.filename}"
        self.s3.upload_fileobj(
            image.content,
            self.bucket_name,
            key,
            ExtraArgs={'ContentType': image.content_type}
        )
        return key
    
    def store_product_images(self, images: Dict[str, ImageUpload]) -> Dict[str, str]:
        """Store multiple images and return URLs"""
        image_urls = {}
        
        for image_type, image in images.items():
            key = f"products/{image_type}/{uuid4()}-{image.filename}"
            
            self.s3.upload_fileobj(
                image.content,
                self.bucket_name,
                key,
                ExtraArgs={'ContentType': image.content_type}
            )
            
            # Generate public URL
            url = f"https://{self.bucket_name}.s3.{self.region}.amazonaws.com/{key}"
            image_urls[image_type] = url
        
        return image_urls
    
    def get_presigned_url(self, key: str, expiration: int = 3600) -> str:
        """Generate presigned URL for private access"""
        return self.s3.generate_presigned_url(
            'get_object',
            Params={'Bucket': self.bucket_name, 'Key': key},
            ExpiresIn=expiration
        )
