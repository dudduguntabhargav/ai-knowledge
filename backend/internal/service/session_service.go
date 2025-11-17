package service

import (
	"time"

	"ai-knowledge/internal/models"
	"ai-knowledge/internal/repository"
)

type SessionService struct {
	SessionRepo *repository.SessionRepository
}

func (s *SessionService) CreateSession(email, token string, expiry time.Time) error {
	session := models.Session{
		UserEmail: email,
		Token:     token,
		ExpiresAt: expiry,
		Revoked:   false,
		CreatedAt: time.Now(),
	}
	return s.SessionRepo.Create(session)
}

func (s *SessionService) RevokeSession(token string) error {
	return s.SessionRepo.RevokeByToken(token)
}

func (s *SessionService) IsSessionRevoked(token string) (bool, error) {
	return s.SessionRepo.IsRevoked(token)
}
