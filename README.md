# Trading212 Portfolio Manager

Una aplicación completa para gestionar y analizar tu portafolio de Trading212, potenciada con Inteligencia Artificial para recomendaciones de inversión y análisis de sentimientos.

## 🚀 Características Principales

### 📊 Gestión de Portafolio
- **Dashboard en tiempo real**: Resumen de P&L, ROI, y distribución de activos.
- **Visualización completa**: Lista detallada de posiciones con búsqueda, filtrado y ordenamiento.
- **Analytics**: Análisis de riesgo, diversificación (HHI) y concentración por sector.
- **Sincronización**: Actualización automática y manual con tu cuenta de Trading212.

### 🤖 Investment Advisor (IA)
- **Recomendaciones Personalizadas**: Sugerencias de inversión basadas en tu perfil de riesgo y preferencias.
- **Análisis Inteligente**: Utiliza Gemini AI para evaluar oportunidades y riesgos.
- **Gestión de Riesgo**: Cálculo automático de Stop Loss y precios objetivo.
- **Sistema Fallback**: Funciona incluso sin API key de Gemini (modo básico).

### 📰 Análisis de Sentimientos
- **Noticias en Tiempo Real**: Integración con NewsAPI para obtener las últimas noticias financieras.
- **Análisis Dual**: Evaluación de sentimientos usando Vader y TextBlob.
- **Scoring**: Puntuación de sentimiento (Positivo/Neutral/Negativo) para cada activo.
- **Integración**: Los datos de sentimiento se incorporan automáticamente en las recomendaciones.

### 💰 Inversiones Disponibles
- **Base de Datos Local**: Acceso rápido a todas las inversiones disponibles en Trading212.
- **Búsqueda Avanzada**: Encuentra activos por nombre, ticker, sector o país.
- **Información Enriquecida**: Logos de empresas y datos detallados.

---

## 📋 Requisitos Previos

- **Python 3.8+**: [Descargar aquí](https://www.python.org/downloads/)
- **Node.js 16+**: [Descargar aquí](https://nodejs.org/)
- **API Key de Trading212**: Necesaria para acceder a tus datos.
- **API Key de Google Gemini** (Opcional): Para funciones avanzadas de IA.
- **API Key de NewsAPI** (Opcional): Para análisis de noticias en tiempo real.

---

## 🛠️ Instalación y Configuración

### 1. Instalación Automática
Ejecuta el script de instalación en PowerShell como Administrador:
```powershell
.\install.ps1
```

### 2. Configuración de API Keys

#### Trading212 API Key (Requerido)
1. Inicia sesión en [Trading212](https://www.trading212.com).
2. Ve a **Settings** -> **API**.
3. Genera una nueva API Key con permisos de **LECTURA** (Account Information, Portfolio, Orders History). **NO habilites permisos de Trading**.
4. Añádela al archivo `backend/.env`:
   ```env
   TRADING212_API_KEY=tu_api_key_aqui
   ```

#### Gemini AI API Key (Opcional - Recomendado)
1. Visita [Google AI Studio](https://aistudio.google.com/).
2. Crea una API Key.
3. Añádela al archivo `backend/.env`:
   ```env
   GEMINI_API_KEY=tu_api_key_aqui
   ```

#### NewsAPI Key (Opcional)
1. Regístrate en [NewsAPI](https://newsapi.org/).
2. Obtén tu API Key.
3. Añádela al archivo `backend/.env`:
   ```env
   NEWS_API_KEY=tu_api_key_aqui
   ```

### 3. Poblar Base de Datos (Inicial)
Para tener la lista completa de inversiones disponibles:
```powershell
.\populate_db.bat
```

---

## 🏃‍♂️ Ejecución

### Opción 1: Script Automático
Inicia tanto el backend como el frontend con un solo comando:
```powershell
.\start.ps1
```

### Opción 2: Manual
**Terminal 1 (Backend):**
```powershell
.\start_backend.bat
```
**Terminal 2 (Frontend):**
```powershell
.\start_frontend.bat
```

### Acceso
- **Frontend (App)**: http://localhost:3000
- **Backend (API)**: http://localhost:5000

---

## 📖 Guía de Uso

### Dashboard
Vista general de tu cuenta. Sincroniza tus datos aquí para ver el estado actual de tu portafolio.

### Investment Advisor
1. Ve a la sección "Investment Advisor".
2. Configura tus preferencias (Monto, Riesgo, Horizonte temporal, Sectores).
3. Recibe recomendaciones detalladas generadas por IA.

### Análisis de Sentimientos
El análisis se ejecuta automáticamente al solicitar recomendaciones. Puedes ver el "Score de Sentimiento" en los detalles de cada activo recomendado.

---

## 🔧 Solución de Problemas

### Error "GEMINI_API_KEY no está configurada"
- Verifica el archivo `.env`.
- Si no deseas usar Gemini, la aplicación usará el modo fallback automáticamente.

### Error "429 Too Many Requests" (Trading212)
- Has excedido el límite de 60 solicitudes por minuto. Espera unos minutos antes de volver a sincronizar.

### Frontend/Backend no inician
- Ejecuta `fix_installation.bat` para reparar dependencias.
- Asegúrate de que los puertos 3000 y 5000 estén libres.

---

## 🏗️ Estructura del Proyecto

```
Trading212/
├── backend/              # API Python/Flask
│   ├── app/
│   │   ├── models/       # Modelos SQLAlchemy
│   │   ├── routes/       # Endpoints API
│   │   ├── services/     # Lógica de negocio (IA, Trading212, News)
│   │   └── utils/        # Utilidades
│   ├── sentiment_analyzer.py # Motor de análisis de sentimientos
│   └── run.py            # Punto de entrada
├── frontend/             # App React
│   ├── src/
│   │   ├── components/   # Componentes UI
│   │   ├── pages/        # Vistas principales
│   │   └── services/     # Comunicación con API
└── scripts/              # Scripts de instalación y ejecución (.bat, .ps1)
```

---

## 🔒 Seguridad

- **Datos Locales**: Toda la información y API Keys se almacenan localmente en tu equipo.
- **Permisos de Lectura**: La aplicación solo requiere permisos de lectura en Trading212. Nunca habilites permisos de ejecución de órdenes.
- **Sin Servidores Externos**: Tus datos financieros no se envían a servidores de terceros (excepto las consultas anónimas a Gemini/NewsAPI si están activadas).

---

## 🔮 Mejoras Futuras

- [ ] Backtesting de estrategias de inversión.
- [ ] Alertas de precio automáticas.
- [ ] Optimización automática de portafolio (Markowitz).
- [ ] Integración con más fuentes de datos financieros.
- [ ] Exportación de reportes en PDF/Excel.

---
**Desarrollado con ❤️ usando Python, Flask, React y Tailwind CSS**
