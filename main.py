import os
from typing import Optional, List, Dict
from fastapi import FastAPI, UploadFile, HTTPException, Depends, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session
from decimal import Decimal
from datetime import datetime
from strawberry.fastapi import GraphQLRouter
from domain.models import ImageUpload, Product, ProductStatus, ProductVariant
from application.service import ImageProcessingService
from application.category_service import CategoryService
from application.product_service import ProductService
from adapters.s3_storage import S3StorageAdapter
from adapters.sqs_queue import SQSQueueAdapter
from adapters.database_category_repository import DatabaseCategoryRepository
from adapters.database_product_repository import DatabaseProductRepository
from adapters.database.config import get_db
from gql.schema import schema

app = FastAPI()

# Add CORS middleware with explicit configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# Tables are created by Docker setup


# Configuration
BUCKET_NAME = os.getenv('S3_BUCKET_NAME', 'your-bucket-name')
RAW_BUCKET_NAME = os.getenv('S3_RAW_BUCKET_NAME', 'your-raw-bucket-name')
QUEUE_URL = os.getenv('SQS_QUEUE_URL', 'your-queue-url')
ANALYSIS_QUEUE_URL = os.getenv('SQS_ANALYSIS_QUEUE_URL', 'your-analysis-queue-url')
SNS_TOPIC_ARN = os.getenv('SNS_TOPIC_ARN', 'your-sns-topic-arn')
AWS_REGION = os.getenv('AWS_DEFAULT_REGION', 'us-east-1')
USE_MOCK_STORAGE = os.getenv('USE_MOCK_STORAGE', 'true').lower() == 'true'

# Dependencies
if USE_MOCK_STORAGE:
    from adapters.mock_s3_storage import MockS3StorageAdapter
    from adapters.mock_sqs_queue import MockSQSQueueAdapter, MockSQSAnalysisQueueAdapter
    from adapters.mock_raw_storage import MockRawImageStorageAdapter
    from adapters.mock_sns_notification import MockSNSNotificationAdapter
    from adapters.mock_social_media import SocialMediaManager
    storage = MockS3StorageAdapter(BUCKET_NAME, AWS_REGION)
    raw_storage = MockRawImageStorageAdapter(RAW_BUCKET_NAME, AWS_REGION)
    queue = MockSQSQueueAdapter(QUEUE_URL)
    analysis_queue = MockSQSAnalysisQueueAdapter(ANALYSIS_QUEUE_URL)
    sns_notification = MockSNSNotificationAdapter(SNS_TOPIC_ARN)
    social_media_manager = SocialMediaManager()
    print("Using Mock S3 Storage, SQS Queues, SNS, and Social Media for development")
else:
    from adapters.s3_storage import S3StorageAdapter
    from adapters.sqs_queue import SQSQueueAdapter
    from adapters.sqs_analysis_queue import SQSAnalysisQueueAdapter
    from adapters.mock_social_media import SocialMediaManager  # Always use mock for now
    storage = S3StorageAdapter(BUCKET_NAME, AWS_REGION)
    raw_storage = S3StorageAdapter(RAW_BUCKET_NAME, AWS_REGION)  # Use same adapter for raw
    queue = SQSQueueAdapter(QUEUE_URL)
    analysis_queue = SQSAnalysisQueueAdapter(ANALYSIS_QUEUE_URL)
    social_media_manager = SocialMediaManager()
    # sns_notification = RealSNSAdapter(SNS_TOPIC_ARN)  # TODO: Implement real SNS
    print("Using Real S3 Storage and SQS Queues")

service = ImageProcessingService(storage, queue)

# GraphQL endpoint
graphql_app = GraphQLRouter(schema)
app.include_router(graphql_app, prefix="/graphql")

# Pydantic models
class CategoryCreate(BaseModel):
    name: str
    description: Optional[str] = None

class CategoryUpdate(BaseModel):
    name: str
    description: Optional[str] = None

class CategoryResponse(BaseModel):
    id: str
    name: str
    description: Optional[str] = None

class ProductVariantCreate(BaseModel):
    variant_name: str
    color_code: str
    color_name: str
    range_details: Dict
    sku_suffix: str
    additional_images: Dict[str, str] = {}
    is_active: bool = True
    created_by: str

class ProductCreate(BaseModel):
    sku_id: str
    title: str
    description: Optional[str] = None
    material: str
    pattern: str
    color_primary: str
    colors: List[Dict[str, str]]
    width_estimate_cm: Optional[int] = None
    scale: str
    special_features: List[str] = []
    image_urls: Dict[str, str] = {}
    created_by: str
    category_id: Optional[str] = None
    status: ProductStatus = ProductStatus.DRAFT
    variants: Optional[List[ProductVariantCreate]] = []

class ProductUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    material: Optional[str] = None
    pattern: Optional[str] = None
    color_primary: Optional[str] = None
    colors: Optional[List[Dict[str, str]]] = None
    width_estimate_cm: Optional[int] = None
    scale: Optional[str] = None
    special_features: Optional[List[str]] = None
    image_urls: Optional[Dict[str, str]] = None
    category_id: Optional[str] = None
    status: Optional[ProductStatus] = None
    variants: Optional[List[ProductVariantCreate]] = None

class ProductResponse(BaseModel):
    id: str
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
    status: ProductStatus
    enabled: bool
    discontinuation_reason: Optional[str] = None
    discontinuation_date: Optional[datetime] = None
    status_notes: Optional[str] = None
    price_table: Optional[Dict] = None
    stock: Optional[Dict] = None
    variants: Optional[List[Dict]] = None

class StockCreateRequest(BaseModel):
    current_stock: int
    reserved_stock: int = 0
    reorder_level: int = 10
    max_stock_level: int = 1000
    unit_of_measure: str = "pieces"
    warehouse_location: Optional[str] = None
    batch_number: Optional[str] = None
    expiry_date: Optional[datetime] = None
    updated_by: str

class StockUpdateRequest(BaseModel):
    current_stock: Optional[int] = None
    reserved_stock: Optional[int] = None
    reorder_level: Optional[int] = None
    max_stock_level: Optional[int] = None
    unit_of_measure: Optional[str] = None
    warehouse_location: Optional[str] = None
    batch_number: Optional[str] = None
    expiry_date: Optional[datetime] = None
    updated_by: str

class StockResponse(BaseModel):
    id: str
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
    last_updated: datetime
    updated_by: str

def convert_product_to_response(product) -> ProductResponse:
    """Helper function to convert Product domain object or dict to ProductResponse"""
    if isinstance(product, dict):
        return ProductResponse(**product)
    else:
        result_dict = product.__dict__.copy()
        if result_dict.get('price_table'):
            result_dict['price_table'] = result_dict['price_table'].__dict__
        if result_dict.get('stock'):
            result_dict['stock'] = result_dict['stock'].__dict__
        if result_dict.get('variants'):
            result_dict['variants'] = [v.__dict__ for v in result_dict['variants']]
        return ProductResponse(**result_dict)

class ProductDiscontinueRequest(BaseModel):
    reason: str
    notes: Optional[str] = None

class ProductStatusUpdateRequest(BaseModel):
    status: ProductStatus
    notes: Optional[str] = None

class ProductVariantUpdate(BaseModel):
    variant_name: Optional[str] = None
    color_code: Optional[str] = None
    color_name: Optional[str] = None
    range_details: Optional[Dict] = None
    sku_suffix: Optional[str] = None
    additional_images: Optional[Dict[str, str]] = None
    is_active: Optional[bool] = None

class ProductVariantResponse(BaseModel):
    id: str
    product_id: str
    variant_name: str
    color_code: str
    color_name: str
    range_details: Dict
    sku_suffix: str
    additional_images: Dict[str, str]
    is_active: bool
    created_by: str
    created_time: datetime
    updated_time: Optional[datetime]

class PriceTableCreate(BaseModel):
    wholesale_price: Decimal
    retail_price: Decimal
    currency: str = "INR"
    created_by: str

class PriceTableUpdate(BaseModel):
    wholesale_price: Optional[Decimal] = None
    retail_price: Optional[Decimal] = None
    currency: Optional[str] = None
    modified_by: str

class PriceTableResponse(BaseModel):
    id: str
    product_id: str
    wholesale_price: Decimal
    retail_price: Decimal
    currency: str
    version: int
    created_by: str
    created_time: datetime
    modified_by: Optional[str]
    modified_time: Optional[datetime]

class RawImageUploadResponse(BaseModel):
    raw_image_key: str
    raw_image_url: str
    analysis_queued: bool
    message: str

class RecommendationResponse(BaseModel):
    id: str
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
    created_time: datetime
    updated_time: Optional[datetime]

class RecommendationUpdateRequest(BaseModel):
    is_considered: bool
    consideration_reason: Optional[str] = None

class CampaignCreateRequest(BaseModel):
    name: str
    platform: str  # instagram, facebook, twitter
    campaign_type: str  # awareness, conversion, engagement
    target_audience: Dict
    budget: Decimal
    currency: str = "USD"
    start_date: datetime
    end_date: datetime
    creative_assets: Dict
    created_by: str

class CampaignResponse(BaseModel):
    id: str
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
    created_time: datetime
    updated_time: Optional[datetime]

class CampaignStatusUpdate(BaseModel):
    status: str  # active, paused, completed

class CampaignMetricResponse(BaseModel):
    id: str
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
    collected_at: datetime

class MetricsCollectionRequest(BaseModel):
    start_date: datetime
    end_date: datetime

@app.post("/upload")
async def upload_image(file: UploadFile):
    if not file.content_type.startswith('image/'):
        raise HTTPException(400, "File must be an image")
    
    image = ImageUpload(
        filename=file.filename,
        content=file.file,
        content_type=file.content_type
    )
    
    image_key = service.upload_and_queue(image)
    return {"image_key": image_key, "status": "queued"}

# Category APIs
@app.post("/categories", response_model=CategoryResponse)
async def create_category(category: CategoryCreate, db: Session = Depends(get_db)):
    category_service = CategoryService(DatabaseCategoryRepository(db))
    result = category_service.create_category(category.name, category.description)
    return CategoryResponse(id=result.id, name=result.name, description=result.description)

@app.get("/categories")
async def get_categories(db: Session = Depends(get_db)):
    category_service = CategoryService(DatabaseCategoryRepository(db))
    categories = category_service.get_all_categories()
    return categories

@app.get("/categories/{category_id}", response_model=CategoryResponse)
async def get_category(category_id: str, db: Session = Depends(get_db)):
    category_service = CategoryService(DatabaseCategoryRepository(db))
    category = category_service.get_category(category_id)
    if not category:
        raise HTTPException(404, "Category not found")
    return CategoryResponse(id=category.id, name=category.name, description=category.description)

@app.put("/categories/{category_id}", response_model=CategoryResponse)
async def update_category(category_id: str, category: CategoryUpdate, db: Session = Depends(get_db)):
    category_service = CategoryService(DatabaseCategoryRepository(db))
    result = category_service.update_category(category_id, category.name, category.description)
    if not result:
        raise HTTPException(404, "Category not found")
    return CategoryResponse(id=result.id, name=result.name, description=result.description)

@app.delete("/categories/{category_id}")
async def delete_category(category_id: str, db: Session = Depends(get_db)):
    category_service = CategoryService(DatabaseCategoryRepository(db))
    success = category_service.delete_category(category_id)
    if not success:
        raise HTTPException(404, "Category not found")
    return {"message": "Category deleted"}

def remove_duplicate_variants(variants: List[ProductVariantCreate]) -> List[ProductVariantCreate]:
    """Remove duplicate variants based on variant_name and sku_suffix combination"""
    seen = set()
    unique_variants = []
    for variant in variants:
        key = (variant.variant_name, variant.sku_suffix)
        if key not in seen:
            seen.add(key)
            unique_variants.append(variant)
    return unique_variants

# Product APIs
@app.post("/products", response_model=ProductResponse)
async def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    product_service = ProductService(DatabaseProductRepository(db), analysis_queue)
    product_repo = DatabaseProductRepository(db)
    
    domain_product = Product(
        id=None,
        sku_id=product.sku_id,
        title=product.title,
        description=product.description,
        material=product.material,
        pattern=product.pattern,
        color_primary=product.color_primary,
        colors=product.colors,
        width_estimate_cm=product.width_estimate_cm,
        scale=product.scale,
        special_features=product.special_features,
        image_urls=product.image_urls,
        created_by=product.created_by,
        category_id=product.category_id,
        created_at=None,
        updated_at=None,
        status=product.status
    )
    result = product_service.create_product(domain_product)
    
    # Create variants if provided
    if product.variants:
        unique_variants = remove_duplicate_variants(product.variants)
        for variant_data in unique_variants:
            variant = ProductVariant(
                id=None,
                product_id=result.id,
                variant_name=variant_data.variant_name,
                color_code=variant_data.color_code,
                color_name=variant_data.color_name,
                range_details=variant_data.range_details,
                sku_suffix=variant_data.sku_suffix,
                additional_images=variant_data.additional_images,
                is_active=variant_data.is_active,
                created_by=variant_data.created_by
            )
            product_repo.create_variant(variant)
    
    # Get updated product with variants
    updated_result = product_repo.get_by_id(result.id)
    return convert_product_to_response(updated_result)

@app.get("/products")
async def get_products(db: Session = Depends(get_db)):
    product_service = ProductService(DatabaseProductRepository(db))
    products = product_service.get_all_products()
    
    return products

@app.get("/products/{product_id}", response_model=ProductResponse)
async def get_product(product_id: str, db: Session = Depends(get_db)):
    product_service = ProductService(DatabaseProductRepository(db))
    product = product_service.get_product(product_id)
    if not product:
        raise HTTPException(404, "Product not found")
    
    return convert_product_to_response(product)

@app.put("/products/{product_id}", response_model=ProductResponse)
async def update_product(product_id: str, product_update: ProductUpdate, db: Session = Depends(get_db)):
    product_service = ProductService(DatabaseProductRepository(db))
    product_repo = DatabaseProductRepository(db)
    existing = product_service.get_product(product_id)
    if not existing:
        raise HTTPException(404, "Product not found")
    
    # Update only provided fields (excluding variants)
    update_data = product_update.dict(exclude_unset=True, exclude={'variants'})
    for key, value in update_data.items():
        setattr(existing, key, value)
    
    result = product_service.update_product(existing)
    
    # Handle variants if provided
    if product_update.variants is not None:
        # Remove existing variants
        product_repo.delete_variants_by_product_id(product_id)
        
        # Add new unique variants
        unique_variants = remove_duplicate_variants(product_update.variants)
        for variant_data in unique_variants:
            variant = ProductVariant(
                id=None,
                product_id=product_id,
                variant_name=variant_data.variant_name,
                color_code=variant_data.color_code,
                color_name=variant_data.color_name,
                range_details=variant_data.range_details,
                sku_suffix=variant_data.sku_suffix,
                additional_images=variant_data.additional_images,
                is_active=variant_data.is_active,
                created_by=variant_data.created_by
            )
            product_repo.create_variant(variant)
    
    # Get updated product with variants
    updated_result = product_repo.get_by_id(result.id)
    return convert_product_to_response(updated_result)

@app.delete("/products/{product_id}")
async def delete_product(product_id: str, db: Session = Depends(get_db)):
    product_service = ProductService(DatabaseProductRepository(db))
    success = product_service.delete_product(product_id)
    if not success:
        raise HTTPException(404, "Product not found")
    return {"message": "Product deleted"}

@app.post("/products/{product_id}/discontinue")
async def discontinue_product(
    product_id: str, 
    discontinue_request: ProductDiscontinueRequest, 
    db: Session = Depends(get_db)
):
    """Discontinue a product with reason"""
    product_service = ProductService(DatabaseProductRepository(db))
    product = product_service.get_product(product_id)
    if not product:
        raise HTTPException(404, "Product not found")
    
    # Update product status and discontinuation info
    from datetime import datetime
    product.status = ProductStatus.DISCONTINUED
    product.discontinuation_reason = discontinue_request.reason
    product.discontinuation_date = datetime.utcnow()
    product.status_notes = discontinue_request.notes
    
    updated_product = product_service.update_product(product)
    
    # Convert price_table to dict if it exists
    result_dict = updated_product.__dict__.copy()
    if result_dict.get('price_table'):
        result_dict['price_table'] = result_dict['price_table'].__dict__
    
    return ProductResponse(**result_dict)

@app.put("/products/{product_id}/status")
async def update_product_status(
    product_id: str,
    status_request: ProductStatusUpdateRequest,
    db: Session = Depends(get_db)
):
    """Update product status with optional notes"""
    product_service = ProductService(DatabaseProductRepository(db))
    product = product_service.get_product(product_id)
    if not product:
        raise HTTPException(404, "Product not found")
    
    # Update status and notes
    product.status = status_request.status
    product.status_notes = status_request.notes
    
    # Clear discontinuation fields if status is not discontinued
    if status_request.status != ProductStatus.DISCONTINUED:
        product.discontinuation_reason = None
        product.discontinuation_date = None
    
    updated_product = product_service.update_product(product)
    
    # Convert price_table to dict if it exists
    result_dict = updated_product.__dict__.copy()
    if result_dict.get('price_table'):
        result_dict['price_table'] = result_dict['price_table'].__dict__
    
    return ProductResponse(**result_dict)

@app.post("/products/{product_id}/enable")
async def enable_product(product_id: str, db: Session = Depends(get_db)):
    """Enable a product"""
    product_service = ProductService(DatabaseProductRepository(db))
    product = product_service.get_product(product_id)
    if not product:
        raise HTTPException(404, "Product not found")
    
    product.enabled = True
    updated_product = product_service.update_product(product)
    
    # Convert price_table to dict if it exists
    result_dict = updated_product.__dict__.copy()
    if result_dict.get('price_table'):
        result_dict['price_table'] = result_dict['price_table'].__dict__
    
    return ProductResponse(**result_dict)

@app.post("/products/{product_id}/disable")
async def disable_product(product_id: str, db: Session = Depends(get_db)):
    """Disable a product"""
    product_service = ProductService(DatabaseProductRepository(db))
    product = product_service.get_product(product_id)
    if not product:
        raise HTTPException(404, "Product not found")
    
    product.enabled = False
    updated_product = product_service.update_product(product)
    
    # Convert price_table to dict if it exists
    result_dict = updated_product.__dict__.copy()
    if result_dict.get('price_table'):
        result_dict['price_table'] = result_dict['price_table'].__dict__
    
    return ProductResponse(**result_dict)

@app.post("/products/{product_id}/images")
async def upload_product_images(
    product_id: str,
    raw: UploadFile = File(...),
    thumbnail: UploadFile = File(None),
    zoom: UploadFile = File(None),
    db: Session = Depends(get_db)
):
    try:
        product_service = ProductService(DatabaseProductRepository(db), analysis_queue)
        product = product_service.get_product(product_id)
        if not product:
            raise HTTPException(404, "Product not found")
        
        # Validate image files
        images_to_upload = {"raw": raw}
        if thumbnail:
            images_to_upload["thumbnail"] = thumbnail
        if zoom:
            images_to_upload["zoom"] = zoom
        
        for img_type, file in images_to_upload.items():
            if file and not file.content_type.startswith('image/'):
                raise HTTPException(400, f"{img_type} file must be an image")
        
        # Convert to ImageUpload objects
        image_uploads = {}
        for img_type, file in images_to_upload.items():
            if file:
                image_uploads[img_type] = ImageUpload(
                    filename=file.filename,
                    content=file.file,
                    content_type=file.content_type
                )
        
        # Store images and get URLs
        image_urls = storage.store_product_images(image_uploads)
        
        # Update product with image URLs
        product.image_urls.update(image_urls)
        updated_product = product_service.update_product(product)
        
        # Queue for GenAI analysis
        from domain.models import ProductAnalysisJob
        analysis_job = ProductAnalysisJob(
            product_id=product_id,
            sku_id=product.sku_id,
            image_urls=image_urls
        )
        analysis_queue.queue_analysis(analysis_job)
        
        return {
            "message": "Images uploaded successfully",
            "image_urls": image_urls,
            "product_id": product_id,
            "analysis_queued": True
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"Internal server error: {str(e)}")

@app.get("/products/{product_id}/images")
async def get_product_images(product_id: str, db: Session = Depends(get_db)):
    product_service = ProductService(DatabaseProductRepository(db))
    product = product_service.get_product(product_id)
    if not product:
        raise HTTPException(404, "Product not found")
    
    return {
        "product_id": product_id,
        "image_urls": product.image_urls
    }

# Product variant endpoints
@app.post("/products/{product_id}/variants", response_model=ProductVariantResponse)
async def create_variant(product_id: str, variant_data: ProductVariantCreate, db: Session = Depends(get_db)):
    product_repo = DatabaseProductRepository(db)
    
    # Check if product exists
    product = product_repo.get_by_id(product_id)
    if not product:
        raise HTTPException(404, "Product not found")
    
    variant = ProductVariant(
        id=None,
        product_id=product_id,
        variant_name=variant_data.variant_name,
        color_code=variant_data.color_code,
        color_name=variant_data.color_name,
        range_details=variant_data.range_details,
        sku_suffix=variant_data.sku_suffix,
        additional_images=variant_data.additional_images,
        is_active=variant_data.is_active,
        created_by=variant_data.created_by
    )
    
    created_variant = product_repo.create_variant(variant)
    return ProductVariantResponse(**created_variant.__dict__)

@app.get("/products/{product_id}/variants", response_model=List[ProductVariantResponse])
async def get_variants(product_id: str, db: Session = Depends(get_db)):
    product_repo = DatabaseProductRepository(db)
    product = product_repo.get_by_id(product_id)
    if not product:
        raise HTTPException(404, "Product not found")
    
    return [ProductVariantResponse(**v.__dict__) for v in product.variants or []]

@app.put("/products/{product_id}/variants/{variant_id}", response_model=ProductVariantResponse)
async def update_variant(product_id: str, variant_id: str, variant_data: ProductVariantUpdate, db: Session = Depends(get_db)):
    product_repo = DatabaseProductRepository(db)
    
    # Get existing variant
    product = product_repo.get_by_id(product_id)
    if not product:
        raise HTTPException(404, "Product not found")
    
    existing_variant = next((v for v in product.variants or [] if v.id == variant_id), None)
    if not existing_variant:
        raise HTTPException(404, "Variant not found")
    
    # Update fields
    update_data = variant_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(existing_variant, key, value)
    
    updated_variant = product_repo.update_variant(existing_variant)
    return ProductVariantResponse(**updated_variant.__dict__)

@app.delete("/products/{product_id}/variants/{variant_id}")
async def delete_variant(product_id: str, variant_id: str, db: Session = Depends(get_db)):
    product_repo = DatabaseProductRepository(db)
    
    # Check if product exists
    product = product_repo.get_by_id(product_id)
    if not product:
        raise HTTPException(404, "Product not found")
    
    success = product_repo.delete_variant(variant_id)
    if not success:
        raise HTTPException(404, "Variant not found")
    
    return {"message": "Variant deleted"}

@app.post("/products/{product_id}/price", response_model=PriceTableResponse)
async def create_price(product_id: str, price_data: PriceTableCreate, db: Session = Depends(get_db)):
    from adapters.database.entities import PriceTableEntity
    from datetime import datetime
    
    price_entity = PriceTableEntity(
        product_id=product_id,
        wholesale_price=price_data.wholesale_price,
        retail_price=price_data.retail_price,
        currency=price_data.currency,
        created_by=price_data.created_by,
        created_time=datetime.utcnow()
    )
    db.add(price_entity)
    db.commit()
    db.refresh(price_entity)
    
    return PriceTableResponse(
        id=str(price_entity.id),
        product_id=str(price_entity.product_id),
        wholesale_price=price_entity.wholesale_price,
        retail_price=price_entity.retail_price,
        currency=price_entity.currency,
        version=price_entity.version,
        created_by=price_entity.created_by,
        created_time=price_entity.created_time,
        modified_by=price_entity.modified_by,
        modified_time=price_entity.modified_time
    )

@app.put("/products/{product_id}/price", response_model=PriceTableResponse)
async def update_price(product_id: str, price_data: PriceTableUpdate, db: Session = Depends(get_db)):
    from adapters.database.entities import PriceTableEntity
    from datetime import datetime
    
    price_entity = db.query(PriceTableEntity).filter(PriceTableEntity.product_id == product_id).first()
    if not price_entity:
        raise HTTPException(status_code=404, detail="Price not found")
    
    if price_data.wholesale_price is not None:
        price_entity.wholesale_price = price_data.wholesale_price
    if price_data.retail_price is not None:
        price_entity.retail_price = price_data.retail_price
    if price_data.currency is not None:
        price_entity.currency = price_data.currency
    price_entity.modified_by = price_data.modified_by
    price_entity.modified_time = datetime.utcnow()
    price_entity.version += 1
    
    db.commit()
    db.refresh(price_entity)
    
    return PriceTableResponse(
        id=str(price_entity.id),
        product_id=str(price_entity.product_id),
        wholesale_price=price_entity.wholesale_price,
        retail_price=price_entity.retail_price,
        currency=price_entity.currency,
        version=price_entity.version,
        created_by=price_entity.created_by,
        created_time=price_entity.created_time,
        modified_by=price_entity.modified_by,
        modified_time=price_entity.modified_time
    )

@app.delete("/products/{product_id}/price")
async def delete_price(product_id: str, db: Session = Depends(get_db)):
    from adapters.database.entities import PriceTableEntity
    
    price_entity = db.query(PriceTableEntity).filter(PriceTableEntity.product_id == product_id).first()
    if not price_entity:
        raise HTTPException(status_code=404, detail="Price not found")
    
    db.delete(price_entity)
    db.commit()
    return {"message": "Price deleted successfully"}

# Raw Image Analysis APIs
@app.post("/raw-images/upload", response_model=RawImageUploadResponse)
async def upload_raw_image(raw: UploadFile = File(...)):
    """Upload raw image for market analysis"""
    if not raw.content_type.startswith('image/'):
        raise HTTPException(400, "File must be an image")
    
    # Store in unprocessed bucket
    image_upload = ImageUpload(
        filename=raw.filename,
        content=raw.file,
        content_type=raw.content_type
    )
    
    raw_image_key = raw_storage.store_raw_image(image_upload)
    raw_image_url = raw_storage.get_raw_image_url(raw_image_key)
    
    # Send SNS notification for agent analysis
    from domain.models import RawImageAnalysisJob
    analysis_job = RawImageAnalysisJob(
        raw_image_key=raw_image_key,
        filename=raw.filename,
        analysis_type="market_analysis"
    )
    sns_notification.send_notification(analysis_job)
    
    return RawImageUploadResponse(
        raw_image_key=raw_image_key,
        raw_image_url=raw_image_url,
        analysis_queued=True,
        message="Raw image uploaded and queued for analysis"
    )

@app.get("/recommendations", response_model=List[RecommendationResponse])
async def get_recommendations(db: Session = Depends(get_db)):
    """Get all recommendations"""
    from adapters.database.entities import RecommendationEntity
    
    recommendations = db.query(RecommendationEntity).order_by(RecommendationEntity.created_time.desc()).all()
    
    return [
        RecommendationResponse(
            id=str(rec.id),
            raw_image_key=rec.raw_image_key,
            analysis_type=rec.analysis_type,
            recommended_products=rec.recommended_products,
            market_insights=rec.market_insights,
            sku_properties=rec.sku_properties,
            confidence_score=rec.confidence_score,
            version=rec.version,
            expiry_date=rec.expiry_date,
            is_considered=rec.is_considered,
            consideration_reason=rec.consideration_reason,
            created_by=rec.created_by,
            created_time=rec.created_time,
            updated_time=rec.updated_time
        ) for rec in recommendations
    ]

@app.get("/recommendations/{recommendation_id}", response_model=RecommendationResponse)
async def get_recommendation(recommendation_id: str, db: Session = Depends(get_db)):
    """Get specific recommendation"""
    from adapters.database.entities import RecommendationEntity
    
    rec = db.query(RecommendationEntity).filter(RecommendationEntity.id == recommendation_id).first()
    if not rec:
        raise HTTPException(404, "Recommendation not found")
    
    return RecommendationResponse(
        id=str(rec.id),
        raw_image_key=rec.raw_image_key,
        analysis_type=rec.analysis_type,
        recommended_products=rec.recommended_products,
        market_insights=rec.market_insights,
        sku_properties=rec.sku_properties,
        confidence_score=rec.confidence_score,
        version=rec.version,
        expiry_date=rec.expiry_date,
        is_considered=rec.is_considered,
        consideration_reason=rec.consideration_reason,
        created_by=rec.created_by,
        created_time=rec.created_time,
        updated_time=rec.updated_time
    )

@app.put("/recommendations/{recommendation_id}/consideration")
async def update_recommendation_consideration(
    recommendation_id: str, 
    update_data: RecommendationUpdateRequest, 
    db: Session = Depends(get_db)
):
    """Update recommendation consideration status"""
    from adapters.database.entities import RecommendationEntity
    from datetime import datetime
    
    rec = db.query(RecommendationEntity).filter(RecommendationEntity.id == recommendation_id).first()
    if not rec:
        raise HTTPException(404, "Recommendation not found")
    
    rec.is_considered = update_data.is_considered
    rec.consideration_reason = update_data.consideration_reason
    rec.updated_time = datetime.utcnow()
    
    db.commit()
    db.refresh(rec)
    
    return {"message": "Recommendation updated successfully"}

# Social Media Campaign APIs
@app.post("/campaigns", response_model=CampaignResponse)
async def create_campaign(campaign_data: CampaignCreateRequest, db: Session = Depends(get_db)):
    """Create a new social media campaign"""
    from adapters.database.entities import CampaignEntity
    from domain.models import Campaign
    
    # Create domain campaign
    domain_campaign = Campaign(
        id=None,
        name=campaign_data.name,
        platform=campaign_data.platform,
        campaign_type=campaign_data.campaign_type,
        target_audience=campaign_data.target_audience,
        budget=campaign_data.budget,
        currency=campaign_data.currency,
        start_date=campaign_data.start_date,
        end_date=campaign_data.end_date,
        status="draft",
        platform_campaign_id=None,
        creative_assets=campaign_data.creative_assets,
        created_by=campaign_data.created_by
    )
    
    # Create campaign on social media platform
    platform_campaign_id = social_media_manager.create_campaign(domain_campaign)
    
    # Save to database
    campaign_entity = CampaignEntity(
        name=campaign_data.name,
        platform=campaign_data.platform,
        campaign_type=campaign_data.campaign_type,
        target_audience=campaign_data.target_audience,
        budget=campaign_data.budget,
        currency=campaign_data.currency,
        start_date=campaign_data.start_date,
        end_date=campaign_data.end_date,
        status="draft",
        platform_campaign_id=platform_campaign_id,
        creative_assets=campaign_data.creative_assets,
        created_by=campaign_data.created_by
    )
    
    db.add(campaign_entity)
    db.commit()
    db.refresh(campaign_entity)
    
    return CampaignResponse(
        id=str(campaign_entity.id),
        name=campaign_entity.name,
        platform=campaign_entity.platform,
        campaign_type=campaign_entity.campaign_type,
        target_audience=campaign_entity.target_audience,
        budget=campaign_entity.budget,
        currency=campaign_entity.currency,
        start_date=campaign_entity.start_date,
        end_date=campaign_entity.end_date,
        status=campaign_entity.status,
        platform_campaign_id=campaign_entity.platform_campaign_id,
        creative_assets=campaign_entity.creative_assets,
        created_by=campaign_entity.created_by,
        created_time=campaign_entity.created_time,
        updated_time=campaign_entity.updated_time
    )

@app.get("/campaigns", response_model=List[CampaignResponse])
async def get_campaigns(db: Session = Depends(get_db)):
    """Get all campaigns"""
    from adapters.database.entities import CampaignEntity
    
    campaigns = db.query(CampaignEntity).order_by(CampaignEntity.created_time.desc()).all()
    
    return [
        CampaignResponse(
            id=str(c.id),
            name=c.name,
            platform=c.platform,
            campaign_type=c.campaign_type,
            target_audience=c.target_audience,
            budget=c.budget,
            currency=c.currency,
            start_date=c.start_date,
            end_date=c.end_date,
            status=c.status,
            platform_campaign_id=c.platform_campaign_id,
            creative_assets=c.creative_assets,
            created_by=c.created_by,
            created_time=c.created_time,
            updated_time=c.updated_time
        ) for c in campaigns
    ]

@app.put("/campaigns/{campaign_id}/status")
async def update_campaign_status(
    campaign_id: str, 
    status_update: CampaignStatusUpdate, 
    db: Session = Depends(get_db)
):
    """Update campaign status (active, paused, completed)"""
    from adapters.database.entities import CampaignEntity
    from datetime import datetime
    
    campaign = db.query(CampaignEntity).filter(CampaignEntity.id == campaign_id).first()
    if not campaign:
        raise HTTPException(404, "Campaign not found")
    
    # Update status on platform
    if campaign.platform_campaign_id:
        social_media_manager.get_adapter(campaign.platform).update_campaign_status(
            campaign.platform_campaign_id, status_update.status
        )
    
    # Update in database
    campaign.status = status_update.status
    campaign.updated_time = datetime.utcnow()
    
    db.commit()
    return {"message": "Campaign status updated successfully"}

@app.post("/campaigns/{campaign_id}/collect-metrics")
async def collect_campaign_metrics(
    campaign_id: str,
    metrics_request: MetricsCollectionRequest,
    db: Session = Depends(get_db)
):
    """Collect metrics for a campaign over a date range"""
    from adapters.database.entities import CampaignEntity, CampaignMetricEntity
    from datetime import timedelta
    
    campaign = db.query(CampaignEntity).filter(CampaignEntity.id == campaign_id).first()
    if not campaign:
        raise HTTPException(404, "Campaign not found")
    
    if not campaign.platform_campaign_id:
        raise HTTPException(400, "Campaign not deployed to platform")
    
    # Collect metrics for each day in the range
    current_date = metrics_request.start_date.date()
    end_date = metrics_request.end_date.date()
    collected_count = 0
    
    while current_date <= end_date:
        # Check if metrics already exist for this date
        existing = db.query(CampaignMetricEntity).filter(
            CampaignMetricEntity.campaign_id == campaign_id,
            CampaignMetricEntity.metric_date == current_date
        ).first()
        
        if not existing:
            # Collect metrics from platform
            metric = social_media_manager.collect_metrics(
                campaign.platform,
                campaign.platform_campaign_id,
                campaign_id,
                datetime.combine(current_date, datetime.min.time())
            )
            
            # Save to database
            metric_entity = CampaignMetricEntity(
                campaign_id=campaign_id,
                metric_date=metric.metric_date,
                impressions=metric.impressions,
                clicks=metric.clicks,
                conversions=metric.conversions,
                spend=metric.spend,
                reach=metric.reach,
                engagement=metric.engagement,
                ctr=metric.ctr,
                cpc=metric.cpc,
                cpm=metric.cpm,
                additional_metrics=metric.additional_metrics
            )
            
            db.add(metric_entity)
            collected_count += 1
        
        current_date += timedelta(days=1)
    
    db.commit()
    return {
        "message": f"Collected metrics for {collected_count} days",
        "campaign_id": campaign_id,
        "date_range": f"{metrics_request.start_date.date()} to {metrics_request.end_date.date()}"
    }

@app.get("/campaigns/{campaign_id}/metrics", response_model=List[CampaignMetricResponse])
async def get_campaign_metrics(
    campaign_id: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get campaign metrics with optional date filtering"""
    from adapters.database.entities import CampaignMetricEntity
    from datetime import datetime
    
    query = db.query(CampaignMetricEntity).filter(CampaignMetricEntity.campaign_id == campaign_id)
    
    if start_date:
        query = query.filter(CampaignMetricEntity.metric_date >= datetime.fromisoformat(start_date))
    if end_date:
        query = query.filter(CampaignMetricEntity.metric_date <= datetime.fromisoformat(end_date))
    
    metrics = query.order_by(CampaignMetricEntity.metric_date.asc()).all()
    
    return [
        CampaignMetricResponse(
            id=str(m.id),
            campaign_id=str(m.campaign_id),
            metric_date=m.metric_date,
            impressions=m.impressions,
            clicks=m.clicks,
            conversions=m.conversions,
            spend=m.spend,
            reach=m.reach,
            engagement=m.engagement,
            ctr=m.ctr,
            cpc=m.cpc,
            cpm=m.cpm,
            additional_metrics=m.additional_metrics,
            collected_at=m.collected_at
        ) for m in metrics
    ]

# Stock Management APIs
@app.post("/products/{product_id}/stock", response_model=StockResponse)
async def create_stock(product_id: str, stock_data: StockCreateRequest, db: Session = Depends(get_db)):
    """Create stock record for a product"""
    from adapters.database.entities import StockEntity
    
    available_stock = stock_data.current_stock - stock_data.reserved_stock
    
    stock_entity = StockEntity(
        product_id=product_id,
        current_stock=stock_data.current_stock,
        reserved_stock=stock_data.reserved_stock,
        available_stock=available_stock,
        reorder_level=stock_data.reorder_level,
        max_stock_level=stock_data.max_stock_level,
        unit_of_measure=stock_data.unit_of_measure,
        warehouse_location=stock_data.warehouse_location,
        batch_number=stock_data.batch_number,
        expiry_date=stock_data.expiry_date,
        updated_by=stock_data.updated_by
    )
    
    db.add(stock_entity)
    db.commit()
    db.refresh(stock_entity)
    
    return StockResponse(
        id=str(stock_entity.id),
        product_id=str(stock_entity.product_id),
        current_stock=stock_entity.current_stock,
        reserved_stock=stock_entity.reserved_stock,
        available_stock=stock_entity.available_stock,
        reorder_level=stock_entity.reorder_level,
        max_stock_level=stock_entity.max_stock_level,
        unit_of_measure=stock_entity.unit_of_measure,
        warehouse_location=stock_entity.warehouse_location,
        batch_number=stock_entity.batch_number,
        expiry_date=stock_entity.expiry_date,
        last_updated=stock_entity.last_updated,
        updated_by=stock_entity.updated_by
    )

@app.put("/products/{product_id}/stock", response_model=StockResponse)
async def update_stock(product_id: str, stock_data: StockUpdateRequest, db: Session = Depends(get_db)):
    """Update stock record for a product"""
    from adapters.database.entities import StockEntity
    
    stock_entity = db.query(StockEntity).filter(StockEntity.product_id == product_id).first()
    if not stock_entity:
        raise HTTPException(404, "Stock record not found")
    
    if stock_data.current_stock is not None:
        stock_entity.current_stock = stock_data.current_stock
    if stock_data.reserved_stock is not None:
        stock_entity.reserved_stock = stock_data.reserved_stock
    if stock_data.reorder_level is not None:
        stock_entity.reorder_level = stock_data.reorder_level
    if stock_data.max_stock_level is not None:
        stock_entity.max_stock_level = stock_data.max_stock_level
    if stock_data.unit_of_measure is not None:
        stock_entity.unit_of_measure = stock_data.unit_of_measure
    if stock_data.warehouse_location is not None:
        stock_entity.warehouse_location = stock_data.warehouse_location
    if stock_data.batch_number is not None:
        stock_entity.batch_number = stock_data.batch_number
    if stock_data.expiry_date is not None:
        stock_entity.expiry_date = stock_data.expiry_date
    
    stock_entity.available_stock = stock_entity.current_stock - stock_entity.reserved_stock
    stock_entity.updated_by = stock_data.updated_by
    
    db.commit()
    db.refresh(stock_entity)
    
    return StockResponse(
        id=str(stock_entity.id),
        product_id=str(stock_entity.product_id),
        current_stock=stock_entity.current_stock,
        reserved_stock=stock_entity.reserved_stock,
        available_stock=stock_entity.available_stock,
        reorder_level=stock_entity.reorder_level,
        max_stock_level=stock_entity.max_stock_level,
        unit_of_measure=stock_entity.unit_of_measure,
        warehouse_location=stock_entity.warehouse_location,
        batch_number=stock_entity.batch_number,
        expiry_date=stock_entity.expiry_date,
        last_updated=stock_entity.last_updated,
        updated_by=stock_entity.updated_by
    )

# API v1 endpoints with ORM operations
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, String, Integer, Numeric, UUID, Boolean, DateTime, ForeignKey, Text, JSON, ARRAY
import uuid
from datetime import datetime

Base = declarative_base()

# ORM Models
class CategoryORM(Base):
    __tablename__ = "categories"
    __table_args__ = {'extend_existing': True}
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)

class ProductORM(Base):
    __tablename__ = "products"
    __table_args__ = {'extend_existing': True}
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    sku_id = Column(String(255), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    material = Column(String(100), nullable=False)
    pattern = Column(String(100), nullable=False)
    color_primary = Column(String(7), nullable=False)
    colors = Column(JSON, nullable=False)
    width_estimate_cm = Column(Integer, nullable=True)
    scale = Column(String(50), nullable=False)
    special_features = Column(ARRAY(String), nullable=False)
    image_urls = Column(JSON, nullable=False)
    created_by = Column(String(255), nullable=False)
    category_id = Column(UUID(as_uuid=True), nullable=True)
    status = Column(String(50), nullable=False)
    discontinuation_reason = Column(Text, nullable=True)
    discontinuation_date = Column(DateTime, nullable=True)
    status_notes = Column(Text, nullable=True)
    enabled = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, nullable=True)

class PartnerORM(Base):
    __tablename__ = "partners"
    __table_args__ = {'extend_existing': True}
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(128), nullable=False)
    code = Column(String(128), nullable=False)
    email = Column(String(255), nullable=True)
    phone = Column(String(50), nullable=True)
    address = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)

class VariantORM(Base):
    __tablename__ = "product_variants"
    __table_args__ = {'extend_existing': True}
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_id = Column(UUID(as_uuid=True), nullable=False)
    variant_name = Column(String(255), nullable=False)
    color_code = Column(String(7), nullable=False)
    color_name = Column(String(100), nullable=False)
    range_details = Column(JSON, nullable=False)
    sku_suffix = Column(String(50), nullable=False)
    additional_images = Column(JSON, nullable=False)
    is_active = Column(Boolean, nullable=False)
    created_by = Column(String(255), nullable=False)
    material = Column(String(100), nullable=True)
    pattern = Column(String(100), nullable=True)

class StockORM(Base):
    __tablename__ = "stock"
    __table_args__ = {'extend_existing': True}
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_id = Column(UUID(as_uuid=True), nullable=False)
    variant_id = Column(UUID(as_uuid=True), nullable=True)
    partner_id = Column(UUID(as_uuid=True), nullable=True)
    quantity_available = Column(Integer, nullable=False, default=0)
    quantity_reserved = Column(Integer, nullable=False, default=0)
    reorder_level = Column(Integer, nullable=False, default=0)
    reorder_quantity = Column(Integer, nullable=False, default=0)
    retail_price = Column(Numeric(10, 2), nullable=True, default=0.00)
    wholesale_price = Column(Numeric(10, 2), nullable=True, default=0.00)
    currency = Column(String(3), nullable=True, default='INR')
    partner_sku = Column(String(100), nullable=True)

# Categories API
@app.get("/api/v1/categories")
async def get_categories_v1(db: Session = Depends(get_db)):
    """Get all categories using ORM"""
    categories = db.query(CategoryORM).all()
    return [{"id": str(cat.id), "name": cat.name, "description": cat.description} for cat in categories]

@app.post("/api/v1/categories")
async def create_category_v1(category: CategoryCreate, db: Session = Depends(get_db)):
    """Create new category using ORM"""
    db_category = CategoryORM(name=category.name, description=category.description)
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return {"id": str(db_category.id), "name": db_category.name, "description": db_category.description}

@app.put("/api/v1/categories/{category_id}")
async def update_category_v1(category_id: str, category: CategoryCreate, db: Session = Depends(get_db)):
    """Update category using ORM"""
    db_category = db.query(CategoryORM).filter(CategoryORM.id == category_id).first()
    if not db_category:
        raise HTTPException(404, "Category not found")
    
    db_category.name = category.name
    db_category.description = category.description
    db.commit()
    return {"id": str(db_category.id), "name": db_category.name, "description": db_category.description}

@app.delete("/api/v1/categories/{category_id}")
async def delete_category_v1(category_id: str, db: Session = Depends(get_db)):
    """Delete category using ORM"""
    db_category = db.query(CategoryORM).filter(CategoryORM.id == category_id).first()
    if not db_category:
        raise HTTPException(404, "Category not found")
    
    db.delete(db_category)
    db.commit()
    return {"message": "Category deleted successfully"}

# Products API
@app.get("/api/v1/products/list")
async def get_products_list_v1(db: Session = Depends(get_db)):
    """Get products with category info using ORM"""
    products = db.query(ProductORM).all()
    result = []
    
    for product in products:
        # Get category using ORM with proper UUID handling
        category = None
        if product.category_id:
            try:
                category = db.query(CategoryORM).filter(CategoryORM.id == str(product.category_id)).first()
            except:
                pass
        category_name = category.name if category else None
        
        # Initialize default values
        total_stock = 0
        min_retail_price = 0.0
        min_wholesale_price = 0.0
        variant_colors = []
        
        # Try to get variants and stock - handle errors gracefully
        try:
            variants = db.query(VariantORM).filter(VariantORM.product_id == product.id).all()
            
            for variant in variants:
                if variant.color_code:
                    variant_colors.append(variant.color_code)
                
                try:
                    stocks = db.query(StockORM).filter(StockORM.variant_id == variant.id).all()
                    for stock in stocks:
                        total_stock += stock.quantity_available or 0
                        
                        if stock.retail_price:
                            retail_price = float(stock.retail_price)
                            if min_retail_price == 0 or retail_price < min_retail_price:
                                min_retail_price = retail_price
                        
                        if stock.wholesale_price:
                            wholesale_price = float(stock.wholesale_price)
                            if min_wholesale_price == 0 or wholesale_price < min_wholesale_price:
                                min_wholesale_price = wholesale_price
                except:
                    pass  # Skip stock calculation if table doesn't exist
        except:
            pass  # Skip variant calculation if table doesn't exist
        
        result.append({
            "product_id": str(product.id),
            "title": product.title,
            "description": product.description,
            "status": product.status or "ACTIVE",
            "category_id": str(product.category_id) if product.category_id else None,
            "category_name": category_name,
            "images": [],  # TODO: Extract from image_urls field or related table
            "total_stock": total_stock,
            "min_retail_price": min_retail_price,
            "min_wholesale_price": min_wholesale_price,
            "variant_colors": list(set(variant_colors)) if variant_colors else []
        })
    
    return result

@app.get("/api/v1/categories/{category_id}/products")
async def get_products_by_category_v1(category_id: str, db: Session = Depends(get_db)):
    """Get products by category ID using ORM"""
    try:
        products = db.query(ProductORM).filter(ProductORM.category_id == category_id).all()
        return [{
            "product_id": str(product.id),
            "title": product.title,
            "description": product.description,
            "status": product.status,
            "sku_id": product.sku_id,
            "enabled": product.enabled
        } for product in products]
    except Exception as e:
        return []

@app.post("/api/v1/products")
async def create_product_v1(product_data: dict, db: Session = Depends(get_db)):
    """Create new product using ORM"""
    if not product_data.get("title"):
        raise HTTPException(400, "Product title is required")
    
    db_product = ProductORM(
        sku_id=product_data.get("sku_id", f"SKU-{uuid.uuid4().hex[:8]}"),
        title=product_data["title"],
        description=product_data.get("description"),
        material=product_data.get("material", "cotton"),
        pattern=product_data.get("pattern", "solid"),
        color_primary=product_data.get("color_primary", "#FFFFFF"),
        colors=product_data.get("colors", []),
        width_estimate_cm=product_data.get("width_estimate_cm"),
        scale=product_data.get("scale", "medium"),
        special_features=product_data.get("special_features", []),
        image_urls=product_data.get("image_urls", []),
        created_by=product_data.get("created_by", "system"),
        category_id=product_data.get("category_id"),
        status=product_data.get("status", "DRAFT"),
        enabled=product_data.get("enabled", True)
    )
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    
    return {
        "id": str(db_product.id),
        "title": db_product.title,
        "description": db_product.description,
        "sku_id": db_product.sku_id,
        "category_id": str(db_product.category_id) if db_product.category_id else None,
        "status": db_product.status,
        "enabled": db_product.enabled
    }

@app.put("/api/v1/products/{product_id}")
async def update_product_v1(product_id: str, product_data: dict, db: Session = Depends(get_db)):
    """Update product using ORM"""
    db_product = db.query(ProductORM).filter(ProductORM.id == product_id).first()
    if not db_product:
        raise HTTPException(404, "Product not found")
    
    for key, value in product_data.items():
        if hasattr(db_product, key):
            setattr(db_product, key, value)
    
    db.commit()
    db.refresh(db_product)
    
    return {
        "id": str(db_product.id),
        "title": db_product.title,
        "description": db_product.description,
        "status": db_product.status,
        "category_id": str(db_product.category_id) if db_product.category_id else None
    }

@app.delete("/api/v1/products/{product_id}")
async def delete_product_v1(product_id: str, db: Session = Depends(get_db)):
    """Delete product using ORM"""
    db_product = db.query(ProductORM).filter(ProductORM.id == product_id).first()
    if not db_product:
        raise HTTPException(404, "Product not found")
    
    # Delete related variants and stock using ORM
    variants = db.query(VariantORM).filter(VariantORM.product_id == product_id).all()
    for variant in variants:
        db.query(StockORM).filter(StockORM.variant_id == variant.id).delete()
        db.delete(variant)
    
    db.delete(db_product)
    db.commit()
    return {"message": "Product deleted successfully"}

@app.put("/api/v1/products/{product_id}/status")
async def update_product_status_v1(product_id: str, status_data: dict, db: Session = Depends(get_db)):
    """Update product status using ORM"""
    db_product = db.query(ProductORM).filter(ProductORM.id == product_id).first()
    if not db_product:
        raise HTTPException(404, "Product not found")
    
    new_status = status_data.get("status")
    if not new_status:
        raise HTTPException(400, "Status is required")
    
    # Validate status values
    valid_statuses = ["DRAFT", "PENDING_REVIEW", "PUBLISHED", "DISCONTINUED"]
    if new_status not in valid_statuses:
        raise HTTPException(400, f"Invalid status. Must be one of: {', '.join(valid_statuses)}")
    
    db_product.status = new_status
    db.commit()
    db.refresh(db_product)
    
    return {
        "id": str(db_product.id),
        "title": db_product.title,
        "status": db_product.status
    }

@app.get("/api/v1/products/{product_id}")
async def get_product_v1(product_id: str, db: Session = Depends(get_db)):
    """Get single product using ORM"""
    product = db.query(ProductORM).filter(ProductORM.id == product_id).first()
    if not product:
        raise HTTPException(404, "Product not found")
    
    return {
        "id": str(product.id),
        "title": product.title,
        "description": product.description,
        "status": product.status,
        "category_id": str(product.category_id) if product.category_id else None
    }

# Partners API
@app.get("/api/v1/partners")
async def get_partners_v1(db: Session = Depends(get_db)):
    """Get all partners using ORM"""
    try:
        partners = db.query(PartnerORM).all()
        return [{
            "id": str(partner.id),
            "name": partner.name,
            "code": partner.code,
            "email": partner.email,
            "phone": partner.phone,
            "address": partner.address,
            "is_active": partner.is_active
        } for partner in partners]
    except Exception as e:
        # Return empty list if partners table doesn't exist
        return []

@app.post("/api/v1/partners")
async def create_partner_v1(partner_data: dict, db: Session = Depends(get_db)):
    """Create new partner using ORM"""
    db_partner = PartnerORM(
        name=partner_data["name"],
        code=partner_data["code"],
        contact_email=partner_data.get("contact_email"),
        contact_phone=partner_data.get("contact_phone"),
        address=partner_data.get("address"),
        is_active=partner_data.get("is_active", True)
    )
    db.add(db_partner)
    db.commit()
    db.refresh(db_partner)
    
    return {
        "id": str(db_partner.id),
        "name": db_partner.name,
        "code": db_partner.code,
        "contact_email": db_partner.contact_email,
        "is_active": db_partner.is_active
    }

# Variants API
@app.post("/api/v1/products/{product_id}/variants")
async def create_variant_v1(product_id: str, variant_data: dict, db: Session = Depends(get_db)):
    """Create product variant using ORM"""
    # Check if product exists using ORM
    product = db.query(ProductORM).filter(ProductORM.id == product_id).first()
    if not product:
        raise HTTPException(404, "Product not found")
    
    db_variant = VariantORM(
        product_id=product_id,
        variant_name=variant_data.get("variant_name", "Default Variant"),
        color_code=variant_data["color_code"],
        color_name=variant_data["color_name"],
        range_details=variant_data.get("range_details", {}),
        sku_suffix=variant_data.get("sku_suffix", "001"),
        additional_images=variant_data.get("additional_images", []),
        is_active=variant_data.get("is_active", True),
        created_by=variant_data.get("created_by", "system"),
        material=variant_data.get("material"),
        pattern=variant_data.get("pattern")
    )
    db.add(db_variant)
    db.commit()
    db.refresh(db_variant)
    
    return {
        "id": str(db_variant.id),
        "product_id": str(db_variant.product_id),
        "variant_name": db_variant.variant_name,
        "color_code": db_variant.color_code,
        "color_name": db_variant.color_name,
        "material": db_variant.material,
        "pattern": db_variant.pattern,
        "is_active": db_variant.is_active
    }

@app.get("/api/v1/products/{product_id}/variants")
async def get_variants_v1(product_id: str, db: Session = Depends(get_db)):
    """Get product variants using ORM"""
    variants = db.query(VariantORM).filter(VariantORM.product_id == product_id).all()
    return [{
        "id": str(variant.id),
        "product_id": str(variant.product_id),
        "variant_name": variant.variant_name,
        "color_code": variant.color_code,
        "color_name": variant.color_name,
        "material": variant.material,
        "pattern": variant.pattern,
        "is_active": variant.is_active
    } for variant in variants]

@app.get("/api/v1/products/{product_id}/variants/{variant_id}")
async def get_variant_v1(product_id: str, variant_id: str, db: Session = Depends(get_db)):
    """Get single variant using ORM"""
    variant = db.query(VariantORM).filter(VariantORM.id == variant_id, VariantORM.product_id == product_id).first()
    if not variant:
        raise HTTPException(404, "Variant not found")
    
    return {
        "id": str(variant.id),
        "product_id": str(variant.product_id),
        "variant_name": variant.variant_name,
        "color_code": variant.color_code,
        "color_name": variant.color_name,
        "material": variant.material,
        "pattern": variant.pattern,
        "is_active": variant.is_active
    }

@app.put("/api/v1/products/{product_id}/variants/{variant_id}")
async def update_variant_v1(product_id: str, variant_id: str, variant_data: dict, db: Session = Depends(get_db)):
    """Update variant using ORM"""
    variant = db.query(VariantORM).filter(VariantORM.id == variant_id, VariantORM.product_id == product_id).first()
    if not variant:
        raise HTTPException(404, "Variant not found")
    
    for key, value in variant_data.items():
        if hasattr(variant, key):
            setattr(variant, key, value)
    
    db.commit()
    db.refresh(variant)
    
    return {
        "id": str(variant.id),
        "product_id": str(variant.product_id),
        "variant_name": variant.variant_name,
        "color_code": variant.color_code,
        "color_name": variant.color_name,
        "material": variant.material,
        "pattern": variant.pattern,
        "is_active": variant.is_active
    }

# Stock API
@app.post("/api/v1/products/{product_id}/variants/{variant_id}/stock")
async def create_stock_v1(product_id: str, variant_id: str, stock_data: dict, db: Session = Depends(get_db)):
    """Create stock record using ORM"""
    # Check if variant exists using ORM
    variant = db.query(VariantORM).filter(VariantORM.id == variant_id, VariantORM.product_id == product_id).first()
    if not variant:
        raise HTTPException(404, "Variant not found")
    
    db_stock = StockORM(
        product_id=product_id,
        variant_id=variant_id,
        partner_id=stock_data.get("partner_id"),
        quantity_available=stock_data.get("quantity_available", 0),
        quantity_reserved=stock_data.get("quantity_reserved", 0),
        reorder_level=stock_data.get("reorder_level", 0),
        reorder_quantity=stock_data.get("reorder_quantity", 0),
        retail_price=stock_data.get("retail_price", 0.00),
        wholesale_price=stock_data.get("wholesale_price", 0.00),
        currency=stock_data.get("currency", "INR"),
        partner_sku=stock_data.get("partner_sku")
    )
    db.add(db_stock)
    db.commit()
    db.refresh(db_stock)
    
    return {
        "id": str(db_stock.id),
        "variant_id": str(db_stock.variant_id),
        "partner_id": str(db_stock.partner_id) if db_stock.partner_id else None,
        "quantity_available": db_stock.quantity_available,
        "retail_price": float(db_stock.retail_price) if db_stock.retail_price else None,
        "wholesale_price": float(db_stock.wholesale_price) if db_stock.wholesale_price else None
    }

@app.get("/api/v1/products/{product_id}/variants/{variant_id}/stock")
async def get_stock_v1(product_id: str, variant_id: str, db: Session = Depends(get_db)):
    """Get stock records using ORM"""
    stocks = db.query(StockORM).filter(StockORM.variant_id == variant_id).all()
    return [{
        "id": str(stock.id),
        "variant_id": str(stock.variant_id),
        "partner_id": str(stock.partner_id) if stock.partner_id else None,
        "quantity_available": stock.quantity_available,
        "retail_price": float(stock.retail_price) if stock.retail_price else None,
        "wholesale_price": float(stock.wholesale_price) if stock.wholesale_price else None
    } for stock in stocks]

@app.put("/api/v1/products/{product_id}/variants/{variant_id}/stock/{stock_id}")
async def update_stock_v1(product_id: str, variant_id: str, stock_id: str, stock_data: dict, db: Session = Depends(get_db)):
    """Update stock record using ORM"""
    stock = db.query(StockORM).filter(
        StockORM.id == stock_id,
        StockORM.variant_id == variant_id,
        StockORM.product_id == product_id
    ).first()
    
    if not stock:
        raise HTTPException(404, "Stock record not found")
    
    for key, value in stock_data.items():
        if hasattr(stock, key):
            setattr(stock, key, value)
    
    db.commit()
    db.refresh(stock)
    
    return {
        "id": str(stock.id),
        "variant_id": str(stock.variant_id),
        "partner_id": str(stock.partner_id) if stock.partner_id else None,
        "quantity_available": stock.quantity_available,
        "retail_price": float(stock.retail_price) if stock.retail_price else None,
        "wholesale_price": float(stock.wholesale_price) if stock.wholesale_price else None
    }

@app.delete("/api/v1/products/{product_id}/variants/{variant_id}/stock/{stock_id}")
async def delete_stock_v1(product_id: str, variant_id: str, stock_id: str, db: Session = Depends(get_db)):
    """Delete stock record using ORM"""
    stock = db.query(StockORM).filter(
        StockORM.id == stock_id,
        StockORM.variant_id == variant_id,
        StockORM.product_id == product_id
    ).first()
    
    if not stock:
        raise HTTPException(404, "Stock record not found")
    
    db.delete(stock)
    db.commit()
    return {"message": "Stock record deleted successfully"}

# Health check endpoint
@app.get("/health")
async def health_check():
    """API health check"""
    return {"status": "healthy", "version": "2.0.0"}
