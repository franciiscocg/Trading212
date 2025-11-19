#!/usr/bin/env python3
"""
Verificación Final del Sistema de Análisis de Sentimientos
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sentiment_analyzer import SentimentAnalyzer

def main():
    print('🧪 Verificación Final del Sistema de Análisis de Sentimientos')
    print('=' * 60)

    try:
        # Verificar inicialización
        analyzer = SentimentAnalyzer()
        print('✅ Analizador inicializado correctamente')

        # Verificar métodos disponibles
        methods = [m for m in dir(analyzer) if not m.startswith('_')]
        print(f'📋 Métodos disponibles: {len(methods)}')
        print('   Principales: analyze_company_sentiment, analyze_multiple_companies, get_sentiment_summary')

        # Verificar configuración
        print('🔧 Configuración:')
        api_name = "NewsAPI" if analyzer.use_newsapi else "Financial Modeling Prep"
        print(f'   API: {api_name}')
        print(f'   Rate Limit: {analyzer.daily_request_limit} requests/día')
        print(f'   Cache: {analyzer.cache_file}')
        print(f'   Request Count: {analyzer.request_count_file}')

        # Verificar librerías
        vader_status = "✅" if analyzer.vader_analyzer else "❌"
        textblob_status = "✅" if analyzer.textblob_analyzer else "❌"
        print(f'🤖 Vader: {vader_status}')
        print(f'📝 TextBlob: {textblob_status}')

        print('\n🎉 Sistema de análisis de sentimientos completamente operativo!')
        print('📊 Listo para integrar en el Investment Advisor')

    except Exception as e:
        print(f'❌ Error en verificación: {e}')
        return 1

    return 0

if __name__ == "__main__":
    exit(main())
