import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

class Config:
    """Configuración base"""
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///trading212.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', 'http://localhost:3000').split(',')
    
    # API Keys
    TRADING212_API_KEY = os.getenv('TRADING212_API_KEY')
    TRADING212_API_URL = os.getenv('TRADING212_API_URL', 'https://live.trading212.com/api/v0')
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
    NEWS_API_KEY = os.getenv('NEWS_API_KEY')
    
    # Sentiment Analysis
    SENTIMENT_CACHE_DIR = os.getenv('SENTIMENT_CACHE_DIR', os.path.join(os.path.dirname(__file__), 'cache'))
    SENTIMENT_REQUEST_LIMIT = int(os.getenv('SENTIMENT_REQUEST_LIMIT', 100))

class DevelopmentConfig(Config):
    """Configuración de desarrollo"""
    DEBUG = True

class ProductionConfig(Config):
    """Configuración de producción"""
    DEBUG = False

class TestingConfig(Config):
    """Configuración de pruebas"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
