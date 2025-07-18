from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_pymongo import PyMongo
from werkzeug.security import generate_password_hash, check_password_hash
from bson.objectid import ObjectId
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
from urllib.parse import quote_plus
import uuid
import math
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.documents import Document
from semantic_search import semantic_search_products


llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",  
    google_api_key="AIzaSyCs5Gq_RHzbMNqalfyDpLTNfxqK9hPq9z4",  # ✅ paste your key here
    temperature=0.2
)

load_dotenv()

app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-here')

# MongoDB connection
username = quote_plus("soni3anuj")
password = quote_plus("Anuj")
uri = f"mongodb+srv://{username}:{password}@cluster0.y8s8phx.mongodb.net/walmart_clone?retryWrites=true&w=majority&appName=Cluster0"
app.config['MONGO_URI'] = uri

mongo = PyMongo(app)



######

# Helper functions
def is_logged_in():
    return 'user_id' in session

def get_current_user():
    if is_logged_in():
        return mongo.db.users.find_one({'_id': ObjectId(session['user_id'])})
    return None

def create_session(user_id):
    session_id = str(uuid.uuid4())
    session_data = {
        'session_id': session_id,
        'user_id': str(user_id),
        'created_at': datetime.utcnow(),
        'last_accessed': datetime.utcnow(),
        'expires_at': datetime.utcnow() + timedelta(days=30),
        'is_active': True
    }
    mongo.db.sessions.insert_one(session_data)
    session['session_id'] = session_id
    session['user_id'] = str(user_id)

# Routes
@app.route('/')
def index():
    # Get featured products
    featured_products = list(mongo.db.products.aggregate([
        {"$sample": {"size": 8}}
    ]))
    
    # Get categories
    categories = mongo.db.products.distinct('category_name')
    
    return render_template('index.html', 
                         featured_products=featured_products,
                         categories=categories,
                         user=get_current_user())

@app.route('/products')
def products():
    page = int(request.args.get('page', 1))
    per_page = 12
    search = request.args.get('search', '').strip()
    category = request.args.get('category', '').strip()
    brand = request.args.get('brand', '').strip()
    min_price = request.args.get('min_price', '')
    max_price = request.args.get('max_price', '')
    sort_by = request.args.get('sort', 'relevance')

    filters = {
        "brand": brand,
        "category": category,
        "min_price": min_price,
        "max_price": max_price
    }

    if search:
        filtered_products = semantic_search_products(search, filters)
    else:
        # fallback to MongoDB query
        mongo_query = {}
        if category:
            mongo_query['category_name'] = {'$regex': category, '$options': 'i'}
        if brand:
            mongo_query['brand'] = brand
        if min_price:
            mongo_query['final_price'] = {'$gte': float(min_price)}
        if max_price:
            mongo_query['final_price'] = mongo_query.get('final_price', {})
            mongo_query['final_price']['$lte'] = float(max_price)
        filtered_products = list(mongo.db.products.find(mongo_query))

    # Sorting
    sort_options = {
        'price_low': lambda x: x.get('final_price', 0),
        'price_high': lambda x: -x.get('final_price', 0),
        'rating': lambda x: -x.get('rating', 0),
        'name': lambda x: x.get('product_name', '').lower()
    }
    if sort_by in sort_options:
        filtered_products.sort(key=sort_options[sort_by])

    # Pagination
    total_products = len(filtered_products)
    total_pages = math.ceil(total_products / per_page)
    paginated = filtered_products[(page - 1) * per_page: page * per_page]

    for product in paginated:
        product['product_id'] = product.get('product_id', str(product.get('_id', '')))
        product['product_name'] = product.get('product_name', 'Unnamed Product')
        product['image_urls']=product.get('image_urls','https://via.placeholder.com/300x300.png?text=No+Image')
        product['main_image'] = product.get('main_image', 'https://via.placeholder.com/300x300.png?text=No+Image')
        product['final_price'] = product.get('final_price', 0.0)
        product['unit_price'] = product.get('unit_price', 0.0)
        product['rating'] = product.get('rating', 0)
        product['review_count'] = product.get('review_count', 0)

    # Dropdown filters
    brands = mongo.db.products.distinct('brand')
    categories = mongo.db.products.distinct('category_name')

    return render_template('products/catalog.html',
                           products=paginated,
                           brands=brands,
                           categories=categories,
                           current_page=page,
                           total_pages=total_pages,
                           total_products=total_products,
                           search=search,
                           category=category,
                           brand=brand,
                           min_price=min_price,
                           max_price=max_price,
                           sort_by=sort_by,
                           user=get_current_user())


# app.py or routes.py
@app.route('/walmart-bot')
def walmart_bot():
    return render_template('plannerBot/Walmart_Expansion_bot.html')


@app.route('/product/<int:product_id>')
def product_detail(product_id):
    print(f"🔍 Looking for product_id: {product_id} (type: {type(product_id)})")
    
    # Your database has integer product_ids, so this should work
    product = mongo.db.products.find_one({'product_id': product_id})
    
    if not product:
        print(f"❌ Product not found: {product_id}")
        # Let's check what product_ids actually exist
        existing_ids = list(mongo.db.products.find({}, {'product_id': 1}).limit(10))
        print(f"🔍 Existing product_ids: {[p['product_id'] for p in existing_ids]}")
        
        flash('Product not found', 'error')
        return redirect(url_for('products'))
    
    print(f"✅ Found product: {product.get('product_name')}")
    
    # Track viewed products
    if 'user_id' in session:
        mongo.db.viewed_products.insert_one({
            'user_id': session['user_id'],
            'product_id': product_id,
            'viewed_at': datetime.utcnow()
        })
    
    # Get related products using category_name
    related_products = list(mongo.db.products.find({
        'category_name': product.get('category_name'),
        'product_id': {'$ne': product_id}
    }).limit(4))
    
    return render_template('products/detail.html',
                           product=product,
                           related_products=related_products,
                           user=get_current_user())

# Alternative route for debugging - shows all products
@app.route('/debug/all-products')
def debug_all_products():
    products = list(mongo.db.products.find({}, {'product_id': 1, 'product_name': 1}).limit(20))
    html = "<h1>All Products</h1>"
    for product in products:
        product_id = product['product_id']
        product_name = product.get('product_name', 'No name')
        html += f'<p><a href="/product/{product_id}">{product_id} - {product_name}</a></p>'
    return html



@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        user = mongo.db.users.find_one({'email': email})
        
        if user and check_password_hash(user['password'], password):
            create_session(user['_id'])
            
            # Update last login
            mongo.db.users.update_one(
                {'_id': user['_id']},
                {'$set': {'last_login': datetime.utcnow()}}
            )
            
            flash('Login successful!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid email or password', 'error')
    
    return render_template('auth/login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        
        # Validation
        if password != confirm_password:
            flash('Passwords do not match', 'error')
            return render_template('auth/register.html')
        
        if mongo.db.users.find_one({'email': email}):
            flash('Email already exists', 'error')
            return render_template('auth/register.html')
        
        if mongo.db.users.find_one({'username': username}):
            flash('Username already exists', 'error')
            return render_template('auth/register.html')
        
        # Create user
        user_data = {
            'username': username,
            'email': email,
            'password': generate_password_hash(password),
            'created_at': datetime.utcnow(),
            'last_login': None,
            'profile': {
                'first_name': '',
                'last_name': '',
                'phone': '',
                'address': ''
            },
            'preferences': {
                'email_notifications': True,
                'sms_notifications': False
            }
        }
        
        result = mongo.db.users.insert_one(user_data)
        create_session(result.inserted_id)
        
        flash('Registration successful!', 'success')
        return redirect(url_for('index'))
    
    return render_template('auth/register.html')

@app.route('/logout')
def logout():
    if 'session_id' in session:
        mongo.db.sessions.update_one(
            {'session_id': session['session_id']},
            {'$set': {'is_active': False}}
        )
    
    session.clear()
    flash('You have been logged out', 'info')
    return redirect(url_for('index'))

@app.route('/cart')
def cart():
    if not is_logged_in():
        flash('Please login to view your cart', 'error')
        return redirect(url_for('login'))
    
    # Get cart items with product details
    cart_items = list(mongo.db.cart.aggregate([
        {'$match': {'user_id': session['user_id']}},
        {'$lookup': {
            'from': 'products',
            'localField': 'product_id',
            'foreignField': 'product_id',
            'as': 'product'
        }},
        {'$unwind': '$product'}
    ]))
    
    # Calculate totals
    subtotal = sum(item['quantity'] * item['product']['final_price'] for item in cart_items)
    tax = subtotal * 0.08
    shipping = 0 if subtotal > 35 else 5.99
    total = subtotal + tax + shipping
    
    return render_template('cart/cart.html',
                         cart_items=cart_items,
                         subtotal=subtotal,
                         tax=tax,
                         shipping=shipping,
                         total=total,
                         user=get_current_user())

@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    if not is_logged_in():
        return jsonify({'success': False, 'message': 'Please login first'})
        
    product_id = int(request.json['product_id'])
    quantity = int(request.json.get('quantity', 1))
        
    # Check if item already in cart
    existing_item = mongo.db.cart.find_one({
        'user_id': session['user_id'],
        'product_id': product_id
    })
        
    if existing_item:
        # Update quantity
        mongo.db.cart.update_one(
            {'_id': existing_item['_id']},
            {'$inc': {'quantity': quantity}}
        )
        flash('Item added to cart successfully!', 'success')
    else:
        # Add new item
        cart_data = {
            'user_id': session['user_id'],
            'product_id': product_id,
            'quantity': quantity,
            'added_at': datetime.utcnow()
        }
        mongo.db.cart.insert_one(cart_data)
        flash('Item added to cart successfully!', 'success')
        
    return jsonify({'success': True, 'message': 'Item added to cart'})

@app.route('/remove_from_cart', methods=['POST'])
def remove_from_cart():
    if not is_logged_in():
        return jsonify({'success': False, 'message': 'Please login first'})
    
    product_id = int(request.json['product_id'])
    
    mongo.db.cart.delete_one({
        'user_id': session['user_id'],
        'product_id': product_id
    })
    
    return jsonify({'success': True, 'message': 'Item removed from cart'})

@app.route('/update_cart', methods=['POST'])
def update_cart():
    if not is_logged_in():
        return jsonify({'success': False, 'message': 'Please login first'})
    
    product_id = int(request.json['product_id'])
    quantity = int(request.json['quantity'])
    
    if quantity <= 0:
        mongo.db.cart.delete_one({
            'user_id': session['user_id'],
            'product_id': product_id
        })
    else:
        mongo.db.cart.update_one(
            {'user_id': session['user_id'], 'product_id': product_id},
            {'$set': {'quantity': quantity}}
        )
    
    return jsonify({'success': True, 'message': 'Cart updated'})

@app.route('/wishlist')
def wishlist():
    if not is_logged_in():
        flash('Please login to view your wishlist', 'error')
        return redirect(url_for('login'))
    
    # Get wishlist items with product details
    wishlist_items = list(mongo.db.wishlist.aggregate([
        {'$match': {'user_id': session['user_id']}},
        {'$lookup': {
            'from': 'products',
            'localField': 'product_id',
            'foreignField': 'product_id',
            'as': 'product'
        }},
        {'$unwind': '$product'}
    ]))
    
    return render_template('wishlist/wishlist.html',
                         wishlist_items=wishlist_items,
                         user=get_current_user())

@app.route('/add_to_wishlist', methods=['POST'])
def add_to_wishlist():
    if not is_logged_in():
        return jsonify({'success': False, 'message': 'Please login first'})
    
    product_id = int(request.json['product_id'])
    
    # Check if already in wishlist
    existing_item = mongo.db.wishlist.find_one({
        'user_id': session['user_id'],
        'product_id': product_id
    })
    
    if not existing_item:
        wishlist_data = {
            'user_id': session['user_id'],
            'product_id': product_id,
            'added_at': datetime.utcnow()
        }
        mongo.db.wishlist.insert_one(wishlist_data)
        return jsonify({'success': True, 'message': 'Item added to wishlist'})
    
    return jsonify({'success': False, 'message': 'Item already in wishlist'})

@app.route('/remove_from_wishlist', methods=['POST'])
def remove_from_wishlist():
    if not is_logged_in():
        return jsonify({'success': False, 'message': 'Please login first'})
    
    product_id = int(request.json['product_id'])
    
    mongo.db.wishlist.delete_one({
        'user_id': session['user_id'],
        'product_id': product_id
    })
    
    return jsonify({'success': True, 'message': 'Item removed from wishlist'})

@app.route('/profile')
def profile():
    if not is_logged_in():
        flash('Please login to view your profile', 'error')
        return redirect(url_for('login'))
    
    user = get_current_user()
    
    # Get recently viewed products
    viewed_products = list(mongo.db.viewed_products.aggregate([
        {'$match': {'user_id': session['user_id']}},
        {'$sort': {'viewed_at': -1}},
        {'$limit': 10},
        {'$lookup': {
            'from': 'products',
            'localField': 'product_id',
            'foreignField': 'product_id',
            'as': 'product'
        }},
        {'$unwind': '$product'}
    ]))
    
    return render_template('auth/profile.html',
                         user=user,
                         viewed_products=viewed_products)

# ---------------smart shopping routes --------------
from semantic_search import semantic_search_products, enhanced_semantic_search, get_diverse_products_by_category
import json
@app.route('/smart_shopping')
def smart_shopping():
    return render_template("smart_shopping.html")

@app.route('/smart_shopping_search', methods=['POST'])
def smart_shopping_search():
    if request.method == 'POST':
        user_prompt = request.form.get('user_prompt', '').strip()
        
        if not user_prompt:
            flash('Please enter a shopping query', 'error')
            return redirect(url_for('smart_shopping'))
        
        try:
            # Test LLM connection first
            llm_available = True
            try:
                test_response = llm.invoke("Hello")
                print(f"LLM test successful: {test_response.content[:50]}...")
            except Exception as llm_error:
                print(f"LLM connection error: {llm_error}")
                llm_available = False
                flash('AI service temporarily unavailable. Using fallback search.', 'warning')
            
            # Generate enhanced queries
            if llm_available:
                enhanced_queries = generate_enhanced_queries(user_prompt)
            else:
                enhanced_queries = get_fallback_queries(user_prompt)
            
            # Validate enhanced queries
            if not enhanced_queries or len(enhanced_queries) == 0:
                print("No enhanced queries generated, using fallback")
                enhanced_queries = get_fallback_queries(user_prompt)
            
            # Search for products using improved semantic search
            product_rows = []
            categories = [query['category'] for query in enhanced_queries]
            
            # Method 1: Try diverse category search first
            try:
                category_products = get_diverse_products_by_category(categories, user_prompt, 6)
                
                for query_data in enhanced_queries:
                    category = query_data['category']
                    search_terms = query_data['search_terms']
                    
                    # Get products from diverse search
                    products = category_products.get(category, [])
                    
                    # If not enough products, try individual search
                    if len(products) < 3:
                        try:
                            additional_products = enhanced_semantic_search(search_terms, category, 6)
                            # Merge without duplicates
                            existing_ids = {p.get('product_id', str(p.get('_id', ''))) for p in products}
                            for prod in additional_products:
                                prod_id = prod.get('product_id', str(prod.get('_id', '')))
                                if prod_id not in existing_ids:
                                    products.append(prod)
                                    existing_ids.add(prod_id)
                                    if len(products) >= 6:
                                        break
                        except Exception as search_error:
                            print(f"Individual search error for {category}: {search_error}")
                    
                    # Final fallback to MongoDB if still not enough products
                    if len(products) < 2:
                        try:
                            mongo_query = {}
                            if category:
                                mongo_query['category_name'] = {'$regex': category, '$options': 'i'}
                            
                            mongo_products = list(mongo.db.products.find(mongo_query).limit(6))
                            
                            # Process mongo products
                            for product in mongo_products:
                                product['product_id'] = product.get('product_id', str(product.get('_id', '')))
                                product['product_name'] = product.get('product_name', 'Unnamed Product')
                                product['main_image'] = product.get('main_image', 'https://via.placeholder.com/300x300.png?text=No+Image')
                                product['final_price'] = product.get('final_price', 0.0)
                                product['unit_price'] = product.get('unit_price', 0.0)
                                product['rating'] = product.get('rating', 0)
                                product['review_count'] = product.get('review_count', 0)
                            
                            # Merge with existing products
                            existing_ids = {p.get('product_id', str(p.get('_id', ''))) for p in products}
                            for prod in mongo_products:
                                prod_id = prod.get('product_id', str(prod.get('_id', '')))
                                if prod_id not in existing_ids:
                                    products.append(prod)
                                    if len(products) >= 6:
                                        break
                        except Exception as mongo_error:
                            print(f"MongoDB fallback error for {category}: {mongo_error}")
                    
                    # Limit to 6 products and add to rows
                    limited_products = products[:6]
                    
                    if limited_products:
                        product_rows.append({
                            'category': category.title(),
                            'products': limited_products,
                            'search_terms': search_terms
                        })
                        print(f"Added {len(limited_products)} products for category: {category}")
                    else:
                        print(f"No products found for category: {category}")
                
            except Exception as e:
                print(f"Error in diverse search: {e}")
                # Fallback to individual searches
                for query_data in enhanced_queries:
                    category = query_data['category']
                    search_terms = query_data['search_terms']
                    
                    try:
                        products = enhanced_semantic_search(search_terms, category, 6)
                        
                        if products:
                            product_rows.append({
                                'category': category.title(),
                                'products': products,
                                'search_terms': search_terms
                            })
                    except Exception as search_error:
                        print(f"Individual search error for {category}: {search_error}")
                        continue
            
            # If no products found at all, provide a generic search
            if not product_rows:
                try:
                    generic_products = enhanced_semantic_search(user_prompt, None, 12)
                    if generic_products:
                        # Group by category
                        category_groups = {}
                        for product in generic_products:
                            cat = product.get('category_name', 'General')
                            if cat not in category_groups:
                                category_groups[cat] = []
                            if len(category_groups[cat]) < 6:
                                category_groups[cat].append(product)
                        
                        for cat, products in category_groups.items():
                            product_rows.append({
                                'category': cat,
                                'products': products,
                                'search_terms': user_prompt
                            })
                except Exception as generic_error:
                    print(f"Generic search error: {generic_error}")
                    flash('No products found for your search. Please try different keywords.', 'info')
            
            return render_template('smart_shopping_results.html',
                                 product_rows=product_rows,
                                 user_prompt=user_prompt,
                                 user=get_current_user())
        
        except Exception as e:
            print(f"Error in smart_shopping_search: {e}")
            import traceback
            traceback.print_exc()
            flash(f'Error processing your request. Please try again.', 'error')
            return redirect(url_for('smart_shopping'))
    
    return redirect(url_for('smart_shopping'))

def generate_enhanced_queries(user_prompt):
    """
    Use LLM to enhance user query and generate structured search queries
    """
    prompt = f"""You are a smart shopping assistant. Analyze the user's shopping query and break it down into exactly 3 different product categories with enhanced search terms.

User Query: "{user_prompt}"

Analyze this query and provide exactly 3 product categories that would be most relevant. For each category, provide enhanced search terms.

IMPORTANT: Respond with ONLY a valid JSON array. No other text, explanations, or formatting.

Format:
[
{{"category": "clothing", "search_terms": "formal dress shirts men business professional"}},
{{"category": "clothing", "search_terms": "dress pants men office work formal"}},
{{"category": "footwear", "search_terms": "formal shoes men office leather dress"}}
]

Categories should be chosen from: clothing, electronics, home, beauty, sports, footwear, accessories, books, toys, health, kitchen, furniture, jewelry, automotive, outdoor

Rules:
1. Always return exactly 3 objects
2. Make categories complementary to the user's scenario
3. Enhance search terms with relevant keywords, style, occasion
4. Keep categories diverse but relevant
5. ONLY return the JSON array, nothing else"""
    
    try:
        # Get response from LLM
        response = llm.invoke(prompt)
        
        # Clean the response content
        response_content = response.content.strip()
        
        # Remove any markdown formatting or extra text
        if response_content.startswith('```'):
            # Extract JSON from markdown code block
            lines = response_content.split('\n')
            json_lines = []
            in_json = False
            for line in lines:
                if line.strip().startswith('['):
                    in_json = True
                if in_json:
                    json_lines.append(line)
                if line.strip().endswith(']') and in_json:
                    break
            response_content = '\n'.join(json_lines)
        
        # Additional cleaning
        response_content = response_content.replace('```json', '').replace('```', '').strip()
        
        if not response_content:
            print("Empty response from LLM")
            return get_fallback_queries(user_prompt)
        
        # Parse the JSON response
        enhanced_queries = json.loads(response_content)
        
        # Validate that we have exactly 3 categories
        if not isinstance(enhanced_queries, list) or len(enhanced_queries) != 3:
            print(f"Invalid response format: {enhanced_queries}")
            return get_fallback_queries(user_prompt)
        
        # Validate each query object
        for query in enhanced_queries:
            if not isinstance(query, dict) or 'category' not in query or 'search_terms' not in query:
                print(f"Invalid query object: {query}")
                return get_fallback_queries(user_prompt)
        
        print(f"Successfully generated queries: {enhanced_queries}")
        return enhanced_queries
        
    except json.JSONDecodeError as e:
        print(f"JSON parsing error: {e}")
        print(f"Response content: {response_content}")
        return get_fallback_queries(user_prompt)
    except Exception as e:
        print(f"Error in generate_enhanced_queries: {e}")
        return get_fallback_queries(user_prompt)

def get_fallback_queries(user_prompt):
    """
    Fallback function to provide default queries if LLM fails
    """
    # Simple keyword-based fallback
    prompt_lower = user_prompt.lower()
    
    # Office/Professional scenarios
    if any(word in prompt_lower for word in ['office', 'work', 'professional', 'business', 'formal', 'interview', 'meeting']):
        return [
            {"category": "clothing", "search_terms": "formal shirts professional business office men women"},
            {"category": "clothing", "search_terms": "dress pants formal office work professional trousers"},
            {"category": "footwear", "search_terms": "formal shoes office dress leather professional"}
        ]
    
    # Casual/Weekend scenarios
    elif any(word in prompt_lower for word in ['casual', 'weekend', 'relaxed', 'comfortable', 'leisure', 'vacation']):
        return [
            {"category": "clothing", "search_terms": "casual shirts comfortable weekend t-shirts tops"},
            {"category": "clothing", "search_terms": "jeans casual pants comfortable denim"},
            {"category": "footwear", "search_terms": "casual shoes sneakers comfortable walking"}
        ]
    
    # Electronics/Tech scenarios
    elif any(word in prompt_lower for word in ['electronics', 'tech', 'gadget', 'device', 'computer', 'phone', 'laptop']):
        return [
            {"category": "electronics", "search_terms": "smartphones mobile phones latest technology"},
            {"category": "electronics", "search_terms": "laptops computers portable notebook"},
            {"category": "electronics", "search_terms": "headphones audio accessories wireless bluetooth"}
        ]
    
    # Home/Kitchen scenarios
    elif any(word in prompt_lower for word in ['home', 'kitchen', 'house', 'furniture', 'apartment', 'living']):
        return [
            {"category": "kitchen", "search_terms": "kitchen appliances cooking utensils tools"},
            {"category": "home", "search_terms": "furniture home decor living room bedroom"},
            {"category": "home", "search_terms": "storage organization home accessories"}
        ]
    
    # Fitness/Sports scenarios
    elif any(word in prompt_lower for word in ['gym', 'fitness', 'workout', 'sports', 'exercise', 'training']):
        return [
            {"category": "sports", "search_terms": "fitness equipment workout gear exercise"},
            {"category": "clothing", "search_terms": "sportswear athletic clothing gym wear"},
            {"category": "sports", "search_terms": "exercise accessories fitness gear equipment"}
        ]
    
    # Beauty/Health scenarios
    elif any(word in prompt_lower for word in ['beauty', 'skincare', 'makeup', 'health', 'personal care']):
        return [
            {"category": "beauty", "search_terms": "skincare products face care moisturizer"},
            {"category": "beauty", "search_terms": "makeup cosmetics beauty products"},
            {"category": "health", "search_terms": "personal care health wellness products"}
        ]
    
    # Student/College scenarios
    elif any(word in prompt_lower for word in ['student', 'college', 'university', 'study', 'school']):
        return [
            {"category": "electronics", "search_terms": "laptops computers student notebook"},
            {"category": "books", "search_terms": "textbooks educational books study materials"},
            {"category": "accessories", "search_terms": "backpacks student accessories school supplies"}
        ]
    
    # Travel scenarios
    elif any(word in prompt_lower for word in ['travel', 'vacation', 'trip', 'journey', 'luggage']):
        return [
            {"category": "accessories", "search_terms": "luggage travel bags suitcase backpack"},
            {"category": "clothing", "search_terms": "travel clothing comfortable vacation wear"},
            {"category": "electronics", "search_terms": "travel accessories gadgets portable chargers"}
        ]
    
    # Generic fallback based on common product types
    else:
        # Try to identify product types from the prompt
        if any(word in prompt_lower for word in ['shirt', 'clothing', 'dress', 'wear', 'outfit', 'fashion']):
            return [
                {"category": "clothing", "search_terms": f"{user_prompt} clothing wear fashion"},
                {"category": "footwear", "search_terms": f"{user_prompt} shoes footwear"},
                {"category": "accessories", "search_terms": f"{user_prompt} accessories fashion"}
            ]
        elif any(word in prompt_lower for word in ['phone', 'computer', 'laptop', 'tablet', 'tech']):
            return [
                {"category": "electronics", "search_terms": f"{user_prompt} electronics technology"},
                {"category": "electronics", "search_terms": f"{user_prompt} accessories cables chargers"},
                {"category": "electronics", "search_terms": f"{user_prompt} devices gadgets"}
            ]
        elif any(word in prompt_lower for word in ['kitchen', 'cooking', 'food', 'recipe']):
            return [
                {"category": "kitchen", "search_terms": f"{user_prompt} kitchen cooking utensils"},
                {"category": "home", "search_terms": f"{user_prompt} home appliances"},
                {"category": "kitchen", "search_terms": f"{user_prompt} food storage containers"}
            ]
        else:
            # Most generic fallback
            return [
                {"category": "clothing", "search_terms": f"{user_prompt} clothing fashion"},
                {"category": "electronics", "search_terms": f"{user_prompt} electronics technology"},
                {"category": "home", "search_terms": f"{user_prompt} home accessories"}
            ]

        
@app.route('/admin')
def admin_dashboard():
    if not is_logged_in():
        flash('Please login to access admin panel', 'error')
        return redirect(url_for('login'))
    
    user = get_current_user()
    if user['username'] != 'admin':  # Simple admin check
        flash('Access denied', 'error')
        return redirect(url_for('index'))
    
    # Get statistics
    total_users = mongo.db.users.count_documents({})
    total_products = mongo.db.products.count_documents({})
    total_orders = mongo.db.cart.count_documents({})
    
    return render_template('admin/dashboard.html',
                         total_users=total_users,
                         total_products=total_products,
                         total_orders=total_orders,
                         user=user)

if __name__ == '__main__':
    app.run(debug=True)