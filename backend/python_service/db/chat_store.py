from pymongo import MongoClient
import os, datetime
from typing import List, Dict, Optional

client = MongoClient(os.getenv("MONGO_URI", "mongodb://localhost:27017"))
db = client["ai_knowledge"]

def save_chat(user_email, query, answer, document_name=None, sources=None):
    db.chats.insert_one({
        "user_email": user_email,
        "query": query,
        "answer": answer,
        "document_name": document_name,
        "sources": sources or [],
        "timestamp": datetime.datetime.utcnow()
    })

def get_user_history(user_email, limit=None):
    query = {"user_email": user_email}
    chats = db.chats.find(query).sort("timestamp", -1)

    if limit:
        chats = chats.limit(limit)

    chats = list(chats)
    chats.reverse()
    return [(c["query"], c["answer"]) for c in chats]

def get_all_conversations(user_email) -> List[Dict]:
    chats = list(db.chats.find(
        {"user_email": user_email}
    ).sort("timestamp", -1))

    return [{
        "id": str(chat["_id"]),
        "query": chat["query"],
        "answer": chat["answer"],
        "document_name": chat.get("document_name"),
        "timestamp": chat["timestamp"].isoformat() if chat.get("timestamp") else None
    } for chat in chats]

def set_active_document(user_email, document_name):
    db.user_context.update_one(
        {"user_email": user_email},
        {"$set": {
            "active_document": document_name,
            "updated_at": datetime.datetime.utcnow()
        }},
        upsert=True
    )

def get_active_document(user_email) -> Optional[str]:
    context = db.user_context.find_one({"user_email": user_email})
    return context.get("active_document") if context else None

def get_user_documents(user_email) -> List[str]:
    docs = db.user_documents.find({"user_email": user_email})
    return [doc["filename"] for doc in docs]

def track_document_upload(user_email, filename, file_type):
    db.user_documents.update_one(
        {"user_email": user_email, "filename": filename},
        {"$set": {
            "file_type": file_type,
            "uploaded_at": datetime.datetime.utcnow()
        }},
        upsert=True
    )
    set_active_document(user_email, filename)

def clear_chat_history(user_email):
    result = db.chats.delete_many({"user_email": user_email})
    return result.deleted_count
