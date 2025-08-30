#!/usr/bin/env python3
"""
Script para poblar la base de datos con las inversiones disponibles de Trading212
Ejecutar: python populate_investments.py
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.services.trading212_service import Trading212Service

def main():
    print("🚀 Iniciando población de inversiones disponibles...")

    # Crear aplicación Flask
    app = create_app()

    with app.app_context():
        try:
            # Crear tablas si no existen
            from app import db
            db.create_all()
            print("✅ Tablas de base de datos creadas/verficadas")

            # Inicializar servicio de Trading212
            trading_service = Trading212Service()
            print("✅ Servicio de Trading212 inicializado")

            # Sincronizar inversiones
            print("📊 Sincronizando inversiones desde Trading212...")
            result = trading_service.sync_available_investments_to_db()

            print("✅ Sincronización completada exitosamente!")
            print(f"   📈 Nuevas inversiones: {result['synced']}")
            print(f"   🔄 Inversiones actualizadas: {result['updated']}")
            print(f"   📊 Total procesadas: {result['total']}")

            # Verificar estadísticas
            from app.models import AvailableInvestment
            total_in_db = AvailableInvestment.query.count()
            print(f"   💾 Total en base de datos: {total_in_db}")

            # Mostrar algunos ejemplos
            sample_investments = AvailableInvestment.query.limit(5).all()
            if sample_investments:
                print("\n📋 Ejemplos de inversiones guardadas:")
                for inv in sample_investments:
                    print(f"   • {inv.name} ({inv.ticker}) - {inv.exchange}")

        except Exception as e:
            print(f"❌ Error durante la población: {e}")
            sys.exit(1)

        except Exception as e:
            print(f"❌ Error durante la población: {e}")
            sys.exit(1)

if __name__ == "__main__":
    main()
