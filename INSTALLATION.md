# Guía de Instalación y Uso - Trading212 Portfolio Manager

## 📋 Requisitos Previos

- **Python 3.8+** - [Descargar aquí](https://www.python.org/downloads/)
- **Node.js 16+** - [Descargar aquí](https://nodejs.org/)
- **API Key de Trading212** - Obténla desde tu cuenta de Trading212

## 🚀 Instalación Rápida

### Opción 1: Script Automático (Recomendado)
```powershell
# Ejecutar en PowerShell como Administrador
.\install.ps1
```

### Opción 2: Instalación Manual

#### 1. Backend (Python/Flask)
```powershell
cd backend
pip install -r requirements.txt
cp .env.example .env
# Editar .env con tu API key de Trading212
```

#### 2. Frontend (React)
```powershell
cd frontend
npm install
```

## ⚙️ Configuración

### 1. Configura tu API Key de Trading212

Edita el archivo `backend/.env`:
```env
TRADING212_API_KEY=tu_api_key_aqui
TRADING212_API_URL=https://live.trading212.com/api/v0
FLASK_ENV=development
SECRET_KEY=tu-clave-secreta
DATABASE_URL=sqlite:///trading212.db
CORS_ORIGINS=http://localhost:3000
```

### 2. Obtener API Key de Trading212

1. Inicia sesión en Trading212
2. Ve a Configuración → API
3. Genera una nueva API key con permisos de lectura
4. Copia la key y pégala en el archivo `.env`

## 🏃‍♂️ Ejecutar la Aplicación

### Opción 1: Script Automático
```powershell
.\start.ps1
```

### Opción 2: Manual

#### Terminal 1 - Backend:
```powershell
cd backend
python run.py
```

#### Terminal 2 - Frontend:
```powershell
cd frontend
npm start
```

### URLs de Acceso:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:5000

## 📱 Funcionalidades

### Dashboard
- ✅ Resumen del portafolio
- ✅ Métricas de rendimiento en tiempo real
- ✅ Gráficos de distribución
- ✅ Top posiciones ganadoras/perdedoras

### Portafolio
- ✅ Lista completa de posiciones
- ✅ Búsqueda y filtrado
- ✅ Ordenamiento por columnas
- ✅ Detalles de P&L por posición

### Analytics
- ✅ Análisis de riesgo avanzado
- ✅ Métricas de diversificación
- ✅ Concentración del portafolio
- ✅ Recomendaciones automáticas

### Configuración
- ✅ Gestión de API Key
- ✅ Estado de conexión
- ✅ Sincronización manual

## 🔧 Desarrollo

### Estructura del Proyecto
```
Trading212/
├── backend/              # API Python/Flask
│   ├── app/
│   │   ├── models/       # Modelos SQLAlchemy
│   │   ├── routes/       # Endpoints API
│   │   ├── services/     # Lógica de negocio
│   │   └── utils/        # Utilidades
│   ├── requirements.txt  # Dependencias Python
│   └── run.py           # Punto de entrada
├── frontend/            # App React
│   ├── src/
│   │   ├── components/  # Componentes React
│   │   ├── pages/       # Páginas principales
│   │   ├── services/    # Servicios API
│   │   └── utils/       # Utilidades
│   └── package.json     # Dependencias Node
└── README.md
```

### API Endpoints

#### Portfolio
- `GET /api/portfolio` - Obtener portafolio
- `POST /api/portfolio/sync` - Sincronizar con Trading212
- `GET /api/portfolio/summary` - Resumen del portafolio

#### Positions
- `GET /api/positions` - Todas las posiciones
- `GET /api/positions/{ticker}` - Posición específica
- `GET /api/positions/winners` - Posiciones ganadoras
- `GET /api/positions/losers` - Posiciones perdedoras

#### Analytics
- `GET /api/analytics/performance` - Métricas de rendimiento
- `GET /api/analytics/allocation` - Análisis de asignación
- `GET /api/analytics/risk` - Métricas de riesgo

#### Auth
- `POST /api/auth/validate` - Validar API key
- `GET /api/auth/status` - Estado de conexión

## 🛠️ Tecnologías Utilizadas

### Backend
- **Flask** - Framework web Python
- **SQLAlchemy** - ORM para base de datos
- **Requests** - Cliente HTTP
- **Pandas** - Análisis de datos
- **SQLite** - Base de datos

### Frontend
- **React 18** - Library UI
- **Tailwind CSS** - Framework CSS
- **Recharts** - Gráficos
- **Axios** - Cliente HTTP
- **React Router** - Navegación

## 🔒 Seguridad

- ✅ API Key almacenada localmente
- ✅ CORS configurado
- ✅ Validación de entrada
- ✅ Solo permisos de lectura requeridos

## 🐛 Solución de Problemas

### Error: "Module not found"
```powershell
# Reinstalar dependencias
cd backend && pip install -r requirements.txt
cd frontend && npm install
```

### Error: "API Key invalid"
- Verifica que la API key sea correcta
- Asegúrate de que tenga permisos de lectura
- Revisa que la URL de la API sea correcta

### Error: "Connection refused"
- Verifica que el backend esté ejecutándose en puerto 5000
- Revisa el firewall de Windows
- Comprueba que no haya otros servicios usando el puerto

### Error: Frontend no carga
- Asegúrate de que Node.js esté instalado
- Verifica que el puerto 3000 esté libre
- Ejecuta `npm install` en la carpeta frontend

## 📊 Próximas Funcionalidades

- [ ] Alertas de precio
- [ ] Exportación de reportes
- [ ] Comparación con benchmarks
- [ ] Análisis técnico
- [ ] Integración con Yahoo Finance
- [ ] Notificaciones push

## 🆘 Soporte

Si tienes problemas:

1. Revisa los logs en la consola
2. Verifica tu configuración de API
3. Consulta la documentación de Trading212
4. Reinicia los servicios

## 📝 Notas Importantes

- Esta aplicación es solo para análisis, no ejecuta trades
- Los datos se actualizan cuando sincronizas manualmente
- La base de datos SQLite se crea automáticamente
- Todos los datos se almacenan localmente
