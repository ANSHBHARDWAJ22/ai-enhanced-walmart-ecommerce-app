import os
from dotenv import load_dotenv
from urllib.parse import quote_plus

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-here')
    
    # MongoDB connection
    username = quote_plus("soni3anuj")
    password = quote_plus("Anuj")
    MONGO_URI = f"mongodb+srv://{username}:{password}@cluster0.y8s8phx.mongodb.net/walmart_clone?retryWrites=true&w=majority&appName=Cluster0"
    
    # Flask settings
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')
    DEBUG = FLASK_ENV == 'development'
    
    # Session settings
    SESSION_COOKIE_SECURE = FLASK_ENV == 'production'
    SESSION_COOKIE_HTTPONLY = True
    PERMANENT_SESSION_LIFETIME = 86400  # 24 hours