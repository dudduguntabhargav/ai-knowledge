from pydantic import BaseModel
from typing import Optional

class QueryRequest(BaseModel):
    user_email: str
    query: str

class TimingMetrics(BaseModel):
    total_time: float
    retrieval_time: float
    llm_time: float
    history_time: float

class QueryResponse(BaseModel):
    answer: str
    sources: list
    document_used: Optional[str] = None
    timing: Optional[TimingMetrics] = None

class UploadResponse(BaseModel):
    message: str
    filename: Optional[str] = None
