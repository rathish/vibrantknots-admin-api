import strawberry
from typing import List, Optional
from sqlalchemy.orm import Session
from .types import Category as CategoryType, Product as ProductType, CategoryInput, ProductInput, ProductStatus as GQLProductStatus
from application.category_service import CategoryService
from application.product_service import ProductService
from adapters.database_category_repository import DatabaseCategoryRepository
from adapters.database_product_repository import DatabaseProductRepository
from adapters.database.config import SessionLocal
from domain.models import Category, Product, ProductStatus

def get_db():
    db = SessionLocal()
    try:
        return db
    finally:
        db.close()

def convert_product_to_gql(product: Product) -> ProductType:
    # Convert domain ProductStatus to GraphQL ProductStatus
    gql_status = GQLProductStatus.DRAFT
    if product.status == ProductStatus.PENDING_REVIEW:
        gql_status = GQLProductStatus.PENDING_REVIEW
    elif product.status == ProductStatus.PUBLISHED:
        gql_status = GQLProductStatus.PUBLISHED
    
    return ProductType(
        id=product.id,
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
        status=gql_status
    )

@strawberry.type
class Query:
    @strawberry.field
    def categories(self) -> List[CategoryType]:
        db = get_db()
        service = CategoryService(DatabaseCategoryRepository(db))
        categories = service.get_all_categories()
        return [CategoryType(id=c.id, name=c.name, description=c.description) for c in categories]
    
    @strawberry.field
    def category(self, id: str) -> Optional[CategoryType]:
        db = get_db()
        service = CategoryService(DatabaseCategoryRepository(db))
        category = service.get_category(id)
        if not category:
            return None
        return CategoryType(id=category.id, name=category.name, description=category.description)
    
    @strawberry.field
    def products(self) -> List[ProductType]:
        db = get_db()
        service = ProductService(DatabaseProductRepository(db))
        products = service.get_all_products()
        return [convert_product_to_gql(p) for p in products]
    
    @strawberry.field
    def product(self, id: str) -> Optional[ProductType]:
        db = get_db()
        service = ProductService(DatabaseProductRepository(db))
        product = service.get_product(id)
        if not product:
            return None
        return convert_product_to_gql(product)

@strawberry.type
class Mutation:
    @strawberry.mutation
    def create_category(self, input: CategoryInput) -> CategoryType:
        db = get_db()
        service = CategoryService(DatabaseCategoryRepository(db))
        category = service.create_category(input.name, input.description)
        return CategoryType(id=category.id, name=category.name, description=category.description)
    
    @strawberry.mutation
    def create_product(self, input: ProductInput) -> ProductType:
        db = get_db()
        service = ProductService(DatabaseProductRepository(db))
        
        # Convert GraphQL ProductStatus to domain ProductStatus
        domain_status = ProductStatus.DRAFT
        if input.status == GQLProductStatus.PENDING_REVIEW:
            domain_status = ProductStatus.PENDING_REVIEW
        elif input.status == GQLProductStatus.PUBLISHED:
            domain_status = ProductStatus.PUBLISHED
        
        product = Product(
            id=None,
            sku_id=input.sku_id,
            title=input.title,
            description=input.description,
            material=input.material,
            pattern=input.pattern,
            color_primary=input.color_primary,
            colors=input.colors,
            width_estimate_cm=input.width_estimate_cm,
            scale=input.scale,
            special_features=input.special_features,
            image_urls=input.image_urls,
            created_by=input.created_by,
            category_id=input.category_id,
            created_at=None,
            updated_at=None,
            status=domain_status
        )
        result = service.create_product(product)
        return convert_product_to_gql(result)
