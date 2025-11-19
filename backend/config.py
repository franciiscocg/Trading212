import os
from dotenv import load_dotenv
import logging

# Cargar variables de entorno
load_dotenv()

logger = logging.getLogger(__name__)

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
    
    @classmethod
    def validate_config(cls):
        """Validar configuración y mostrar advertencias si faltan API keys opcionales"""
        warnings = []
        errors = []
        
        # API Keys opcionales con advertencias
        if not cls.TRADING212_API_KEY:
            warnings.append("⚠️  TRADING212_API_KEY no configurada - Las funciones de sincronización con Trading212 no funcionarán")
        
        if not cls.GEMINI_API_KEY:
            warnings.append("⚠️  GEMINI_API_KEY no configurada - El análisis con IA no estará disponible")
        
        if not cls.NEWS_API_KEY:
            warnings.append("⚠️  NEWS_API_KEY no configurada - El análisis de sentimiento de noticias será limitado")
        
        # Logging de advertencias
        if warnings:
            logger.warning("Configuración incompleta detectada:")
            for warning in warnings:
                logger.warning(warning)
        
        # Errors críticos que impedirían el funcionamiento básico
        if errors:
            logger.error("Errores de configuración críticos:")
            for error in errors:
                logger.error(error)
            raise ValueError("Configuración inválida. Revisa los errores arriba.")
        
        if not warnings:
            logger.info("✅ Configuración validada correctamente")
        
        return True

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
