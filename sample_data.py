#!/usr/bin/env python3
"""
Sample data insertion script for Walmart Clone
Run this script to populate your MongoDB database with sample products
"""

from pymongo import MongoClient
from urllib.parse import quote_plus
from datetime import datetime
import random

# MongoDB connection
username = quote_plus("soni3anuj")
password = quote_plus("Anuj")
uri = f"mongodb+srv://{username}:{password}@cluster0.y8s8phx.mongodb.net/walmart_clone?retryWrites=true&w=majority&appName=Cluster0"

client = MongoClient(uri)
db = client.walmart_clone

# Sample products data
sample_products = [
    {
        "product_id": 1,
        "product_name": "Apple iPhone 14 Pro 128GB - Deep Purple",
        "final_price": 999.99,
        "unit_price": 1099.99,
        "rating": 4.8,
        "review_count": 2547,
        "brand": "Apple",
        "category_name": "Electronics",
        "main_image": "https://images.pexels.com/photos/788946/pexels-photo-788946.jpeg?auto=compress&cs=tinysrgb&w=400",
        "description": "Experience the iPhone 14 Pro with its Always-On display, 48MP Main camera, and A16 Bionic chip.",
        "available_for_delivery": True,
        "available_for_pickup": True,
        "seller": "Walmart",
        "categories": ["Electronics", "Cell Phones"],
        "tags": ["smartphone", "apple", "ios"],
        "sku": 12345,
        "upc": 123456789012,
        "currency": "USD"
    },
    {
        "product_id": 2,
        "product_name": "Samsung 65\" Class 4K UHD Smart TV",
        "final_price": 549.99,
        "unit_price": 699.99,
        "rating": 4.5,
        "review_count": 1823,
        "brand": "Samsung",
        "category_name": "Electronics",
        "main_image": "https://images.pexels.com/photos/1201996/pexels-photo-1201996.jpeg?auto=compress&cs=tinysrgb&w=400",
        "description": "Immerse yourself in stunning 4K resolution with this Samsung Smart TV featuring HDR and built-in streaming apps.",
        "available_for_delivery": True,
        "available_for_pickup": True,
        "seller": "Walmart",
        "categories": ["Electronics", "TVs"],
        "tags": ["tv", "samsung", "4k", "smart"],
        "sku": 12346,
        "upc": 123456789013,
        "currency": "USD"
    },
    {
        "product_id": 3,
        "product_name": "Nike Air Max 270 Men's Shoes",
        "final_price": 149.99,
        "unit_price": 180.00,
        "rating": 4.6,
        "review_count": 892,
        "brand": "Nike",
        "category_name": "Fashion",
        "main_image": "https://images.pexels.com/photos/1464625/pexels-photo-1464625.jpeg?auto=compress&cs=tinysrgb&w=400",
        "description": "Step into comfort with Nike's Air Max 270 featuring the largest heel Air unit yet for all-day comfort.",
        "available_for_delivery": True,
        "available_for_pickup": True,
        "seller": "Nike",
        "categories": ["Fashion", "Shoes", "Men"],
        "tags": ["shoes", "nike", "air max", "men"],
        "sku": 12347,
        "upc": 123456789014,
        "currency": "USD"
    },
    {
        "product_id": 4,
        "product_name": "KitchenAid Stand Mixer - Empire Red",
        "final_price": 379.99,
        "unit_price": 449.99,
        "rating": 4.9,
        "review_count": 3245,
        "brand": "KitchenAid",
        "category_name": "Home & Kitchen",
        "main_image": "https://images.pexels.com/photos/4686967/pexels-photo-4686967.jpeg?auto=compress&cs=tinysrgb&w=400",
        "description": "The iconic KitchenAid Stand Mixer with 10 speeds and multiple attachments for all your baking needs.",
        "available_for_delivery": True,
        "available_for_pickup": True,
        "seller": "KitchenAid",
        "categories": ["Home & Kitchen", "Appliances"],
        "tags": ["kitchen", "mixer", "baking", "appliance"],
        "sku": 12348,
        "upc": 123456789015,
        "currency": "USD"
    },
    {
        "product_id": 5,
        "product_name": "Levi's 501 Original Fit Men's Jeans",
        "final_price": 59.99,
        "unit_price": 79.99,
        "rating": 4.4,
        "review_count": 1567,
        "brand": "Levi's",
        "category_name": "Fashion",
        "main_image": "https://images.pexels.com/photos/1598507/pexels-photo-1598507.jpeg?auto=compress&cs=tinysrgb&w=400",
        "description": "The original blue jean since 1873. A classic straight fit with a timeless look.",
        "available_for_delivery": True,
        "available_for_pickup": True,
        "seller": "Levi's",
        "categories": ["Fashion", "Clothing", "Men"],
        "tags": ["jeans", "levis", "denim", "men"],
        "sku": 12349,
        "upc": 123456789016,
        "currency": "USD"
    },
    {
        "product_id": 6,
        "product_name": "Sony WH-1000XM4 Wireless Noise Canceling Headphones",
        "final_price": 279.99,
        "unit_price": 349.99,
        "rating": 4.7,
        "review_count": 2156,
        "brand": "Sony",
        "category_name": "Electronics",
        "main_image": "https://images.pexels.com/photos/3394650/pexels-photo-3394650.jpeg?auto=compress&cs=tinysrgb&w=400",
        "description": "Industry-leading noise canceling with Dual Noise Sensor technology and up to 30-hour battery life.",
        "available_for_delivery": True,
        "available_for_pickup": True,
        "seller": "Sony",
        "categories": ["Electronics", "Audio", "Headphones"],
        "tags": ["headphones", "sony", "wireless", "noise canceling"],
        "sku": 12350,
        "upc": 123456789017,
        "currency": "USD"
    },
    {
        "product_id": 7,
        "product_name": "Instant Pot Duo 7-in-1 Electric Pressure Cooker",
        "final_price": 89.99,
        "unit_price": 119.99,
        "rating": 4.6,
        "review_count": 4532,
        "brand": "Instant Pot",
        "category_name": "Home & Kitchen",
        "main_image": "https://images.pexels.com/photos/4686967/pexels-photo-4686967.jpeg?auto=compress&cs=tinysrgb&w=400",
        "description": "7 appliances in 1: pressure cooker, slow cooker, rice cooker, steamer, sauté pan, yogurt maker, and warmer.",
        "available_for_delivery": True,
        "available_for_pickup": True,
        "seller": "Instant Pot",
        "categories": ["Home & Kitchen", "Appliances"],
        "tags": ["pressure cooker", "instant pot", "kitchen", "appliance"],
        "sku": 12351,
        "upc": 123456789018,
        "currency": "USD"
    },
    {
        "product_id": 8,
        "product_name": "Adidas Ultraboost 22 Running Shoes",
        "final_price": 189.99,
        "unit_price": 220.00,
        "rating": 4.5,
        "review_count": 1234,
        "brand": "Adidas",
        "category_name": "Sports & Outdoors",
        "main_image": "https://images.pexels.com/photos/1464625/pexels-photo-1464625.jpeg?auto=compress&cs=tinysrgb&w=400",
        "description": "Experience endless energy return with these running shoes featuring BOOST midsole technology.",
        "available_for_delivery": True,
        "available_for_pickup": True,
        "seller": "Adidas",
        "categories": ["Sports & Outdoors", "Shoes", "Running"],
        "tags": ["running shoes", "adidas", "ultraboost", "sports"],
        "sku": 12352,
        "upc": 123456789019,
        "currency": "USD"
    },
    {
        "product_id": 9,
        "product_name": "Nintendo Switch OLED Model",
        "final_price": 349.99,
        "unit_price": 349.99,
        "rating": 4.8,
        "review_count": 3421,
        "brand": "Nintendo",
        "category_name": "Electronics",
        "main_image": "https://images.pexels.com/photos/442576/pexels-photo-442576.jpeg?auto=compress&cs=tinysrgb&w=400",
        "description": "Nintendo Switch with a vibrant 7-inch OLED screen for handheld and docked gaming modes.",
        "available_for_delivery": True,
        "available_for_pickup": True,
        "seller": "Nintendo",
        "categories": ["Electronics", "Gaming", "Consoles"],
        "tags": ["nintendo", "switch", "gaming", "console"],
        "sku": 12353,
        "upc": 123456789020,
        "currency": "USD"
    },
    {
        "product_id": 10,
        "product_name": "Dyson V15 Detect Cordless Vacuum",
        "final_price": 749.99,
        "unit_price": 849.99,
        "rating": 4.7,
        "review_count": 1876,
        "brand": "Dyson",
        "category_name": "Home & Garden",
        "main_image": "https://images.pexels.com/photos/4686967/pexels-photo-4686967.jpeg?auto=compress&cs=tinysrgb&w=400",
        "description": "Powerful cordless vacuum with laser dust detection and intelligent suction adjustment.",
        "available_for_delivery": True,
        "available_for_pickup": True,
        "seller": "Dyson",
        "categories": ["Home & Garden", "Cleaning", "Vacuums"],
        "tags": ["vacuum", "dyson", "cordless", "cleaning"],
        "sku": 12354,
        "upc": 123456789021,
        "currency": "USD"
    }
]

def insert_sample_data():
    """Insert sample data into MongoDB collections"""
    
    print("Connecting to MongoDB...")
    
    try:
        # Test connection
        client.admin.command('ping')
        print("Successfully connected to MongoDB!")
        
        # Clear existing products
        print("Clearing existing products...")
        db.products.delete_many({})
        
        # Insert sample products
        print("Inserting sample products...")
        result = db.products.insert_many(sample_products)
        print(f"Inserted {len(result.inserted_ids)} products")
        
        # Create indexes for better performance
        print("Creating indexes...")
        db.products.create_index("product_id", unique=True)
        db.products.create_index("product_name")
        db.products.create_index("category_name")
        db.products.create_index("brand")
        db.products.create_index("final_price")
        db.products.create_index("rating")
        
        # Create indexes for other collections
        db.users.create_index("email", unique=True)
        db.users.create_index("username", unique=True)
        db.cart.create_index([("user_id", 1), ("product_id", 1)])
        db.wishlist.create_index([("user_id", 1), ("product_id", 1)])
        db.sessions.create_index("session_id", unique=True)
        db.sessions.create_index("user_id")
        db.viewed_products.create_index([("user_id", 1), ("viewed_at", -1)])
        
        print("Sample data insertion completed successfully!")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    insert_sample_data()