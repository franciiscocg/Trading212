# Sistema de Inversiones Disponibles

Este sistema permite almacenar y mostrar todas las inversiones disponibles en Trading212 de manera eficiente.

## 🚀 Características

- ✅ **Base de datos local**: Todas las inversiones se almacenan localmente para acceso rápido
- ✅ **Logos de empresas**: Muestra logos de empresas usando Clearbit API
- ✅ **Búsqueda rápida**: Búsqueda instantánea por nombre o ticker
- ✅ **Paginación**: Carga eficiente de grandes listas
- ✅ **Sincronización automática**: Actualización automática desde Trading212
- ✅ **Caché inteligente**: Reduce llamadas a la API

## 📋 Requisitos Previos

1. **Base de datos configurada** en `.env`
2. **API Key de Trading212** configurada
3. **Entorno virtual** activado

## 🛠️ Configuración Inicial

### 1. Poblar Base de Datos

Ejecuta el script de población para cargar todas las inversiones:

```bash
# Windows
populate_db.bat

# O manualmente
cd backend
python populate_investments.py
```

### 2. Verificar Instalación

```bash
# Verificar que las inversiones se cargaron
curl http://localhost:5000/api/investments/available?limit=5
```

## 🔧 Endpoints de API

### Obtener Inversiones
```http
GET /api/investments/available?exchange=NASDAQ&limit=50&offset=0
```

### Buscar Inversiones
```http
GET /api/investments/search?q=apple&limit=20
```

### Obtener Exchanges
```http
GET /api/investments/exchanges
```

### Sincronizar Manualmente
```http
POST /api/investments/sync
```

### Limpiar Caché
```http
POST /api/investments/cache/clear?type=instruments
```

## 📊 Estructura de Datos

Cada inversión incluye:
- `ticker`: Símbolo (ej: "AAPL")
- `name`: Nombre completo (ej: "Apple Inc.")
- `logo_url`: URL del logo de la empresa
- `current_price`: Precio actual
- `current_price_eur`: Precio en euros
- `exchange`: Bolsa donde se negocia
- `sector`: Sector económico
- `country`: País de origen

## 🎨 Interfaz de Usuario

La página de inversiones muestra:
- ✅ Logo de la empresa (cuando disponible)
- ✅ Nombre y ticker juntos
- ✅ Precio en euros y moneda original
- ✅ Información de exchange, sector y país
- ✅ Búsqueda en tiempo real
- ✅ Filtros por exchange

## 🔄 Sincronización

### Automática
- Se ejecuta automáticamente cuando no hay datos en la base de datos
- Fallback a API cuando falla la consulta local

### Manual
- Endpoint `/api/investments/sync` para forzar sincronización
- Script `populate_investments.py` para carga inicial

## 🐛 Solución de Problemas

### Sin datos mostrados
1. Verifica que la base de datos esté poblada
2. Ejecuta `populate_db.bat`
3. Revisa logs del backend

### Logos no aparecen
- Los logos se cargan desde Clearbit API
- Si no aparecen, es normal (no todos los tickers tienen logo)
- Fallback automático oculta logos que no cargan

### Búsqueda lenta
- Asegúrate de que los índices de base de datos estén creados
- La búsqueda usa índices en `ticker`, `name`, `exchange` y `sector`

## 📈 Rendimiento

- **Carga inicial**: ~5000 inversiones en ~2-3 minutos
- **Búsqueda**: < 100ms con índices
- **Paginación**: 50 elementos por página
- **Caché**: 30 minutos para instrumentos, 1 hora para exchanges

## 🔧 Mantenimiento

### Actualizar datos
```bash
# Diariamente o cuando sea necesario
curl -X POST http://localhost:5000/api/investments/sync
```

### Limpiar caché
```bash
# Si hay problemas de rendimiento
curl -X POST http://localhost:5000/api/investments/cache/clear
```

### Verificar estado
```bash
curl http://localhost:5000/api/investments/health
```
