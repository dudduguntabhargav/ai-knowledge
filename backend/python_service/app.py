import os
import time
from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI, UploadFile, Form, File
from fastapi.responses import JSONResponse, StreamingResponse
from typing import Optional
from models.ai_models import QueryRequest, QueryResponse, UploadResponse, TimingMetrics
from rag_pipeline import process_query, store_document, process_query_stream
from db.chat_store import save_chat, get_all_conversations, get_user_documents, clear_chat_history
import json

app = FastAPI(title="LangChain RAG Service - ChatGPT-like Interface")

@app.post("/upload", response_model=UploadResponse)
async def upload_doc(user_email: str = Form(...), file: UploadFile = File(...)):
    content = await file.read()
    filename = store_document(user_email, content, file.filename)
    return {
        "message": f"Document '{filename}' uploaded and set as active context",
        "filename": filename
    }

@app.post("/upload-and-query")
async def upload_and_query(
    user_email: str = Form(...),
    query: str = Form(...),
    file: UploadFile = File(...)
):
    total_start_time = time.time()

    content = await file.read()
    filename = store_document(user_email, content, file.filename)

    answer, sources, timings, document_used = process_query(
        user_email,
        query,
        document_filter=filename
    )

    source_docs = [{"filename": doc.metadata.get("filename"), "page": doc.metadata.get("chunk_index")} for doc in sources]
    save_chat(user_email, query, answer, document_name=filename, sources=source_docs)

    total_time = time.time() - total_start_time

    return {
        "answer": answer,
        "sources": sources,
        "document_used": document_used,
        "timing": {
            "total_time": round(total_time, 3),
            "retrieval_time": round(timings.get('retrieval_time', 0), 3),
            "llm_time": round(timings.get('llm_time', 0), 3)
        }
    }

@app.post("/query", response_model=QueryResponse)
async def query_ai(req: QueryRequest):
    total_start_time = time.time()

    answer, sources, timings, document_used = process_query(req.user_email, req.query)

    source_docs = [{"filename": doc.metadata.get("filename"), "page": doc.metadata.get("chunk_index")} for doc in sources]
    save_chat(req.user_email, req.query, answer, document_name=document_used, sources=source_docs)

    total_time = time.time() - total_start_time

    timing_metrics = TimingMetrics(
        total_time=round(total_time, 3),
        retrieval_time=round(timings.get('retrieval_time', 0), 3),
        llm_time=round(timings.get('llm_time', 0), 3),
        history_time=round(timings.get('history_time', 0), 3)
    )

    return {
        "answer": answer,
        "sources": sources,
        "document_used": document_used,
        "timing": timing_metrics
    }

@app.post("/query-stream")
async def query_ai_stream(req: QueryRequest):
    def generate():
        try:
            for chunk in process_query_stream(req.user_email, req.query):
                yield f"data: {json.dumps({'chunk': chunk})}\n\n"

            yield f"data: {json.dumps({'done': True})}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )

@app.get("/conversations/{user_email}")
async def get_conversations(user_email: str):
    conversations = get_all_conversations(user_email)
    return {"conversations": conversations}

@app.get("/documents/{user_email}")
async def get_documents(user_email: str):
    documents = get_user_documents(user_email)
    return {"documents": documents}

@app.delete("/conversations/{user_email}")
async def clear_conversations(user_email: str):
    deleted_count = clear_chat_history(user_email)
    return {"message": f"Deleted {deleted_count} conversations", "deleted_count": deleted_count}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "RAG AI Service"}
