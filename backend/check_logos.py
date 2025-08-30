#!/usr/bin/env python3
"""Script para verificar y actualizar logos que no están disponibles"""

import sys
import os

# Agregar el directorio backend al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.models import AvailableInvestment, db
import requests
from datetime import datetime

def check_logo_exists(url):
    """Verificar si un logo existe"""
    if not url:
        return False
    try:
        response = requests.head(url, timeout=2)
        return response.status_code == 200
    except:
        return False

def main():
    app = create_app()
    with app.app_context():
        try:
            print("🔍 Verificando logos existentes...")

            # Obtener todas las inversiones con logos
            investments_with_logos = AvailableInvestment.query.filter(
                AvailableInvestment.logo_url.isnot(None)
            ).all()

            print(f"📊 Encontrados {len(investments_with_logos)} registros con logos")

            updated_count = 0
            removed_count = 0

            for investment in investments_with_logos:
                if not check_logo_exists(investment.logo_url):
                    print(f"❌ Logo no disponible para {investment.ticker}: {investment.logo_url}")
                    investment.logo_url = None
                    removed_count += 1
                else:
                    updated_count += 1

            # Commit changes
            db.session.commit()

            print("✅ Verificación completada!")
            print(f"📈 Logos válidos mantenidos: {updated_count}")
            print(f"🗑️  Logos inválidos removidos: {removed_count}")

        except Exception as e:
            print(f"❌ Error durante la verificación: {e}")
            db.session.rollback()
            sys.exit(1)

if __name__ == "__main__":
    main()
