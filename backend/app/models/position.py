from app import db
from datetime import datetime

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
