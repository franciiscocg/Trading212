from flask import Blueprint, request, jsonify
from app.services.trading212_service import Trading212Service
from app.models import Portfolio, Position
from app import db
import logging

logger = logging.getLogger(__name__)
portfolio_bp = Blueprint('portfolio', __name__)

@portfolio_bp.route('/', methods=['GET'])
def get_portfolio():
    """Obtener información del portafolio"""
    try:
        user_id = request.args.get('user_id', 'default')
        
        # Intentar obtener datos reales de Trading212 primero
        from app.services.trading212_service import Trading212Service
        
        try:
            trading_service = Trading212Service()
            portfolio_data = trading_service.sync_portfolio_data(user_id)
            return jsonify(portfolio_data)
        except Exception as api_error:
            logger.warning(f"Error getting real Trading212 data: {api_error}")
            
            # Como fallback, buscar datos guardados en la base de datos
            portfolio = Portfolio.query.filter_by(user_id=user_id).first()
            
            if not portfolio:
                return jsonify({'error': 'Portfolio not found. Please configure your Trading212 API key and sync your data.'}), 404
            
            # Obtener posiciones
            positions = Position.query.filter_by(portfolio_id=portfolio.id).all()
            
            response = portfolio.to_dict()
            response['positions'] = [pos.to_dict() for pos in positions]
            
            return jsonify(response)
    
    except Exception as e:
        logger.error(f"Error getting portfolio: {e}")
        return jsonify({'error': str(e)}), 500

@portfolio_bp.route('/sync', methods=['POST'])
def sync_portfolio():
    """Sincronizar portafolio desde Trading212"""
    try:
        user_id = request.json.get('user_id', 'default') if request.json else 'default'
        
        # Inicializar servicio de Trading212
        trading212_service = Trading212Service()
        
        # Sincronizar datos (ahora maneja la base de datos internamente)
        portfolio_data = trading212_service.sync_portfolio_data(user_id)
        
        return jsonify({
            'message': 'Portfolio synchronized successfully',
            'portfolio': portfolio_data
        })
    
    except Exception as e:
        logger.error(f"Error syncing portfolio: {e}")
        return jsonify({'error': f'Failed to sync portfolio: {str(e)}'}), 500

@portfolio_bp.route('/summary', methods=['GET'])
def get_portfolio_summary():
    """Obtener resumen del portafolio"""
    try:
        user_id = request.args.get('user_id', 'default')
        
        portfolio = Portfolio.query.filter_by(user_id=user_id).first()
        if not portfolio:
            return jsonify({'error': 'Portfolio not found'}), 404
        
        positions = Position.query.filter_by(portfolio_id=portfolio.id).all()
        
        # Calcular métricas adicionales
        total_positions = len(positions)
        winning_positions = len([p for p in positions if p.unrealized_pnl > 0])
        losing_positions = len([p for p in positions if p.unrealized_pnl < 0])
        
        # Top ganadores y perdedores
        top_winners = sorted(positions, key=lambda x: x.unrealized_pnl_pct, reverse=True)[:5]
        top_losers = sorted(positions, key=lambda x: x.unrealized_pnl_pct)[:5]
        
        # Diversificación por sector (simulada)
        sectors = {}
        for pos in positions:
            sector = pos.sector or 'Unknown'
            if sector not in sectors:
                sectors[sector] = {'value': 0, 'count': 0}
            sectors[sector]['value'] += pos.market_value
            sectors[sector]['count'] += 1
        
        summary = {
            'portfolio': portfolio.to_dict(),
            'metrics': {
                'total_positions': total_positions,
                'winning_positions': winning_positions,
                'losing_positions': losing_positions,
                'win_rate': (winning_positions / total_positions * 100) if total_positions > 0 else 0
            },
            'top_winners': [pos.to_dict() for pos in top_winners],
            'top_losers': [pos.to_dict() for pos in top_losers],
            'sector_allocation': sectors
        }
        
        return jsonify(summary)
    
    except Exception as e:
        logger.error(f"Error getting portfolio summary: {e}")
        return jsonify({'error': str(e)}), 500
