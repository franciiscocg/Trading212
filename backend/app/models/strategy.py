from app import db
from datetime import datetime

class Strategy(db.Model):
    """Modelo para estrategias de inversión generadas"""
    __tablename__ = 'strategies'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(100), nullable=False)
    strategy_json = db.Column(db.JSON, nullable=False)  # Estrategia completa en JSON
    status = db.Column(db.String(20), default='PENDING')  # PENDING, ACTIVE, COMPLETED, CANCELLED
    risk_level = db.Column(db.String(20))  # CONSERVATIVE, MODERATE, AGGRESSIVE
    timeframe_weeks = db.Column(db.Integer, default=2)  # Horizonte temporal en semanas
    target_return_min = db.Column(db.Float)  # Retorno esperado mínimo %
    target_return_max = db.Column(db.Float)  # Retorno esperado máximo %
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    target_end_date = db.Column(db.DateTime, nullable=True)
    completed_at = db.Column(db.DateTime, nullable=True)
    
    # Métricas de rendimiento real (cuando la estrategia se completa)
    actual_return = db.Column(db.Float, nullable=True)
    positions_executed = db.Column(db.Integer, default=0)
    positions_profitable = db.Column(db.Integer, default=0)
    
    def to_dict(self):
        """Convertir estrategia a diccionario"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'strategy': self.strategy_json,
            'status': self.status,
            'risk_level': self.risk_level,
            'timeframe_weeks': self.timeframe_weeks,
            'target_return_range': [self.target_return_min, self.target_return_max] if self.target_return_min else None,
            'created_at': self.created_at.isoformat(),
            'target_end_date': self.target_end_date.isoformat() if self.target_end_date else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'actual_performance': {
                'return': self.actual_return,
                'positions_executed': self.positions_executed,
                'positions_profitable': self.positions_profitable,
                'success_rate': (self.positions_profitable / self.positions_executed * 100) if self.positions_executed > 0 else None
            } if self.actual_return is not None else None
        }
    
    def __repr__(self):
        return f'<Strategy {self.id} - {self.status} - {self.user_id}>'
