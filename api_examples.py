#!/usr/bin/env python3
"""
Admin API Examples and Testing Script

This script demonstrates all API endpoints with practical examples.
Run this script to test the complete API functionality.
"""

import requests
import json
import time
from typing import Dict, Any

BASE_URL = "http://localhost:8000"

class AdminAPIClient:
    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url
        self.session = requests.Session()
        
    def _request(self, method: str, endpoint: str, **kwargs) -> Dict[Any, Any]:
        """Make HTTP request with error handling"""
        url = f"{self.base_url}{endpoint}"
        try:
            response = self.session.request(method, url, **kwargs)
            response.raise_for_status()
            return response.json() if response.content else {}
        except requests.exceptions.RequestException as e:
            print(f"❌ {method} {endpoint} failed: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Response: {e.response.text}")
            return {}
    
    def health_check(self):
        """Test health endpoint"""
        print("🔍 Testing Health Check...")
        result = self._request("GET", "/health")
        if result:
            print(f"✅ Health: {result}")
        return result
    
    def create_category(self, name: str, description: str = None) -> Dict[Any, Any]:
        """Create a new category"""
        print(f"📁 Creating category: {name}")
        data = {"name": name}
        if description:
            data["description"] = description
            
        result = self._request("POST", "/categories", json=data)
        if result:
            print(f"✅ Category created: {result['id']}")
        return result
    
    def get_categories(self):
        """Get all categories"""
        print("📁 Getting all categories...")
        result = self._request("GET", "/categories")
        if result:
            print(f"✅ Found {len(result)} categories")
        return result
    
    def create_partner(self, name: str, code: str, email: str = None) -> Dict[Any, Any]:
        """Create a new partner"""
        print(f"🤝 Creating partner: {name}")
        data = {
            "name": name,
            "code": code,
            "contact_email": email or f"contact@{code.lower()}.com",
            "contact_phone": "+1-555-0123",
            "address": f"123 {name} Street, Business City, BC 12345",
            "is_active": True
        }
        
        result = self._request("POST", "/api/v1/partners", json=data)
        if result:
            print(f"✅ Partner created: {result['id']}")
        return result
    
    def create_product(self, title: str, category_id: str = None, **kwargs) -> Dict[Any, Any]:
        """Create a new product"""
        print(f"📱 Creating product: {title}")
        data = {
            "title": title,
            "description": kwargs.get("description", f"High-quality {title}"),
            "sku_id": kwargs.get("sku_id", title.upper().replace(" ", "")),
            "special_features": kwargs.get("special_features", ["Premium Quality", "Latest Technology"]),
            "image_urls": kwargs.get("image_urls", {
                "main": f"https://example.com/{title.lower().replace(' ', '-')}-main.jpg",
                "gallery": f"https://example.com/{title.lower().replace(' ', '-')}-gallery.jpg"
            }),
            "created_by": "admin@company.com",
            "status": "ACTIVE"
        }
        
        if category_id:
            data["category_id"] = category_id
            
        result = self._request("POST", "/products", json=data)
        if result:
            print(f"✅ Product created: {result['id']}")
        return result
    
    def create_variant(self, product_id: str, color_code: str, color_name: str, **kwargs) -> Dict[Any, Any]:
        """Create a product variant"""
        print(f"🎨 Creating variant: {color_name} for product {product_id[:8]}...")
        data = {
            "color_code": color_code,
            "color_name": color_name,
            "size": kwargs.get("size", "Standard"),
            "material": kwargs.get("material", "Premium"),
            "weight": kwargs.get("weight", 150.0),
            "dimensions": kwargs.get("dimensions", {
                "length": 15.0,
                "width": 7.5,
                "height": 0.8
            })
        }
        
        result = self._request("POST", f"/api/v1/products/{product_id}/variants", json=data)
        if result:
            print(f"✅ Variant created: {result['id']}")
        return result
    
    def add_stock(self, product_id: str, variant_id: str, quantity: int, retail_price: float = None, partner_id: str = None) -> Dict[Any, Any]:
        """Add stock for a variant"""
        print(f"📦 Adding stock: {quantity} units for variant {variant_id[:8]}...")
        data = {
            "quantity_available": quantity,
            "retail_price": retail_price or 99.99,
            "wholesale_price": (retail_price or 99.99) * 0.8
        }
        
        if partner_id:
            data["partner_id"] = partner_id
            
        result = self._request("POST", f"/api/v1/products/{product_id}/variants/{variant_id}/stock", json=data)
        if result:
            print(f"✅ Stock added successfully")
        return result
    
    def get_product_list(self):
        """Get comprehensive product list"""
        print("📋 Getting product list with stock info...")
        result = self._request("GET", "/api/v1/products/list")
        if result:
            print(f"✅ Found {len(result)} products with stock info")
            for product in result[:3]:  # Show first 3
                print(f"  - {product['title']}: {product['total_stock']} units, ${product['min_retail_price']}")
        return result
    
    def get_variants_with_stock(self, product_id: str):
        """Get variants with stock information"""
        print(f"🎨 Getting variants with stock for product {product_id[:8]}...")
        result = self._request("GET", f"/api/v1/products/{product_id}/variants/with-stock")
        if result:
            print(f"✅ Found {len(result)} variants with stock")
        return result
    
    def enable_product(self, product_id: str):
        """Enable a product"""
        print(f"✅ Enabling product {product_id[:8]}...")
        result = self._request("PATCH", f"/api/v1/products/{product_id}/enable")
        if result:
            print(f"✅ Product enabled")
        return result
    
    def disable_product(self, product_id: str):
        """Disable a product"""
        print(f"❌ Disabling product {product_id[:8]}...")
        result = self._request("PATCH", f"/api/v1/products/{product_id}/disable")
        if result:
            print(f"✅ Product disabled")
        return result

def run_complete_demo():
    """Run complete API demonstration"""
    print("🚀 Starting Admin API Complete Demo")
    print("=" * 50)
    
    client = AdminAPIClient()
    
    # 1. Health Check
    health = client.health_check()
    if not health:
        print("❌ API is not healthy. Please check if the server is running.")
        return
    
    print("\n" + "=" * 50)
    
    # 2. Create Categories
    print("📁 CATEGORY MANAGEMENT")
    electronics = client.create_category("Electronics", "Electronic devices and accessories")
    clothing = client.create_category("Clothing", "Apparel and fashion items")
    
    categories = client.get_categories()
    
    print("\n" + "=" * 50)
    
    # 3. Create Partners
    print("🤝 PARTNER MANAGEMENT")
    partner1 = client.create_partner("TechCorp Solutions", "TECH001", "contact@techcorp.com")
    partner2 = client.create_partner("Fashion Hub", "FASH001", "info@fashionhub.com")
    
    print("\n" + "=" * 50)
    
    # 4. Create Products
    print("📱 PRODUCT MANAGEMENT")
    iphone = client.create_product(
        "iPhone 15 Pro",
        category_id=electronics.get("id") if electronics else None,
        description="Latest iPhone with advanced features",
        special_features=["Face ID", "Wireless Charging", "5G", "ProRAW Camera"],
        sku_id="IPH15PRO001"
    )
    
    tshirt = client.create_product(
        "Premium Cotton T-Shirt",
        category_id=clothing.get("id") if clothing else None,
        description="Comfortable premium cotton t-shirt",
        special_features=["100% Cotton", "Pre-shrunk", "Breathable"],
        sku_id="TSHIRT001"
    )
    
    print("\n" + "=" * 50)
    
    # 5. Create Variants
    print("🎨 VARIANT MANAGEMENT")
    variants = []
    
    if iphone:
        # iPhone variants
        black_variant = client.create_variant(
            iphone["id"], "#000000", "Space Black",
            size="128GB", material="Titanium", weight=187.0
        )
        white_variant = client.create_variant(
            iphone["id"], "#FFFFFF", "Silver",
            size="256GB", material="Titanium", weight=187.0
        )
        variants.extend([black_variant, white_variant])
    
    if tshirt:
        # T-shirt variants
        red_variant = client.create_variant(
            tshirt["id"], "#FF0000", "Red",
            size="L", material="Cotton", weight=200.0
        )
        blue_variant = client.create_variant(
            tshirt["id"], "#0000FF", "Blue",
            size="M", material="Cotton", weight=180.0
        )
        variants.extend([red_variant, blue_variant])
    
    print("\n" + "=" * 50)
    
    # 6. Add Stock
    print("📦 STOCK MANAGEMENT")
    for variant in variants:
        if variant:
            product_id = variant["product_id"]
            variant_id = variant["id"]
            
            # Add stock with different quantities and prices
            if "iPhone" in variant.get("product_id", ""):
                client.add_stock(product_id, variant_id, 50, 999.99, partner1.get("id"))
            else:
                client.add_stock(product_id, variant_id, 100, 29.99, partner2.get("id"))
    
    print("\n" + "=" * 50)
    
    # 7. Get Product List
    print("📋 INVENTORY OVERVIEW")
    product_list = client.get_product_list()
    
    print("\n" + "=" * 50)
    
    # 8. Get Variants with Stock
    print("🎨 VARIANT STOCK DETAILS")
    if iphone:
        client.get_variants_with_stock(iphone["id"])
    
    print("\n" + "=" * 50)
    
    # 9. Product Status Management
    print("⚙️ PRODUCT STATUS MANAGEMENT")
    if iphone:
        client.disable_product(iphone["id"])
        time.sleep(1)
        client.enable_product(iphone["id"])
    
    print("\n" + "=" * 50)
    print("🎉 Demo completed successfully!")
    print("\n📚 Check the API documentation at: http://localhost:8000/docs")
    print("🔍 Try GraphQL at: http://localhost:8000/graphql")

def run_quick_test():
    """Run quick API test"""
    print("⚡ Quick API Test")
    client = AdminAPIClient()
    
    # Test basic endpoints
    health = client.health_check()
    categories = client.get_categories()
    products = client.get_product_list()
    
    print(f"\n📊 Quick Stats:")
    print(f"  - API Status: {'✅ Healthy' if health else '❌ Unhealthy'}")
    print(f"  - Categories: {len(categories) if categories else 0}")
    print(f"  - Products: {len(products) if products else 0}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "quick":
        run_quick_test()
    else:
        run_complete_demo()
