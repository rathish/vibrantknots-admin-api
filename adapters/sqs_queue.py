import boto3
import json
from domain.ports import QueuePort
from domain.models import ProcessingJob

class SQSQueueAdapter(QueuePort):
    def __init__(self, queue_url: str):
        self.sqs = boto3.client('sqs')
        self.queue_url = queue_url
    
    def queue_job(self, job: ProcessingJob) -> None:
        message = {
            'image_key': job.image_key,
            'filename': job.filename
        }
        self.sqs.send_message(
            QueueUrl=self.queue_url,
            MessageBody=json.dumps(message)
        )
