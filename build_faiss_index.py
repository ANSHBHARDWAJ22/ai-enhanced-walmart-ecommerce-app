# build_faiss_index.py

from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.documents import Document
from pymongo import MongoClient
from urllib.parse import quote_plus

# ✅ 1. MongoDB Atlas Connection Setup
username = quote_plus("soni3anuj")
password = quote_plus("Anuj")
uri = f"mongodb+srv://{username}:{password}@cluster0.y8s8phx.mongodb.net/walmart_clone?retryWrites=true&w=majority&appName=Cluster0"

# ✅ 2. Connect to MongoDB
client = MongoClient(uri)
db = client["walmart_clone"]
collection = db["products"]

# ✅ 3. Load product data into LangChain Documents
# ✅ 3. Load product data into LangChain Documents
documents = []
for product in collection.find():
    text = f"{product.get('product_name', '')} {product.get('description', '')} {product.get('brand', '')} {product.get('category_name', '')}"
    metadata = {
        "product_id": product.get("product_id"),
        "product_name": product.get("product_name", "Unnamed Product"),
        "final_price": product.get("final_price", 0.0),
        "unit_price": product.get("unit_price", 0.0),
        "brand": product.get("brand", "Unknown"),
        "category_name": product.get("category_name", "Miscellaneous"),
        "rating": product.get("rating", 0),
        "review_count": product.get("review_count", 0),
        "main_image": product.get("main_image", "https://via.placeholder.com/300x300.png?text=No+Image"),
        "url": product.get("url", "#"),
        "image_urls": product.get("image_urls","https://via.placeholder.com/300x300.png?text=No+Image")
    }
    documents.append(Document(page_content=text, metadata=metadata))


# ✅ 4. Load embedding model
embedding = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

# ✅ 5. Build FAISS index
vectorstore = FAISS.from_documents(documents, embedding)

# ✅ 6. Save index locally
vectorstore.save_local("faiss_product_index")

print("✅ FAISS index created and saved to 'faiss_product_index'")



