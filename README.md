# VibrantKnots Admin API

FastAPI application with hexagonal architecture for comprehensive product and category management.

## 🏗️ Architecture

- **Hexagonal Architecture** - Clean separation of concerns with ports and adapters
- **100% ORM-based** - No raw SQL, all database operations through ORM
- **PostgreSQL** - Robust relational database with full ACID compliance
- **S3 Integration** - Scalable image storage
- **SQS Integration** - Event-driven processing for GenAI analysis

## 🚀 Features

- **Product Management** - Complete CRUD with variants, stock, and pricing
- **Category Management** - Hierarchical product organization
- **Partner Management** - Business partner relationships
- **Stock Management** - Multi-variant, multi-partner inventory tracking
- **Image Management** - S3-based product image handling
- **Status Management** - Product lifecycle control (Draft → Active → Discontinued)
- **GraphQL API** - Flexible query interface
- **REST API** - Comprehensive RESTful endpoints

## 🐳 Docker Setup

### Quick Start

```bash
# Start all services
docker compose up -d

# View application logs
docker compose logs -f app

# View database logs
docker compose logs -f db

# Stop all services
docker compose down
```

### Configuration

Update `.env.docker` with your AWS credentials:

```bash
S3_BUCKET_NAME=your-actual-bucket
SQS_QUEUE_URL=https://sqs.region.amazonaws.com/account/queue
SQS_ANALYSIS_QUEUE_URL=https://sqs.region.amazonaws.com/account/analysis-queue
AWS_ACCESS_KEY_ID=your-key
AWS_SECRET_ACCESS_KEY=your-secret
```

## 📡 API Endpoints

### Base URLs
- **REST API**: http://localhost:8000
- **GraphQL**: http://localhost:8000/graphql
- **API Documentation**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Core Endpoints

#### Health & Status
- `GET /health` - API health check

#### Categories
- `POST /categories` - Create category
- `GET /categories` - List all categories
- `PUT /categories/{id}` - Update category
- `DELETE /categories/{id}` - Delete category

#### Partners
- `POST /api/v1/partners` - Create partner
- `GET /api/v1/partners` - List partners
- `GET /api/v1/partners/{id}` - Get partner details
- `PUT /api/v1/partners/{id}` - Update partner

#### Products
- `POST /products` - Create product
- `GET /products` - List products (basic)
- `GET /api/v1/products/list` - **Enhanced product list with stock/pricing**
- `GET /products/{id}` - Get product details
- `PUT /products/{id}` - Update product
- `DELETE /products/{id}` - Delete product

#### Product Variants
- `POST /api/v1/products/{id}/variants` - Create variant
- `GET /api/v1/products/{id}/variants` - List variants
- `GET /api/v1/products/{id}/variants/with-stock` - **Variants with stock info**
- `GET /api/v1/products/{id}/variants/{variant_id}` - Get variant
- `PUT /api/v1/products/{id}/variants/{variant_id}` - Update variant
- `DELETE /api/v1/products/{id}/variants/{variant_id}` - Delete variant

#### Stock Management
- `POST /api/v1/products/{id}/variants/{variant_id}/stock` - Add stock
- `GET /api/v1/products/{id}/variants/{variant_id}/stock` - Get stock records
- `PUT /api/v1/products/{id}/variants/{variant_id}/stock/{stock_id}` - Update stock
- `DELETE /api/v1/products/{id}/variants/{variant_id}/stock/{stock_id}` - Delete stock

#### Product Status
- `PATCH /api/v1/products/{id}/enable` - Enable product
- `PATCH /api/v1/products/{id}/disable` - Disable product
- `PATCH /api/v1/products/{id}/discontinue` - Discontinue product
- `PATCH /api/v1/products/{id}/status` - Update status

## 📋 Usage Examples

### 1. Complete Product Setup Flow

```bash
# 1. Create category
curl -X POST "http://localhost:8000/categories" \
  -H "Content-Type: application/json" \
  -d '{"name": "Electronics", "description": "Electronic devices"}'

# 2. Create partner
curl -X POST "http://localhost:8000/api/v1/partners" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "TechCorp Solutions",
    "code": "TECH001",
    "contact_email": "contact@techcorp.com",
    "is_active": true
  }'

# 3. Create product
curl -X POST "http://localhost:8000/products" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "iPhone 15 Pro",
    "description": "Latest iPhone with advanced features",
    "category_id": "CATEGORY_ID",
    "status": "ACTIVE"
  }'

# 4. Create variant
curl -X POST "http://localhost:8000/api/v1/products/PRODUCT_ID/variants" \
  -H "Content-Type: application/json" \
  -d '{
    "color_code": "#000000",
    "color_name": "Space Black",
    "size": "128GB",
    "material": "Titanium"
  }'

# 5. Add stock
curl -X POST "http://localhost:8000/api/v1/products/PRODUCT_ID/variants/VARIANT_ID/stock" \
  -H "Content-Type: application/json" \
  -d '{
    "quantity_available": 100,
    "retail_price": 999.99,
    "wholesale_price": 899.99,
    "partner_id": "PARTNER_ID"
  }'
```

### 2. Inventory Management

```bash
# Get comprehensive product list with stock
curl "http://localhost:8000/api/v1/products/list"

# Get variants with stock for specific product
curl "http://localhost:8000/api/v1/products/PRODUCT_ID/variants/with-stock"

# Update stock quantity
curl -X PUT "http://localhost:8000/api/v1/products/PRODUCT_ID/variants/VARIANT_ID/stock/STOCK_ID" \
  -H "Content-Type: application/json" \
  -d '{"quantity_available": 75}'
```

### 3. Product Status Management

```bash
# Enable product
curl -X PATCH "http://localhost:8000/api/v1/products/PRODUCT_ID/enable"

# Disable product
curl -X PATCH "http://localhost:8000/api/v1/products/PRODUCT_ID/disable"

# Discontinue with reason
curl -X PATCH "http://localhost:8000/api/v1/products/PRODUCT_ID/discontinue?reason=end-of-life"
```

## 🧪 Testing & Examples

### Interactive Testing

1. **Swagger UI**: Visit http://localhost:8000/docs for interactive API testing
2. **GraphQL Playground**: Visit http://localhost:8000/graphql for GraphQL queries
3. **ReDoc**: Visit http://localhost:8000/redoc for alternative documentation

### Automated Testing

```bash
# Run comprehensive API demo
python3 api_examples.py

# Run quick API test
python3 api_examples.py quick

# Run unit tests with coverage
docker compose exec app pytest --cov=. --cov-report=term-missing

# Run specific test file
docker compose exec app pytest tests/test_products.py -v
```

## 🗄️ Database

### Connection Details
- **Host**: localhost:5433 (mapped from container port 5432)
- **Database**: admin_api
- **User**: admin
- **Password**: password

### Schema Overview

```
categories
├── id (UUID, PK)
├── name (VARCHAR)
└── description (TEXT)

products
├── id (UUID, PK)
├── title (VARCHAR)
├── description (TEXT)
├── category_id (UUID, FK → categories.id)
├── status (ENUM: DRAFT, ACTIVE, INACTIVE, DISCONTINUED)
└── timestamps

product_variants
├── id (UUID, PK)
├── product_id (UUID, FK → products.id)
├── color_code (VARCHAR)
├── color_name (VARCHAR)
├── size (VARCHAR)
├── material (VARCHAR)
└── dimensions (JSONB)

stock
├── id (UUID, PK)
├── variant_id (UUID, FK → product_variants.id)
├── partner_id (UUID, FK → partners.id)
├── quantity_available (INTEGER)
├── retail_price (DECIMAL)
└── wholesale_price (DECIMAL)

partners
├── id (UUID, PK)
├── name (VARCHAR)
├── code (VARCHAR, UNIQUE)
├── contact_email (VARCHAR)
└── is_active (BOOLEAN)
```

## 📊 Sample Data

The API includes comprehensive sample data for testing:

```bash
# Add sample data
python3 add_comprehensive_dummy_data.py

# View data summary
python3 show_dummy_data_summary.py
```

## 🔍 Key Features

### Enhanced Product List Endpoint
`GET /api/v1/products/list` provides:
- Product basic information
- Category names
- Total stock across variants
- Minimum retail/wholesale prices
- Available variant colors
- Product images

### Variants with Stock
`GET /api/v1/products/{id}/variants/with-stock` provides:
- Complete variant details
- Associated stock records
- Partner information
- Pricing data

### Comprehensive Status Management
- Enable/disable products
- Discontinue with reasons
- Status transitions with validation

## 🏛️ Architecture Principles

### Hexagonal Architecture
```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Adapters      │    │   Application    │    │     Domain      │
│                 │    │                  │    │                 │
│ • REST API      │◄──►│ • Services       │◄──►│ • Entities      │
│ • Database      │    │ • Use Cases      │    │ • Value Objects │
│ • S3 Storage    │    │ • Ports          │    │ • Business Logic│
│ • SQS Queue     │    │                  │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

### ORM-Only Database Access
- No raw SQL queries
- All operations through SQLAlchemy ORM
- Type-safe database interactions
- Automatic relationship handling

## 🚀 Development

### Local Development
```bash
# Install dependencies
pip install -r requirements.txt

# Run development server
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Run tests
pytest --cov=. --cov-report=html
```

### Code Quality
```bash
# Format code
black .

# Lint code
flake8 .

# Type checking
mypy .
```

## 🤝 Contributing

1. Follow hexagonal architecture principles
2. Maintain comprehensive test coverage
3. Use ORM-only database access
4. Add comprehensive API documentation
5. Include usage examples

## 📄 License

MIT License - see LICENSE file for details.
