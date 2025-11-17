package repository

import (
	"context"
	"time"

	"ai-knowledge/internal/models"
	"go.mongodb.org/mongo-driver/bson"
	"go.mongodb.org/mongo-driver/mongo"
)

type SessionRepository struct {
	Collection *mongo.Collection
}

func NewSessionRepository(db *mongo.Client) *SessionRepository {
	return &SessionRepository{
		Collection: db.Database("ai_platform").Collection("sessions"),
	}
}

func (r *SessionRepository) Create(session models.Session) error {
	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()
	_, err := r.Collection.InsertOne(ctx, session)
	return err
}

func (r *SessionRepository) RevokeByToken(token string) error {
	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()
	_, err := r.Collection.UpdateOne(ctx, bson.M{"token": token}, bson.M{"$set": bson.M{"revoked": true}})
	return err
}

func (r *SessionRepository) IsRevoked(token string) (bool, error) {
	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()
	var session models.Session
	err := r.Collection.FindOne(ctx, bson.M{"token": token}).Decode(&session)
	if err != nil {
		if err == mongo.ErrNoDocuments {
			return false, nil
		}
		return false, err
	}
	return session.Revoked, nil
}
