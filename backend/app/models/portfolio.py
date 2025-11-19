from app import db
from datetime import datetime

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
