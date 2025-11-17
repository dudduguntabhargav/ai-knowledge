package handler

import (
	"io"
	"net/http"
	"time"

	"ai-knowledge/internal/client"
	"ai-knowledge/internal/models"
	"github.com/gin-gonic/gin"
)

type RAGHandler struct {
	PythonClient *client.PythonClient
}

func NewRAGHandler(pythonClient *client.PythonClient) *RAGHandler {
	return &RAGHandler{
		PythonClient: pythonClient,
	}
}

// UploadDocument proxies document upload to Python service
func (h *RAGHandler) UploadDocument(c *gin.Context) {
	startTime := time.Now()

	// Extract user email from JWT context (set by AuthMiddleware)
	email, exists := c.Get("email")
	if !exists {
		c.JSON(http.StatusUnauthorized, gin.H{"error": "Email not found in token"})
		return
	}
	userEmail := email.(string)

	// Get uploaded file
	file, err := c.FormFile("file")
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "File is required"})
		return
	}

	// Open file
	fileContent, err := file.Open()
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to open file"})
		return
	}
	defer fileContent.Close()

	// Read file content
	content, err := io.ReadAll(fileContent)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to read file"})
		return
	}

	// Forward to Python service
	pythonStart := time.Now()
	resp, err := h.PythonClient.UploadDocument(userEmail, file.Filename, content)
	pythonTime := time.Since(pythonStart).Milliseconds()

	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	totalTime := time.Since(startTime).Milliseconds()

	c.JSON(http.StatusOK, gin.H{
		"message": resp.Message,
		"timing": gin.H{
			"total_time_ms":  totalTime,
			"python_api_ms":  pythonTime,
			"gateway_overhead_ms": totalTime - pythonTime,
		},
	})
}

// QueryRAG proxies RAG query to Python service
func (h *RAGHandler) QueryRAG(c *gin.Context) {
	startTime := time.Now()

	// Extract user email from JWT context (set by AuthMiddleware)
	email, exists := c.Get("email")
	if !exists {
		c.JSON(http.StatusUnauthorized, gin.H{"error": "Email not found in token"})
		return
	}
	userEmail := email.(string)

	// Parse request
	var req struct {
		Query string `json:"query" binding:"required"`
	}
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	// Create query request for Python service
	queryReq := models.QueryRequest{
		UserEmail: userEmail,
		Query:     req.Query,
	}

	// Forward to Python service
	pythonStart := time.Now()
	resp, err := h.PythonClient.QueryRAG(queryReq)
	pythonTime := time.Since(pythonStart).Milliseconds()

	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	totalTime := time.Since(startTime).Milliseconds()

	// Add gateway timing to response
	c.JSON(http.StatusOK, gin.H{
		"answer":  resp.Answer,
		"sources": resp.Sources,
		"timing": gin.H{
			"total_time_ms":          totalTime,
			"python_api_ms":          pythonTime,
			"gateway_overhead_ms":    totalTime - pythonTime,
			"python_internal_timing": resp.Timing,
		},
	})
}
