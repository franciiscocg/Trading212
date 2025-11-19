from app import db
from datetime import datetime

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
