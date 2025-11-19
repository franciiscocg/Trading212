from flask import Blueprint, request, jsonify
import logging
from datetime import datetime, timedelta
from app.models import Strategy, Portfolio
from app.services.strategy_analyzer import StrategyAnalyzer
from app import db

logger = logging.getLogger(__name__)
strategy_bp = Blueprint('strategy', __name__)

# Inicializar el analizador de estrategias
strategy_analyzer = StrategyAnalyzer()


@strategy_bp.route('/generate', methods=['POST'])
def generate_strategy():
    """
    Generar una nueva estrategia de inversión automatizada
    
    Request Body:
    {
        "user_id": "default",
        "timeframe_weeks": 2,  // 1 o 2 semanas
        "risk_tolerance": "MODERATE"  // CONSERVATIVE, MODERATE, AGGRESSIVE
    }
    """
    try:
        data = request.get_json()
        user_id = data.get('user_id', 'default')
        timeframe_weeks = data.get('timeframe_weeks', 2)
        risk_tolerance = data.get('risk_tolerance', 'MODERATE').upper()
        
        # Validar parámetros
        if timeframe_weeks not in [1, 2]:
            return jsonify({
                'error': 'Invalid timeframe',
                'message': 'El horizonte temporal debe ser 1 o 2 semanas'
            }), 400
        
        if risk_tolerance not in ['CONSERVATIVE', 'MODERATE', 'AGGRESSIVE']:
            return jsonify({
                'error': 'Invalid risk tolerance',
                'message': 'La tolerancia al riesgo debe ser CONSERVATIVE, MODERATE o AGGRESSIVE'
            }), 400
        
        logger.info(f"📊 Generando estrategia para user {user_id}, timeframe: {timeframe_weeks} semanas, risk: {risk_tolerance}")
        
        # Generar estrategia usando el analizador
        strategy_json = strategy_analyzer.generate_winning_strategy(
            user_id=user_id,
            timeframe_weeks=timeframe_weeks,
            risk_tolerance=risk_tolerance
        )
        
        # Guardar estrategia en la base de datos
        target_end_date = datetime.utcnow() + timedelta(weeks=timeframe_weeks)
        
        new_strategy = Strategy(
            user_id=user_id,
            strategy_json=strategy_json,
            status='PENDING',
            risk_level=risk_tolerance,
            timeframe_weeks=timeframe_weeks,
            target_return_min=strategy_json.get('expected_return_range', [0, 0])[0],
            target_return_max=strategy_json.get('expected_return_range', [0, 0])[1],
            target_end_date=target_end_date
        )
        
        db.session.add(new_strategy)
        db.session.commit()
        
        logger.info(f"✅ Estrategia guardada con ID {new_strategy.id}")
        
        return jsonify({
            'success': True,
            'strategy_id': new_strategy.id,
            'strategy': new_strategy.to_dict(),
            'message': 'Estrategia generada exitosamente'
        })
        
    except Exception as e:
        logger.error(f"❌ Error generando estrategia: {e}", exc_info=True)
        db.session.rollback()
        return jsonify({
            'error': str(e),
            'message': 'Error generando la estrategia de inversión'
        }), 500


@strategy_bp.route('/history', methods=['GET'])
def get_strategy_history():
    """
    Obtener historial de estrategias del usuario
    
    Query params:
    - user_id: ID del usuario (default: 'default')
    - status: Filtrar por status (opcional)
    - limit: Límite de resultados (default: 10)
    """
    try:
        user_id = request.args.get('user_id', 'default')
        status = request.args.get('status')
        limit = int(request.args.get('limit', 10))
        
        # Construir query
        query = Strategy.query.filter_by(user_id=user_id)
        
        if status:
            query = query.filter_by(status=status.upper())
        
        # Ordenar por más reciente primero
        strategies = query.order_by(Strategy.created_at.desc()).limit(limit).all()
        
        return jsonify({
            'success': True,
            'count': len(strategies),
            'strategies': [s.to_dict() for s in strategies]
        })
        
    except Exception as e:
        logger.error(f"❌ Error obteniendo historial de estrategias: {e}")
        return jsonify({
            'error': str(e),
            'message': 'Error obteniendo historial de estrategias'
        }), 500


@strategy_bp.route('/<int:strategy_id>', methods=['GET'])
def get_strategy(strategy_id):
    """Obtener una estrategia específica por ID"""
    try:
        strategy = Strategy.query.get(strategy_id)
        
        if not strategy:
            return jsonify({
                'error': 'Strategy not found',
                'message': f'No se encontró la estrategia con ID {strategy_id}'
            }), 404
        
        return jsonify({
            'success': True,
            'strategy': strategy.to_dict()
        })
        
    except Exception as e:
        logger.error(f"❌ Error obteniendo estrategia {strategy_id}: {e}")
        return jsonify({
            'error': str(e),
            'message': 'Error obteniendo la estrategia'
        }), 500


@strategy_bp.route('/<int:strategy_id>', methods=['PATCH'])
def update_strategy_status():
    """
    Actualizar el status de una estrategia
    
    Request Body:
    {
        "status": "ACTIVE"  // PENDING, ACTIVE, COMPLETED, CANCELLED
    }
    """
    try:
        strategy_id = request.view_args['strategy_id']
        data = request.get_json()
        new_status = data.get('status', '').upper()
        
        # Validar status
        valid_statuses = ['PENDING', 'ACTIVE', 'COMPLETED', 'CANCELLED']
        if new_status not in valid_statuses:
            return jsonify({
                'error': 'Invalid status',
                'message': f'El status debe ser uno de: {", ".join(valid_statuses)}'
            }), 400
        
        # Buscar estrategia
        strategy = Strategy.query.get(strategy_id)
        if not strategy:
            return jsonify({
                'error': 'Strategy not found',
                'message': f'No se encontró la estrategia con ID {strategy_id}'
            }), 404
        
        # Actualizar status
        old_status = strategy.status
        strategy.status = new_status
        
        # Si se completa, guardar timestamp
        if new_status == 'COMPLETED':
            strategy.completed_at = datetime.utcnow()
            
            # Opcionalmente, actualizar métricas de rendimiento real
            actual_performance = data.get('actual_performance')
            if actual_performance:
                strategy.actual_return = actual_performance.get('return')
                strategy.positions_executed = actual_performance.get('positions_executed', 0)
                strategy.positions_profitable = actual_performance.get('positions_profitable', 0)
        
        db.session.commit()
        
        logger.info(f"✅ Estrategia {strategy_id} actualizada: {old_status} -> {new_status}")
        
        return jsonify({
            'success': True,
            'strategy': strategy.to_dict(),
            'message': f'Estrategia actualizada a {new_status}'
        })
        
    except Exception as e:
        logger.error(f"❌ Error actualizando estrategia {strategy_id}: {e}")
        db.session.rollback()
        return jsonify({
            'error': str(e),
            'message': 'Error actualizando la estrategia'
        }), 500


@strategy_bp.route('/active', methods=['GET'])
def get_active_strategy():
    """
    Obtener la estrategia activa actual del usuario
    
    Query params:
    - user_id: ID del usuario (default: 'default')
    """
    try:
        user_id = request.args.get('user_id', 'default')
        
        # Buscar estrategia activa
        strategy = Strategy.query.filter_by(
            user_id=user_id,
            status='ACTIVE'
        ).order_by(Strategy.created_at.desc()).first()
        
        if not strategy:
            return jsonify({
                'success': True,
                'strategy': None,
                'message': 'No hay estrategia activa'
            })
        
        return jsonify({
            'success': True,
            'strategy': strategy.to_dict()
        })
        
    except Exception as e:
        logger.error(f"❌ Error obteniendo estrategia activa: {e}")
        return jsonify({
            'error': str(e),
            'message': 'Error obteniendo estrategia activa'
        }), 500


@strategy_bp.route('/stats', methods=['GET'])
def get_strategy_stats():
    """
    Obtener estadísticas de estrategias del usuario
    
    Query params:
    - user_id: ID del usuario (default: 'default')
    """
    try:
        user_id = request.args.get('user_id', 'default')
        
        # Contar estrategias por status
        total = Strategy.query.filter_by(user_id=user_id).count()
        pending = Strategy.query.filter_by(user_id=user_id, status='PENDING').count()
        active = Strategy.query.filter_by(user_id=user_id, status='ACTIVE').count()
        completed = Strategy.query.filter_by(user_id=user_id, status='COMPLETED').count()
        cancelled = Strategy.query.filter_by(user_id=user_id, status='CANCELLED').count()
        
        # Calcular tasa de éxito (estrategias completadas con retorno positivo)
        completed_strategies = Strategy.query.filter_by(
            user_id=user_id,
            status='COMPLETED'
        ).all()
        
        successful_count = len([s for s in completed_strategies if s.actual_return and s.actual_return > 0])
        success_rate = (successful_count / completed) * 100 if completed > 0 else 0
        
        # Retorno promedio de estrategias completadas
        avg_return = None
        if completed_strategies:
            returns = [s.actual_return for s in completed_strategies if s.actual_return is not None]
            if returns:
                avg_return = sum(returns) / len(returns)
        
        return jsonify({
            'success': True,
            'stats': {
                'total_strategies': total,
                'by_status': {
                    'pending': pending,
                    'active': active,
                    'completed': completed,
                    'cancelled': cancelled
                },
                'success_rate': round(success_rate, 2),
                'avg_return': round(avg_return, 2) if avg_return else None,
                'successful_strategies': successful_count
            }
        })
        
    except Exception as e:
        logger.error(f"❌ Error obteniendo estadísticas de estrategias: {e}")
        return jsonify({
            'error': str(e),
            'message': 'Error obteniendo estadísticas'
        }), 500
