package routes

import (
	"ai-knowledge/internal/client"
	"ai-knowledge/internal/config"
	"ai-knowledge/internal/handler"
	"ai-knowledge/internal/middleware"
	"ai-knowledge/internal/service"
	"github.com/gin-gonic/gin"
	"go.mongodb.org/mongo-driver/mongo"
)

func RegisterRoutes(router *gin.Engine, db *mongo.Client, cfg *config.Config, authService *service.AuthService, sessionService *service.SessionService) {
	api := router.Group("/api/v1")

	// Auth handler
	authHandler := &handler.AuthHandler{
		AuthService: authService,
	}

	// Python client for RAG operations
	pythonClient := client.NewPythonClient(cfg.PythonAIURL)
	ragHandler := handler.NewRAGHandler(pythonClient)

	// Public routes
	api.POST("/register", authHandler.Register)
	api.POST("/login", authHandler.Login)
	api.GET("/health", func(c *gin.Context) {
		c.JSON(200, gin.H{"status": "ok"})
	})

	// Protected routes (require JWT authentication)
	protected := api.Group("/")
	protected.Use(middleware.AuthMiddleware(cfg.JWTSecret, sessionService))
	{
		// Auth operations
		protected.POST("/logout", authHandler.Logout)
		protected.GET("/me", func(c *gin.Context) {
			email, _ := c.Get("email")
			c.JSON(200, gin.H{"message": "Authenticated!", "email": email})
		})

		protected.POST("/upload", ragHandler.UploadDocument)
		protected.POST("/query", ragHandler.QueryRAG)
	}
}
