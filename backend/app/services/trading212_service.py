import requests
import os
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import logging
import time
from functools import wraps

logger = logging.getLogger(__name__)

# Decorador para reintentos con backoff exponencial
def retry_with_backoff(max_retries=3, backoff_factor=2):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_retries - 1:
                        raise
                    if "rate limit" in str(e).lower() or "429" in str(e):
                        wait_time = backoff_factor ** attempt
                        logger.warning(f"Rate limit hit, waiting {wait_time}s before retry {attempt + 1}/{max_retries}")
                        time.sleep(wait_time)
                    else:
                        raise
            return None
        return wrapper
    return decorator

class Trading212API:
    """Cliente para la API de Trading212"""
    
    def __init__(self, api_key: str = None, base_url: str = None):
        self.api_key = api_key or os.getenv('TRADING212_API_KEY')
        self.base_url = base_url or os.getenv('TRADING212_API_URL', 'https://live.trading212.com/api/v0')
        
        if not self.api_key:
            logger.error("Trading212 API key not configured")
            raise ValueError("API key de Trading212 es requerida. Configúrala en el archivo .env como TRADING212_API_KEY")
        
        if not self.api_key.strip():
            logger.error("Trading212 API key is empty")
            raise ValueError("API key de Trading212 está vacía")
        
        self.headers = {
            'Authorization': self.api_key,
            'Content-Type': 'application/json'
        }
        logger.info(f"Trading212API initialized with base_url: {self.base_url}")
    
    @retry_with_backoff(max_retries=3, backoff_factor=2)
    def _make_request(self, method: str, endpoint: str, params: Dict = None, data: Dict = None) -> Dict:
        """Realizar petición HTTP a la API con reintentos automáticos"""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        try:
            logger.debug(f"Making {method} request to {endpoint}")
            response = requests.request(
                method=method,
                url=url,
                headers=self.headers,
                params=params,
                json=data,
                timeout=30
            )
            
            if response.status_code == 429:
                logger.warning(f"Trading212 API rate limit reached for {endpoint}")
                raise Exception("Trading212 API rate limit reached. Please wait a few minutes before trying again.")
            
            if response.status_code == 401:
                logger.error("Trading212 API authentication failed - invalid API key")
                raise Exception("API key inválida. Verifica tu configuración en Settings.")
            
            response.raise_for_status()
            logger.debug(f"Request to {endpoint} successful")
            return response.json()
        
        except requests.exceptions.Timeout:
            logger.error(f"Timeout en petición a {endpoint}")
            raise Exception(f"Timeout al conectar con Trading212. Intenta nuevamente.")
        except requests.exceptions.RequestException as e:
            logger.error(f"Error en petición a Trading212 {endpoint}: {e}")
            if "429" in str(e):
                raise Exception("Trading212 API rate limit reached. Please wait a few minutes before trying again.")
            raise Exception(f"Error connecting to Trading212: {str(e)}")
    
    def get_account_info(self) -> Dict:
        """Obtener información de la cuenta"""
        return self._make_request('GET', '/equity/account/info')
    
    def get_account_cash(self) -> Dict:
        """Obtener balance de efectivo"""
        return self._make_request('GET', '/equity/account/cash')
    
    def get_portfolio(self) -> List[Dict]:
        """Obtener todas las posiciones del portafolio"""
        return self._make_request('GET', '/equity/portfolio')
    
    def get_position(self, ticker: str) -> Optional[Dict]:
        """Obtener posición específica por ticker"""
        try:
            return self._make_request('GET', f'/equity/portfolio/{ticker}')
        except Exception:
            return None
    
    def get_orders(self, cursor: str = None, limit: int = 50) -> Dict:
        """Obtener órdenes"""
        params = {'limit': limit}
        if cursor:
            params['cursor'] = cursor
        
        return self._make_request('GET', '/equity/orders', params=params)
    
    def get_historical_orders(self, cursor: str = None, limit: int = 50) -> Dict:
        """Obtener histórico de órdenes"""
        params = {'limit': limit}
        if cursor:
            params['cursor'] = cursor
        
        return self._make_request('GET', '/equity/orders/historical', params=params)
    
    def get_dividends(self, cursor: str = None, limit: int = 50) -> Dict:
        """Obtener dividendos"""
        params = {'limit': limit}
        if cursor:
            params['cursor'] = cursor
        
        return self._make_request('GET', '/equity/dividends', params=params)
    
    def get_instruments(self, exchange: str = None, limit: int = 100) -> List[Dict]:
        """Obtener lista de instrumentos disponibles"""
        params = {'limit': limit}
        if exchange:
            params['exchange'] = exchange
        
        return self._make_request('GET', '/equity/metadata/instruments', params=params)
    
    def get_exchanges(self) -> List[Dict]:
        """Obtener lista de exchanges disponibles"""
        return self._make_request('GET', '/equity/metadata/exchanges')
    
    def search_instruments(self, query: str, limit: int = 50) -> List[Dict]:
        """Buscar instrumentos por nombre o ticker"""
        params = {'query': query, 'limit': limit}
        return self._make_request('GET', '/equity/metadata/instruments/search', params=params)

class Trading212Service:
    """Servicio para gestionar datos de Trading212"""
    
    def __init__(self):
        self.api = Trading212API()
        self._exchange_rates = None
    
    def get_exchange_rate(self, from_currency: str, to_currency: str = 'EUR') -> float:
        """Obtener tasa de cambio actualizada"""
        if from_currency == to_currency:
            return 1.0
        
        # Cachear tasas por 1 hora
        if self._exchange_rates is None:
            try:
                import requests
                response = requests.get('https://api.exchangerate-api.com/v4/latest/USD', timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    self._exchange_rates = data.get('rates', {})
                    logger.info(f"Tasas de cambio actualizadas: USD->EUR = {self._exchange_rates.get('EUR', 0.95)}")
                else:
                    logger.warning("No se pudieron obtener tasas de cambio, usando fallback")
                    self._exchange_rates = {'EUR': 0.95, 'GBP': 0.85, 'USD': 1.0}
            except Exception as e:
                logger.error(f"Error obteniendo tasas de cambio: {e}")
                # Fallback a tasas aproximadas
                self._exchange_rates = {'EUR': 0.95, 'GBP': 0.85, 'USD': 1.0}
        
        # Convertir de from_currency a USD, luego a to_currency
        if from_currency == 'USD':
            return self._exchange_rates.get(to_currency, 0.95)
        elif to_currency == 'USD':
            rate_to_usd = self._exchange_rates.get(from_currency, 1.0)
            return 1.0 / rate_to_usd if rate_to_usd > 0 else 1.0
        else:
            # Conversión indirecta via USD
            to_usd = 1.0 / self._exchange_rates.get(from_currency, 1.0)
            from_usd = self._exchange_rates.get(to_currency, 1.0)
            return to_usd * from_usd
    
    def sync_portfolio_data(self, user_id: str = 'default') -> Dict:
        """Sincronizar datos del portafolio desde Trading212"""
        try:
            from app.models import Portfolio, Position, db
            
            logger.info(f"Starting portfolio sync for user: {user_id}")
            
            # Obtener información básica
            account_info = self.api.get_account_info()
            cash_info = self.api.get_account_cash()
            portfolio_positions = self.api.get_portfolio()
            
            # Trading212 devuelve precios en USD para la mayoría de instrumentos
            # Obtener tasa de conversión USD -> EUR en tiempo real
            usd_to_eur = self.get_exchange_rate('USD', 'EUR')
            logger.info(f"Using exchange rate USD -> EUR: {usd_to_eur}")
            
            logger.info(f"Retrieved {len(portfolio_positions)} positions from Trading212")
            
            # Calcular métricas del portafolio
            total_value = 0
            total_unrealized_pnl = 0            
            positions_data = []
            
            for position in portfolio_positions:
                # Obtener valores seguros (nunca None)
                quantity = float(position.get('quantity', 0) or 0)
                current_price = float(position.get('currentPrice', 0) or 0)
                average_price = float(position.get('averagePrice', 0) or 0)
                
                # Convertir precios de USD a EUR usando tasa en tiempo real
                current_price_eur = current_price * usd_to_eur
                average_price_eur = average_price * usd_to_eur
                
                market_value = quantity * current_price_eur
                cost_basis = quantity * average_price_eur
                unrealized_pnl = market_value - cost_basis
                unrealized_pnl_pct = (unrealized_pnl / cost_basis * 100) if cost_basis > 0 else 0
                
                total_value += market_value
                total_unrealized_pnl += unrealized_pnl
                
                positions_data.append({
                    'ticker': position.get('ticker', 'UNKNOWN'),
                    'name': position.get('ticker', 'UNKNOWN'),  # Trading212 no siempre proporciona el nombre completo
                    'quantity': quantity,
                    'avg_cost': average_price_eur,
                    'current_price': current_price_eur,
                    'market_value': market_value,
                    'cost_basis': cost_basis,
                    'unrealized_pnl': unrealized_pnl,
                    'unrealized_pnl_percent': unrealized_pnl_pct,
                    'currency': 'EUR'
                })
            
            # Obtener cash balance y convertir de USD a EUR
            free_cash = float(cash_info.get('free', 0) or 0) * usd_to_eur
            blocked_cash = float(cash_info.get('blocked', 0) or 0) * usd_to_eur
            cash_balance = free_cash + blocked_cash
            total_portfolio_value = total_value + cash_balance
              # Actualizar o crear portafolio en la base de datos
            portfolio = Portfolio.query.filter_by(user_id=user_id).first()
            if not portfolio:
                logger.info(f"Creating new portfolio for user: {user_id}")
                portfolio = Portfolio(user_id=user_id)
                db.session.add(portfolio)
            else:
                logger.info(f"Updating existing portfolio for user: {user_id}")
            
            portfolio.total_value = total_portfolio_value
            portfolio.cash_balance = cash_balance
            portfolio.invested_amount = total_value
            portfolio.unrealized_pnl = total_unrealized_pnl
            portfolio.updated_at = datetime.utcnow()
            
            # Actualización incremental de posiciones en lugar de borrar todo
            existing_positions = {pos.ticker: pos for pos in Position.query.filter_by(portfolio_id=portfolio.id).all()}
            
            current_tickers = set()
            for pos_data in positions_data:
                ticker = pos_data['ticker']
                current_tickers.add(ticker)
                
                if ticker in existing_positions:
                    # Actualizar posición existente
                    position = existing_positions[ticker]
                    position.quantity = pos_data['quantity']
                    position.average_price = pos_data['avg_cost']
                    position.current_price = pos_data['current_price']
                    position.market_value = pos_data['market_value']
                    position.unrealized_pnl = pos_data['unrealized_pnl']
                    position.unrealized_pnl_pct = pos_data['unrealized_pnl_percent']
                    position.updated_at = datetime.utcnow()
                    logger.debug(f"Updated position: {ticker}")
                else:
                    # Crear nueva posición
                    position = Position(
                        portfolio_id=portfolio.id,
                        ticker=ticker,
                        company_name=pos_data['name'],
                        quantity=pos_data['quantity'],
                        average_price=pos_data['avg_cost'],
                        current_price=pos_data['current_price'],
                        market_value=pos_data['market_value'],
                        unrealized_pnl=pos_data['unrealized_pnl'],
                        unrealized_pnl_pct=pos_data['unrealized_pnl_percent'],
                        currency=pos_data['currency']
                    )
                    db.session.add(position)
                    logger.debug(f"Created new position: {ticker}")
            
            # Eliminar posiciones que ya no existen
            for ticker, position in existing_positions.items():
                if ticker not in current_tickers:
                    logger.info(f"Removing closed position: {ticker}")
                    db.session.delete(position)
            
            db.session.commit()
            logger.info(f"Portfolio sync completed successfully for user: {user_id}")
            # Preparar respuesta
            response_data = {
                'id': portfolio.id,
                'user_id': user_id,
                'total_value': total_portfolio_value,
                'cash_balance': cash_balance,
                'invested_amount': total_value,
                'unrealized_pnl': total_unrealized_pnl,
                'total_return_percent': (total_unrealized_pnl / total_value * 100) if total_value > 0 else 0,
                'last_updated': portfolio.updated_at.isoformat(),  # Usar updated_at
                'positions': positions_data,
                'account_info': account_info
            }
            
            return response_data
        
        except Exception as e:
            logger.error(f"Error sincronizando portafolio para user {user_id}: {e}", exc_info=True)
            db.session.rollback()
            raise
    
    def sync_transaction_history(self, days_back: int = 30) -> List[Dict]:
        """Sincronizar historial de transacciones"""
        try:
            transactions = []
            
            # Obtener órdenes históricas
            historical_orders = self.api.get_historical_orders(limit=200)
            orders = historical_orders.get('items', [])
            
            for order in orders:
                if order.get('status') == 'FILLED':
                    transactions.append({
                        'type': 'TRADE',
                        'side': order.get('side'),  # BUY/SELL
                        'ticker': order.get('ticker'),
                        'quantity': order.get('quantity'),
                        'price': order.get('fillPrice'),
                        'total_amount': order.get('fillResult', {}).get('fillCost', 0),
                        'fees': order.get('fillResult', {}).get('fees', {}).get('fillCostCommission', 0),
                        'date': order.get('dateCreated')
                    })
            
            # Obtener dividendos
            dividends = self.api.get_dividends(limit=100)
            dividend_items = dividends.get('items', [])
            
            for dividend in dividend_items:
                transactions.append({
                    'type': 'DIVIDEND',
                    'ticker': dividend.get('ticker'),
                    'amount': dividend.get('amount'),
                    'date': dividend.get('paidOn')
                })
            
            return transactions
        
        except Exception as e:
            logger.error(f"Error sincronizando transacciones: {e}")
            raise
    
    def sync_available_investments_to_db(self):
        """Sincronizar todas las inversiones disponibles a la base de datos"""
        try:
            from app.models import AvailableInvestment, db
            
            logger.info("Starting sync of available investments to database...")
            
            # Obtener exchanges primero
            exchanges_data = self.api.get_exchanges()
            exchange_map = {ex['id']: ex['name'] for ex in exchanges_data}
            
            # Obtener todas las inversiones disponibles (sin límite para sincronización completa)
            instruments = self.api.get_instruments(limit=5000)  # Máximo razonable
            
            synced_count = 0
            updated_count = 0
            
            for instrument in instruments:
                # Limpiar el ticker (remover sufijos como _US_EQ)
                raw_ticker = instrument.get('ticker', '')
                clean_ticker = raw_ticker.split('_')[0] if '_' in raw_ticker else raw_ticker
                
                # Intentar determinar el exchange basado en el ticker
                exchange_name = self._guess_exchange_from_ticker(clean_ticker)
                
                # Verificar si ya existe
                existing = AvailableInvestment.query.filter_by(ticker=clean_ticker).first()
                
                # Generar URL del logo usando Clearbit (sin verificación síncrona)
                # El frontend puede manejar la verificación lazy o usar un placeholder si falla
                logo_url = f"https://logo.clearbit.com/{clean_ticker.lower()}.com" if clean_ticker else None
                
                if existing:
                    # Actualizar
                    existing.name = instrument.get('name', '')
                    existing.isin = instrument.get('isin', '')
                    existing.currency = instrument.get('currencyCode', 'EUR')
                    existing.exchange = exchange_name
                    existing.type = instrument.get('type', '')
                    existing.current_price = float(instrument.get('maxOpenQuantity', 0) or 0)
                    existing.current_price_eur = float(instrument.get('maxOpenQuantity', 0) or 0)
                    existing.min_trade_quantity = 1
                    existing.max_trade_quantity = int(instrument.get('maxOpenQuantity', 1000000) or 1000000)
                    existing.is_tradable = True
                    existing.logo_url = logo_url
                    existing.last_updated = datetime.utcnow()
                    updated_count += 1
                else:
                    # Crear nuevo
                    new_investment = AvailableInvestment(
                        ticker=clean_ticker,
                        name=instrument.get('name', ''),
                        isin=instrument.get('isin', ''),
                        currency=instrument.get('currencyCode', 'EUR'),
                        exchange=exchange_name,
                        type=instrument.get('type', ''),
                        current_price=float(instrument.get('maxOpenQuantity', 0) or 0),
                        current_price_eur=float(instrument.get('maxOpenQuantity', 0) or 0),
                        min_trade_quantity=1,
                        max_trade_quantity=int(instrument.get('maxOpenQuantity', 1000000) or 1000000),
                        is_tradable=True,
                        logo_url=logo_url
                    )
                    db.session.add(new_investment)
                    synced_count += 1
            
            db.session.commit()
            logger.info(f"Sync completed: {synced_count} new investments, {updated_count} updated")
            
            return {
                'synced': synced_count,
                'updated': updated_count,
                'total': len(instruments)
            }
        
        except Exception as e:
            logger.error(f"Error syncing available investments to database: {e}")
            db.session.rollback()
            raise
    
    def _guess_exchange_from_ticker(self, ticker):
        """Intentar determinar el exchange basado en el ticker"""
        if not ticker:
            return 'UNKNOWN'
        
        ticker_upper = ticker.upper()
        
        # Exchanges comunes basados en sufijos o patrones conocidos
        if ticker_upper.endswith('.L'):
            return 'LSE'
        elif ticker_upper.endswith('.DE'):
            return 'XETRA'
        elif ticker_upper.endswith('.PA'):
            return 'EURONEXT'
        elif ticker_upper.endswith('.MI'):
            return 'BORSA_ITALIANA'
        elif ticker_upper.endswith('.AS'):
            return 'EURONEXT'
        elif ticker_upper.endswith('.BR'):
            return 'EURONEXT'
        elif ticker_upper.endswith('.OL'):
            return 'OSLO'
        elif ticker_upper.endswith('.ST'):
            return 'NASDAQ_OMX'
        elif ticker_upper.endswith('.HE'):
            return 'HELSINKI'
        elif ticker_upper.endswith('.CO'):
            return 'NASDAQ_OMX'
        elif ticker_upper.endswith('.LS'):
            return 'EURONEXT'
        elif len(ticker) <= 4 and ticker_upper.isalpha():
            return 'NYSE'  # Asumir NYSE para tickers cortos alfabéticos
        else:
            return 'NASDAQ'  # Default para tickers más largos
    
    def get_available_investments_from_db(self, exchange=None, limit=100, offset=0, search=None):
        """Obtener inversiones disponibles desde la base de datos"""
        try:
            from app.models import AvailableInvestment
            from app import db
            
            query = AvailableInvestment.query
            
            # Filtros
            if exchange:
                query = query.filter(AvailableInvestment.exchange == exchange)
            
            if search:
                search_term = f"%{search}%"
                query = query.filter(
                    db.or_(
                        AvailableInvestment.ticker.ilike(search_term),
                        AvailableInvestment.name.ilike(search_term)
                    )
                )
            
            # Ordenar por nombre
            query = query.order_by(AvailableInvestment.name)
            
            # Paginación
            total = query.count()
            investments = query.offset(offset).limit(limit).all()
            
            return {
                'instruments': [inv.to_dict() for inv in investments],
                'total': total,
                'page': offset // limit + 1,
                'limit': limit,
                'offset': offset,
                'has_more': offset + limit < total
            }
        
        except Exception as e:
            logger.error(f"Error getting available investments from database: {e}")
            raise
    
    def get_exchanges_from_db(self):
        """Obtener lista de exchanges desde la base de datos"""
        try:
            from app.models import AvailableInvestment
            from app import db
            
            exchanges = db.session.query(
                AvailableInvestment.exchange,
                db.func.count(AvailableInvestment.id).label('count')
            ).group_by(AvailableInvestment.exchange).all()
            
            return [
                {'code': exchange, 'name': exchange, 'count': count}
                for exchange, count in exchanges if exchange
            ]
        
        except Exception as e:
            logger.error(f"Error getting exchanges from database: {e}")
            raise
    
    def search_available_instruments(self, query: str, limit: int = 50) -> List[Dict]:
        """Buscar instrumentos disponibles por nombre o ticker"""
        try:
            return self.api.search_instruments(query=query, limit=limit)
        except Exception as e:
            logger.error(f"Error searching instruments: {e}")
            raise
