package bootstrap

import (
	"context"
	"log"
	"net/http"
	"time"

	"ai-knowledge/internal/config"
	"ai-knowledge/internal/db"
	"ai-knowledge/internal/repository"
	"ai-knowledge/internal/routes"
	"ai-knowledge/internal/service"
	"github.com/gin-gonic/gin"
)

type App struct {
	Router *gin.Engine
	Server *http.Server
}

func InitializeApp(cfg *config.Config) *App {

	router := gin.New()
	router.Use(gin.Logger())
	router.Use(gin.Recovery())

	client, err := db.ConnectMongo(cfg.MongoURI)
	if err != nil {
		log.Fatalf(" MongoDB connection failed: %v", err)
	}

	userRepo := repository.NewRepository(client)
	sessionRepo := repository.NewSessionRepository(client)

	sessionService := &service.SessionService{SessionRepo: sessionRepo}
	authService := &service.AuthService{
		UserRepo:       userRepo,
		SessionService: sessionService,
		JWTSecret:      cfg.JWTSecret,
	}

	routes.RegisterRoutes(router, client, cfg, authService, sessionService)

	server := &http.Server{
		Addr:    ":" + cfg.AppPort,
		Handler: router,
	}

	log.Println("Application initialized successfully")
	return &App{Router: router, Server: server}
}

func (a *App) Run(addr string) error {
	log.Printf("Starting Gin server on %s", addr)
	return a.Server.ListenAndServe()
}

func (a *App) Shutdown(ctx context.Context) error {
	log.Println("Shutting down Gin server")
	ctx, cancel := context.WithTimeout(ctx, 10*time.Second)
	defer cancel()
	return a.Server.Shutdown(ctx)
}
