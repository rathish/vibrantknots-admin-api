#!/bin/bash

# Admin API - Product Creation Examples
# Base URL for all API calls
BASE_URL="http://localhost:8000/api/v1"

echo "🚀 Admin API Product Creation Examples"
echo "======================================"

# 1. Create Category
echo "📁 Creating category..."
CATEGORY_RESPONSE=$(curl -s -X POST "$BASE_URL/categories" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Electronics",
    "description": "Electronic devices and accessories"
  }')

CATEGORY_ID=$(echo $CATEGORY_RESPONSE | grep -o '"id":"[^"]*"' | cut -d'"' -f4)
echo "✅ Category created: $CATEGORY_ID"

# 2. Create Partner
echo "🤝 Creating partner..."
PARTNER_RESPONSE=$(curl -s -X POST "$BASE_URL/partners" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "TechCorp Solutions",
    "code": "TECH001",
    "contact_email": "contact@techcorp.com",
    "contact_phone": "+1-555-0123",
    "address": "123 Tech Street, Silicon Valley, CA 94000",
    "is_active": true
  }')

PARTNER_ID=$(echo $PARTNER_RESPONSE | grep -o '"id":"[^"]*"' | cut -d'"' -f4)
echo "✅ Partner created: $PARTNER_ID"

# 3. Create Product
echo "📱 Creating product..."
PRODUCT_RESPONSE=$(curl -s -X POST "$BASE_URL/products" \
  -H "Content-Type: application/json" \
  -d "{
    \"title\": \"iPhone 15 Pro\",
    \"description\": \"Latest iPhone with advanced features\",
    \"sku_id\": \"IPH15PRO001\",
    \"special_features\": [\"Face ID\", \"Wireless Charging\", \"5G\"],
    \"image_urls\": {
      \"main\": \"https://example.com/iphone15-main.jpg\",
      \"gallery\": \"https://example.com/iphone15-gallery.jpg\"
    },
    \"created_by\": \"curl_user\",
    \"category_id\": \"$CATEGORY_ID\",
    \"status\": \"ACTIVE\"
  }")

PRODUCT_ID=$(echo $PRODUCT_RESPONSE | grep -o '"id":"[^"]*"' | cut -d'"' -f4)
echo "✅ Product created: $PRODUCT_ID"

# 4. Create Variant
echo "🎨 Creating variant..."
VARIANT_RESPONSE=$(curl -s -X POST "$BASE_URL/products/$PRODUCT_ID/variants" \
  -H "Content-Type: application/json" \
  -d '{
    "color_code": "#000000",
    "color_name": "Space Black",
    "size": "128GB",
    "material": "Titanium",
    "weight": 187.0,
    "dimensions": {
      "length": 159.9,
      "width": 76.7,
      "height": 8.25
    }
  }')

VARIANT_ID=$(echo $VARIANT_RESPONSE | grep -o '"id":"[^"]*"' | cut -d'"' -f4)
echo "✅ Variant created: $VARIANT_ID"

# 5. Add Stock
echo "📦 Adding stock..."
STOCK_RESPONSE=$(curl -s -X POST "$BASE_URL/products/$PRODUCT_ID/variants/$VARIANT_ID/stock" \
  -H "Content-Type: application/json" \
  -d "{
    \"quantity_available\": 100,
    \"retail_price\": 999.99,
    \"wholesale_price\": 899.99,
    \"partner_id\": \"$PARTNER_ID\"
  }")

echo "✅ Stock added successfully"

# 6. Get Product List
echo "📋 Getting product list..."
curl -s "$BASE_URL/products/list" | head -c 200
echo "..."

echo ""
echo "🎉 Complete product setup finished!"
echo "Product ID: $PRODUCT_ID"
echo "Variant ID: $VARIANT_ID"
echo ""
echo "📚 View API docs: http://localhost:8000/docs"
