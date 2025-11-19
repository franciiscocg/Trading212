#!/usr/bin/env python3
"""
Script de Análisis de Sentimientos para Empresas
===============================================

Este script analiza el sentimiento de noticias recientes para una lista de símbolos bursátiles
utilizando la API de NewsAPI y dos librerías de análisis de sentimientos:
- Vader (SentimentIntensityAnalyzer)
- TextBlob

Incluye sistema de cache y rate limiting para optimizar el uso de la API.

Autor: Trading212 Portfolio Manager
Fecha: 2025
"""

import requests
import json
import time
from typing import Dict, List, Optional, Tuple
import logging
from datetime import datetime, timedelta
import os
from flask import current_app

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SentimentAnalyzer:
    """
    Clase para analizar sentimientos de noticias de empresas
    """

    def __init__(self, api_key: str = None, use_newsapi: bool = True):
        """
        Inicializar el analizador de sentimientos

        Args:
            api_key: API key de NewsAPI (opcional, toma de config si es None)
            use_newsapi: Si True, usa NewsAPI (recomendado)
        """
        self.use_newsapi = use_newsapi
        
        # Intentar obtener API key de la app context si es posible, sino usar argumento o env
        if api_key:
            self.api_key = api_key
        else:
            try:
                self.api_key = current_app.config.get('NEWS_API_KEY')
            except:
                self.api_key = os.getenv('NEWS_API_KEY')

        if use_newsapi:
            self.base_url = "https://newsapi.org/v2/everything"
        else:
            self.base_url = "https://financialmodelingprep.com/api/v3/stock_news"

        self.session = requests.Session()

        # Configurar headers para mejor compatibilidad
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

        # Sistema de rate limiting y cache
        try:
            self.daily_request_limit = current_app.config.get('SENTIMENT_REQUEST_LIMIT', 100)
            cache_dir = current_app.config.get('SENTIMENT_CACHE_DIR', 'cache')
        except:
            self.daily_request_limit = 100
            cache_dir = 'cache'
            
        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir)
            
        self.cache_file = os.path.join(cache_dir, 'sentiment_cache.json')
        self.request_count_file = os.path.join(cache_dir, 'request_count.json')

        # Cargar estado de rate limiting
        self.request_count = self._load_request_count()
        self.cache = self._load_cache()

        # Intentar importar las librerías de análisis de sentimientos
        self.vader_analyzer = None
        self.textblob_analyzer = None

        try:
            from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
            self.vader_analyzer = SentimentIntensityAnalyzer()
            logger.info("✅ Vader Sentiment Analyzer cargado correctamente")
        except ImportError:
            logger.warning("❌ No se pudo cargar vaderSentiment. Instala con: pip install vaderSentiment")

        try:
            from textblob import TextBlob
            self.textblob_analyzer = TextBlob
            logger.info("✅ TextBlob cargado correctamente")
        except ImportError:
            logger.warning("❌ No se pudo cargar textblob. Instala con: pip install textblob")

        if not self.vader_analyzer and not self.textblob_analyzer:
            # No levantar error aquí para permitir funcionamiento básico sin librerías
            logger.warning("⚠️ No hay librerías de análisis de sentimiento disponibles. Se usarán valores neutros.")

    def _load_request_count(self) -> Dict:
        """Cargar contador de requests del día"""
        try:
            if os.path.exists(self.request_count_file):
                with open(self.request_count_file, 'r') as f:
                    data = json.load(f)
                    # Verificar si es del día actual
                    if data.get('date') == str(datetime.now().date()):
                        return data
        except Exception as e:
            logger.warning(f"Error al cargar contador de requests: {e}")

        # Retornar valores por defecto
        return {
            'date': str(datetime.now().date()),
            'count': 0
        }

    def _save_request_count(self):
        """Guardar contador de requests"""
        try:
            with open(self.request_count_file, 'w') as f:
                json.dump(self.request_count, f)
        except Exception as e:
            logger.warning(f"Error al guardar contador de requests: {e}")

    def _load_cache(self) -> Dict:
        """Cargar cache de resultados"""
        try:
            if os.path.exists(self.cache_file):
                with open(self.cache_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            logger.warning(f"Error al cargar cache: {e}")
        return {}

    def _save_cache(self):
        """Guardar cache de resultados"""
        try:
            with open(self.cache_file, 'w') as f:
                json.dump(self.cache, f)
        except Exception as e:
            logger.warning(f"Error al guardar cache: {e}")

    def _can_make_request(self) -> bool:
        """Verificar si se puede hacer una request"""
        # Resetear contador si es un nuevo día
        if self.request_count['date'] != str(datetime.now().date()):
            self.request_count = {
                'date': str(datetime.now().date()),
                'count': 0
            }
            self._save_request_count()

        return self.request_count['count'] < self.daily_request_limit

    def _increment_request_count(self):
        """Incrementar contador de requests"""
        self.request_count['count'] += 1
        self._save_request_count()

    def _get_cache_key(self, symbol: str, limit: int) -> str:
        """Generar clave de cache"""
        today = datetime.now().date()
        return f"{symbol}_{limit}_{today}"

    def get_company_news(self, symbol: str, limit: int = 10) -> List[Dict]:
        """
        Obtener noticias recientes para un símbolo bursátil con cache y rate limiting

        Args:
            symbol: Símbolo bursátil (ej: 'AAPL', 'GOOGL')
            limit: Número máximo de noticias a obtener

        Returns:
            Lista de diccionarios con información de las noticias
        """
        # Verificar cache primero
        cache_key = self._get_cache_key(symbol, limit)
        if cache_key in self.cache:
            logger.info(f"✅ Usando datos del cache para {symbol}")
            return self.cache[cache_key]

        # Verificar si podemos hacer una request
        if not self._can_make_request():
            logger.warning(f"⚠️ Límite diario alcanzado ({self.daily_request_limit} requests)")
            logger.info("💡 Usando datos de ejemplo para demostración...")
            sample_data = self._get_sample_news_data(symbol, limit)
            # Guardar en cache para evitar llamadas futuras
            self.cache[cache_key] = sample_data
            self._save_cache()
            return sample_data

        try:
            if self.use_newsapi:
                # Usar NewsAPI
                params = {
                    'q': f'"{symbol}" OR "{symbol} stock" OR "{symbol} shares"',  # Búsqueda más específica
                    'sortBy': 'publishedAt',
                    'language': 'en',
                    'pageSize': min(limit, 20),  # NewsAPI limita a 20 por request
                    'apiKey': self.api_key
                }

                logger.info(f"📡 Descargando noticias para {symbol} usando NewsAPI...")
                response = self.session.get(self.base_url, params=params, timeout=30)

                # Verificar si la respuesta es exitosa
                if response.status_code == 401:
                    logger.warning("⚠️ API key inválida o expirada")
                    logger.info("💡 Usando datos de ejemplo para demostración...")
                    sample_data = self._get_sample_news_data(symbol, limit)
                    self.cache[cache_key] = sample_data
                    self._save_cache()
                    return sample_data
                elif response.status_code == 429:
                    logger.warning("⚠️ Rate limit excedido en NewsAPI")
                    logger.info("💡 Usando datos de ejemplo para demostración...")
                    sample_data = self._get_sample_news_data(symbol, limit)
                    self.cache[cache_key] = sample_data
                    self._save_cache()
                    return sample_data
                elif response.status_code != 200:
                    logger.warning(f"⚠️ Error HTTP {response.status_code}: {response.text}")
                    logger.info("💡 Usando datos de ejemplo para demostración...")
                    sample_data = self._get_sample_news_data(symbol, limit)
                    self.cache[cache_key] = sample_data
                    self._save_cache()
                    return sample_data

                news_data = response.json()

                if news_data.get('status') != 'ok':
                    logger.warning(f"⚠️ Error en respuesta de NewsAPI: {news_data.get('message', 'Unknown error')}")
                    logger.info("💡 Usando datos de ejemplo para demostración...")
                    sample_data = self._get_sample_news_data(symbol, limit)
                    self.cache[cache_key] = sample_data
                    self._save_cache()
                    return sample_data

                articles = news_data.get('articles', [])

                # Convertir formato de NewsAPI al formato esperado
                formatted_articles = []
                for article in articles:
                    formatted_articles.append({
                        'title': article.get('title', ''),
                        'publishedDate': article.get('publishedAt', ''),
                        'content': article.get('description', ''),
                        'url': article.get('url', ''),
                        'source': article.get('source', {}).get('name', '')
                    })

                if not formatted_articles:
                    logger.warning(f"⚠️ No se encontraron noticias para {symbol}")
                    # Guardar lista vacía en cache para evitar requests futuras
                    self.cache[cache_key] = []
                    self._save_cache()
                    return []

                # Incrementar contador de requests y guardar en cache
                self._increment_request_count()
                self.cache[cache_key] = formatted_articles
                self._save_cache()

                logger.info(f"✅ Obtenidas {len(formatted_articles)} noticias para {symbol}")
                return formatted_articles

            else:
                # Usar Financial Modeling Prep
                params = {
                    'tickers': symbol,
                    'limit': limit,
                    'apikey': self.api_key
                }

                logger.info(f"📡 Descargando noticias para {symbol} usando FMP...")
                response = self.session.get(self.base_url, params=params, timeout=30)

                # Verificar si la respuesta es exitosa
                if response.status_code == 403:
                    logger.warning("⚠️ API key inválida o expirada para Financial Modeling Prep")
                    logger.info("💡 Usando datos de ejemplo para demostración...")
                    sample_data = self._get_sample_news_data(symbol, limit)
                    self.cache[cache_key] = sample_data
                    self._save_cache()
                    return sample_data
                elif response.status_code != 200:
                    logger.warning(f"⚠️ Error HTTP {response.status_code}: {response.text}")
                    logger.info("💡 Usando datos de ejemplo para demostración...")
                    sample_data = self._get_sample_news_data(symbol, limit)
                    self.cache[cache_key] = sample_data
                    self._save_cache()
                    return sample_data

                news_data = response.json()

                if not news_data:
                    logger.warning(f"⚠️ No se encontraron noticias para {symbol}")
                    self.cache[cache_key] = []
                    self._save_cache()
                    return []

                # Incrementar contador de requests y guardar en cache
                self._increment_request_count()
                self.cache[cache_key] = news_data
                self._save_cache()

                logger.info(f"✅ Obtenidas {len(news_data)} noticias para {symbol}")
                return news_data

        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Error al obtener noticias para {symbol}: {str(e)}")
            # En caso de error, usar datos de ejemplo y guardar en cache
            sample_data = self._get_sample_news_data(symbol, limit)
            self.cache[cache_key] = sample_data
            self._save_cache()
            return sample_data
        except Exception as e:
            logger.error(f"❌ Error inesperado al procesar noticias para {symbol}: {str(e)}")
            # En caso de error, usar datos de ejemplo y guardar en cache
            sample_data = self._get_sample_news_data(symbol, limit)
            self.cache[cache_key] = sample_data
            self._save_cache()
            return sample_data

    def analyze_sentiment_vader(self, text: str) -> Dict[str, float]:
        """
        Analizar sentimiento usando Vader

        Args:
            text: Texto a analizar

        Returns:
            Diccionario con scores de Vader
        """
        if not self.vader_analyzer:
            return {'compound': 0.0, 'pos': 0.0, 'neu': 0.0, 'neg': 0.0}

        try:
            scores = self.vader_analyzer.polarity_scores(text)
            return scores
        except Exception as e:
            logger.error(f"❌ Error en análisis Vader: {e}")
            return {'compound': 0.0, 'pos': 0.0, 'neu': 0.0, 'neg': 0.0}

    def analyze_sentiment_textblob(self, text: str) -> Dict[str, float]:
        """
        Analizar sentimiento usando TextBlob

        Args:
            text: Texto a analizar

        Returns:
            Diccionario con polaridad y subjetividad
        """
        if not self.textblob_analyzer:
            return {'polarity': 0.0, 'subjectivity': 0.0}

        try:
            blob = self.textblob_analyzer(text)
            return {
                'polarity': blob.sentiment.polarity,
                'subjectivity': blob.sentiment.subjectivity
            }
        except Exception as e:
            logger.error(f"❌ Error en análisis TextBlob: {e}")
            return {'polarity': 0.0, 'subjectivity': 0.0}

    def analyze_company_sentiment(self, symbol: str, news_limit: int = 10) -> Dict:
        """
        Analizar el sentimiento general de una empresa basado en sus noticias

        Args:
            symbol: Símbolo bursátil
            news_limit: Número máximo de noticias a analizar

        Returns:
            Diccionario con análisis completo de sentimientos
        """
        logger.info(f"🔍 Analizando sentimiento para {symbol}...")

        # Obtener noticias
        news = self.get_company_news(symbol, news_limit)

        if not news:
            return {
                'symbol': symbol,
                'news_count': 0,
                'error': 'No se encontraron noticias',
                'sentiment': {
                    'vader_compound': 0.0,
                    'textblob_polarity': 0.0,
                    'textblob_subjectivity': 0.0,
                    'overall_score': 0.0
                },
                'news_analysis': []
            }

        # Analizar cada noticia
        news_analysis = []
        total_vader_compound = 0.0
        total_textblob_polarity = 0.0
        total_textblob_subjectivity = 0.0

        for i, article in enumerate(news, 1):
            title = article.get('title', '')
            if not title:
                continue

            # Analizar sentimientos
            vader_scores = self.analyze_sentiment_vader(title)
            textblob_scores = self.analyze_sentiment_textblob(title)

            # Acumular scores
            total_vader_compound += vader_scores['compound']
            total_textblob_polarity += textblob_scores['polarity']
            total_textblob_subjectivity += textblob_scores['subjectivity']

            # Guardar análisis individual
            news_analysis.append({
                'id': i,
                'title': title,
                'published_date': article.get('publishedDate', ''),
                'vader': vader_scores,
                'textblob': textblob_scores
            })

        # Calcular promedios
        news_count = len(news_analysis)
        avg_vader_compound = total_vader_compound / news_count if news_count > 0 else 0.0
        avg_textblob_polarity = total_textblob_polarity / news_count if news_count > 0 else 0.0
        avg_textblob_subjectivity = total_textblob_subjectivity / news_count if news_count > 0 else 0.0

        # Calcular score general (promedio de Vader compound y TextBlob polarity)
        overall_score = (avg_vader_compound + avg_textblob_polarity) / 2

        result = {
            'symbol': symbol,
            'news_count': news_count,
            'sentiment': {
                'vader_compound': round(avg_vader_compound, 4),
                'textblob_polarity': round(avg_textblob_polarity, 4),
                'textblob_subjectivity': round(avg_textblob_subjectivity, 4),
                'overall_score': round(overall_score, 4)
            },
            'news_analysis': news_analysis,
            'last_updated': datetime.now().isoformat()
        }

        logger.info(f"✅ Análisis completado para {symbol}: Score general = {result['sentiment']['overall_score']}")
        return result

    def analyze_multiple_companies(self, symbols: List[str], news_limit: int = 10, delay: float = 1.0) -> List[Dict]:
        """
        Analizar sentimientos para múltiples empresas

        Args:
            symbols: Lista de símbolos bursátiles
            news_limit: Número máximo de noticias por empresa
            delay: Segundos de espera entre peticiones para evitar rate limits

        Returns:
            Lista con análisis de sentimientos para cada empresa
        """
        results = []

        logger.info(f"🚀 Iniciando análisis de {len(symbols)} empresas...")

        for i, symbol in enumerate(symbols, 1):
            logger.info(f"📊 Procesando {i}/{len(symbols)}: {symbol}")

            try:
                analysis = self.analyze_company_sentiment(symbol, news_limit)
                results.append(analysis)

                # Esperar entre peticiones para evitar rate limits
                if i < len(symbols):
                    logger.info(f"⏳ Esperando {delay} segundos antes de la siguiente petición...")
                    time.sleep(delay)

            except Exception as e:
                logger.error(f"❌ Error al analizar {symbol}: {e}")
                results.append({
                    'symbol': symbol,
                    'news_count': 0,
                    'error': str(e),
                    'sentiment': {
                        'vader_compound': 0.0,
                        'textblob_polarity': 0.0,
                        'textblob_subjectivity': 0.0,
                        'overall_score': 0.0
                    },
                    'news_analysis': []
                })

        logger.info(f"🎉 Análisis completado para {len(results)} empresas")
        return results

    def get_sentiment_summary(self, analysis_results: List[Dict]) -> Dict:
        """
        Generar resumen del análisis de sentimientos

        Args:
            analysis_results: Resultados del análisis

        Returns:
            Diccionario con estadísticas resumen
        """
        if not analysis_results:
            return {'error': 'No hay resultados para resumir'}

        total_companies = len(analysis_results)
        companies_with_news = len([r for r in analysis_results if r['news_count'] > 0])

        # Calcular estadísticas
        scores = [r['sentiment']['overall_score'] for r in analysis_results if r['news_count'] > 0]
        avg_score = sum(scores) / len(scores) if scores else 0.0

        # Clasificar sentimientos
        positive = len([s for s in scores if s > 0.1])
        negative = len([s for s in scores if s < -0.1])
        neutral = len([s for s in scores if -0.1 <= s <= 0.1])

        return {
            'total_companies': total_companies,
            'companies_with_news': companies_with_news,
            'average_sentiment_score': round(avg_score, 4),
            'sentiment_distribution': {
                'positive': positive,
                'negative': negative,
                'neutral': neutral
            },
            'top_positive': sorted(
                [(r['symbol'], r['sentiment']['overall_score']) for r in analysis_results if r['news_count'] > 0],
                key=lambda x: x[1], reverse=True
            )[:5],
            'top_negative': sorted(
                [(r['symbol'], r['sentiment']['overall_score']) for r in analysis_results if r['news_count'] > 0],
                key=lambda x: x[1]
            )[:5]
        }

    def _get_sample_news_data(self, symbol: str, limit: int) -> List[Dict]:
        """
        Proporciona datos de ejemplo para demostración cuando la API no está disponible

        Args:
            symbol: Símbolo bursátil
            limit: Número máximo de noticias

        Returns:
            Lista de diccionarios con datos de ejemplo
        """
        sample_data = {
            'AAPL': [
                {
                    'title': 'Apple Inc. Reports Strong Q3 Earnings, Beating Analyst Expectations',
                    'publishedDate': '2025-01-15T10:30:00Z',
                    'content': 'Apple reported better-than-expected quarterly earnings, with revenue growth driven by strong iPhone sales.',
                    'url': 'https://example.com/apple-earnings',
                    'source': 'Financial Times'
                },
                {
                    'title': 'Apple Stock Rises 5% After Positive Analyst Upgrades',
                    'publishedDate': '2025-01-14T14:20:00Z',
                    'content': 'Several Wall Street analysts upgraded Apple stock following the earnings report.',
                    'url': 'https://example.com/apple-upgrade',
                    'source': 'Bloomberg'
                },
                {
                    'title': 'Apple Faces Supply Chain Challenges in China',
                    'publishedDate': '2025-01-13T09:15:00Z',
                    'content': 'Apple may face production delays due to ongoing supply chain issues in China.',
                    'url': 'https://example.com/apple-supply-chain',
                    'source': 'Reuters'
                }
            ],
            'TSLA': [
                {
                    'title': 'Tesla Delivers Record Number of Vehicles in Q4',
                    'publishedDate': '2025-01-15T11:00:00Z',
                    'content': 'Tesla achieved record vehicle deliveries, surpassing market expectations.',
                    'url': 'https://example.com/tesla-deliveries',
                    'source': 'CNBC'
                },
                {
                    'title': 'Tesla Stock Surges on EV Market Share Gains',
                    'publishedDate': '2025-01-14T16:45:00Z',
                    'content': 'Tesla continues to dominate the electric vehicle market with increasing market share.',
                    'url': 'https://example.com/tesla-market-share',
                    'source': 'MarketWatch'
                },
                {
                    'title': 'Tesla Faces Competition from Chinese EV Makers',
                    'publishedDate': '2025-01-12T08:30:00Z',
                    'content': 'Chinese electric vehicle manufacturers are posing increasing competition to Tesla.',
                    'url': 'https://example.com/tesla-competition',
                    'source': 'The Wall Street Journal'
                }
            ],
            'GOOGL': [
                {
                    'title': 'Google Cloud Revenue Grows 25% Year-Over-Year',
                    'publishedDate': '2025-01-15T13:20:00Z',
                    'content': 'Alphabet\'s cloud business showed strong growth in the latest quarter.',
                    'url': 'https://example.com/google-cloud-growth',
                    'source': 'TechCrunch'
                },
                {
                    'title': 'Google Announces New AI Initiatives',
                    'publishedDate': '2025-01-14T10:00:00Z',
                    'content': 'Google unveiled several new artificial intelligence projects and partnerships.',
                    'url': 'https://example.com/google-ai',
                    'source': 'Wired'
                },
                {
                    'title': 'Google Faces Antitrust Scrutiny in Europe',
                    'publishedDate': '2025-01-11T12:15:00Z',
                    'content': 'European regulators continue investigation into Google\'s business practices.',
                    'url': 'https://example.com/google-antitrust',
                    'source': 'BBC News'
                }
            ]
        }

        # Obtener datos de ejemplo para el símbolo solicitado
        news_data = sample_data.get(symbol.upper(), [])

        # Si no hay datos específicos para el símbolo, usar datos genéricos
        if not news_data:
            news_data = [
                {
                    'title': f'{symbol.upper()} Shows Positive Market Performance',
                    'publishedDate': '2025-01-15T10:00:00Z',
                    'content': f'{symbol.upper()} demonstrated strong market performance in recent trading sessions.',
                    'url': f'https://example.com/{symbol.lower()}-performance',
                    'source': 'Market News'
                },
                {
                    'title': f'Analysts Optimistic About {symbol.upper()} Future Prospects',
                    'publishedDate': '2025-01-14T14:30:00Z',
                    'content': f'Wall Street analysts remain optimistic about {symbol.upper()}\'s growth potential.',
                    'url': f'https://example.com/{symbol.lower()}-outlook',
                    'source': 'Financial Review'
                },
                {
                    'title': f'{symbol.upper()} Announces Strategic Business Updates',
                    'publishedDate': '2025-01-13T09:45:00Z',
                    'content': f'{symbol.upper()} revealed important updates regarding its business strategy.',
                    'url': f'https://example.com/{symbol.lower()}-updates',
                    'source': 'Business Daily'
                }
            ]

        # Limitar el número de resultados
        return news_data[:limit]


def main():
    """
    Función principal para demostrar el uso del analizador
    """
    # Lista de ejemplo de símbolos bursátiles
    sample_symbols = ['AAPL', 'GOOGL', 'MSFT', 'TSLA', 'AMZN']

    print("📰 Analizador de Sentimientos de Noticias Bursátiles")
    print("=" * 60)

    try:
        # Inicializar analizador
        analyzer = SentimentAnalyzer()

        # Analizar empresas
        results = analyzer.analyze_multiple_companies(sample_symbols, news_limit=5, delay=2.0)

        # Mostrar resultados
        print("\n📊 RESULTADOS DEL ANÁLISIS:")
        print("-" * 60)

        for result in results:
            print(f"\n🏢 {result['symbol']}:")
            if result['news_count'] > 0:
                sentiment = result['sentiment']
                print(f"   🎯 Score general: {sentiment['overall_score']:.4f}")
                print(f"   🤖 Vader: {sentiment['vader_compound']:.4f}")
                print(f"   📝 TextBlob: {sentiment['textblob_polarity']:.4f}")
                print(f"   📈 Noticias analizadas: {result['news_count']}")
            else:
                print(f"   ❌ {result.get('error', 'Sin datos')}")

        # Mostrar resumen
        summary = analyzer.get_sentiment_summary(results)
        print("\n📈 RESUMEN GENERAL:")
        print("-" * 60)
        print(f"🏢 Empresas analizadas: {summary['total_companies']}")
        print(f"📰 Empresas con noticias: {summary['companies_with_news']}")
        print(f"📊 Sentimiento promedio: {summary['average_sentiment_score']:.4f}")
        print(f"😊 Sentimiento positivo: {summary['sentiment_distribution']['positive']}")
        print(f"😔 Sentimiento negativo: {summary['sentiment_distribution']['negative']}")
        print(f"😐 Sentimiento neutral: {summary['sentiment_distribution']['neutral']}")

        if summary['top_positive']:
            print("\n🥇 Top 3 empresas más positivas:")
            for symbol, score in summary['top_positive'][:3]:
                print(f"   {symbol}: {score:.4f}")

        if summary['top_negative']:
            print("\n🥇 Top 3 empresas más negativas:")
            for symbol, score in summary['top_negative'][:3]:
                print(f"   {symbol}: {score:.4f}")
    except Exception as e:
        logger.error(f"❌ Error en la ejecución principal: {e}")
        print(f"\n❌ Error: {e}")
        print("\n💡 Asegúrate de tener instaladas las dependencias:")
        print("   pip install requests vaderSentiment textblob")


if __name__ == "__main__":
    main()
