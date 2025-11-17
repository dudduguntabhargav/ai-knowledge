import os
import time
from dotenv import load_dotenv

# Load environment variables BEFORE importing other modules
load_dotenv()

from fastapi import FastAPI, UploadFile, Form
from models.ai_models import QueryRequest, QueryResponse, UploadResponse, TimingMetrics
from rag_pipeline import process_query, store_document
from db.chat_store import save_chat

app = FastAPI(title="LangChain RAG Service")

@app.post("/upload", response_model=UploadResponse)
async def upload_doc(user_email: str = Form(...), file: UploadFile = None):
    content = await file.read()
    store_document(user_email, content, file.filename)
    return {"message": "Document uploaded successfully"}

@app.post("/query", response_model=QueryResponse)
async def query_ai(req: QueryRequest):
    # Track total time for the entire API call
    total_start_time = time.time()

    # Process the query
    answer, sources, timings = process_query(req.user_email, req.query)

    # Save chat history
    save_chat(req.user_email, req.query, answer)

    # Calculate total time
    total_time = time.time() - total_start_time

    # Create timing metrics
    timing_metrics = TimingMetrics(
        total_time=round(total_time, 3),
        retrieval_time=round(timings['retrieval_time'], 3),
        llm_time=round(timings['llm_time'], 3),
        history_time=round(timings['history_time'], 3)
    )

    return {
        "answer": answer,
        "sources": sources,
        "timing": timing_metrics
    }
