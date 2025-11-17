package repository

import (
	"context"
	"time"

	"ai-knowledge/internal/models"
	"go.mongodb.org/mongo-driver/bson"
	"go.mongodb.org/mongo-driver/mongo"
)

type UserRepository struct {
	Collection *mongo.Collection
}

func NewRepository(db *mongo.Client) *UserRepository {
	return &UserRepository{
		Collection: db.Database("ai_platform").Collection("users"),
	}
}

func (r *UserRepository) Create(user models.User) error {
	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()
	_, err := r.Collection.InsertOne(ctx, user)
	return err
}

func (r *UserRepository) FindByEmail(email string) (*models.User, error) {
	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()
	var user models.User
	err := r.Collection.FindOne(ctx, bson.M{"email": email}).Decode(&user)
	if err != nil {
		return nil, err
	}
	return &user, nil
}
