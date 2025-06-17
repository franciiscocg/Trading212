@echo off
echo 🚀 Iniciando Backend (Python/Flask)...



:: Activar entorno virtual
call venv\Scripts\activate.bat

cd backend

:: Verificar que el archivo .env existe
if not exist ".env" (
    echo ⚠️  Archivo .env no encontrado. Creando desde ejemplo...
    copy ".env.example" ".env"
    echo 📝 Por favor configura tu API key en backend\.env
    pause
)

:: Iniciar servidor Flask
echo 🌐 Servidor iniciando en http://localhost:5000...
python run.py

pause
