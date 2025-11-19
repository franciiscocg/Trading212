import logging
import os
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import google.generativeai as genai
import pandas as pd
import numpy as np

from app.models import Portfolio, Position, PriceHistory, AvailableInvestment
from app.services.sentiment_analyzer import SentimentAnalyzer
from app import db

logger = logging.getLogger(__name__)


class StrategyAnalyzer:
    """Servicio para generar estrategias de inversión automatizadas usando IA"""
    
    def __init__(self):
        self.gemini_api_key = os.getenv('GEMINI_API_KEY')
        self.sentiment_analyzer = SentimentAnalyzer()
        
        if self.gemini_api_key:
            genai.configure(api_key=self.gemini_api_key)
            logger.info("✅ StrategyAnalyzer inicializado con Gemini AI")
        else:
            logger.warning("⚠️ GEMINI_API_KEY no configurada, usando análisis básico")
    
    def generate_winning_strategy(
        self,
        user_id: str = 'default',
        timeframe_weeks: int = 2,
        risk_tolerance: str = 'MODERATE'
    ) -> Dict:
        """
        Generar estrategia ganadora automática para 1-2 semanas
        
        Args:
            user_id: ID del usuario
            timeframe_weeks: Horizonte temporal en semanas (1 o 2)
            risk_tolerance: CONSERVATIVE, MODERATE, AGGRESSIVE
            
        Returns:
            Dict con estrategia completa incluyendo recomendaciones, stop-loss, take-profit
        """
        try:
            logger.info(f"🎯 Generando estrategia ganadora para user {user_id}, timeframe: {timeframe_weeks} semanas")
            
            # 1. Obtener datos del portfolio actual
            portfolio_data = self._get_portfolio_data(user_id)
            
            # 2. Obtener análisis técnico de instrumentos disponibles
            technical_analysis = self._get_technical_analysis()
            
            # 3. Obtener análisis de sentimiento para top instrumentos
            sentiment_analysis = self._get_sentiment_analysis(technical_analysis.get('top_candidates', []))
            
            # 4. Construir prompt para Gemini AI
            prompt = self._build_strategy_prompt(
                portfolio_data=portfolio_data,
                technical_analysis=technical_analysis,
                sentiment_analysis=sentiment_analysis,
                timeframe_weeks=timeframe_weeks,
                risk_tolerance=risk_tolerance
            )
            
            # 5. Generar estrategia con Gemini AI
            if self.gemini_api_key:
                strategy_json = self._call_gemini_for_strategy(prompt)
            else:
                strategy_json = self._create_fallback_strategy(
                    portfolio_data, timeframe_weeks, risk_tolerance
                )
            
            # 6. Validar y enriquecer estrategia
            strategy_json = self._validate_and_enrich_strategy(strategy_json, portfolio_data)
            
            logger.info(f"✅ Estrategia generada exitosamente con {len(strategy_json.get('recommended_positions', []))} posiciones")
            
            return strategy_json
            
        except Exception as e:
            logger.error(f"❌ Error generando estrategia: {e}", exc_info=True)
            raise
    
    def _get_portfolio_data(self, user_id: str) -> Dict:
        """Obtener datos actuales del portfolio"""
        portfolio = Portfolio.query.filter_by(user_id=user_id).first()
        
        if not portfolio:
            logger.warning(f"Portfolio no encontrado para user {user_id}, asumiendo nuevo inversor")
            return {
                'total_value': 0.0,
                'cash_balance': 1000.0,  # Valor por defecto
                'invested_amount': 0.0,
                'unrealized_pnl': 0.0,
                'positions': []
            }
        
        positions = Position.query.filter_by(portfolio_id=portfolio.id).all()
        
        return {
            'total_value': portfolio.total_value,
            'cash_balance': portfolio.cash_balance,
            'invested_amount': portfolio.invested_amount,
            'unrealized_pnl': portfolio.unrealized_pnl,
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
    
    def _get_technical_analysis(self, limit: int = 20) -> Dict:
        """
        Analizar datos históricos para identificar tendencias y oportunidades
        
        Returns:
            Dict con análisis técnico y candidatos top
        """
        try:
            # Obtener instrumentos más negociados/populares
            available_instruments = AvailableInvestment.query.filter_by(
                is_tradable=True
            ).order_by(AvailableInvestment.current_price.desc()).limit(100).all()
            
            candidates = []
            
            for instrument in available_instruments:
                # Obtener histórico de precios (últimos 30 días)
                price_history = PriceHistory.query.filter_by(
                    ticker=instrument.ticker
                ).order_by(PriceHistory.timestamp.desc()).limit(30).all()
                
                if len(price_history) < 5:
                    continue  # No suficiente data histórica
                
                # Convertir a DataFrame para análisis
                df = pd.DataFrame([
                    {'date': ph.timestamp, 'close': ph.price, 'volume': ph.volume}
                    for ph in price_history
                ])
                df = df.sort_values('date')
                
                # Calcular indicadores técnicos básicos
                df['ma_5'] = df['close'].rolling(window=5).mean()
                df['ma_10'] = df['close'].rolling(window=10).mean()
                df['volatility'] = df['close'].pct_change().std()
                
                # Tendencia (precio actual vs media móvil)
                current_price = df['close'].iloc[-1]
                ma_5 = df['ma_5'].iloc[-1] if not pd.isna(df['ma_5'].iloc[-1]) else current_price
                ma_10 = df['ma_10'].iloc[-1] if not pd.isna(df['ma_10'].iloc[-1]) else current_price
                
                trend_score = 0
                if current_price > ma_5:
                    trend_score += 1
                if current_price > ma_10:
                    trend_score += 1
                if ma_5 > ma_10:
                    trend_score += 1
                
                # Calcular momentum (% cambio últimos 7 días)
                if len(df) >= 7:
                    momentum = (current_price - df['close'].iloc[-7]) / df['close'].iloc[-7] * 100
                else:
                    momentum = 0
                
                candidates.append({
                    'ticker': instrument.ticker,
                    'name': instrument.name,
                    'current_price': float(current_price),
                    'trend_score': trend_score,
                    'momentum': float(momentum),
                    'volatility': float(df['volatility'].iloc[-1]) if not pd.isna(df['volatility'].iloc[-1]) else 0.1,
                    'ma_5': float(ma_5),
                    'ma_10': float(ma_10)
                })
            
            # Ordenar por score técnico (combinación de trend y momentum)
            candidates.sort(key=lambda x: x['trend_score'] + (x['momentum'] / 10), reverse=True)
            
            return {
                'top_candidates': candidates[:limit],
                'total_analyzed': len(candidates),
                'analysis_date': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error en análisis técnico: {e}", exc_info=True)
            return {
                'top_candidates': [],
                'total_analyzed': 0,
                'error': str(e)
            }
    
    def _get_sentiment_analysis(self, candidates: List[Dict]) -> Dict:
        """Obtener análisis de sentimiento para candidatos top"""
        if not candidates:
            return {'sentiments': {}}
        
        try:
            # Limitar a top 10 para no saturar NewsAPI
            top_tickers = [c['ticker'] for c in candidates[:10]]
            
            logger.info(f"📰 Analizando sentimiento para {len(top_tickers)} instrumentos")
            
            results = self.sentiment_analyzer.analyze_multiple_companies(
                top_tickers,
                news_limit=5,
                delay=0.5
            )
            
            sentiments = {}
            for result in results:
                sentiments[result['symbol']] = {
                    'overall_score': result['sentiment']['overall_score'],
                    'news_count': result['news_count'],
                    'interpretation': self._interpret_sentiment(result['sentiment']['overall_score'])
                }
            
            return {'sentiments': sentiments}
            
        except Exception as e:
            logger.error(f"Error en análisis de sentimiento: {e}")
            return {'sentiments': {}}
    
    def _interpret_sentiment(self, score: float) -> str:
        """Interpretar score de sentimiento"""
        if score >= 0.1:
            return "Muy positivo"
        elif score >= 0.05:
            return "Positivo"
        elif score >= -0.05:
            return "Neutral"
        elif score >= -0.1:
            return "Negativo"
        else:
            return "Muy negativo"
    
    def _build_strategy_prompt(
        self,
        portfolio_data: Dict,
        technical_analysis: Dict,
        sentiment_analysis: Dict,
        timeframe_weeks: int,
        risk_tolerance: str
    ) -> str:
        """Construir prompt comprehensivo para Gemini AI"""
        
        prompt = f"""
Eres un estratega de inversión experto especializado en operaciones de corto plazo (1-2 semanas). Tu objetivo es generar una estrategia ganadora optimizada basada en datos reales de mercado.

CONTEXTO DEL INVERSOR:
- Valor Total del Portfolio: €{portfolio_data['total_value']:.2f}
- Cash Disponible: €{portfolio_data['cash_balance']:.2f}
- Monto Invertido: €{portfolio_data['invested_amount']:.2f}
- P&L No Realizado: €{portfolio_data['unrealized_pnl']:.2f}
- Posiciones Actuales: {len(portfolio_data['positions'])}

POSICIONES ACTUALES:
"""
        
        for pos in portfolio_data['positions']:
            prompt += f"- {pos['ticker']}: {pos['quantity']} unidades, Valor: €{pos['market_value']:.2f}, P&L: {pos['unrealized_pnl_pct']:.2f}%\n"
        
        prompt += f"""

ANÁLISIS TÉCNICO - TOP CANDIDATOS:
"""
        
        for candidate in technical_analysis.get('top_candidates', [])[:10]:
            ticker = candidate['ticker']
            sentiment_info = sentiment_analysis.get('sentiments', {}).get(ticker, {})
            sentiment_text = f" | Sentimiento: {sentiment_info.get('interpretation', 'N/A')} ({sentiment_info.get('overall_score', 0):.2f})" if sentiment_info else ""
            
            prompt += f"""
{ticker} - {candidate['name']}
  Precio Actual: €{candidate['current_price']:.2f}
  Trend Score: {candidate['trend_score']}/3
  Momentum (7d): {candidate['momentum']:.2f}%
  Volatilidad: {candidate['volatility']:.4f}
  MA5: €{candidate['ma_5']:.2f} | MA10: €{candidate['ma_10']:.2f}{sentiment_text}
"""
        
        prompt += f"""

PARÁMETROS DE LA ESTRATEGIA:
- Horizonte Temporal: {timeframe_weeks} semana(s)
- Tolerancia al Riesgo: {risk_tolerance}
- Fecha de Análisis: {datetime.now().strftime('%Y-%m-%d')}

RESTRICCIONES Y OBJETIVOS:
1. Cash Disponible: €{portfolio_data['cash_balance']:.2f} (NO EXCEDER este monto)
2. Diversificación: Mínimo 3 posiciones, máximo 7 posiciones
3. Asignación por Posición: 
   - CONSERVATIVE: Máx 20% del cash disponible por posición
   - MODERATE: Máx 30% del cash disponible por posición
   - AGGRESSIVE: Máx 40% del cash disponible por posición
4. Stop-Loss OBLIGATORIO para cada posición (5-15% según riesgo)
5. Take-Profit OBLIGATORIO para cada posición (8-25% según riesgo y timeframe)

INSTRUCCIONES CRÍTICAS:
1. Analiza EXHAUSTIVAMENTE los datos técnicos y de sentimiento
2. Selecciona instrumentos con:
   - Trend Score alto (≥2/3 preferiblemente)
   - Momentum positivo o neutral
   - Sentimiento favorable (≥ Neutral)
   - Volatilidad apropiada según tolerancia al riesgo
3. Para CADA posición recomendada, calcula:
   - Cantidad de unidades a comprar (basado en precio actual y asignación)
   - Precio de entrada (precio actual del mercado)
   - Stop-Loss (precio específico, NO porcentaje)
   - Take-Profit (precio específico, NO porcentaje)
   - % de asignación del cash disponible
4. Genera un razonamiento detallado explicando por qué cada posición es óptima
5. Calcula retorno esperado REALISTA basado en análisis técnico y temporal

FORMATO DE RESPUESTA (JSON PURO, SIN MARKDOWN):
{{
  "overall_strategy": "Descripción estratégica global (2-3 frases)",
  "risk_level": "{risk_tolerance}",
  "expected_return_range": [min_return_pct, max_return_pct],
  "timeframe_weeks": {timeframe_weeks},
  "total_investment": total_euros_a_invertir,
  "cash_remaining": cash_que_queda_disponible,
  "recommended_positions": [
    {{
      "ticker": "TICKER",
      "action": "BUY",
      "quantity": número_entero_de_unidades,
      "entry_price": precio_actual_mercado,
      "stop_loss": precio_stop_loss,
      "take_profit": precio_take_profit,
      "allocation_pct": porcentaje_del_cash_disponible,
      "investment_amount": cantidad_euros_invertir,
      "reasoning": "Por qué esta posición es ganadora (análisis técnico + sentimiento + catalistas)",
      "expected_return_pct": retorno_esperado_porcentaje,
      "risk_rating": "LOW/MEDIUM/HIGH"
    }}
  ],
  "risk_management": {{
    "max_portfolio_loss": "X% máximo de pérdida del portfolio",
    "position_sizing_method": "Descripción del método usado",
    "diversification_score": "Score de diversificación (1-10)"
  }},
  "execution_plan": {{
    "order": "Orden sugerido de ejecución (ej: comenzar por posición más fuerte)",
    "timing": "Mejor momento para ejecutar (ej: apertura de mercado, tras anuncio, etc.)",
    "monitoring": "Cómo monitorear la estrategia durante el período"
  }}
}}

GENERA LA ESTRATEGIA AHORA (SOLO JSON, SIN TEXTO ADICIONAL):
"""
        
        return prompt
    
    def _call_gemini_for_strategy(self, prompt: str) -> Dict:
        """Llamar a Gemini AI para generar estrategia"""
        if not self.gemini_api_key:
            raise Exception("GEMINI_API_KEY no configurada")
        
        # Lista de modelos a intentar en orden de preferencia
        models_to_try = [
            "models/gemini-2.5-flash",
            "models/gemini-2.0-flash",
            "models/gemini-2.5-pro"
        ]
        
        last_error = None
        
        for model_name in models_to_try:
            try:
                logger.info(f"🤖 Intentando generar estrategia con {model_name}...")
                
                model = genai.GenerativeModel(
                    model_name=model_name,
                    generation_config={
                        "temperature": 0.7,
                        "top_p": 0.9,
                        "response_mime_type": "application/json"
                    }
                )
                
                response = model.generate_content(prompt)
                
                if not response or not response.text:
                    raise Exception("No se recibió respuesta válida de Gemini")
                
                full_response = response.text
                
                # Limpiar respuesta
                clean_response = full_response.strip()
                if clean_response.startswith('```json'):
                    clean_response = clean_response[7:-3]
                elif clean_response.startswith('```'):
                    clean_response = clean_response[3:-3]
                
                strategy = json.loads(clean_response)
                
                logger.info(f"✅ Estrategia generada exitosamente con {model_name}")
                return strategy
                
            except Exception as e:
                last_error = e
                error_msg = str(e).lower()
                
                if "429" in error_msg or "quota" in error_msg or "rate limit" in error_msg:
                    logger.warning(f"⚠️ Cuota excedida para {model_name}, intentando siguiente modelo...")
                    continue
                elif "404" in error_msg or "not found" in error_msg:
                    logger.warning(f"⚠️ Modelo {model_name} no disponible, intentando siguiente...")
                    continue
                else:
                    logger.error(f"❌ Error con {model_name}: {e}")
                    continue
        
        # Si todos los modelos fallaron, usar fallback
        logger.error(f"❌ Todos los modelos de Gemini fallaron. Último error: {last_error}")
        logger.info("🔄 Usando estrategia de fallback...")
        raise Exception(f"No se pudo generar estrategia con Gemini AI. Último error: {last_error}")
    
    def _create_fallback_strategy(
        self,
        portfolio_data: Dict,
        timeframe_weeks: int,
        risk_tolerance: str
    ) -> Dict:
        """Crear estrategia de fallback cuando Gemini no está disponible"""
        cash_available = portfolio_data['cash_balance']
        
        # Estrategia conservadora básica
        return {
            "overall_strategy": f"Estrategia diversificada de {timeframe_weeks} semanas con enfoque en ETFs globales y acciones de calidad",
            "risk_level": risk_tolerance,
            "expected_return_range": [3, 8],
            "timeframe_weeks": timeframe_weeks,
            "total_investment": cash_available * 0.7,
            "cash_remaining": cash_available * 0.3,
            "recommended_positions": [
                {
                    "ticker": "VWCE.DE",
                    "action": "BUY",
                    "quantity": int((cash_available * 0.3) / 110),
                    "entry_price": 110.0,
                    "stop_loss": 100.0,
                    "take_profit": 120.0,
                    "allocation_pct": 30,
                    "investment_amount": cash_available * 0.3,
                    "reasoning": "ETF global diversificado con baja volatilidad, ideal para base del portfolio",
                    "expected_return_pct": 5.5,
                    "risk_rating": "LOW"
                },
                {
                    "ticker": "MSFT",
                    "action": "BUY",
                    "quantity": int((cash_available * 0.25) / 420),
                    "entry_price": 420.0,
                    "stop_loss": 385.0,
                    "take_profit": 455.0,
                    "allocation_pct": 25,
                    "investment_amount": cash_available * 0.25,
                    "reasoning": "Líder tecnológico con sólidos fundamentos y exposición a IA",
                    "expected_return_pct": 7.0,
                    "risk_rating": "MEDIUM"
                },
                {
                    "ticker": "NVDA",
                    "action": "BUY",
                    "quantity": int((cash_available * 0.15) / 950),
                    "entry_price": 950.0,
                    "stop_loss": 850.0,
                    "take_profit": 1050.0,
                    "allocation_pct": 15,
                    "investment_amount": cash_available * 0.15,
                    "reasoning": "Líder en semiconductores para IA, alto potencial de crecimiento",
                    "expected_return_pct": 10.0,
                    "risk_rating": "HIGH"
                }
            ],
            "risk_management": {
                "max_portfolio_loss": "12% máximo",
                "position_sizing_method": "Asignación basada en volatilidad y correlación",
                "diversification_score": "7/10"
            },
            "execution_plan": {
                "order": "1. VWCE.DE (base), 2. MSFT (core), 3. NVDA (growth)",
                "timing": "Ejecutar en horario de apertura europea para mejor liquidez",
                "monitoring": "Revisar diariamente stops, ajustar si hay volatilidad extrema"
            }
        }
    
    def _validate_and_enrich_strategy(self, strategy: Dict, portfolio_data: Dict) -> Dict:
        """Validar y enriquecer estrategia generada"""
        
        # Validar que no exceda cash disponible
        total_investment = strategy.get('total_investment', 0)
        cash_available = portfolio_data['cash_balance']
        
        if total_investment > cash_available:
            logger.warning(f"⚠️ Estrategia excede cash disponible, ajustando...")
            # Escalar proporcionalmente
            scale_factor = cash_available / total_investment * 0.95  # 95% para margen de seguridad
            
            for position in strategy.get('recommended_positions', []):
                position['quantity'] = int(position['quantity'] * scale_factor)
                position['investment_amount'] = position['investment_amount'] * scale_factor
            
            strategy['total_investment'] = cash_available * 0.95
            strategy['cash_remaining'] = cash_available * 0.05
        
        # Añadir timestamps
        strategy['generated_at'] = datetime.utcnow().isoformat()
        strategy['valid_until'] = (datetime.utcnow() + timedelta(weeks=strategy.get('timeframe_weeks', 2))).isoformat()
        
        # Calcular métricas adicionales
        positions = strategy.get('recommended_positions', [])
        if positions:
            # Filtrar None values y convertir a float
            returns = [float(p.get('expected_return_pct', 0) or 0) for p in positions]
            avg_expected_return = np.mean(returns) if returns else 0
            strategy['avg_expected_return'] = round(avg_expected_return, 2)
        
        return strategy
