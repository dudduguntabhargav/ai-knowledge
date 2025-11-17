package models

import "time"

type User struct {
	ID        string    `bson:"_id,omitempty" json:"id,omitempty"`
	Name      string    `bson:"name" json:"name" binding:"required"`
	Email     string    `bson:"email" json:"email" binding:"required,email"`
	Password  string    `bson:"password" json:"password,omitempty"`
	CreatedAt time.Time `bson:"created_at" json:"created_at"`
}
