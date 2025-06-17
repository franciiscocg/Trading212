import React, { useState, useEffect } from 'react';
import { analyticsService } from '../services/api';
import { formatCurrency, formatPercentage, getValueColor } from '../utils/formatters';
import { 
  ShieldCheckIcon, 
  ExclamationTriangleIcon,
  ChartPieIcon,
  TrendingUpIcon
} from '../utils/icons';
import LoadingSpinner from '../components/LoadingSpinner';
import PortfolioChart from '../components/Charts';

export default function Analytics() {
  const [performance, setPerformance] = useState(null);
  const [allocation, setAllocation] = useState(null);
  const [risk, setRisk] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadAnalyticsData();
  }, []);

  const loadAnalyticsData = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const [performanceResponse, allocationResponse, riskResponse] = await Promise.all([
        analyticsService.getPerformanceMetrics(),
        analyticsService.getAllocationAnalysis(),
        analyticsService.getRiskMetrics()
      ]);
      
      setPerformance(performanceResponse.data);
      setAllocation(allocationResponse.data);
      setRisk(riskResponse.data);
    } catch (err) {
      setError('Error cargando datos de analytics');
      console.error('Analytics error:', err);
    } finally {
      setLoading(false);
    }
  };

  const getRiskLevelColor = (level) => {
    switch (level) {
      case 'HIGH': return 'text-red-600 bg-red-50';
      case 'MEDIUM': return 'text-yellow-600 bg-yellow-50';
      case 'LOW': return 'text-green-600 bg-green-50';
      default: return 'text-gray-600 bg-gray-50';
    }
  };

  const getRiskIcon = (level) => {
    switch (level) {
      case 'HIGH': return <ExclamationTriangleIcon className="h-5 w-5 text-red-500" />;
      case 'MEDIUM': return <ExclamationTriangleIcon className="h-5 w-5 text-yellow-500" />;
      case 'LOW': return <ShieldCheckIcon className="h-5 w-5 text-green-500" />;
      default: return <ShieldCheckIcon className="h-5 w-5 text-gray-500" />;
    }
  };

  if (loading) {
    return <LoadingSpinner />;
  }

  if (error) {
    return (
      <div className="text-center py-12">
        <div className="text-red-600 mb-4">{error}</div>
        <button onClick={loadAnalyticsData} className="btn-primary">
          Reintentar
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Analytics</h1>
        <p className="mt-1 text-sm text-gray-600">
          Análisis detallado de tu portafolio
        </p>
      </div>

      {/* Métricas de rendimiento */}
      <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
        <div className="card">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <TrendingUpIcon className="h-8 w-8 text-trading-blue" />
            </div>
            <div className="ml-4">
              <div className="text-sm font-medium text-gray-500">Rendimiento Total</div>
              <div className={`text-2xl font-bold ${getValueColor(performance?.total_return_pct)}`}>
                {formatPercentage(performance?.total_return_pct)}
              </div>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <ChartPieIcon className="h-8 w-8 text-purple-600" />
            </div>
            <div className="ml-4">
              <div className="text-sm font-medium text-gray-500">Tasa de Éxito</div>
              <div className="text-2xl font-bold text-gray-900">
                {formatPercentage(performance?.win_rate)}
              </div>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              {getRiskIcon(risk?.risk_level)}
            </div>
            <div className="ml-4">
              <div className="text-sm font-medium text-gray-500">Nivel de Riesgo</div>
              <div className={`text-lg font-bold px-2 py-1 rounded ${getRiskLevelColor(risk?.risk_level)}`}>
                {risk?.risk_level || 'N/A'}
              </div>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <ShieldCheckIcon className="h-8 w-8 text-green-600" />
            </div>
            <div className="ml-4">
              <div className="text-sm font-medium text-gray-500">Diversificación</div>
              <div className="text-2xl font-bold text-gray-900">
                {performance?.positions_count || 0}
              </div>
              <div className="text-sm text-gray-500">posiciones</div>
            </div>
          </div>
        </div>
      </div>

      {/* Gráficos de asignación */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="card">
          <h3 className="text-lg font-medium text-gray-900 mb-4">
            Asignación por Posición
          </h3>
          <PortfolioChart data={allocation?.top_holdings || []} />
        </div>

        <div className="card">
          <h3 className="text-lg font-medium text-gray-900 mb-4">
            Asignación por Sector
          </h3>
          <PortfolioChart data={allocation?.sector_allocation || []} />
        </div>
      </div>

      {/* Análisis de riesgo */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="card">
          <h3 className="text-lg font-medium text-gray-900 mb-4">
            Métricas de Riesgo
          </h3>
          <div className="space-y-4">
            <div className="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
              <span className="text-gray-600">Concentración (HHI)</span>
              <span className="font-medium text-gray-900">
                {risk?.concentration_index?.toFixed(0) || 0}
              </span>
            </div>
            <div className="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
              <span className="text-gray-600">Posición Más Grande</span>
              <span className="font-medium text-gray-900">
                {formatPercentage(risk?.largest_position_pct)}
              </span>
            </div>
            <div className="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
              <span className="text-gray-600">Top 5 Concentración</span>
              <span className="font-medium text-gray-900">
                {formatPercentage(risk?.top_5_concentration)}
              </span>
            </div>
            <div className="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
              <span className="text-gray-600">Total Posiciones</span>
              <span className="font-medium text-gray-900">
                {risk?.total_positions || 0}
              </span>
            </div>
          </div>
        </div>

        <div className="card">
          <h3 className="text-lg font-medium text-gray-900 mb-4">
            Recomendaciones
          </h3>
          <div className="space-y-3">
            {risk?.recommendations?.map((recommendation, index) => (
              <div key={index} className="flex items-start space-x-3 p-3 bg-blue-50 rounded-lg">
                <div className="flex-shrink-0 mt-0.5">
                  <div className="h-2 w-2 bg-trading-blue rounded-full"></div>
                </div>
                <div className="text-sm text-gray-700">
                  {recommendation}
                </div>
              </div>
            )) || (
              <div className="text-gray-500 text-sm">
                No hay recomendaciones disponibles
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Detalles de rendimiento */}
      <div className="card">
        <h3 className="text-lg font-medium text-gray-900 mb-4">
          Desglose de Rendimiento
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="text-center">
            <div className="text-sm text-gray-500 mb-2">P&L No Realizado</div>
            <div className={`text-2xl font-bold ${getValueColor(performance?.unrealized_pnl)}`}>
              {formatCurrency(performance?.unrealized_pnl)}
            </div>
          </div>
          <div className="text-center">
            <div className="text-sm text-gray-500 mb-2">P&L Realizado</div>
            <div className={`text-2xl font-bold ${getValueColor(performance?.realized_pnl)}`}>
              {formatCurrency(performance?.realized_pnl)}
            </div>
          </div>
          <div className="text-center">
            <div className="text-sm text-gray-500 mb-2">Total P&L</div>
            <div className={`text-2xl font-bold ${getValueColor(performance?.total_pnl)}`}>
              {formatCurrency(performance?.total_pnl)}
            </div>
          </div>
        </div>
      </div>

      {/* Concentración por sector */}
      <div className="card">
        <h3 className="text-lg font-medium text-gray-900 mb-4">
          Concentración por Sector
        </h3>
        <div className="space-y-3">
          {Object.entries(risk?.sector_concentration || {}).map(([sector, percentage]) => (
            <div key={sector} className="flex justify-between items-center">
              <span className="text-gray-600">{sector}</span>
              <div className="flex items-center space-x-3">
                <div className="w-32 bg-gray-200 rounded-full h-2">
                  <div 
                    className="bg-trading-blue h-2 rounded-full" 
                    style={{ width: `${Math.min(percentage, 100)}%` }}
                  ></div>
                </div>
                <span className="text-sm font-medium text-gray-900 w-12 text-right">
                  {formatPercentage(percentage)}
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
