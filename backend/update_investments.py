#!/usr/bin/env python3
"""Script para actualizar inversiones existentes con tickers limpios y exchanges"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.models import AvailableInvestment, db
from datetime import datetime

def guess_exchange_from_ticker(ticker):
    """Intentar determinar el exchange basado en el ticker"""
    if not ticker:
        return 'UNKNOWN'

    ticker_upper = ticker.upper()

    # Exchanges comunes basados en sufijos o patrones conocidos
    if ticker_upper.endswith('.L'):
        return 'LSE'
    elif ticker_upper.endswith('.DE'):
        return 'XETRA'
    elif ticker_upper.endswith('.PA'):
        return 'EURONEXT'
    elif ticker_upper.endswith('.MI'):
        return 'BORSA_ITALIANA'
    elif ticker_upper.endswith('.AS'):
        return 'EURONEXT'
    elif ticker_upper.endswith('.BR'):
        return 'EURONEXT'
    elif ticker_upper.endswith('.OL'):
        return 'OSLO'
    elif ticker_upper.endswith('.ST'):
        return 'NASDAQ_OMX'
    elif ticker_upper.endswith('.HE'):
        return 'HELSINKI'
    elif ticker_upper.endswith('.CO'):
        return 'NASDAQ_OMX'
    elif ticker_upper.endswith('.LS'):
        return 'EURONEXT'
    elif len(ticker) <= 4 and ticker_upper.isalpha():
        return 'NYSE'  # Asumir NYSE para tickers cortos alfabéticos
    else:
        return 'NASDAQ'  # Default para tickers más largos

def main():
    app = create_app()
    with app.app_context():
        try:
            print("🔄 Updating existing investments with clean tickers and exchanges...")

            # Obtener todas las inversiones
            investments = AvailableInvestment.query.all()
            updated_count = 0

            for investment in investments:
                # Limpiar el ticker (remover sufijos como _US_EQ)
                raw_ticker = investment.ticker
                clean_ticker = raw_ticker.split('_')[0] if '_' in raw_ticker else raw_ticker

                # Solo actualizar si el ticker cambió
                if clean_ticker != raw_ticker:
                    # Verificar si ya existe un registro con el ticker limpio
                    existing_clean = AvailableInvestment.query.filter_by(ticker=clean_ticker).first()
                    if existing_clean and existing_clean.id != investment.id:
                        # Si existe, eliminar el duplicado
                        print(f"🗑️  Removing duplicate: {raw_ticker} -> {clean_ticker}")
                        db.session.delete(investment)
                        continue

                    # Actualizar el ticker
                    investment.ticker = clean_ticker
                    print(f"🔧 Updated ticker: {raw_ticker} -> {clean_ticker}")

                # Actualizar exchange basado en el ticker limpio
                new_exchange = guess_exchange_from_ticker(investment.ticker)
                if investment.exchange != new_exchange:
                    investment.exchange = new_exchange
                    print(f"🏛️  Updated exchange for {investment.ticker}: {investment.exchange} -> {new_exchange}")

                # Actualizar logo URL
                new_logo_url = f"https://logo.clearbit.com/{investment.ticker.lower()}.com"
                if investment.logo_url != new_logo_url:
                    investment.logo_url = new_logo_url

                investment.last_updated = datetime.utcnow()
                updated_count += 1

            db.session.commit()
            print(f"✅ Update completed! Updated {updated_count} investments")

            # Mostrar estadísticas
            total_count = AvailableInvestment.query.count()
            exchanges = db.session.query(
                AvailableInvestment.exchange,
                db.func.count(AvailableInvestment.id).label('count')
            ).group_by(AvailableInvestment.exchange).all()

            print(f"📊 Total investments: {total_count}")
            print("🏛️  Exchange distribution:")
            for exchange, count in exchanges:
                if exchange:
                    print(f"   {exchange}: {count}")

        except Exception as e:
            print(f"❌ Error during update: {e}")
            db.session.rollback()
            sys.exit(1)

if __name__ == "__main__":
    main()
