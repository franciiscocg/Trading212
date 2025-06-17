from app import db
from datetime import datetime
from sqlalchemy import func

class Portfolio(db.Model):
    """Modelo para el portafolio general"""
    __tablename__ = 'portfolios'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(100), nullable=False)
    total_value = db.Column(db.Float, default=0.0)
    cash_balance = db.Column(db.Float, default=0.0)
    invested_amount = db.Column(db.Float, default=0.0)
    unrealized_pnl = db.Column(db.Float, default=0.0)
    realized_pnl = db.Column(db.Float, default=0.0)
    currency = db.Column(db.String(10), default='EUR')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relaciones
    positions = db.relationship('Position', backref='portfolio', lazy=True, cascade='all, delete-orphan')
    transactions = db.relationship('Transaction', backref='portfolio', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'total_value': self.total_value,
            'cash_balance': self.cash_balance,
            'invested_amount': self.invested_amount,
            'unrealized_pnl': self.unrealized_pnl,
            'realized_pnl': self.realized_pnl,
            'currency': self.currency,
            'total_pnl': self.unrealized_pnl + self.realized_pnl,
            'total_return_pct': (self.unrealized_pnl + self.realized_pnl) / self.invested_amount * 100 if self.invested_amount > 0 else 0,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class Position(db.Model):
    """Modelo para posiciones individuales"""
    __tablename__ = 'positions'
    
    id = db.Column(db.Integer, primary_key=True)
    portfolio_id = db.Column(db.Integer, db.ForeignKey('portfolios.id'), nullable=False)
    ticker = db.Column(db.String(20), nullable=False)
    company_name = db.Column(db.String(200))
    quantity = db.Column(db.Float, nullable=False)
    average_price = db.Column(db.Float, nullable=False)
    current_price = db.Column(db.Float, default=0.0)
    market_value = db.Column(db.Float, default=0.0)
    unrealized_pnl = db.Column(db.Float, default=0.0)
    unrealized_pnl_pct = db.Column(db.Float, default=0.0)
    currency = db.Column(db.String(10), default='EUR')
    sector = db.Column(db.String(100))
    exchange = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relaciones
    transactions = db.relationship('Transaction', backref='position', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'ticker': self.ticker,
            'company_name': self.company_name,
            'quantity': self.quantity,
            'average_price': self.average_price,
            'current_price': self.current_price,
            'market_value': self.market_value,
            'unrealized_pnl': self.unrealized_pnl,
            'unrealized_pnl_pct': self.unrealized_pnl_pct,
            'currency': self.currency,
            'sector': self.sector,
            'exchange': self.exchange,
            'cost_basis': self.quantity * self.average_price,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class Transaction(db.Model):
    """Modelo para transacciones"""
    __tablename__ = 'transactions'
    
    id = db.Column(db.Integer, primary_key=True)
    portfolio_id = db.Column(db.Integer, db.ForeignKey('portfolios.id'), nullable=False)
    position_id = db.Column(db.Integer, db.ForeignKey('positions.id'), nullable=True)
    transaction_type = db.Column(db.String(20), nullable=False)  # BUY, SELL, DIVIDEND, etc.
    ticker = db.Column(db.String(20), nullable=False)
    quantity = db.Column(db.Float, nullable=False)
    price = db.Column(db.Float, nullable=False)
    total_amount = db.Column(db.Float, nullable=False)
    fees = db.Column(db.Float, default=0.0)
    currency = db.Column(db.String(10), default='EUR')
    transaction_date = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'transaction_type': self.transaction_type,
            'ticker': self.ticker,
            'quantity': self.quantity,
            'price': self.price,
            'total_amount': self.total_amount,
            'fees': self.fees,
            'currency': self.currency,
            'transaction_date': self.transaction_date.isoformat(),
            'created_at': self.created_at.isoformat()
        }

class PriceHistory(db.Model):
    """Modelo para historial de precios"""
    __tablename__ = 'price_history'
    
    id = db.Column(db.Integer, primary_key=True)
    ticker = db.Column(db.String(20), nullable=False)
    price = db.Column(db.Float, nullable=False)
    volume = db.Column(db.Integer, default=0)
    timestamp = db.Column(db.DateTime, nullable=False)
    
    # Índice para consultas rápidas
    __table_args__ = (db.Index('idx_ticker_timestamp', 'ticker', 'timestamp'),)
    
    def to_dict(self):
        return {
            'ticker': self.ticker,
            'price': self.price,
            'volume': self.volume,
            'timestamp': self.timestamp.isoformat()
        }
