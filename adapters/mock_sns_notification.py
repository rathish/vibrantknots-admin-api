import json
from domain.models import RawImageAnalysisJob

class MockSNSNotificationAdapter:
    def __init__(self, topic_arn: str):
        self.topic_arn = topic_arn
        self.notifications = []
    
    def send_notification(self, job: RawImageAnalysisJob):
        """Mock SNS notification - just log it"""
        message = {
            "raw_image_key": job.raw_image_key,
            "filename": job.filename,
            "analysis_type": job.analysis_type,
            "topic_arn": self.topic_arn
        }
        self.notifications.append(message)
        print(f"Mock SNS: Sent notification for raw image analysis {job.raw_image_key}")
        return {"MessageId": f"mock-{len(self.notifications)}"}
