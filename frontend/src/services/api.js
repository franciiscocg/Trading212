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
    console.error('API Error:', error);
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
