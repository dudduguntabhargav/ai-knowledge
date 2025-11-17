package db

import (
	"context"
	"time"

	"go.mongodb.org/mongo-driver/mongo"
	"go.mongodb.org/mongo-driver/mongo/options"
)

func ConnectMongo(uri string) (*mongo.Client, error){
	ctx, cancel := context.WithTimeout(context.Background(), time.Second*100)
	defer cancel()

	client, err := mongo.Connect(ctx, options.Client().ApplyURI(uri))

	if err!=nil{
		return nil, err
	}

	if err:= client.Ping(ctx, nil); err!=nil{
		return nil, err
	}

	return client, nil
}