#!/usr/bin/env python3
"""
Script de Prueba para Endpoints de Análisis de Sentimientos
=======================================================

Este script prueba los nuevos endpoints de análisis de sentimientos
integrados en el Investment Advisor.
"""

import requests
import json
import time
from datetime import datetime

def test_sentiment_endpoints():
    """Probar los endpoints de análisis de sentimientos"""

    base_url = "http://localhost:5000/api"  # URL base correcta con prefijo /api

    print("🧪 Probando Endpoints de Análisis de Sentimientos")
    print("=" * 60)

    # Prueba 1: Análisis de sentimientos para múltiples símbolos
    print("\n📊 Prueba 1: Análisis de sentimientos múltiple")
    print("-" * 40)

    test_data = {
        "symbols": ["AAPL", "GOOGL", "MSFT"],
        "news_limit": 3
    }

    try:
        response = requests.post(f"{base_url}/investment-advisor/sentiment-analysis",
                               json=test_data, timeout=30)

        if response.status_code == 200:
            result = response.json()
            print("✅ Endpoint múltiple funcionando correctamente")
            print(f"   📈 Símbolos analizados: {result.get('symbols_analyzed', 0)}")
            print(f"   📰 Límite de noticias: {result.get('news_limit', 0)}")

            if 'results' in result:
                for res in result['results'][:2]:  # Mostrar solo los primeros 2
                    sentiment = res.get('sentiment', {})
                    print(f"   {res['symbol']}: Score = {sentiment.get('overall_score', 0):.4f}")
        else:
            print(f"❌ Error en endpoint múltiple: {response.status_code}")
            print(f"   Respuesta: {response.text}")

    except requests.exceptions.RequestException as e:
        print(f"❌ Error de conexión en endpoint múltiple: {e}")
        print("💡 Asegúrate de que el servidor Flask esté ejecutándose")

    # Prueba 2: Análisis de sentimientos para un símbolo individual
    print("\n📊 Prueba 2: Análisis de sentimientos individual")
    print("-" * 40)

    try:
        response = requests.get(f"{base_url}/investment-advisor/sentiment-analysis/AAPL?news_limit=3",
                              timeout=30)

        if response.status_code == 200:
            result = response.json()
            print("✅ Endpoint individual funcionando correctamente")

            if 'result' in result:
                res = result['result']
                sentiment = res.get('sentiment', {})
                print(f"   {res['symbol']}: Score = {sentiment.get('overall_score', 0):.4f}")
                print(f"   📰 Noticias analizadas: {res.get('news_count', 0)}")
        else:
            print(f"❌ Error en endpoint individual: {response.status_code}")
            print(f"   Respuesta: {response.text}")

    except requests.exceptions.RequestException as e:
        print(f"❌ Error de conexión en endpoint individual: {e}")

    # Prueba 3: Verificar integración en análisis de inversiones
    print("\n📊 Prueba 3: Integración en Investment Advisor")
    print("-" * 40)

    investment_data = {
        "user_id": "test_user",
        "preferences": {
            "riskTolerance": "medium",
            "investmentAmount": 1000,
            "sectors": ["technology"],
            "investmentHorizon": "1-3-years"
        }
    }

    try:
        response = requests.post(f"{base_url}/investment-advisor/analyze",
                               json=investment_data, timeout=60)

        if response.status_code == 200:
            result = response.json()
            print("✅ Investment Advisor funcionando correctamente")

            if 'recommendations' in result:
                recommendations = result['recommendations']
                print(f"   📋 Recomendaciones generadas: {len(recommendations)}")

                # Verificar si incluyen análisis de sentimientos
                has_sentiment = any('sentimentAnalysis' in rec for rec in recommendations)
                if has_sentiment:
                    print("✅ Análisis de sentimientos integrado en recomendaciones")
                    for rec in recommendations[:2]:  # Mostrar solo las primeras 2
                        if 'sentimentAnalysis' in rec:
                            sentiment = rec['sentimentAnalysis']
                            print(f"   {rec['symbol']}: Sentimiento = {sentiment.get('sentiment_interpretation', 'N/A')}")
                else:
                    print("⚠️ Recomendaciones no incluyen análisis de sentimientos")
            else:
                print("⚠️ No se encontraron recomendaciones en la respuesta")
        else:
            print(f"❌ Error en Investment Advisor: {response.status_code}")
            print(f"   Respuesta: {response.text}")

    except requests.exceptions.RequestException as e:
        print(f"❌ Error de conexión en Investment Advisor: {e}")

    print("\n🎉 Pruebas completadas")
    print("=" * 60)
    print(f"📅 Fecha de prueba: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    test_sentiment_endpoints()
