from sqlalchemy import Column, String, Text, Integer, DateTime, Enum as SQLEnum, ForeignKey, Numeric, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from domain.models import ProductStatus
import uuid

Base = declarative_base()

class CategoryEntity(Base):
    __tablename__ = "categories"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    products = relationship("ProductEntity", back_populates="category")

class PriceTableEntity(Base):
    __tablename__ = "price_tables"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id"), nullable=False, unique=True)
    wholesale_price = Column(Numeric(10, 2), nullable=False)
    retail_price = Column(Numeric(10, 2), nullable=False)
    currency = Column(String(3), nullable=False, default='INR')
    version = Column(Integer, nullable=False, default=1)
    created_by = Column(String(255), nullable=False)
    created_time = Column(DateTime(timezone=True), server_default=func.now())
    modified_by = Column(String(255), nullable=True)
    modified_time = Column(DateTime(timezone=True), onupdate=func.now())
    
    product = relationship("ProductEntity", back_populates="price_table")

class RecommendationEntity(Base):
    __tablename__ = "recommendations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    raw_image_key = Column(String(500), nullable=False)
    analysis_type = Column(String(50), nullable=False, default='market_analysis')
    recommended_products = Column(JSONB, nullable=False, default=[])
    market_insights = Column(JSONB, nullable=False, default={})
    sku_properties = Column(JSONB, nullable=False, default={})
    confidence_score = Column(Numeric(3, 2), nullable=True)
    version = Column(Integer, nullable=False, default=1)
    expiry_date = Column(DateTime(timezone=True), nullable=True)
    is_considered = Column(Boolean, nullable=False, default=False)
    consideration_reason = Column(Text, nullable=True)
    created_by = Column(String(255), nullable=False, default='agent')
    created_time = Column(DateTime(timezone=True), server_default=func.now())
    updated_time = Column(DateTime(timezone=True), onupdate=func.now())

class CampaignEntity(Base):
    __tablename__ = "campaigns"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    platform = Column(String(50), nullable=False)  # instagram, facebook, twitter, etc
    campaign_type = Column(String(50), nullable=False)  # awareness, conversion, engagement
    target_audience = Column(JSONB, nullable=False, default={})
    budget = Column(Numeric(10, 2), nullable=False)
    currency = Column(String(3), nullable=False, default='USD')
    start_date = Column(DateTime(timezone=True), nullable=False)
    end_date = Column(DateTime(timezone=True), nullable=False)
    status = Column(String(20), nullable=False, default='draft')  # draft, active, paused, completed
    platform_campaign_id = Column(String(255), nullable=True)  # External platform ID
    creative_assets = Column(JSONB, nullable=False, default={})
    created_by = Column(String(255), nullable=False)
    created_time = Column(DateTime(timezone=True), server_default=func.now())
    updated_time = Column(DateTime(timezone=True), onupdate=func.now())
    
    metrics = relationship("CampaignMetricEntity", back_populates="campaign")

class CampaignMetricEntity(Base):
    __tablename__ = "campaign_metrics"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    campaign_id = Column(UUID(as_uuid=True), ForeignKey("campaigns.id"), nullable=False)
    metric_date = Column(DateTime(timezone=True), nullable=False)
    impressions = Column(Integer, nullable=False, default=0)
    clicks = Column(Integer, nullable=False, default=0)
    conversions = Column(Integer, nullable=False, default=0)
    spend = Column(Numeric(10, 2), nullable=False, default=0)
    reach = Column(Integer, nullable=False, default=0)
    engagement = Column(Integer, nullable=False, default=0)
    ctr = Column(Numeric(5, 4), nullable=False, default=0)  # Click-through rate
    cpc = Column(Numeric(10, 2), nullable=False, default=0)  # Cost per click
    cpm = Column(Numeric(10, 2), nullable=False, default=0)  # Cost per mille
    additional_metrics = Column(JSONB, nullable=False, default={})
    collected_at = Column(DateTime(timezone=True), server_default=func.now())
    
    campaign = relationship("CampaignEntity", back_populates="metrics")

class StockEntity(Base):
    __tablename__ = "stocks"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id"), nullable=False, unique=True)
    current_stock = Column(Integer, nullable=False, default=0)
    reserved_stock = Column(Integer, nullable=False, default=0)
    available_stock = Column(Integer, nullable=False, default=0)
    reorder_level = Column(Integer, nullable=False, default=10)
    max_stock_level = Column(Integer, nullable=False, default=1000)
    unit_of_measure = Column(String(20), nullable=False, default='pieces')
    warehouse_location = Column(String(100), nullable=True)
    batch_number = Column(String(50), nullable=True)
    expiry_date = Column(DateTime(timezone=True), nullable=True)
    last_updated = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    updated_by = Column(String(255), nullable=False)
    
    product = relationship("ProductEntity", back_populates="stock")

class ProductVariantEntity(Base):
    __tablename__ = "product_variants"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id"), nullable=False)
    variant_name = Column(String(255), nullable=False)
    color_code = Column(String(7), nullable=False)
    color_name = Column(String(100), nullable=False)
    range_details = Column(JSONB, nullable=False, default={})
    sku_suffix = Column(String(50), nullable=False)
    additional_images = Column(JSONB, nullable=False, default={})
    is_active = Column(Boolean, nullable=False, default=True)
    created_by = Column(String(255), nullable=False)
    created_time = Column(DateTime(timezone=True), server_default=func.now())
    updated_time = Column(DateTime(timezone=True), onupdate=func.now())
    
    product = relationship("ProductEntity", back_populates="variants")

class ProductEntity(Base):
    __tablename__ = "products"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    sku_id = Column(String(255), nullable=False, unique=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    material = Column(String(100), nullable=False)
    pattern = Column(String(100), nullable=False)
    color_primary = Column(String(7), nullable=False)
    colors = Column(JSONB, nullable=False)
    width_estimate_cm = Column(Integer, nullable=True)
    scale = Column(String(50), nullable=False)
    special_features = Column(ARRAY(String), nullable=False, default=[])
    image_urls = Column(JSONB, nullable=False, default={})
    created_by = Column(String(255), nullable=False)
    category_id = Column(UUID(as_uuid=True), ForeignKey("categories.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    status = Column(SQLEnum(ProductStatus), nullable=False, default=ProductStatus.DRAFT)
    enabled = Column(Boolean, nullable=False, default=True)
    discontinuation_reason = Column(Text, nullable=True)
    discontinuation_date = Column(DateTime(timezone=True), nullable=True)
    status_notes = Column(Text, nullable=True)
    
    category = relationship("CategoryEntity", back_populates="products")
    price_table = relationship("PriceTableEntity", back_populates="product", uselist=False)
    stock = relationship("StockEntity", back_populates="product", uselist=False)
    variants = relationship("ProductVariantEntity", back_populates="product")
