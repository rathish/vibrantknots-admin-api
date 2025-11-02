from dataclasses import dataclass
from typing import BinaryIO, Optional, List, Dict
from datetime import datetime
from enum import Enum
from decimal import Decimal

@dataclass
class ImageUpload:
    filename: str
    content: BinaryIO
    content_type: str

@dataclass
class ProcessingJob:
    image_key: str
    filename: str

@dataclass
class ProductAnalysisJob:
    product_id: str
    sku_id: str
    image_urls: Dict[str, str]
    analysis_type: str = "genai_analysis"

@dataclass
class RawImageAnalysisJob:
    raw_image_key: str
    filename: str
    analysis_type: str = "market_analysis"

@dataclass
class Category:
    id: Optional[str]
    name: str
    description: Optional[str] = None

class ProductStatus(Enum):
    DRAFT = "draft"
    PENDING_REVIEW = "pending_review"
    PUBLISHED = "published"
    DISCONTINUED = "discontinued"

@dataclass
class PriceTable:
    id: Optional[str]
    product_id: str
    wholesale_price: Decimal
    retail_price: Decimal
    currency: str
    version: int
    created_by: str
    created_time: datetime
    modified_by: Optional[str] = None
    modified_time: Optional[datetime] = None

@dataclass
class Recommendation:
    id: Optional[str]
    raw_image_key: str
    analysis_type: str
    recommended_products: List[Dict]
    market_insights: Dict
    sku_properties: Dict
    confidence_score: Optional[Decimal]
    version: int
    expiry_date: Optional[datetime]
    is_considered: bool
    consideration_reason: Optional[str]
    created_by: str
    created_time: Optional[datetime] = None
    updated_time: Optional[datetime] = None

@dataclass
class Campaign:
    id: Optional[str]
    name: str
    platform: str
    campaign_type: str
    target_audience: Dict
    budget: Decimal
    currency: str
    start_date: datetime
    end_date: datetime
    status: str
    platform_campaign_id: Optional[str]
    creative_assets: Dict
    created_by: str
    created_time: Optional[datetime] = None
    updated_time: Optional[datetime] = None

@dataclass
class CampaignMetric:
    id: Optional[str]
    campaign_id: str
    metric_date: datetime
    impressions: int
    clicks: int
    conversions: int
    spend: Decimal
    reach: int
    engagement: int
    ctr: Decimal
    cpc: Decimal
    cpm: Decimal
    additional_metrics: Dict
    collected_at: Optional[datetime] = None

@dataclass
class Stock:
    id: Optional[str]
    product_id: str
    current_stock: int
    reserved_stock: int
    available_stock: int
    reorder_level: int
    max_stock_level: int
    unit_of_measure: str
    warehouse_location: Optional[str]
    batch_number: Optional[str]
    expiry_date: Optional[datetime]
    last_updated: Optional[datetime]
    updated_by: str

@dataclass
class ProductVariant:
    id: Optional[str]
    product_id: str
    variant_name: str
    color_code: str
    color_name: str
    range_details: Dict
    sku_suffix: str
    additional_images: Dict[str, str]
    is_active: bool
    created_by: str
    created_time: Optional[datetime] = None
    updated_time: Optional[datetime] = None

@dataclass
class Product:
    id: Optional[str]
    sku_id: str
    title: str
    description: Optional[str]
    material: str
    pattern: str
    color_primary: str
    colors: List[Dict[str, str]]
    width_estimate_cm: Optional[int]
    scale: str
    special_features: List[str]
    image_urls: Dict[str, str]
    created_by: str
    category_id: Optional[str]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    status: ProductStatus
    enabled: bool = True
    discontinuation_reason: Optional[str] = None
    discontinuation_date: Optional[datetime] = None
    status_notes: Optional[str] = None
    price_table: Optional[PriceTable] = None
    stock: Optional[Stock] = None
    variants: List[ProductVariant] = None
