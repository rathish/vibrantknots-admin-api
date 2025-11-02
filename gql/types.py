import strawberry
from typing import Optional, List, Dict
from enum import Enum

@strawberry.enum
class ProductStatus(Enum):
    DRAFT = "draft"
    PENDING_REVIEW = "pending_review"
    PUBLISHED = "published"

@strawberry.type
class Category:
    id: str
    name: str
    description: Optional[str]

@strawberry.type
class Product:
    id: str
    sku_id: str
    title: str
    description: Optional[str]
    material: str
    pattern: str
    color_primary: str
    colors: strawberry.scalars.JSON
    width_estimate_cm: Optional[int]
    scale: str
    special_features: List[str]
    image_urls: strawberry.scalars.JSON
    created_by: str
    category_id: Optional[str]
    status: ProductStatus

@strawberry.input
class CategoryInput:
    name: str
    description: Optional[str] = None

@strawberry.input
class ProductInput:
    sku_id: str
    title: str
    description: Optional[str] = None
    material: str
    pattern: str
    color_primary: str
    colors: strawberry.scalars.JSON
    width_estimate_cm: Optional[int] = None
    scale: str
    special_features: List[str] = strawberry.field(default_factory=list)
    image_urls: strawberry.scalars.JSON = strawberry.field(default_factory=dict)
    created_by: str
    category_id: Optional[str] = None
    status: ProductStatus = ProductStatus.DRAFT
