package models

import "time"

type Session struct {
	ID        string    `bson:"_id,omitempty" json:"id,omitempty"`
	UserEmail string    `bson:"user_email" json:"user_email"`
	Token     string    `bson:"token" json:"token"`
	ExpiresAt time.Time `bson:"expires_at" json:"expires_at"`
	Revoked   bool      `bson:"revoked" json:"revoked"`
	CreatedAt time.Time `bson:"created_at" json:"created_at"`
}
