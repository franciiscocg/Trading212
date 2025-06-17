# 🔑 Configuración de API Key de Trading212

## ¿Qué es una API Key?

Una API Key es una clave de acceso que permite a aplicaciones externas conectarse de forma segura a tu cuenta de Trading212 para obtener información sobre tu portafolio.

## ⚠️ Importante sobre Límites de Velocidad

Trading212 tiene límites estrictos en su API:
- **Máximo 60 solicitudes por minuto**
- Si excedes este límite, recibirás un error "429 Too Many Requests"
- Debes esperar unos minutos antes de hacer más solicitudes

## 📋 Cómo Obtener tu API Key

### Paso 1: Acceder a Trading212
1. Ve a [Trading212.com](https://www.trading212.com)
2. Inicia sesión en tu cuenta

### Paso 2: Navegar a Configuración de API
1. Ve a **"Settings"** (Configuración)
2. Busca la sección **"API"** 
3. Haz clic en **"Generate API Key"** o **"Create New Token"**

### Paso 3: Configurar Permisos
- ✅ **Account Information** (Información de cuenta)
- ✅ **Portfolio** (Portafolio)
- ✅ **Orders History** (Historial de órdenes)
- ❌ **Trading** (NO habilites trading para mayor seguridad)

### Paso 4: Guardar la API Key
1. Copia la API key generada
2. **⚠️ IMPORTANTE**: Guárdala de forma segura
3. No la compartas con nadie
4. No la subas a repositorios públicos

## 🔧 Configurar en la Aplicación

### Opción 1: Desde la Interfaz Web
1. Ve a **Settings** en la aplicación
2. Pega tu API key en el campo correspondiente
3. Haz clic en **"Validate API Key"**
4. Si es válida, aparecerá un mensaje de confirmación

### Opción 2: Desde el Archivo .env
1. Abre `backend/.env`
2. Reemplaza `your_trading212_api_key_here` con tu API key real:
   ```
   TRADING212_API_KEY=tu_api_key_aqui
   ```
3. Guarda el archivo
4. Reinicia el backend

## 🛠️ Solución de Problemas

### Error "Invalid API Key"
- ✅ Verifica que la API key esté copiada correctamente
- ✅ Asegúrate de que tenga los permisos correctos
- ✅ Verifica que tu cuenta de Trading212 esté activa

### Error "429 Too Many Requests"
- ⏱️ Espera 2-3 minutos antes de intentar de nuevo
- 🔄 Evita hacer múltiples sincronizaciones seguidas
- 📊 Una sincronización por hora es suficiente para la mayoría de usuarios

### Error "Connection Failed"
- 🌐 Verifica tu conexión a internet
- 🔥 Verifica que no haya firewall bloqueando la conexión
- 🏢 Si estás en una red corporativa, puede estar bloqueada

## 🔐 Seguridad

### ✅ Buenas Prácticas
- Usa API keys con permisos mínimos necesarios
- No habilites permisos de trading
- Regenera la API key periódicamente
- No compartas tu API key

### ❌ Lo que NO hacer
- No habilites permisos de trading innecesarios
- No guardes la API key en archivos públicos
- No uses la misma API key en múltiples aplicaciones
- No ignores los límites de velocidad

## 📊 Uso Recomendado

- **Sincronización manual**: Cuando quieras ver datos actualizados
- **Frecuencia recomendada**: 1-2 veces por día máximo
- **Horarios sugeridos**: Al inicio del día de trading y al final

## 🆘 Soporte

Si tienes problemas:
1. Revisa la documentación oficial de Trading212
2. Verifica que tu cuenta tenga acceso a la API
3. Contacta al soporte de Trading212 si persisten los problemas

---

**Nota**: Esta aplicación es independiente y no está afiliada oficialmente con Trading212.
