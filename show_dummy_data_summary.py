#!/usr/bin/env python3
"""
Display summary of all dummy variant, stock and price data
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def show_dummy_data_summary():
    """Display comprehensive summary of dummy data"""
    
    print("🏪 VARIANT, STOCK & PRICING DUMMY DATA SUMMARY")
    print("=" * 60)
    
    # Get all products
    response = requests.get(f"{BASE_URL}/products")
    if response.status_code != 200:
        print("❌ Failed to fetch products")
        return
    
    products = response.json()
    
    # Filter for our dummy products
    dummy_products = [p for p in products if p["sku_id"] in ["COT-001", "SLK-001", "LIN-001"]]
    
    total_variants = 0
    total_stock_records = 0
    total_inventory = 0
    
    for product in dummy_products:
        print(f"\n📦 {product['title']}")
        print(f"   SKU: {product['sku_id']} | Material: {product['material']}")
        
        # Get variants with stock
        response = requests.get(f"{BASE_URL}/api/v1/products/{product['id']}/variants/with-stock")
        if response.status_code != 200:
            print("   ❌ Failed to fetch variants")
            continue
            
        variants = response.json()
        total_variants += len(variants)
        
        for variant in variants:
            print(f"\n   🎨 {variant['color_name']} ({variant['color_code']})")
            print(f"      SKU Suffix: {variant['sku_suffix']}")
            
            variant_total_stock = 0
            for stock in variant['stock_records']:
                total_stock_records += 1
                variant_total_stock += stock['available_quantity']
                total_inventory += stock['available_quantity']
                
                print(f"      📊 Partner {stock['partner_id'][:8]}...")
                print(f"         Stock: {stock['available_quantity']} units")
                print(f"         Retail: ₹{stock['retail_price']} | Wholesale: ₹{stock['wholesale_price']}")
            
            print(f"      📈 Total Stock: {variant_total_stock} units")
    
    # Get categories and partners count
    categories_response = requests.get(f"{BASE_URL}/categories")
    partners_response = requests.get(f"{BASE_URL}/partners")
    
    categories_count = len(categories_response.json()) if categories_response.status_code == 200 else 0
    partners_count = len(partners_response.json()) if partners_response.status_code == 200 else 0
    
    print(f"\n" + "=" * 60)
    print(f"📊 SUMMARY STATISTICS")
    print(f"=" * 60)
    print(f"🏷️  Categories: {categories_count}")
    print(f"🤝 Partners: {partners_count}")
    print(f"📦 Products (Dummy): {len(dummy_products)}")
    print(f"🎨 Variants: {total_variants}")
    print(f"📊 Stock Records: {total_stock_records}")
    print(f"📈 Total Inventory: {total_inventory:,} units")
    
    # Calculate pricing ranges
    all_retail_prices = []
    all_wholesale_prices = []
    
    for product in dummy_products:
        response = requests.get(f"{BASE_URL}/api/v1/products/{product['id']}/variants/with-stock")
        if response.status_code == 200:
            variants = response.json()
            for variant in variants:
                for stock in variant['stock_records']:
                    all_retail_prices.append(stock['retail_price'])
                    all_wholesale_prices.append(stock['wholesale_price'])
    
    if all_retail_prices:
        print(f"💰 Price Range:")
        print(f"   Retail: ₹{min(all_retail_prices):.2f} - ₹{max(all_retail_prices):.2f}")
        print(f"   Wholesale: ₹{min(all_wholesale_prices):.2f} - ₹{max(all_wholesale_prices):.2f}")
    
    print(f"\n🎯 API ENDPOINTS TO TEST:")
    print(f"   GET /products - List all products")
    print(f"   GET /categories - List all categories") 
    print(f"   GET /partners - List all partners")
    for product in dummy_products:
        print(f"   GET /api/v1/products/{product['id']}/variants/with-stock")
    
    print(f"\n✅ Dummy data is ready for testing!")

if __name__ == "__main__":
    show_dummy_data_summary()
