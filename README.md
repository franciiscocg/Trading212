# Trading212 Portfolio Manager

Una aplicación completa para gestionar y analizar tu portafolio de Trading212.

## 🚀 Instalación Rápida

### Requisitos Previos
- **Python 3.8+** - [Descargar aquí](https://www.python.org/downloads/)
- **Node.js 16+** - [Descargar aquí](https://nodejs.org/)

### Instalación Automática
```cmd
install.bat
```

### Configuración
1. Edita `backend\.env` y añade tu API key de Trading212:
```env
TRADING212_API_KEY=tu_api_key_aqui
```

### Ejecutar Aplicación
```cmd
:: Backend (en una ventana)
start_backend.bat

:: Frontend (en otra ventana)  
start_frontend.bat
```

### Acceder a la Aplicación
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:5000

## 📊 Características

### Dashboard
- ✅ Resumen del portafolio en tiempo real
- ✅ Métricas de rendimiento (P&L, ROI)
- ✅ Gráficos de distribución de activos
- ✅ Top posiciones ganadoras/perdedoras

### Portafolio
- ✅ Vista completa de todas las posiciones
- ✅ Búsqueda y filtrado avanzado
- ✅ Ordenamiento por columnas
- ✅ Detalles de P&L por posición

### Analytics
- ✅ Análisis de riesgo del portafolio
- ✅ Métricas de diversificación (HHI)
- ✅ Concentración por sector
- ✅ Recomendaciones automáticas de mejora

### Configuración
- ✅ Gestión segura de API Key
- ✅ Estado de conexión con Trading212
- ✅ Sincronización manual de datos

## 🔧 Solución de Problemas

### Error de Instalación
```cmd
fix_installation.bat
```

### Python no encontrado
- Instala Python desde python.org
- Marca "Add to PATH" durante la instalación

### Node.js no encontrado
- Instala Node.js desde nodejs.org
- Reinicia la terminal después de la instalación

## � Obtener API Key de Trading212

1. Inicia sesión en Trading212
2. Ve a **Configuración** → **API**
3. Genera nueva API key con permisos de **lectura**
4. Copia la key y pégala en `backend\.env`

## 🏗️ Estructura del Proyecto

```
Trading212/
├── backend/              # API Python/Flask
│   ├── app/
│   │   ├── models/       # Modelos de base de datos
│   │   ├── routes/       # Endpoints de la API
│   │   ├── services/     # Integración Trading212
│   │   └── utils/        # Utilidades
│   ├── requirements.txt  # Dependencias Python
│   └── run.py           # Servidor Flask
├── frontend/            # Aplicación React
│   ├── src/
│   │   ├── components/  # Componentes React
│   │   ├── pages/       # Páginas principales
│   │   ├── services/    # Cliente API
│   │   └── utils/       # Utilidades frontend
│   └── package.json     # Dependencias Node
├── install.bat          # Instalación automática
├── start_backend.bat    # Ejecutar backend
├── start_frontend.bat   # Ejecutar frontend
└── README.md
```

## 🛠️ Tecnologías

### Backend
- **Flask** - Framework web
- **SQLAlchemy** - ORM base de datos  
- **Pandas** - Análisis de datos
- **Requests** - Cliente HTTP
- **SQLite** - Base de datos

### Frontend
- **React 18** - Biblioteca UI
- **Tailwind CSS** - Framework CSS
- **Recharts** - Gráficos
- **Axios** - Cliente HTTP
- **React Router** - Navegación

## 📈 API Endpoints

- `GET /api/portfolio` - Datos del portafolio
- `POST /api/portfolio/sync` - Sincronizar con Trading212
- `GET /api/positions` - Todas las posiciones
- `GET /api/analytics/performance` - Métricas de rendimiento
- `GET /api/analytics/risk` - Análisis de riesgo

## 🔒 Seguridad

- ✅ API Key almacenada localmente
- ✅ Solo permisos de lectura requeridos
- ✅ CORS configurado para localhost
- ✅ Validación de entrada en API

## 📝 Notas Importantes

- Esta aplicación es **solo para análisis**, no ejecuta trades
- Los datos se actualizan cuando sincronizas manualmente
- Todos los datos se almacenan en tu computadora
- La API key nunca se envía a servidores externos
