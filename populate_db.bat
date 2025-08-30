@echo off
echo 🚀 Poblando base de datos con inversiones disponibles...
echo.

cd /d "%~dp0backend"

if not exist ".env" (
    echo ❌ Archivo .env no encontrado. Copia .env.example a .env y configura las variables.
    pause
    exit /b 1
)

echo 📦 Activando entorno virtual...
call ..\venv\Scripts\activate.bat

echo 🐍 Ejecutando script de población...
python populate_investments.py

echo.
echo ✅ Proceso completado.
pause
