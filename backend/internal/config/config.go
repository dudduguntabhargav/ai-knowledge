package config

import (
	"log"

	"github.com/spf13/viper"
)

type Config struct {
	AppEnv       string `mapstructure:"APP_ENV"`
	AppPort      string `mapstructure:"APP_PORT"`
	MongoURI     string `mapstructure:"MONGO_URI"`
	MongoDB      string `mapstructure:"MONGO_DB"`
	JWTSecret    string `mapstructure:"JWT_SECRET"`
	PythonAIURL  string `mapstructure:"PYTHON_AI_URL"`
	LogLevel     string `mapstructure:"LOG_LEVEL"`
}

func LoadConfig(path string) (*Config, error) {
	viper.AddConfigPath(path)
	viper.SetConfigName(".env")
	viper.SetConfigType("env")
	viper.AutomaticEnv()

	if err := viper.ReadInConfig(); err != nil {
		log.Printf("No .env file found, using system environment variables")
	}

	var cfg Config
	if err := viper.Unmarshal(&cfg); err != nil {
		return nil, err
	}

	// Default values (in case something is missing)
	if cfg.AppPort == "" {
		cfg.AppPort = "8080"
	}
	if cfg.LogLevel == "" {
		cfg.LogLevel = "info"
	}

	return &cfg, nil
}
