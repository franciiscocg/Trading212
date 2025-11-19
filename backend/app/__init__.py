from flask import Flask, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Cargar variables de entorno
load_dotenv()

# Inicializar extensiones
db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    
    # Cargar configuración
    env = os.getenv('FLASK_ENV', 'default')
    from config import config
    app.config.from_object(config[env])
    
    # Validar configuración
    try:
        config[env].validate_config()
    except Exception as e:
        logger.error(f"Error validando configuración: {e}")
    
    # Inicializar extensiones
    db.init_app(app)
    
    # Configurar CORS
    CORS(app, origins=app.config['CORS_ORIGINS'])
      # Registrar blueprints
    from app.routes.portfolio import portfolio_bp
    from app.routes.positions import positions_bp
    from app.routes.analytics import analytics_bp
    from app.routes.auth import auth_bp
    from app.routes.investment_advisor import investment_advisor_bp
    from app.routes.investments import investments_bp
    from app.routes.strategy import strategy_bp
    
    app.register_blueprint(portfolio_bp, url_prefix='/api/portfolio')
    app.register_blueprint(positions_bp, url_prefix='/api/positions')
    app.register_blueprint(analytics_bp, url_prefix='/api/analytics')
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(investment_advisor_bp, url_prefix='/api/investment-advisor')
    app.register_blueprint(investments_bp, url_prefix='/api/investments')
    app.register_blueprint(strategy_bp, url_prefix='/api/strategy')
    
    # Health check route
    @app.route('/api/health', methods=['GET'])
    def health_check():
        return jsonify({
            'status': 'healthy',
            'message': 'Trading212 Portfolio Manager API is running',
            'version': '1.0.0'
        })
    
    # Default route for testing
    @app.route('/api/', methods=['GET'])
    def api_root():
        return jsonify({
            'message': 'Trading212 Portfolio Manager API',
            'endpoints': [
                '/api/health',
                '/api/portfolio',
                '/api/positions', 
                '/api/analytics',
                '/api/auth'
            ]
        })
    
    # Crear tablas de base de datos
    with app.app_context():
        db.create_all()
    
    return app
