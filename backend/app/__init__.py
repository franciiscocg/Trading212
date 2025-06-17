from flask import Flask, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os

# Cargar variables de entorno
load_dotenv()

# Inicializar extensiones
db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    
    # Configuración
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///trading212.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Inicializar extensiones
    db.init_app(app)
    
    # Configurar CORS
    CORS(app, origins=os.getenv('CORS_ORIGINS', 'http://localhost:3000').split(','))
    
    # Registrar blueprints
    from app.routes.portfolio import portfolio_bp
    from app.routes.positions import positions_bp
    from app.routes.analytics import analytics_bp
    from app.routes.auth import auth_bp
    
    app.register_blueprint(portfolio_bp, url_prefix='/api/portfolio')
    app.register_blueprint(positions_bp, url_prefix='/api/positions')
    app.register_blueprint(analytics_bp, url_prefix='/api/analytics')
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    
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
