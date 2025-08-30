import requests
import os
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class Trading212API:
    """Cliente para la API de Trading212"""
    
    def __init__(self, api_key: str = None, base_url: str = None):
        self.api_key = api_key or os.getenv('TRADING212_API_KEY')
        self.base_url = base_url or os.getenv('TRADING212_API_URL', 'https://live.trading212.com/api/v0')
        
        if not self.api_key:
            raise ValueError("API key de Trading212 es requerida")        
        self.headers = {
            'Authorization': self.api_key,
            'Content-Type': 'application/json'
        }
    
    def _make_request(self, method: str, endpoint: str, params: Dict = None, data: Dict = None) -> Dict:
        """Realizar petición HTTP a la API"""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        try:
            response = requests.request(
                method=method,
                url=url,
                headers=self.headers,
                params=params,
                json=data,
                timeout=30
            )
            
            if response.status_code == 429:
                logger.warning("Trading212 API rate limit reached")
                raise Exception("Trading212 API rate limit reached. Please wait a few minutes before trying again.")
            
            response.raise_for_status()
            return response.json()
        
        except requests.exceptions.RequestException as e:
            logger.error(f"Error en petición a Trading212: {e}")
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
    
    def get_exports(self) -> List[Dict]:
        """Obtener lista de exportaciones disponibles"""
        return self._make_request('GET', '/equity/exports')
    
    def request_export(self, data_included: Dict, time_from: datetime, time_to: datetime) -> Dict:
        """Solicitar exportación de datos"""
        data = {
            'dataIncluded': data_included,
            'timeFrom': time_from.isoformat(),
            'timeTo': time_to.isoformat()
        }
        return self._make_request('POST', '/equity/exports', data=data)

class Trading212Service:
    """Servicio para gestionar datos de Trading212"""
    
    def __init__(self):
        self.api = Trading212API()
        # Tasa de conversión USD a EUR (aproximada, actualizar según necesidad)
        self.usd_to_eur_rate = 0.927
    
    def sync_portfolio_data(self, user_id: str = 'default') -> Dict:
        """Sincronizar datos del portafolio desde Trading212"""
        try:
            from app.models import Portfolio, Position, db
            
            # Obtener información básica
            account_info = self.api.get_account_info()
            cash_info = self.api.get_account_cash()
            portfolio_positions = self.api.get_portfolio()
            
            # Calcular métricas del portafolio
            total_value = 0
            total_unrealized_pnl = 0            
            positions_data = []
            
            for position in portfolio_positions:
                # Obtener valores seguros (nunca None)
                quantity = float(position.get('quantity', 0) or 0)
                current_price = float(position.get('currentPrice', 0) or 0)
                average_price = float(position.get('averagePrice', 0) or 0)
                
                market_value = quantity * current_price * self.usd_to_eur_rate
                cost_basis = quantity * average_price * self.usd_to_eur_rate
                unrealized_pnl = market_value - cost_basis
                unrealized_pnl_pct = (unrealized_pnl / cost_basis * 100) if cost_basis > 0 else 0
                
                total_value += market_value
                total_unrealized_pnl += unrealized_pnl
                
                positions_data.append({
                    'ticker': position.get('ticker', 'UNKNOWN'),
                    'name': position.get('ticker', 'UNKNOWN'),  # Trading212 no siempre proporciona el nombre completo
                    'quantity': quantity,
                    'avg_cost': average_price * self.usd_to_eur_rate,
                    'current_price': current_price * self.usd_to_eur_rate,
                    'market_value': market_value,
                    'cost_basis': cost_basis,
                    'unrealized_pnl': unrealized_pnl,
                    'unrealized_pnl_percent': unrealized_pnl_pct,
                    'currency': 'EUR'  # Convertido a EUR
                })
            
            # Obtener cash balance de forma segura
            free_cash = float(cash_info.get('free', 0) or 0) * self.usd_to_eur_rate
            blocked_cash = float(cash_info.get('blocked', 0) or 0) * self.usd_to_eur_rate
            cash_balance = free_cash + blocked_cash
            total_portfolio_value = total_value + cash_balance
              # Actualizar o crear portafolio en la base de datos
            portfolio = Portfolio.query.filter_by(user_id=user_id).first()
            if not portfolio:
                portfolio = Portfolio(user_id=user_id)
                db.session.add(portfolio)
            
            portfolio.total_value = total_portfolio_value
            portfolio.cash_balance = cash_balance
            portfolio.invested_amount = total_value
            portfolio.unrealized_pnl = total_unrealized_pnl
            portfolio.updated_at = datetime.utcnow()  # Usar updated_at en lugar de last_updated            
            # Limpiar posiciones existentes
            Position.query.filter_by(portfolio_id=portfolio.id).delete()
            
            # Crear nuevas posiciones
            for pos_data in positions_data:
                position = Position(
                    portfolio_id=portfolio.id,
                    ticker=pos_data['ticker'],
                    company_name=pos_data['name'],  # Usar company_name en lugar de name
                    quantity=pos_data['quantity'],
                    average_price=pos_data['avg_cost'],
                    current_price=pos_data['current_price'],
                    market_value=pos_data['market_value'],
                    unrealized_pnl=pos_data['unrealized_pnl'],
                    unrealized_pnl_pct=pos_data['unrealized_pnl_percent'],  # Corregir nombre del campo
                    currency=pos_data['currency']
                )
                db.session.add(position)
            
            db.session.commit()
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
            logger.error(f"Error sincronizando portafolio: {e}")
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
