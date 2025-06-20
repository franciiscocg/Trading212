from flask import Blueprint, request, jsonify
import logging
import json
import os
from datetime import datetime
from app.models import Portfolio, Position, db
import google.generativeai as genai
import yfinance as yf
import time

logger = logging.getLogger(__name__)
investment_advisor_bp = Blueprint('investment_advisor', __name__)

def get_gemini_api_key():
    """Obtener la API key de Gemini desde las variables de entorno"""
    return os.getenv('GEMINI_API_KEY')

def call_gemini_api(prompt):
    """Llamar a la API de Gemini 2.5 Pro usando la nueva librería google-genai con streaming"""
    api_key = get_gemini_api_key()
    if not api_key:
        raise Exception("GEMINI_API_KEY no está configurada")
    
    try:
        # Configurar cliente de Gemini
        genai.configure(api_key=api_key)
          # Configurar el modelo con thinking y respuesta estructurada
        model = genai.GenerativeModel(
            model_name="gemini-2.0-flash-thinking-exp",  # Usando el modelo más avanzado disponible
            generation_config={
                "response_mime_type": "application/json",
                "temperature": 0.7,
                "top_p": 0.9,
            }
        )
        
        logger.info("Iniciando análisis con Gemini 2.0 Flash Thinking Exp")
        logger.info(f"Prompt length: {len(prompt)} caracteres")
        
        # Generar contenido usando streaming para mejor rendimiento
        response_chunks = []
        
        for chunk in model.generate_content(prompt, stream=True):
            if chunk.text:
                response_chunks.append(chunk.text)
        
        # Combinar todos los chunks en una respuesta completa
        full_response = ''.join(response_chunks)
        
        if not full_response.strip():
            raise Exception("No se recibió respuesta válida de Gemini")
            
        logger.info(f"Respuesta recibida de Gemini: {len(full_response)} caracteres")
        return full_response
        
    except Exception as e:
        logger.error(f"Error calling Gemini API: {e}")
        
        # Fallback a modelos alternativos si el principal falla
        try:
            logger.info("Intentando fallback con gemini-2.5-pro")
            model_fallback = genai.GenerativeModel(
                model_name="gemini-2.5-pro",
                generation_config={
                    "response_mime_type": "application/json",
                    "temperature": 0.7,
                }
            )
            
            response = model_fallback.generate_content(prompt)
            if response and response.text:
                logger.info("Fallback exitoso con gemini-2.5-pro")
                return response.text
                
        except Exception as fallback_error:
            logger.error(f"Fallback también falló: {fallback_error}")
        
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
    """Crear el prompt para Gemini 2.5 Pro basado en los datos del portafolio y preferencias"""
    
    portfolio_summary = ""
    if portfolio_data and portfolio_data.get('portfolio') and portfolio_data['portfolio'] is not None:
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
    else:
        portfolio_summary = """
Portafolio Actual:
- Nuevo inversor sin portafolio existente
- Buscando realizar primera inversión
"""

    prompt = f"""
Eres un asesor financiero experto con capacidades de razonamiento avanzado. Utiliza las capacidades de thinking de Gemini 2.5 Pro para analizar profundamente cada aspecto antes de generar recomendaciones.

PROCESO DE ANÁLISIS REQUERIDO:
1. PIENSA PASO A PASO sobre el contexto macroeconómico actual
2. ANALIZA DETALLADAMENTE el portafolio existente y su composición
3. EVALÚA CUIDADOSAMENTE las preferencias y restricciones del inversor
4. CONSIDERA MÚLTIPLES ESCENARIOS de mercado
5. FUNDAMENTA CADA RECOMENDACIÓN con análisis cuantitativo y cualitativo

CONTEXTO ACTUAL DEL MERCADO (Junio 2025):
- Entorno macroeconómico: Considera inflación, tasas de interés, política monetaria
- Revolución de la IA: Impacto en valoraciones y oportunidades sectoriales
- Transición energética: Oportunidades en renovables y sostenibilidad
- Geopolítica: Tensiones comerciales y sus efectos en los mercados
- Valuaciones: Analiza si los mercados están sobrevalorados o infravalorados

IMPORTANTE - INSTRUMENTOS DISPONIBLES EN TRADING212 INVEST:
Recomienda ÚNICAMENTE instrumentos que estén disponibles en Trading212 Invest. Los tipos de instrumentos disponibles incluyen:

1. ACCIONES INDIVIDUALES (formato: TICKER):
   - Acciones europeas: ASML, SAP, LVMH, NESN, INGA, etc.
   - Acciones estadounidenses: AAPL, MSFT, GOOGL, AMZN, TSLA, NVDA, META, etc.
   - Acciones del Reino Unido: BP, SHEL, AZN, ULVR, etc.

2. ETFs DISPONIBLES EN TRADING212 (formato: TICKER):
   - ETFs de Vanguard: VWCE.DE (Vanguard FTSE All-World), VUSA.AS (S&P 500), etc.
   - ETFs de iShares: IWDA.AS (MSCI World), EIMI.AS (Emerging Markets), IUIT.AS (Technology), etc.
   - ETFs de SPDR: SPY5.DE (S&P 500), etc.
   - ETFs sectoriales: QQQ (Nasdaq 100), VTI (Total Stock Market), etc.

3. INSTRUMENTOS ESPECÍFICOS REALES Y VERIFICADOS:
   - VWCE.DE: Vanguard FTSE All-World UCITS ETF (Diversificación global)
   - IWDA.AS: iShares Core MSCI World UCITS ETF (Mercados desarrollados)
   - EIMI.AS: iShares Core MSCI Emerging Markets IMI UCITS ETF
   - VUSA.AS: Vanguard S&P 500 UCITS ETF
   - QQQ: Invesco QQQ Trust ETF (Tecnología/Nasdaq 100) - USAR ESTE PARA TECNOLOGÍA

NO uses símbolos como TEC0.DE, IUIT.AS, XTCH.DE que no están disponibles. Para tecnología, usa QQQ.

NO recomiendas instrumentos ficticios o que no existan realmente en Trading212.

{portfolio_summary}

PERFIL DEL INVERSOR:
- Tolerancia al Riesgo: {preferences.get('riskTolerance', 'medium')}
- Horizonte de Inversión: {preferences.get('investmentHorizon', '1-3-years')}
- Cantidad a Invertir: €{preferences.get('investmentAmount', 1000)}
- Sectores Preferidos: {preferences.get('sectors', ['diversificado'])}
- Enfoque Sostenible: {preferences.get('sustainability', False)}

METODOLOGÍA DE ANÁLISIS:
1. ANÁLISIS FUNDAMENTAL PROFUNDO:
   - Evalúa métricas financieras (P/E, ROE, deuda, crecimiento)
   - Analiza la posición competitiva y ventajas del negocio
   - Considera catalistas específicos y riesgos potenciales

2. ANÁLISIS TÉCNICO:
   - Evalúa niveles de soporte y resistencia
   - Analiza tendencias y momentum
   - Identifica puntos de entrada y salida óptimos

3. ANÁLISIS DE RIESGO CUANTITATIVO:
   - Calcula volatilidad esperada y correlaciones
   - Determina máximo drawdown potencial
   - Evalúa ratio riesgo-retorno

4. CONSTRUCCIÓN DE PORTAFOLIO:
   - Optimiza la asignación de activos
   - Considera diversificación sectorial y geográfica
   - Establece cronograma de implementación

CRÍTICO: Responde ÚNICAMENTE con un objeto JSON válido, sin texto adicional, markdown o comentarios. La respuesta debe ser JSON puro que pueda ser parseado directamente. Usa SOLO tickers reales disponibles en Trading212 Invest. Estructura requerida:

{{
  "topRecommendation": {{
    "symbol": "VWCE.DE",
    "name": "Vanguard FTSE All-World UCITS ETF"
  }},
  "expectedReturn": 0.12,
  "overallRisk": "MEDIUM",
  "recommendations": [
    {{
      "symbol": "MSFT",
      "name": "Microsoft Corporation",
      "currentPrice": 340.50,
      "targetPrice": 400.00,
      "stopLoss": 300.00,
      "potentialReturn": 0.175,
      "risk": "MEDIUM",
      "strategy": "Comprar y mantener por 12-18 meses",
      "reasoning": "Líder en cloud computing y AI con sólidos fundamentos financieros",
      "timeHorizon": "12-18 meses",
      "keyMetrics": {{
        "P/E": "28.5",
        "ROE": "45%",
        "MarketCap": "2.5T USD"
      }},
      "tradingInstructions": "Disponible en Trading212 como MSFT. Considera DCA (Dollar Cost Averaging) para reducir volatilidad."
    }}
  ],
  "riskAnalysis": {{
    "volatility": 0.18,
    "maxDrawdown": 0.25,
    "sharpeRatio": 1.2
  }},
  "marketInsights": "Análisis del mercado actual y cómo afecta a las recomendaciones disponibles en Trading212..."
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
            {'portfolio': portfolio_summary} if portfolio_summary else {'portfolio': None}, 
            preferences, 
            data.get('marketConditions', 'current')
        )        # Llamar a Gemini API
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
                
                # Enriquecer recomendaciones con precios reales
                if 'recommendations' in analysis_result:
                    analysis_result['recommendations'] = enrich_recommendations_with_real_prices(
                        analysis_result['recommendations']
                    )
                        
            except Exception as gemini_error:
                logger.warning(f"Gemini API failed, using fallback: {gemini_error}")
                analysis_result = create_fallback_analysis(preferences)
                
                # Enriquecer fallback con precios reales también
                if 'recommendations' in analysis_result:
                    analysis_result['recommendations'] = enrich_recommendations_with_real_prices(
                        analysis_result['recommendations']
                    )
        else:
            logger.info("GEMINI_API_KEY not configured, using fallback analysis")
            analysis_result = create_fallback_analysis(preferences)
            
            # Enriquecer fallback con precios reales también
            if 'recommendations' in analysis_result:
                analysis_result['recommendations'] = enrich_recommendations_with_real_prices(
                    analysis_result['recommendations']
                )
        
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
                "strategy": "Inversión a largo plazo en mercados globales diversificados",
                "reasoning": "ETF que replica el índice FTSE All-World, proporcionando exposición diversificada a mercados desarrollados y emergentes con costos bajos",
                "timeHorizon": "3-5 años",
                "keyMetrics": {
                    "TER": "0.22%",
                    "AUM": "€15B+",
                    "Dividend Yield": "2.1%"
                },
                "tradingInstructions": "Disponible en Trading212 como VWCE.DE. Ideal para DCA mensual."
            }
        ]
    elif risk_level == 'HIGH':
        recommendations = [
            {
                "symbol": "NVDA",
                "name": "NVIDIA Corporation",
                "currentPrice": 950.0,
                "targetPrice": 1200.0,
                "stopLoss": 750.0,
                "potentialReturn": 0.26,
                "risk": "HIGH",
                "strategy": "Crecimiento agresivo en inteligencia artificial",
                "reasoning": "Líder absoluto en semiconductores para IA, con demanda exponencial en centros de datos y aplicaciones de machine learning",
                "timeHorizon": "1-2 años",
                "keyMetrics": {
                    "P/E": "65.2",
                    "Revenue Growth": "126%",
                    "Market Cap": "2.3T USD"
                },
                "tradingInstructions": "Disponible en Trading212 como NVDA. Considera volatilidad alta y position sizing adecuado."
            }
        ]
    else:  # MEDIUM
        recommendations = [
            {
                "symbol": "IUIT.AS",
                "name": "iShares Core MSCI World Information Technology UCITS ETF",
                "currentPrice": 15.0,
                "targetPrice": 18.0,
                "stopLoss": 12.5,
                "potentialReturn": 0.20,
                "risk": "MEDIUM",
                "strategy": "Diversificación en tecnología global con gestión pasiva",
                "reasoning": "ETF que replica el índice MSCI World Information Technology, proporcionando exposición diversificada a empresas de tecnología de mercados desarrollados",
                "timeHorizon": "1-3 años",
                "keyMetrics": {
                    "TER": "0.25%",
                    "AUM": "€8B+",
                    "Companies": "150+"
                },
                "tradingInstructions": "Disponible en Trading212 como IUIT.AS. Excelente opción para exposición al sector tecnológico global."
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
        "marketInsights": f"Basado en tu perfil de riesgo {risk_level.lower()} y cantidad de inversión de €{investment_amount}, estas recomendaciones están diseñadas para maximizar el retorno ajustado al riesgo. Todos los instrumentos están disponibles en Trading212 Invest y pueden ser comprados directamente desde la plataforma.",
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

def get_real_time_price(symbol):
    """Obtener precio en tiempo real usando Yahoo Finance"""
    try:        # Mapeo de símbolos de Trading212 a Yahoo Finance
        symbol_mapping = {
            'VWCE.DE': 'VWCE.DE',
            'IWDA.AS': 'IWDA.AS', 
            'TEC0.DE': 'QQQ',  # Usando QQQ como alternativo para tecnología
            'MSFT': 'MSFT',
            'NVDA': 'NVDA',
            'AAPL': 'AAPL',
            'GOOGL': 'GOOGL',
            'AMZN': 'AMZN',
            'TSLA': 'TSLA',
            'META': 'META',
            'NFLX': 'NFLX',
            'AMD': 'AMD',
            'CRM': 'CRM',
            'ADBE': 'ADBE',
            'EIMI.AS': 'EIMI.AS',
            'VUSA.AS': 'VUSA.AS',
            'QQQ': 'QQQ',
            'VTI': 'VTI',
            'SPY': 'SPY'
        }
        
        # Obtener símbolo correspondiente para Yahoo Finance
        yf_symbol = symbol_mapping.get(symbol, symbol)
        
        # Crear ticker object
        ticker = yf.Ticker(yf_symbol)
        
        # Obtener información rápida del ticker
        info = ticker.fast_info
        if hasattr(info, 'last_price') and info.last_price:
            return float(info.last_price)
        
        # Fallback: obtener datos históricos del último día
        hist = ticker.history(period="1d", interval="1m")
        if not hist.empty:
            return float(hist['Close'].iloc[-1])
            
        # Si no se puede obtener el precio, devolver None
        logger.warning(f"No se pudo obtener precio para {symbol}")
        return None
        
    except Exception as e:
        logger.error(f"Error obteniendo precio para {symbol}: {e}")
        return None

def get_multiple_prices(symbols):
    """Obtener precios para múltiples símbolos de forma eficiente"""
    prices = {}
    
    try:        # Mapeo de símbolos
        symbol_mapping = {
            'VWCE.DE': 'VWCE.DE',
            'IWDA.AS': 'IWDA.AS', 
            'TEC0.DE': 'QQQ',  # Usando QQQ como alternativo para tecnología
            'MSFT': 'MSFT',
            'NVDA': 'NVDA',
            'AAPL': 'AAPL',
            'GOOGL': 'GOOGL',
            'AMZN': 'AMZN',
            'TSLA': 'TSLA',
            'META': 'META',
            'EIMI.AS': 'EIMI.AS',
            'VUSA.AS': 'VUSA.AS',
            'QQQ': 'QQQ',
            'VTI': 'VTI',
            'SPY': 'SPY'
        }
        
        # Convertir a símbolos de Yahoo Finance
        yf_symbols = [symbol_mapping.get(symbol, symbol) for symbol in symbols]
        
        # Descargar datos para todos los símbolos de una vez
        tickers = yf.download(yf_symbols, period="1d", interval="1d", group_by='ticker', progress=False)
        
        # Extraer precios
        for i, symbol in enumerate(symbols):
            yf_symbol = symbol_mapping.get(symbol, symbol)
            try:
                if len(yf_symbols) == 1:
                    # Si solo hay un símbolo, la estructura es diferente
                    price = float(tickers['Close'].iloc[-1])
                else:
                    # Múltiples símbolos
                    price = float(tickers[(yf_symbol, 'Close')].iloc[-1])
                prices[symbol] = price
            except:
                # Fallback individual si falla
                individual_price = get_real_time_price(symbol)
                if individual_price:
                    prices[symbol] = individual_price
                    
    except Exception as e:
        logger.error(f"Error descargando precios múltiples: {e}")
        # Fallback a llamadas individuales
        for symbol in symbols:
            price = get_real_time_price(symbol)
            if price:
                prices[symbol] = price
    
    return prices

def enrich_recommendations_with_real_prices(recommendations):
    """Enriquecer recomendaciones con precios reales"""
    if not recommendations:
        return recommendations
        
    # Extraer símbolos de las recomendaciones
    symbols = [rec.get('symbol') for rec in recommendations if rec.get('symbol')]
    
    if not symbols:
        return recommendations
        
    # Obtener precios reales
    logger.info(f"Obteniendo precios en tiempo real para: {symbols}")
    real_prices = get_multiple_prices(symbols)
    
    # Actualizar recomendaciones con precios reales
    for rec in recommendations:
        symbol = rec.get('symbol')
        if symbol and symbol in real_prices:
            current_price = real_prices[symbol]
            rec['currentPrice'] = round(current_price, 2)
            
            # Recalcular target price y stop loss basado en el precio actual
            potential_return = rec.get('potentialReturn', 0.1)
            if potential_return and current_price:
                rec['targetPrice'] = round(current_price * (1 + potential_return), 2)
                rec['stopLoss'] = round(current_price * 0.85, 2)  # 15% stop loss
                
            logger.info(f"Precio actualizado para {symbol}: €{current_price}")
    
    return recommendations
