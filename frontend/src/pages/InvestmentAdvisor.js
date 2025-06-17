import React, { useState, useEffect } from 'react';
import { portfolioService, analyticsService, investmentAdvisorService } from '../services/api';
import { formatCurrency, formatPercentage, getValueColor } from '../utils/formatters';
import { 
  ChartBarIcon,
  LightBulbIcon,
  ExclamationTriangleIcon
} from '../utils/icons';
import LoadingSpinner from '../components/LoadingSpinner';

export default function InvestmentAdvisor() {  const [analysis, setAnalysis] = useState(null);
  const [portfolioData, setPortfolioData] = useState(null);
  const [analyzing, setAnalyzing] = useState(false);
  const [error, setError] = useState(null);
  const [preferences, setPreferences] = useState({
    riskTolerance: 'medium',
    investmentHorizon: '1-3-years',
    investmentAmount: 1000,
    sectors: [],
    excludeRegions: []
  });

  useEffect(() => {
    loadPortfolioData();
  }, []);

  const loadPortfolioData = async () => {
    try {
      const [portfolioResponse, analyticsResponse] = await Promise.all([
        portfolioService.getPortfolio(),
        analyticsService.getPerformanceMetrics()
      ]);
      setPortfolioData({
        portfolio: portfolioResponse.data,
        analytics: analyticsResponse.data
      });
    } catch (err) {
      console.error('Error loading portfolio data:', err);
    }
  };
  const analyzeInvestments = async () => {
    setAnalyzing(true);
    setError(null);
    
    try {
      // Preparar datos para el análisis
      const analysisData = {
        portfolio: portfolioData,
        preferences: preferences,
        marketConditions: 'current'
      };

      // Llamar al servicio de Investment Advisor
      const response = await investmentAdvisorService.analyzeInvestments(analysisData);
      setAnalysis(response.data);
    } catch (err) {
      let errorMessage = 'Error generando recomendaciones de inversión';
      
      if (err.response?.status === 429) {
        errorMessage = 'Límite de API excedido. Inténtalo de nuevo en unos minutos.';
      } else if (err.response?.status === 401) {
        errorMessage = 'API Key de Gemini no configurada. Contacta al administrador.';
      } else if (err.response?.status >= 500) {
        errorMessage = 'Error del servidor durante el análisis.';
      }
      
      setError(errorMessage);
      console.error('Analysis error:', err);
    } finally {
      setAnalyzing(false);
    }
  };

  const getRiskColor = (risk) => {
    switch (risk) {
      case 'HIGH': return 'text-red-600 bg-red-50 border-red-200';
      case 'MEDIUM': return 'text-yellow-600 bg-yellow-50 border-yellow-200';
      case 'LOW': return 'text-green-600 bg-green-50 border-green-200';
      default: return 'text-gray-600 bg-gray-50 border-gray-200';
    }
  };

  const getHorizonLabel = (horizon) => {
    switch (horizon) {
      case 'short': return 'Corto plazo (< 1 año)';
      case '1-3-years': return 'Medio plazo (1-3 años)';
      case 'long': return 'Largo plazo (> 3 años)';
      default: return horizon;
    }
  };
  if (analyzing && !analysis) {
    return <LoadingSpinner />;
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Investment Advisor</h1>
          <p className="mt-1 text-sm text-gray-600">
            Recomendaciones de inversión inteligentes powered by AI
          </p>
        </div>
        <div className="mt-4 sm:mt-0">
          <button
            onClick={analyzeInvestments}
            disabled={analyzing || !portfolioData}
            className="btn-primary flex items-center space-x-2"
          >
            <LightBulbIcon className={`h-4 w-4 ${analyzing ? 'animate-pulse' : ''}`} />
            <span>{analyzing ? 'Analizando...' : 'Generar Recomendaciones'}</span>
          </button>
        </div>
      </div>

      {/* Configuración de Preferencias */}
      <div className="card">
        <h3 className="text-lg font-medium text-gray-900 mb-4">
          Preferencias de Inversión
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Tolerancia al Riesgo
            </label>
            <select
              value={preferences.riskTolerance}
              onChange={(e) => setPreferences({...preferences, riskTolerance: e.target.value})}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-trading-blue"
            >
              <option value="low">Conservador</option>
              <option value="medium">Moderado</option>
              <option value="high">Agresivo</option>
            </select>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Horizonte de Inversión
            </label>
            <select
              value={preferences.investmentHorizon}
              onChange={(e) => setPreferences({...preferences, investmentHorizon: e.target.value})}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-trading-blue"
            >              <option value="short">Corto plazo (&lt; 1 año)</option>
              <option value="1-3-years">Medio plazo (1-3 años)</option>
              <option value="long">Largo plazo (&gt; 3 años)</option>
            </select>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Cantidad a Invertir (€)
            </label>
            <input
              type="number"
              value={preferences.investmentAmount}
              onChange={(e) => setPreferences({...preferences, investmentAmount: parseInt(e.target.value)})}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-trading-blue"
              min="100"
              step="100"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Estado del Análisis
            </label>
            <div className="flex items-center space-x-2 py-2">
              <div className={`h-3 w-3 rounded-full ${
                analyzing ? 'bg-yellow-400 animate-pulse' : 
                analysis ? 'bg-green-400' : 'bg-gray-300'
              }`}></div>
              <span className="text-sm text-gray-600">
                {analyzing ? 'Analizando...' : analysis ? 'Completado' : 'Pendiente'}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Error Display */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-md p-4">
          <div className="flex">
            <div className="flex-shrink-0">
              <ExclamationTriangleIcon className="h-5 w-5 text-red-400" />
            </div>
            <div className="ml-3">
              <p className="text-sm font-medium text-red-800">{error}</p>
            </div>
          </div>
        </div>
      )}

      {/* Loading State */}
      {analyzing && (
        <div className="card text-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-trading-blue mx-auto mb-4"></div>
          <h3 className="text-lg font-medium text-gray-900 mb-2">
            Analizando oportunidades de inversión...
          </h3>
          <p className="text-gray-600">
            Esto puede tomar unos momentos mientras procesamos los datos del mercado
          </p>
        </div>
      )}

      {/* Resultados del Análisis */}
      {analysis && !analyzing && (
        <div className="space-y-6">
          {/* Resumen Ejecutivo */}
          <div className="card bg-gradient-to-r from-green-500 to-blue-600 text-white">
            <h3 className="text-xl font-bold mb-4">Resumen de Recomendaciones</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <div className="text-sm opacity-90">Recomendación Principal</div>
                <div className="text-lg font-bold">{analysis.topRecommendation?.symbol}</div>
                <div className="text-sm opacity-75">{analysis.topRecommendation?.name}</div>
              </div>
              <div>
                <div className="text-sm opacity-90">Potencial de Retorno</div>
                <div className="text-lg font-bold">{formatPercentage(analysis.expectedReturn)}</div>
                <div className="text-sm opacity-75">En {getHorizonLabel(preferences.investmentHorizon)}</div>
              </div>
              <div>
                <div className="text-sm opacity-90">Nivel de Riesgo</div>
                <div className="text-lg font-bold">
                  {analysis.overallRisk === 'HIGH' ? '🔴 Alto' : 
                   analysis.overallRisk === 'MEDIUM' ? '🟡 Medio' : '🟢 Bajo'}
                </div>
                <div className="text-sm opacity-75">Basado en tu perfil</div>
              </div>
            </div>
          </div>

          {/* Recomendaciones Detalladas */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {analysis.recommendations?.map((rec, index) => (
              <div key={index} className="card border-l-4 border-trading-blue">
                <div className="flex justify-between items-start mb-3">
                  <div>
                    <h4 className="text-lg font-bold text-gray-900">{rec.symbol}</h4>
                    <p className="text-sm text-gray-600">{rec.name}</p>
                  </div>
                  <div className={`px-2 py-1 rounded text-xs font-medium border ${getRiskColor(rec.risk)}`}>
                    {rec.risk}
                  </div>
                </div>
                
                <div className="space-y-3">
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <span className="text-gray-500">Precio Actual:</span>
                      <div className="font-medium">{formatCurrency(rec.currentPrice)}</div>
                    </div>
                    <div>
                      <span className="text-gray-500">Objetivo:</span>
                      <div className="font-medium text-green-600">{formatCurrency(rec.targetPrice)}</div>
                    </div>
                    <div>
                      <span className="text-gray-500">Stop Loss:</span>
                      <div className="font-medium text-red-600">{formatCurrency(rec.stopLoss)}</div>
                    </div>
                    <div>
                      <span className="text-gray-500">Potencial:</span>
                      <div className={`font-medium ${getValueColor(rec.potentialReturn)}`}>
                        {formatPercentage(rec.potentialReturn)}
                      </div>
                    </div>
                  </div>
                  
                  <div className="pt-3 border-t border-gray-200">
                    <div className="text-sm text-gray-600 mb-2">
                      <strong>Estrategia:</strong> {rec.strategy}
                    </div>
                    <div className="text-sm text-gray-600">
                      <strong>Razón:</strong> {rec.reasoning}
                    </div>
                  </div>
                  
                  {rec.keyMetrics && (
                    <div className="bg-gray-50 rounded-lg p-3">
                      <div className="text-xs font-medium text-gray-700 mb-2">Métricas Clave</div>
                      <div className="grid grid-cols-2 gap-2 text-xs">
                        {Object.entries(rec.keyMetrics).map(([key, value]) => (
                          <div key={key} className="flex justify-between">
                            <span className="text-gray-500">{key}:</span>
                            <span className="font-medium">{value}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>

          {/* Análisis de Riesgo */}
          {analysis.riskAnalysis && (
            <div className="card">
              <h3 className="text-lg font-medium text-gray-900 mb-4">
                Análisis de Riesgo
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="text-center">
                  <div className="text-sm text-gray-500 mb-1">Volatilidad Esperada</div>
                  <div className="text-xl font-bold text-gray-900">
                    {formatPercentage(analysis.riskAnalysis.volatility)}
                  </div>
                </div>
                <div className="text-center">
                  <div className="text-sm text-gray-500 mb-1">Máxima Pérdida</div>
                  <div className="text-xl font-bold text-red-600">
                    {formatPercentage(analysis.riskAnalysis.maxDrawdown)}
                  </div>
                </div>
                <div className="text-center">
                  <div className="text-sm text-gray-500 mb-1">Sharpe Ratio</div>
                  <div className="text-xl font-bold text-gray-900">
                    {analysis.riskAnalysis.sharpeRatio?.toFixed(2) || 'N/A'}
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Market Insights */}
          {analysis.marketInsights && (
            <div className="card">
              <h3 className="text-lg font-medium text-gray-900 mb-4">
                Insights del Mercado
              </h3>
              <div className="prose prose-sm max-w-none">
                <p className="text-gray-700">{analysis.marketInsights}</p>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Estado inicial */}
      {!analysis && !analyzing && !error && (
        <div className="card text-center py-12">
          <ChartBarIcon className="h-16 w-16 text-gray-300 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">
            Listo para Analizar
          </h3>
          <p className="text-gray-600 mb-4">
            Configura tus preferencias y genera recomendaciones de inversión personalizadas
          </p>
          <button
            onClick={analyzeInvestments}
            disabled={!portfolioData}
            className="btn-primary"
          >
            Comenzar Análisis
          </button>
        </div>
      )}
    </div>
  );
}
