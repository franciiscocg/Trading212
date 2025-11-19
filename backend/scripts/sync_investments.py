#!/usr/bin/env python3
"""Script para sincronizar inversiones disponibles a la base de datos"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.services.trading212_service import Trading212Service

def main():
    app = create_app()
    with app.app_context():
        try:
            service = Trading212Service()
            result = service.sync_available_investments_to_db()
            print("✅ Sync completed successfully!")
            print(f"📊 Results: {result}")
        except Exception as e:
            print(f"❌ Error during sync: {e}")
            sys.exit(1)

if __name__ == "__main__":
    main()
