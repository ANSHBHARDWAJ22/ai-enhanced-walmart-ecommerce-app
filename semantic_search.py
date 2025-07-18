from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from dotenv import load_dotenv
import re

load_dotenv()

# Load FAISS index and embedding model only once
embedding = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
vectorstore = FAISS.load_local(
    "faiss_product_index", 
    embeddings=embedding,
    allow_dangerous_deserialization=True  # ✅ use only if you trust the .pkl file
)

def semantic_search_products(query, filters=None, k=20):
    """
    Perform semantic search with optional filters on product metadata.
    
    Args:
        query (str): User search query.
        filters (dict): Dictionary with optional filters like 'brand', 'category', 'min_price', 'max_price'.
        k (int): Number of top results to retrieve from FAISS (increased for better filtering).
    
    Returns:
        list of product metadata dictionaries.
    """
    filters = filters or {}
    
    try:
        # Retrieve similar documents using FAISS with higher k for better filtering
        retrieved_docs = vectorstore.similarity_search(query, k=k)
        all_products = [doc.metadata for doc in retrieved_docs]
        
        def matches_filters(product):
            # Category filter - more flexible matching
            if filters.get('category'):
                filter_category = filters['category'].lower().strip()
                product_category = product.get('category_name', '').lower().strip()
                
                # Check if filter category is contained in product category or vice versa
                if filter_category and not (filter_category in product_category or product_category in filter_category):
                    return False
            
            # Brand filter - exact match but case insensitive
            if filters.get('brand'):
                filter_brand = filters['brand'].lower().strip()
                product_brand = product.get('brand', '').lower().strip()
                
                if filter_brand and filter_brand != product_brand:
                    return False
            
            # Price filters
            try:
                price = float(product.get('final_price', 0))
                
                if filters.get('min_price'):
                    min_price = float(filters['min_price'])
                    if price < min_price:
                        return False
                
                if filters.get('max_price'):
                    max_price = float(filters['max_price'])
                    if price > max_price:
                        return False
                        
            except (ValueError, TypeError):
                # If price conversion fails, don't filter by price
                pass
            
            return True
        
        # Filter products based on criteria
        filtered_products = list(filter(matches_filters, all_products))
        
        # Remove duplicates based on product_id
        seen_ids = set()
        unique_products = []
        for product in filtered_products:
            product_id = product.get('product_id', str(product.get('_id', '')))
            if product_id not in seen_ids:
                seen_ids.add(product_id)
                unique_products.append(product)
        
        return unique_products
        
    except Exception as e:
        print(f"Error in semantic_search_products: {e}")
        return []

def enhanced_semantic_search(query, category_filter=None, max_results=10):
    """
    Enhanced semantic search with better category filtering and diverse results.
    
    Args:
        query (str): Search query
        category_filter (str): Optional category to filter by
        max_results (int): Maximum number of results to return
    
    Returns:
        list of product metadata dictionaries
    """
    try:
        # Start with a higher k to get more diverse results
        k = min(max_results * 3, 50)  # Get 3x more results than needed for better filtering
        
        # Enhance query with category if provided
        enhanced_query = query
        if category_filter:
            enhanced_query = f"{query} {category_filter}"
        
        # Perform semantic search
        retrieved_docs = vectorstore.similarity_search(enhanced_query, k=k)
        all_products = [doc.metadata for doc in retrieved_docs]
        
        # Filter by category if specified
        if category_filter:
            category_lower = category_filter.lower().strip()
            filtered_products = []
            for product in all_products:
                product_category = product.get('category_name', '').lower().strip()
                if category_lower in product_category or product_category in category_lower:
                    filtered_products.append(product)
            all_products = filtered_products
        
        # Remove duplicates and ensure required fields
        seen_ids = set()
        unique_products = []
        for product in all_products:
            product_id = product.get('product_id', str(product.get('_id', '')))
            if product_id not in seen_ids:
                seen_ids.add(product_id)
                
                # Ensure required fields exist
                product['product_id'] = product_id
                product['product_name'] = product.get('product_name', 'Unnamed Product')
                product['main_image'] = product.get('main_image', 'https://via.placeholder.com/300x300.png?text=No+Image')
                product['final_price'] = product.get('final_price', 0.0)
                product['unit_price'] = product.get('unit_price', 0.0)
                product['rating'] = product.get('rating', 0)
                product['review_count'] = product.get('review_count', 0)
                product['category_name'] = product.get('category_name', 'Unknown')
                product['brand'] = product.get('brand', 'Unknown')
                
                unique_products.append(product)
        
        # Return up to max_results
        return unique_products[:max_results]
        
    except Exception as e:
        print(f"Error in enhanced_semantic_search: {e}")
        return []

def get_diverse_products_by_category(categories, query, products_per_category=6):
    """
    Get diverse products for multiple categories with a single query.
    
    Args:
        categories (list): List of category names
        query (str): Search query
        products_per_category (int): Number of products per category
    
    Returns:
        dict: Dictionary with category as key and list of products as value
    """
    try:
        # Get a large set of results
        k = len(categories) * products_per_category * 3  # 3x buffer for better diversity
        retrieved_docs = vectorstore.similarity_search(query, k=k)
        all_products = [doc.metadata for doc in retrieved_docs]
        
        # Organize products by category
        category_products = {}
        for category in categories:
            category_products[category] = []
        
        # Distribute products to categories
        for product in all_products:
            product_category = product.get('category_name', '').lower().strip()
            
            # Find matching category
            for target_category in categories:
                target_lower = target_category.lower().strip()
                if (target_lower in product_category or 
                    product_category in target_lower or
                    any(word in product_category for word in target_lower.split())):
                    
                    if len(category_products[target_category]) < products_per_category:
                        # Ensure required fields
                        product['product_id'] = product.get('product_id', str(product.get('_id', '')))
                        product['product_name'] = product.get('product_name', 'Unnamed Product')
                        product['main_image'] = product.get('main_image', 'https://via.placeholder.com/300x300.png?text=No+Image')
                        product['final_price'] = product.get('final_price', 0.0)
                        product['unit_price'] = product.get('unit_price', 0.0)
                        product['rating'] = product.get('rating', 0)
                        product['review_count'] = product.get('review_count', 0)
                        
                        category_products[target_category].append(product)
                        break
        
        return category_products
        
    except Exception as e:
        print(f"Error in get_diverse_products_by_category: {e}")
        return {category: [] for category in categories}