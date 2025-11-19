from flask import Blueprint, request, jsonify
from app.models import Portfolio, Position, Transaction
from app import db
from datetime import datetime, timedelta
import pandas as pd
import json
import logging

logger = logging.getLogger(__name__)
analytics_bp = Blueprint('analytics', __name__)

@analytics_bp.route('/performance', methods=['GET'])
def get_performance_metrics():
    """Obtener métricas de rendimiento"""
    try:
        user_id = request.args.get('user_id', 'default')
        days = request.args.get('days', 30, type=int)
        
        portfolio = Portfolio.query.filter_by(user_id=user_id).first()
        if not portfolio:
            return jsonify({'error': 'Portfolio not found'}), 404
        
        positions = Position.query.filter_by(portfolio_id=portfolio.id).all()
        
        # Métricas básicas
        total_positions = len(positions)
        winning_positions = len([p for p in positions if p.unrealized_pnl > 0])
        losing_positions = len([p for p in positions if p.unrealized_pnl < 0])
          # Calcular métricas de riesgo
        position_values = [p.market_value for p in positions]
        total_value = sum(position_values) if position_values else 0
        
        # Concentración (HHI - Herfindahl-Hirschman Index)
        if total_value > 0:
            concentrations = [(value / total_value) ** 2 for value in position_values]
            hhi = sum(concentrations) * 10000  # Multiplicar por 10000 para escala estándar
        else:
            hhi = 0
        
        # Diversificación por sector
        sector_allocation = {}
        for pos in positions:
            sector = pos.sector or 'Unknown'
            if sector not in sector_allocation:
                sector_allocation[sector] = 0
            sector_allocation[sector] += pos.market_value
        
        # Beta del portafolio (simulado)
        portfolio_beta = 1.0  # En una implementación real, calcularías esto con datos históricos
        
        metrics = {
            'total_value': portfolio.total_value,
            'unrealized_pnl': portfolio.unrealized_pnl,
            'realized_pnl': portfolio.realized_pnl,
            'total_pnl': portfolio.unrealized_pnl + portfolio.realized_pnl,
            'total_return_pct': (portfolio.unrealized_pnl + portfolio.realized_pnl) / portfolio.invested_amount * 100 if portfolio.invested_amount > 0 else 0,
            'positions_count': total_positions,
            'winning_positions': winning_positions,
            'losing_positions': losing_positions,
            'win_rate': (winning_positions / total_positions * 100) if total_positions > 0 else 0,
            'concentration_index': hhi,
            'sector_allocation': sector_allocation,
            'portfolio_beta': portfolio_beta,
            'cash_percentage': (portfolio.cash_balance / portfolio.total_value * 100) if portfolio.total_value > 0 else 0
        }
        
        return jsonify(metrics)
    
    except Exception as e:
        logger.error(f"Error getting performance metrics: {e}")
        return jsonify({'error': str(e)}), 500

@analytics_bp.route('/allocation', methods=['GET'])
def get_allocation_analysis():
    """Análisis de asignación del portafolio"""
    try:
        user_id = request.args.get('user_id', 'default')
        
        portfolio = Portfolio.query.filter_by(user_id=user_id).first()
        if not portfolio:
            return jsonify({'error': 'Portfolio not found'}), 404
        
        positions = Position.query.filter_by(portfolio_id=portfolio.id).all()
        
        # Asignación por posición
        position_allocation = []
        for pos in positions:
            percentage = (pos.market_value / portfolio.total_value * 100) if portfolio.total_value > 0 else 0
            position_allocation.append({
                'ticker': pos.ticker,
                'company_name': pos.company_name,
                'value': pos.market_value,
                'percentage': percentage,
                'unrealized_pnl': pos.unrealized_pnl,
                'unrealized_pnl_pct': pos.unrealized_pnl_pct
            })
        
        # Ordenar por valor
        position_allocation.sort(key=lambda x: x['value'], reverse=True)
        
        # Top 10 posiciones
        top_holdings = position_allocation[:10]
        
        # Asignación por sector
        sector_allocation = {}
        for pos in positions:
            sector = pos.sector or 'Unknown'
            if sector not in sector_allocation:
                sector_allocation[sector] = {'value': 0, 'count': 0, 'positions': []}
            
            sector_allocation[sector]['value'] += pos.market_value
            sector_allocation[sector]['count'] += 1
            sector_allocation[sector]['positions'].append(pos.ticker)
        
        # Convertir a lista y agregar porcentajes
        sector_list = []
        for sector, data in sector_allocation.items():
            percentage = (data['value'] / portfolio.total_value * 100) if portfolio.total_value > 0 else 0
            sector_list.append({
                'sector': sector,
                'value': data['value'],
                'percentage': percentage,
                'count': data['count'],
                'positions': data['positions']
            })
        
        sector_list.sort(key=lambda x: x['value'], reverse=True)
        
        allocation = {
            'total_positions': len(positions),
            'total_value': portfolio.total_value,
            'cash_balance': portfolio.cash_balance,
            'cash_percentage': (portfolio.cash_balance / portfolio.total_value * 100) if portfolio.total_value > 0 else 0,
            'top_holdings': top_holdings,
            'sector_allocation': sector_list,
            'position_allocation': position_allocation
        }
        
        return jsonify(allocation)
    
    except Exception as e:
        logger.error(f"Error getting allocation analysis: {e}")
        return jsonify({'error': str(e)}), 500

@analytics_bp.route('/risk', methods=['GET'])
def get_risk_metrics():
    """Métricas de riesgo del portafolio"""
    try:
        user_id = request.args.get('user_id', 'default')
        
        portfolio = Portfolio.query.filter_by(user_id=user_id).first()
        if not portfolio:
            return jsonify({'error': 'Portfolio not found'}), 404
        
        positions = Position.query.filter_by(portfolio_id=portfolio.id).all()
        
        if not positions:
            return jsonify({
                'concentration_risk': 0,
                'sector_concentration': {},
                'largest_position_pct': 0,
                'top_5_concentration': 0,
                'risk_level': 'LOW'
            })
        
        # Calcular concentraciones
        position_values = [p.market_value for p in positions]
        total_value = sum(position_values)
        
        position_percentages = [(value / total_value * 100) for value in position_values]
        position_percentages.sort(reverse=True)
        
        # Métricas de concentración
        largest_position_pct = position_percentages[0] if position_percentages else 0
        top_5_concentration = sum(position_percentages[:5])
        
        # Índice de concentración HHI
        hhi = sum([(pct / 100) ** 2 for pct in position_percentages]) * 10000
        
        # Concentración por sector
        sector_values = {}
        for pos in positions:
            sector = pos.sector or 'Unknown'
            if sector not in sector_values:
                sector_values[sector] = 0
            sector_values[sector] += pos.market_value
        
        sector_concentrations = {}
        for sector, value in sector_values.items():
            sector_concentrations[sector] = (value / total_value * 100)
        
        # Evaluar nivel de riesgo
        risk_level = 'LOW'
        if largest_position_pct > 20 or hhi > 2500:
            risk_level = 'HIGH'
        elif largest_position_pct > 10 or hhi > 1500:
            risk_level = 'MEDIUM'
        
        risk_metrics = {
            'concentration_index': hhi,
            'concentration_risk': 'HIGH' if hhi > 2500 else 'MEDIUM' if hhi > 1500 else 'LOW',
            'largest_position_pct': largest_position_pct,
            'top_5_concentration': top_5_concentration,
            'sector_concentration': sector_concentrations,
            'total_positions': len(positions),
            'risk_level': risk_level,
            'recommendations': _get_risk_recommendations(largest_position_pct, hhi, len(positions))
        }
        
        return jsonify(risk_metrics)
    
    except Exception as e:
        logger.error(f"Error getting risk metrics: {e}")
        return jsonify({'error': str(e)}), 500

def _get_risk_recommendations(largest_pos_pct, hhi, total_positions):
    """Generar recomendaciones basadas en métricas de riesgo"""
    recommendations = []
    
    if largest_pos_pct > 20:
        recommendations.append("Considera reducir la posición más grande para disminuir el riesgo de concentración")
    
    if hhi > 2500:
        recommendations.append("Tu portafolio está muy concentrado. Considera diversificar más")
    
    if total_positions < 10:
        recommendations.append("Considera aumentar el número de posiciones para mejor diversificación")
    
    if not recommendations:
        recommendations.append("Tu portafolio tiene un buen nivel de diversificación")
    
    return recommendations
