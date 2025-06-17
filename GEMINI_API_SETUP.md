# Configuración de Gemini AI API

## Obtener API Key de Gemini

1. **Visita Google AI Studio**
   - Ve a [https://aistudio.google.com/](https://aistudio.google.com/)
   - Inicia sesión con tu cuenta de Google

2. **Crear una nueva API Key**
   - Haz clic en "Get API Key" en el menú lateral
   - Selecciona "Create API Key"
   - Elige tu proyecto de Google Cloud (o crea uno nuevo)
   - Copia la API Key generada

3. **Configurar en el Backend**
   - Abre el archivo `backend/.env`
   - Agrega la línea: `GEMINI_API_KEY=tu_api_key_aqui`
   - Ejemplo:
     ```
     GEMINI_API_KEY=AIzaSyBxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
     ```

4. **Reiniciar el Backend**
   - Detén el servidor backend (Ctrl+C)
   - Reinicia con: `python run.py`

## Funcionalidades del Investment Advisor

### ✨ **Análisis Inteligente**
- **Recomendaciones personalizadas** basadas en tu portafolio actual
- **Análisis de riesgo** adaptado a tu tolerancia
- **Precios objetivo y stop loss** calculados por AI
- **Horizonte temporal** específico para cada inversión

### 🎯 **Configuración de Preferencias**
- **Tolerancia al riesgo**: Conservador, Moderado, Agresivo
- **Horizonte de inversión**: Corto, medio o largo plazo
- **Cantidad a invertir**: Configurable según tu presupuesto

### 📊 **Métricas Avanzadas**
- **Análisis fundamental** con P/E, ROE, etc.
- **Análisis técnico** con niveles de soporte/resistencia
- **Volatilidad esperada** y Sharpe ratio
- **Insights del mercado** actualizados

### 🛡️ **Gestión de Riesgo**
- **Stop loss automático** calculado por AI
- **Diversificación recomendada**
- **Máxima pérdida potencial**
- **Análisis de correlación** con tu portafolio actual

## Uso Recomendado

1. **Configura tus preferencias** antes del primer análisis
2. **Revisa las recomendaciones** cuidadosamente
3. **Considera tu situación financiera** personal
4. **No inviertas más de lo que puedes permitirte perder**
5. **Usa las recomendaciones como guía**, no como garantía

## Limitaciones

- Las recomendaciones son generadas por AI y no constituyen asesoramiento financiero profesional
- Los mercados son impredecibles y las inversiones conllevan riesgo
- Siempre haz tu propia investigación antes de invertir
- Considera consultar con un asesor financiero profesional

## Troubleshooting

### Error "GEMINI_API_KEY no está configurada"
- Verifica que la API key está en el archivo `.env`
- Reinicia el backend después de agregar la key
- Asegúrate de que no hay espacios extra en la configuración

### Error "Error comunicándose con Gemini API"
- Verifica tu conexión a internet
- Confirma que la API key es válida
- Revisa que tienes cuota disponible en Google AI Studio

### Análisis muy lento
- Es normal que tome 10-30 segundos
- Gemini procesa mucha información para dar recomendaciones precisas
- Ten paciencia durante el análisis

## Mejoras Futuras

- [ ] Integración con datos de mercado en tiempo real
- [ ] Backtesting de estrategias
- [ ] Alertas de precio automáticas
- [ ] Portfolio optimization automático
- [ ] Análisis de sentimiento del mercado
