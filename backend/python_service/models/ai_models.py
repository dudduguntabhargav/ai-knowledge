from pydantic import BaseModel
from typing import Optional

class QueryRequest(BaseModel):
    user_email: str
    query: str

class TimingMetrics(BaseModel):
    total_time: float  # Total query processing time in seconds
    retrieval_time: float  # Time to retrieve documents from vector store
    llm_time: float  # Time for OpenAI API call
    history_time: float  # Time to load chat history

class QueryResponse(BaseModel):
    answer: str
    sources: list
    timing: Optional[TimingMetrics] = None

class UploadResponse(BaseModel):
    message: str
