package models

// RAG request/response models for communicating with Python service

type QueryRequest struct {
	UserEmail string `json:"user_email" binding:"required,email"`
	Query     string `json:"query" binding:"required"`
}

type TimingMetrics struct {
	TotalTime     float64 `json:"total_time"`
	RetrievalTime float64 `json:"retrieval_time"`
	LLMTime       float64 `json:"llm_time"`
	HistoryTime   float64 `json:"history_time"`
}

type SourceDocument struct {
	ID          interface{}       `json:"id"`
	Metadata    map[string]string `json:"metadata"`
	PageContent string            `json:"page_content"`
	Type        string            `json:"type"`
}

type QueryResponse struct {
	Answer  string           `json:"answer"`
	Sources []SourceDocument `json:"sources"`
	Timing  *TimingMetrics   `json:"timing,omitempty"`
}

type UploadResponse struct {
	Message string `json:"message"`
}
