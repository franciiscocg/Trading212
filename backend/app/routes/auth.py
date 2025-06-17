from flask import Blueprint, request, jsonify
import logging

logger = logging.getLogger(__name__)
auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/validate', methods=['POST'])
def validate_api_key():
    """Validar API key de Trading212"""
    try:
        api_key = request.json.get('api_key')
        
        if not api_key:
            return jsonify({'error': 'API key is required'}), 400
        
        # Probar la API key con Trading212
        from app.services.trading212_service import Trading212API
        
        try:
            # Crear instancia temporal para probar la conexión
            test_api = Trading212API(api_key=api_key)
            
            # Intentar obtener información básica de la cuenta
            account_info = test_api.get_account_info()
            
            return jsonify({
                'valid': True,
                'message': 'API key is valid and connected to Trading212',
                'account_info': {
                    'currencyCode': account_info.get('currencyCode'),
                    'id': account_info.get('id')[:8] + '...' if account_info.get('id') else None  # Partial ID for privacy
                }
            })
            
        except Exception as api_error:
            logger.warning(f"Trading212 API validation failed: {api_error}")
            return jsonify({
                'valid': False,
                'error': 'Invalid API key or connection failed',
                'details': str(api_error)
            }), 400
    
    except Exception as e:
        logger.error(f"Error validating API key: {e}")
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/status', methods=['GET'])
def get_connection_status():
    """Obtener estado de conexión con Trading212"""
    try:
        # En una implementación real, verificarías la conexión con Trading212
        return jsonify({
            'connected': True,
            'api_status': 'active',
            'last_sync': '2024-01-01T12:00:00Z'
        })
    
    except Exception as e:
        logger.error(f"Error getting connection status: {e}")
        return jsonify({'error': str(e)}), 500
