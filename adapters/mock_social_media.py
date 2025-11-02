import random
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, List
from domain.models import Campaign, CampaignMetric

class MockSocialMediaAdapter:
    def __init__(self, platform: str):
        self.platform = platform
        self.campaigns = {}
    
    def create_campaign(self, campaign: Campaign) -> str:
        """Create campaign on platform and return platform campaign ID"""
        platform_id = f"{self.platform}_{random.randint(1000, 9999)}"
        self.campaigns[platform_id] = campaign
        print(f"Mock {self.platform}: Created campaign {campaign.name} with ID {platform_id}")
        return platform_id
    
    def update_campaign_status(self, platform_campaign_id: str, status: str) -> bool:
        """Update campaign status (active, paused, completed)"""
        if platform_campaign_id in self.campaigns:
            print(f"Mock {self.platform}: Updated campaign {platform_campaign_id} status to {status}")
            return True
        return False
    
    def collect_metrics(self, platform_campaign_id: str, date: datetime) -> CampaignMetric:
        """Collect metrics for a specific date"""
        # Generate mock metrics
        impressions = random.randint(1000, 50000)
        clicks = random.randint(50, impressions // 20)
        conversions = random.randint(1, clicks // 10)
        spend = Decimal(str(random.uniform(10, 500)))
        reach = random.randint(800, impressions)
        engagement = random.randint(20, clicks * 2)
        
        ctr = Decimal(str(clicks / impressions * 100)) if impressions > 0 else Decimal('0')
        cpc = spend / clicks if clicks > 0 else Decimal('0')
        cpm = spend / impressions * 1000 if impressions > 0 else Decimal('0')
        
        return CampaignMetric(
            id=None,
            campaign_id="",  # Will be set by caller
            metric_date=date,
            impressions=impressions,
            clicks=clicks,
            conversions=conversions,
            spend=spend,
            reach=reach,
            engagement=engagement,
            ctr=ctr,
            cpc=cpc,
            cpm=cpm,
            additional_metrics={
                "video_views": random.randint(0, impressions // 2),
                "shares": random.randint(0, engagement // 5),
                "saves": random.randint(0, engagement // 3)
            }
        )

class MockInstagramAdapter(MockSocialMediaAdapter):
    def __init__(self):
        super().__init__("instagram")

class MockFacebookAdapter(MockSocialMediaAdapter):
    def __init__(self):
        super().__init__("facebook")

class MockTwitterAdapter(MockSocialMediaAdapter):
    def __init__(self):
        super().__init__("twitter")

class SocialMediaManager:
    def __init__(self):
        self.adapters = {
            "instagram": MockInstagramAdapter(),
            "facebook": MockFacebookAdapter(),
            "twitter": MockTwitterAdapter()
        }
    
    def get_adapter(self, platform: str):
        return self.adapters.get(platform.lower())
    
    def create_campaign(self, campaign: Campaign) -> str:
        adapter = self.get_adapter(campaign.platform)
        if adapter:
            return adapter.create_campaign(campaign)
        raise ValueError(f"Unsupported platform: {campaign.platform}")
    
    def collect_metrics(self, platform: str, platform_campaign_id: str, campaign_id: str, date: datetime) -> CampaignMetric:
        adapter = self.get_adapter(platform)
        if adapter:
            metric = adapter.collect_metrics(platform_campaign_id, date)
            metric.campaign_id = campaign_id
            return metric
        raise ValueError(f"Unsupported platform: {platform}")
