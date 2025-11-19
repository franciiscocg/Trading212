from app import db
from datetime import datetime

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
