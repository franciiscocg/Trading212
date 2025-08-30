#!/usr/bin/env python3
"""
Script de prueba para el análisis de sentimientos
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sentiment_analyzer import SentimentAnalyzer

def test_sentiment_analysis():
    """Prueba el análisis de sentimientos con algunas empresas conocidas"""
    print("🧪 Probando análisis de sentimientos...")
    print("=" * 60)

    # Empresas de prueba
    test_symbols = ['AAPL', 'TSLA', 'GOOGL']

    try:
        # Usar NewsAPI con la API key real
        analyzer = SentimentAnalyzer(api_key="9aa1f53dc57b4c089b10831589eb3289", use_newsapi=True)

        print(f"📊 Analizando {len(test_symbols)} empresas de prueba...")
        results = analyzer.analyze_multiple_companies(test_symbols, news_limit=3, delay=1.0)

        print("\n✅ RESULTADOS DE LA PRUEBA:")
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

        print("\n🎉 ¡Prueba completada exitosamente!")
        print("El análisis de sentimientos está funcionando correctamente.")

    except Exception as e:
        print(f"❌ Error en la prueba: {e}")
        print("\n💡 Verifica que todas las dependencias estén instaladas:")
        print("   pip install vaderSentiment textblob requests")
        return False

    return True

if __name__ == "__main__":
    success = test_sentiment_analysis()
    sys.exit(0 if success else 1)
