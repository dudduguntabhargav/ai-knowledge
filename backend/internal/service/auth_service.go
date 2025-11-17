package service

import (
	"errors"
	"time"

	"ai-knowledge/internal/models"
	"ai-knowledge/internal/repository"
	"ai-knowledge/internal/utils"
)

type AuthService struct {
	UserRepo       *repository.UserRepository
	JWTSecret      string
	SessionService *SessionService
}

func (s *AuthService) Register(user models.User) error {
	existing, _ := s.UserRepo.FindByEmail(user.Email)
	if existing != nil {
		return errors.New("email already registered")
	}
	hashed, _ := utils.HashPassword(user.Password)
	user.Password = hashed
	user.CreatedAt = time.Now()
	return s.UserRepo.Create(user)
}

func (s *AuthService) Login(email, password string) (string, error) {
	user, err := s.UserRepo.FindByEmail(email)
	if err != nil {
		return "", errors.New("invalid email or password")
	}
	if !utils.CheckPassword(password, user.Password) {
		return "", errors.New("invalid email or password")
	}
	token, _ := utils.GenerateToken(user.Email, s.JWTSecret)
	expiry := time.Now().Add(24 * time.Hour)
	_ = s.SessionService.CreateSession(user.Email, token, expiry)
	return token, nil
}

func (s *AuthService) Logout(token string) error {
	return s.SessionService.RevokeSession(token)
}
