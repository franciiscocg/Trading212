from app import db
from datetime import datetime

class AvailableInvestment(db.Model):
    """Modelo para inversiones disponibles en Trading212"""
    __tablename__ = 'available_investments'
    
    id = db.Column(db.Integer, primary_key=True)
    ticker = db.Column(db.String(20), nullable=False, unique=True)
    name = db.Column(db.String(200), nullable=False)
    isin = db.Column(db.String(20))
    currency = db.Column(db.String(10), default='USD')
    exchange = db.Column(db.String(50))
    type = db.Column(db.String(50))  # STOCK, ETF, etc.
    sector = db.Column(db.String(100))
    country = db.Column(db.String(100))
    current_price = db.Column(db.Float)
    current_price_eur = db.Column(db.Float)
    min_trade_quantity = db.Column(db.Integer, default=1)
    max_trade_quantity = db.Column(db.Integer, default=1000000)
    trading_hours = db.Column(db.Text)  # JSON string
    is_tradable = db.Column(db.Boolean, default=True)
    logo_url = db.Column(db.String(500))
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Índices para búsquedas rápidas
    __table_args__ = (
        db.Index('idx_ticker_name', 'ticker', 'name'),
        db.Index('idx_exchange', 'exchange'),
        db.Index('idx_sector', 'sector'),
        db.Index('idx_type', 'type'),
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'ticker': self.ticker,
            'name': self.name,
            'isin': self.isin,
            'currency': self.currency,
            'exchange': self.exchange,
            'type': self.type,
            'sector': self.sector,
            'country': self.country,
            'current_price': self.current_price,
            'current_price_eur': self.current_price_eur,
            'min_trade_quantity': self.min_trade_quantity,
            'max_trade_quantity': self.max_trade_quantity,
            'trading_hours': self.trading_hours,
            'is_tradable': self.is_tradable,
            'logo_url': self.logo_url,
            'last_updated': self.last_updated.isoformat() if self.last_updated else None
        }
