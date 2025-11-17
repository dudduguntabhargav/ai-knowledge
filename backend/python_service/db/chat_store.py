from pymongo import MongoClient
import os, datetime

client = MongoClient(os.getenv("MONGO_URI", "mongodb://localhost:27017"))
db = client["ai_knowledge"]

def save_chat(user_email, query, answer):
    """Save chat Q/A to MongoDB."""
    db.chats.insert_one({
        "user_email": user_email,
        "query": query,
        "answer": answer,
        "timestamp": datetime.datetime.utcnow()
    })

def get_user_history(user_email):
    """Return chat history as tuples (query, answer)."""
    chats = list(db.chats.find({"user_email": user_email}).sort("timestamp", 1))
    return [(c["query"], c["answer"]) for c in chats]
