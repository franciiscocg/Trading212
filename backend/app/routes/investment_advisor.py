from flask import Blueprint, request, jsonify
import logging
import json
import os
import requests
from datetime import datetime
from app.models import Portfolio, Position, db

logger = logging.getLogger(__name__)
investment_advisor_bp = Blueprint('investment_advisor', __name__)

def get_gemini_api_key():
    """Obtener la API key de Gemini desde las variables de entorno"""
    return os.getenv('GEMINI_API_KEY')

def call_gemini_api(prompt):
    """Llamar a la API de Gemini con el prompt dado"""
    api_key = get_gemini_api_key()
    if not api_key:
        raise Exception("GEMINI_API_KEY no está configurada")
      # URL de la API de Gemini (actualizada para usar gemini-1.5-flash)
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    
    headers = {
        'Content-Type': 'application/json',
    }
    
    data = {
        "contents": [{
            "parts": [{
                "text": prompt
            }]
        }]
    }
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        if 'candidates' in result and len(result['candidates']) > 0:
            content = result['candidates'][0]['content']['parts'][0]['text']
            return content
        else:
            raise Exception("No se recibió respuesta válida de Gemini")
            
    except requests.exceptions.RequestException as e:
        logger.error(f"Error calling Gemini API: {e}")
        raise Exception(f"Error comunicándose con Gemini API: {str(e)}")

def get_portfolio_summary(user_id):
    """Obtener resumen del portafolio del usuario"""
    portfolio = Portfolio.query.filter_by(user_id=user_id).first()
    if not portfolio:
        return None
    
    positions = Position.query.filter_by(portfolio_id=portfolio.id).all()
    
    return {
        'total_value': portfolio.total_value,
        'cash_balance': portfolio.cash_balance,
        'unrealized_pnl': portfolio.unrealized_pnl,
        'positions_count': len(positions),
        'positions': [
            {
                'ticker': pos.ticker,
                'quantity': pos.quantity,
                'market_value': pos.market_value,
                'unrealized_pnl': pos.unrealized_pnl,
                'unrealized_pnl_pct': pos.unrealized_pnl_pct
            }
            for pos in positions
        ]
    }

def create_investment_prompt(portfolio_data, preferences, market_conditions):
    """Crear el prompt para Gemini basado en los datos del portafolio y preferencias"""
    
    portfolio_summary = ""
    if portfolio_data and 'portfolio' in portfolio_data:
        p = portfolio_data['portfolio']
        portfolio_summary = f"""
Portafolio Actual:
- Valor Total: €{p.get('total_value', 0):.2f}
- Efectivo Disponible: €{p.get('cash_balance', 0):.2f}
- P&L No Realizado: €{p.get('unrealized_pnl', 0):.2f}
- Número de Posiciones: {p.get('positions_count', 0)}
"""
        
        if 'analytics' in portfolio_data:
            a = portfolio_data['analytics']
            portfolio_summary += f"""
Métricas del Portafolio:
- Rendimiento Total: {a.get('total_return_pct', 0):.2f}%
- Tasa de Éxito: {a.get('win_rate', 0):.2f}%
- Concentración (HHI): {a.get('concentration_index', 0):.0f}
"""

    prompt = f"""
Eres un asesor financiero experto especializado en inversiones. Basándote en la siguiente información, proporciona recomendaciones de inversión detalladas y específicas.

{portfolio_summary}

Preferencias del Inversor:
- Tolerancia al Riesgo: {preferences.get('riskTolerance', 'medium')}
- Horizonte de Inversión: {preferences.get('investmentHorizon', '1-3-years')}
- Cantidad a Invertir: €{preferences.get('investmentAmount', 1000)}

Instrucciones:
1. Proporciona 3-5 recomendaciones específicas de inversión (acciones, ETFs, o sectores)
2. Para cada recomendación incluye:
   - Símbolo del ticker (si aplica)
   - Precio aproximado de entrada
   - Precio objetivo
   - Stop loss recomendado
   - Horizonte temporal específico
   - Nivel de riesgo (LOW/MEDIUM/HIGH)
   - Razón fundamental para la inversión
   - Métricas financieras clave (P/E, ROE, etc. si aplica)

3. Proporciona un análisis de riesgo general con:
   - Volatilidad esperada
   - Máxima pérdida potencial
   - Diversificación recomendada

4. Incluye insights del mercado actual y cómo afectan las recomendaciones

IMPORTANTE: Responde ÚNICAMENTE en formato JSON válido con la siguiente estructura:
{{
  "topRecommendation": {{
    "symbol": "TICKER",
    "name": "Nombre de la empresa/ETF"
  }},
  "expectedReturn": 0.12,
  "overallRisk": "MEDIUM",
  "recommendations": [
    {{
      "symbol": "TICKER1",
      "name": "Nombre completo",
      "currentPrice": 100.50,
      "targetPrice": 120.00,
      "stopLoss": 85.00,
      "potentialReturn": 0.194,
      "risk": "MEDIUM",
      "strategy": "Comprar y mantener por 12-18 meses",
      "reasoning": "Razón detallada para la inversión",
      "timeHorizon": "12-18 meses",
      "keyMetrics": {{
        "P/E": "15.2",
        "ROE": "18%",
        "Debt/Equity": "0.3"
      }}
    }}
  ],
  "riskAnalysis": {{
    "volatility": 0.18,
    "maxDrawdown": 0.25,
    "sharpeRatio": 1.2
  }},
  "marketInsights": "Análisis del mercado actual y cómo afecta a las recomendaciones..."
}}

Fecha actual: {datetime.now().strftime('%Y-%m-%d')}
"""
    
    return prompt

@investment_advisor_bp.route('/analyze', methods=['POST'])
def analyze_investments():
    """Analizar y generar recomendaciones de inversión usando Gemini AI"""
    try:
        data = request.get_json()
        user_id = data.get('user_id', 'default')
        preferences = data.get('preferences', {})
        
        # Obtener datos del portafolio
        portfolio_summary = get_portfolio_summary(user_id)
          # Crear prompt para Gemini
        prompt = create_investment_prompt(
            {'portfolio': portfolio_summary}, 
            preferences, 
            data.get('marketConditions', 'current')
        )
        # Llamar a Gemini API
        api_key = get_gemini_api_key()
        if api_key:
            logger.info("Calling Gemini API for investment analysis")
            try:
                gemini_response = call_gemini_api(prompt)
                
                # Parsear la respuesta JSON
                clean_response = gemini_response.strip()
                if clean_response.startswith('```json'):
                    clean_response = clean_response[7:-3]
                elif clean_response.startswith('```'):
                    clean_response = clean_response[3:-3]
                
                analysis_result = json.loads(clean_response)
                
                # Validar que tiene la estructura esperada
                required_fields = ['topRecommendation', 'expectedReturn', 'overallRisk', 'recommendations']
                for field in required_fields:
                    if field not in analysis_result:
                        raise ValueError(f"Missing required field: {field}")
                        
            except Exception as gemini_error:
                logger.warning(f"Gemini API failed, using fallback: {gemini_error}")
                analysis_result = create_fallback_analysis(preferences)
        else:
            logger.info("GEMINI_API_KEY not configured, using fallback analysis")
            analysis_result = create_fallback_analysis(preferences)
        
        # Agregar metadatos
        analysis_result['timestamp'] = datetime.now().isoformat()
        analysis_result['preferences'] = preferences
        analysis_result['portfolioSummary'] = portfolio_summary
        
        return jsonify(analysis_result)
    
    except Exception as e:
        logger.error(f"Error in investment analysis: {e}")
        return jsonify({
            'error': str(e),
            'message': 'Error generando recomendaciones de inversión'
        }), 500

def create_fallback_analysis(preferences):
    """Crear análisis de fallback cuando Gemini no está disponible"""
    risk_level = preferences.get('riskTolerance', 'medium').upper()
    investment_amount = preferences.get('investmentAmount', 1000)
    
    # Recomendaciones básicas basadas en el perfil de riesgo
    if risk_level == 'LOW':
        recommendations = [
            {
                "symbol": "VWCE.DE",
                "name": "Vanguard FTSE All-World UCITS ETF",
                "currentPrice": 110.0,
                "targetPrice": 125.0,
                "stopLoss": 95.0,
                "potentialReturn": 0.136,
                "risk": "LOW",
                "strategy": "Inversión a largo plazo en mercados globales",
                "reasoning": "ETF diversificado que replica el mercado mundial",
                "timeHorizon": "3-5 años",
                "keyMetrics": {
                    "TER": "0.22%",
                    "AUM": "€15B",
                    "Yield": "2.1%"
                }
            }
        ]
    elif risk_level == 'HIGH':
        recommendations = [
            {
                "symbol": "TSLA",
                "name": "Tesla Inc.",
                "currentPrice": 250.0,
                "targetPrice": 320.0,
                "stopLoss": 200.0,
                "potentialReturn": 0.28,
                "risk": "HIGH",
                "strategy": "Crecimiento en vehículos eléctricos",
                "reasoning": "Líder en EVs con potencial de crecimiento",
                "timeHorizon": "1-2 años",
                "keyMetrics": {
                    "P/E": "65.2",
                    "Growth": "25%",
                    "Beta": "2.1"
                }
            }
        ]
    else:  # MEDIUM
        recommendations = [
            {
                "symbol": "MSFT",
                "name": "Microsoft Corporation",
                "currentPrice": 340.0,
                "targetPrice": 400.0,
                "stopLoss": 300.0,
                "potentialReturn": 0.176,
                "risk": "MEDIUM",
                "strategy": "Crecimiento estable en cloud computing",
                "reasoning": "Empresa sólida con crecimiento en Azure y AI",
                "timeHorizon": "1-3 años",
                "keyMetrics": {
                    "P/E": "28.5",
                    "ROE": "45%",
                    "Dividend": "2.8%"
                }
            }
        ]
    
    return {
        "topRecommendation": recommendations[0],
        "expectedReturn": recommendations[0]["potentialReturn"],
        "overallRisk": risk_level,
        "recommendations": recommendations,
        "riskAnalysis": {
            "volatility": 0.15 if risk_level == 'LOW' else 0.25 if risk_level == 'HIGH' else 0.20,
            "maxDrawdown": 0.10 if risk_level == 'LOW' else 0.35 if risk_level == 'HIGH' else 0.20,
            "sharpeRatio": 1.5 if risk_level == 'LOW' else 0.8 if risk_level == 'HIGH' else 1.2
        },
        "marketInsights": f"Basado en tu perfil de riesgo {risk_level.lower()} y cantidad de inversión de €{investment_amount}, estas recomendaciones están diseñadas para maximizar el retorno ajustado al riesgo.",
        "timestamp": datetime.now().isoformat(),
        "source": "fallback_analysis"
    }

@investment_advisor_bp.route('/market-data/<symbol>', methods=['GET'])
def get_market_data(symbol):
    """Obtener datos de mercado para un símbolo específico (placeholder)"""
    try:
        # En una implementación real, esto llamaría a una API de mercado real
        # como Alpha Vantage, Yahoo Finance, etc.
        
        mock_data = {
            "symbol": symbol.upper(),
            "price": 100.0,
            "change": 2.5,
            "changePercent": 2.56,
            "volume": 1000000,
            "marketCap": 50000000000,
            "pe": 15.2,
            "lastUpdate": datetime.now().isoformat()
        }
        
        return jsonify(mock_data)
        
    except Exception as e:
        logger.error(f"Error getting market data for {symbol}: {e}")
        return jsonify({'error': str(e)}), 500
