from flask import Blueprint, request, jsonify
from app.models import Position, Portfolio
from app import db
import logging

logger = logging.getLogger(__name__)
positions_bp = Blueprint('positions', __name__)

@positions_bp.route('/', methods=['GET'])
def get_positions():
    """Obtener todas las posiciones"""
    try:
        user_id = request.args.get('user_id', 'default')
        
        portfolio = Portfolio.query.filter_by(user_id=user_id).first()
        if not portfolio:
            # Si no hay datos en la base de datos, sugerir sincronización
            return jsonify({
                'error': 'No portfolio data found. Please sync your Trading212 data first.',
                'suggestion': 'Click the "Sync" button to fetch your real portfolio data from Trading212.'
            }), 404
        
        positions = Position.query.filter_by(portfolio_id=portfolio.id).all()
        
        return jsonify([pos.to_dict() for pos in positions])
    
    except Exception as e:
        logger.error(f"Error getting positions: {e}")
        return jsonify({'error': str(e)}), 500

@positions_bp.route('/<ticker>', methods=['GET'])
def get_position(ticker):
    """Obtener posición específica por ticker"""
    try:
        user_id = request.args.get('user_id', 'default')
        
        portfolio = Portfolio.query.filter_by(user_id=user_id).first()
        if not portfolio:
            return jsonify({'error': 'Portfolio not found'}), 404
        
        position = Position.query.filter_by(
            portfolio_id=portfolio.id,
            ticker=ticker.upper()
        ).first()
        
        if not position:
            return jsonify({'error': 'Position not found'}), 404
        
        return jsonify(position.to_dict())
    
    except Exception as e:
        logger.error(f"Error getting position {ticker}: {e}")
        return jsonify({'error': str(e)}), 500

@positions_bp.route('/winners', methods=['GET'])
def get_winning_positions():
    """Obtener posiciones ganadoras"""
    try:
        user_id = request.args.get('user_id', 'default')
        limit = request.args.get('limit', 10, type=int)
        
        portfolio = Portfolio.query.filter_by(user_id=user_id).first()
        if not portfolio:
            return jsonify({'error': 'Portfolio not found'}), 404
        
        positions = Position.query.filter_by(portfolio_id=portfolio.id)\
                                 .filter(Position.unrealized_pnl > 0)\
                                 .order_by(Position.unrealized_pnl_pct.desc())\
                                 .limit(limit).all()
        
        return jsonify([pos.to_dict() for pos in positions])
    
    except Exception as e:
        logger.error(f"Error getting winning positions: {e}")
        return jsonify({'error': str(e)}), 500

@positions_bp.route('/losers', methods=['GET'])
def get_losing_positions():
    """Obtener posiciones perdedoras"""
    try:
        user_id = request.args.get('user_id', 'default')
        limit = request.args.get('limit', 10, type=int)
        
        portfolio = Portfolio.query.filter_by(user_id=user_id).first()
        if not portfolio:
            return jsonify({'error': 'Portfolio not found'}), 404
        
        positions = Position.query.filter_by(portfolio_id=portfolio.id)\
                                 .filter(Position.unrealized_pnl < 0)\
                                 .order_by(Position.unrealized_pnl_pct.asc())\
                                 .limit(limit).all()
        
        return jsonify([pos.to_dict() for pos in positions])
    
    except Exception as e:
        logger.error(f"Error getting losing positions: {e}")
        return jsonify({'error': str(e)}), 500

@positions_bp.route('/search', methods=['GET'])
def search_positions():
    """Buscar posiciones por ticker o nombre"""
    try:
        user_id = request.args.get('user_id', 'default')
        query = request.args.get('q', '').strip()
        
        if not query:
            return jsonify([])
        
        portfolio = Portfolio.query.filter_by(user_id=user_id).first()
        if not portfolio:
            return jsonify({'error': 'Portfolio not found'}), 404
        
        positions = Position.query.filter_by(portfolio_id=portfolio.id)\
                                 .filter(
                                     db.or_(
                                         Position.ticker.contains(query.upper()),
                                         Position.company_name.contains(query)
                                     )
                                 ).all()
        
        return jsonify([pos.to_dict() for pos in positions])
    
    except Exception as e:
        logger.error(f"Error searching positions: {e}")
        return jsonify({'error': str(e)}), 500
