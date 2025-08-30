from flask import Blueprint, request, jsonify
from app.services.trading212_service import Trading212Service
import logging

logger = logging.getLogger(__name__)
investments_bp = Blueprint('investments', __name__)

@investments_bp.route('/health', methods=['GET'])
def health_check():
    """Verificar el estado de la API y servicios"""
    try:
        trading_service = Trading212Service()
        
        # Verificar caché
        cache_stats = trading_service.get_cache_stats()
        
        # Intentar una llamada simple para verificar conectividad
        try:
            # Solo verificar si podemos hacer una llamada, no necesitamos los datos
            test_call = trading_service.api._make_request('GET', '/equity/account/info')
            api_status = 'healthy'
        except Exception as e:
            if 'rate limit' in str(e).lower():
                api_status = 'rate_limited'
            else:
                api_status = 'error'
        
        return jsonify({
            'status': 'healthy',
            'api_status': api_status,
            'cache': cache_stats,
            'rate_limiting': {
                'last_request_time': trading_service.api.last_request_time,
                'request_count': trading_service.api.request_count,
                'max_requests_per_window': trading_service.api.max_requests_per_window,
                'rate_limit_window': trading_service.api.rate_limit_window
            }
        })
    
    except Exception as e:
        logger.error(f"Error en health check: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@investments_bp.route('/available', methods=['GET'])
def get_available_investments():
    """Obtener lista de inversiones disponibles con paginación desde la base de datos"""
    try:
        user_id = request.args.get('user_id', 'default')
        exchange = request.args.get('exchange')
        limit = min(int(request.args.get('limit', 50)), 200)  # Máximo 200 por página
        offset = int(request.args.get('offset', 0))
        
        trading_service = Trading212Service()
        
        # Intentar obtener desde la base de datos primero
        try:
            result = trading_service.get_available_investments_from_db(
                exchange=exchange, 
                limit=limit, 
                offset=offset
            )
            
            # Si no hay resultados en la base de datos, intentar sincronizar
            if result['total'] == 0:
                logger.info("No investments found in database, attempting to sync...")
                sync_result = trading_service.sync_available_investments_to_db()
                logger.info(f"Sync completed: {sync_result}")
                
                # Reintentar obtener desde la base de datos
                result = trading_service.get_available_investments_from_db(
                    exchange=exchange, 
                    limit=limit, 
                    offset=offset
                )
            
            return jsonify(result)
            
        except Exception as db_error:
            logger.warning(f"Database query failed, falling back to API: {db_error}")
            # Fallback a la API si la base de datos falla
            instruments = trading_service.get_available_instruments(
                exchange=exchange, 
                limit=limit + offset + 100  # Obtener más para paginación
            )
            
            # Aplicar paginación en el servidor
            paginated_instruments = instruments[offset:offset + limit]
            total_count = len(instruments)
            
            return jsonify({
                'instruments': paginated_instruments,
                'total': total_count,
                'page': offset // limit + 1,
                'limit': limit,
                'offset': offset,
                'has_more': offset + limit < total_count,
                'source': 'api_fallback'
            })
    
    except Exception as e:
        logger.error(f"Error obteniendo inversiones disponibles: {e}")
        return jsonify({'error': f'Failed to get available investments: {str(e)}'}), 500

@investments_bp.route('/search', methods=['GET'])
def search_investments():
    """Buscar inversiones por nombre o ticker desde la base de datos"""
    try:
        query = request.args.get('q', '')
        limit = int(request.args.get('limit', 50))
        
        if not query:
            return jsonify({'error': 'Query parameter is required'}), 400
        
        trading_service = Trading212Service()
        
        # Intentar buscar en la base de datos primero
        try:
            result = trading_service.get_available_investments_from_db(
                search=query, 
                limit=limit
            )
            
            # Si no hay resultados, intentar sincronizar y buscar nuevamente
            if result['total'] == 0:
                logger.info("No search results found in database, attempting to sync...")
                sync_result = trading_service.sync_available_investments_to_db()
                logger.info(f"Sync completed: {sync_result}")
                
                # Reintentar búsqueda
                result = trading_service.get_available_investments_from_db(
                    search=query, 
                    limit=limit
                )
            
            return jsonify(result)
            
        except Exception as db_error:
            logger.warning(f"Database search failed, falling back to API: {db_error}")
            # Fallback a la API
            instruments = trading_service.search_available_instruments(query=query, limit=limit)
            
            return jsonify({
                'instruments': instruments,
                'total': len(instruments),
                'query': query,
                'limit': limit,
                'source': 'api_fallback'
            })
    
    except Exception as e:
        logger.error(f"Error buscando inversiones: {e}")
        return jsonify({'error': f'Failed to search investments: {str(e)}'}), 500

@investments_bp.route('/exchanges', methods=['GET'])
def get_exchanges():
    """Obtener lista de exchanges disponibles desde la base de datos"""
    try:
        trading_service = Trading212Service()
        
        # Intentar obtener desde la base de datos primero
        try:
            exchanges = trading_service.get_exchanges_from_db()
            
            # Si no hay exchanges en la base de datos, intentar sincronizar
            if not exchanges:
                logger.info("No exchanges found in database, attempting to sync...")
                sync_result = trading_service.sync_available_investments_to_db()
                logger.info(f"Sync completed: {sync_result}")
                
                # Reintentar obtener exchanges
                exchanges = trading_service.get_exchanges_from_db()
            
            return jsonify({
                'exchanges': exchanges,
                'total': len(exchanges)
            })
            
        except Exception as db_error:
            logger.warning(f"Database query failed, falling back to API: {db_error}")
            # Fallback a la API
            exchanges = trading_service.get_exchanges()
            
            return jsonify({
                'exchanges': exchanges,
                'total': len(exchanges),
                'source': 'api_fallback'
            })
    
    except Exception as e:
        logger.error(f"Error obteniendo exchanges: {e}")
        # En caso de rate limit, devolver una respuesta especial
        if 'rate limit' in str(e).lower():
            return jsonify({
                'error': 'RATE_LIMIT',
                'message': 'Se ha alcanzado el límite de velocidad de la API. Los datos se cargarán desde el caché si están disponibles.',
                'cached': True
            }), 429
        return jsonify({'error': f'Failed to get exchanges: {str(e)}'}), 500
@investments_bp.route('/sync', methods=['POST'])
def sync_investments():
    """Sincronizar inversiones disponibles desde Trading212 a la base de datos"""
    try:
        trading_service = Trading212Service()
        result = trading_service.sync_available_investments_to_db()
        
        return jsonify({
            'message': 'Investments sync completed successfully',
            'synced': result['synced'],
            'updated': result['updated'],
            'total_processed': result['total']
        })
    
    except Exception as e:
        logger.error(f"Error syncing investments: {e}")
        return jsonify({'error': f'Failed to sync investments: {str(e)}'}), 500
