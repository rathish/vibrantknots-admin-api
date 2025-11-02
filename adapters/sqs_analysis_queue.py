import boto3
import json
from domain.ports import ProductAnalysisQueuePort
from domain.models import ProductAnalysisJob

class SQSAnalysisQueueAdapter(ProductAnalysisQueuePort):
    def __init__(self, queue_url: str):
        self.sqs = boto3.client('sqs')
        self.queue_url = queue_url
    
    def queue_analysis(self, job: ProductAnalysisJob) -> None:
        message = {
            'product_id': job.product_id,
            'sku_id': job.sku_id,
            'image_urls': job.image_urls,
            'analysis_type': job.analysis_type,
            'timestamp': str(job.__dict__.get('timestamp', 'now'))
        }
        
        self.sqs.send_message(
            QueueUrl=self.queue_url,
            MessageBody=json.dumps(message),
            MessageAttributes={
                'analysis_type': {
                    'StringValue': job.analysis_type,
                    'DataType': 'String'
                }
            }
        )
