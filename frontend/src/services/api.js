import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';

// Crear instancia de axios con configuración base
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor para manejar errores globalmente
api.interceptors.response.use(
  (response) => response,
  (error) => {
    // Logging mejorado de errores
    if (error.response) {
      // El servidor respondió con un código de error
      console.error('API Error Response:', {
        status: error.response.status,
        data: error.response.data,
        endpoint: error.config?.url
      });
      
      // Mejorar mensajes de error para el usuario
      if (error.response.status === 429) {
        error.userMessage = 'Trading212 API rate limit alcanzado. Por favor espera unos minutos.';
      } else if (error.response.status === 401) {
        error.userMessage = 'API key inválida. Verifica tu configuración en Settings.';
      } else if (error.response.status === 500) {
        error.userMessage = error.response.data?.error || 'Error del servidor. Por favor intenta nuevamente.';
      } else if (error.response.status === 404) {
        error.userMessage = 'No se encontraron datos. Sincroniza tu portafolio primero.';
      }
    } else if (error.request) {
      // La petición se hizo pero no hubo respuesta
      console.error('API No Response:', error.message);
      error.userMessage = 'No se pudo conectar con el servidor. Verifica que el backend esté corriendo.';
    } else {
      // Error al configurar la petición
      console.error('API Request Error:', error.message);
      error.userMessage = 'Error configurando la petición: ' + error.message;
    }
    
    return Promise.reject(error);
  }
);

// Servicios de Portfolio
export const portfolioService = {
  getPortfolio: (userId = 'default') => 
    api.get(`/portfolio?user_id=${userId}`),
  
  syncPortfolio: (userId = 'default') =>
    api.post('/portfolio/sync', { user_id: userId }),
  
  getPortfolioSummary: (userId = 'default') =>
    api.get(`/portfolio?user_id=${userId}`),
};

// Servicios de Posiciones
export const positionsService = {
  getPositions: (userId = 'default') =>
    api.get(`/positions?user_id=${userId}`),
  
  getPosition: (ticker, userId = 'default') =>
    api.get(`/positions/${ticker}?user_id=${userId}`),
  
  getWinningPositions: (userId = 'default', limit = 10) =>
    api.get(`/positions/winners?user_id=${userId}&limit=${limit}`),
  
  getLosingPositions: (userId = 'default', limit = 10) =>
    api.get(`/positions/losers?user_id=${userId}&limit=${limit}`),
  
  searchPositions: (query, userId = 'default') =>
    api.get(`/positions/search?q=${query}&user_id=${userId}`),
};

// Servicios de Analytics
export const analyticsService = {
  getPerformanceMetrics: (userId = 'default', days = 30) =>
    api.get(`/analytics/performance?user_id=${userId}&days=${days}`),
  
  getAllocationAnalysis: (userId = 'default') =>
    api.get(`/analytics/allocation?user_id=${userId}`),
  
  getRiskMetrics: (userId = 'default') =>
    api.get(`/analytics/risk?user_id=${userId}`),
};

// Servicios de Autenticación
export const authService = {
  validateApiKey: (apiKey) =>
    api.post('/auth/validate', { api_key: apiKey }),
  
  getConnectionStatus: () =>
    api.get('/auth/status'),
};

// Servicios de Investment Advisor
export const investmentAdvisorService = {
  analyzeInvestments: (data) =>
    api.post('/investment-advisor/analyze', data),
  
  getMarketData: (symbol) =>
    api.get(`/investment-advisor/market-data/${symbol}`),
};

// Servicios de Inversiones
export const investmentsService = {
  getAvailable: (params = {}) => {
    const queryParams = new URLSearchParams();
    Object.keys(params).forEach(key => {
      if (params[key] !== null && params[key] !== undefined && params[key] !== '') {
        queryParams.append(key, params[key]);
      }
    });
    return api.get(`/investments/available?${queryParams.toString()}`);
  },

  search: (query, limit = 50) =>
    api.get(`/investments/search?q=${encodeURIComponent(query)}&limit=${limit}`),

  getExchanges: () =>
    api.get('/investments/exchanges'),

  sync: () =>
    api.post('/investments/sync'),

  // Servicios de análisis de sentimientos
  analyzeSentiment: (symbols, newsLimit = 5) =>
    api.post('/investments/sentiment-analysis', {
      symbols: symbols,
      news_limit: newsLimit
    }),

  getSentimentForSymbol: (symbol, newsLimit = 5) =>
    api.get(`/investments/sentiment-analysis/${symbol}?news_limit=${newsLimit}`),
};

// Servicios de Estrategia (Winning Strategy)
export const strategyService = {
  generate: (params = {}) =>
    api.post('/strategy/generate', {
      user_id: params.user_id || 'default',
      timeframe_weeks: params.timeframe_weeks || 2,
      risk_tolerance: params.risk_tolerance || 'MODERATE'
    }),
  
  getHistory: (userId = 'default', status = null, limit = 10) => {
    const queryParams = new URLSearchParams({ user_id: userId, limit });
    if (status) queryParams.append('status', status);
    return api.get(`/strategy/history?${queryParams.toString()}`);
  },
  
  getStrategy: (strategyId) =>
    api.get(`/strategy/${strategyId}`),
  
  updateStatus: (strategyId, status, actualPerformance = null) => {
    const payload = { status };
    if (actualPerformance) {
      payload.actual_performance = actualPerformance;
    }
    return api.patch(`/strategy/${strategyId}`, payload);
  },
  
  getActive: (userId = 'default') =>
    api.get(`/strategy/active?user_id=${userId}`),
  
  getStats: (userId = 'default') =>
    api.get(`/strategy/stats?user_id=${userId}`),
};

// Health check para verificar conectividad
export const healthCheck = () => api.get('/health');

// Función para verificar conectividad general
export const checkConnectivity = async () => {
  try {
    const response = await healthCheck();
    console.log('✅ API conectada:', response.data);
    return true;
  } catch (error) {
    console.error('❌ Error de conectividad API:', error.message);
    return false;
  }
};

export default api;
