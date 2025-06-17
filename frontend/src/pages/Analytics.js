import React, { useState, useEffect } from 'react';
import { analyticsService, portfolioService } from '../services/api';
import { formatCurrency, formatPercentage, getValueColor } from '../utils/formatters';
import { 
  ShieldCheckIcon, 
  ExclamationTriangleIcon,
  ChartPieIcon,
  TrendingUpIcon,
  ArrowPathIcon,
  CheckCircleIcon,
  DocumentChartBarIcon
} from '../utils/icons';
import LoadingSpinner from '../components/LoadingSpinner';
import PortfolioChart from '../components/Charts';

export default function Analytics() {  const [performance, setPerformance] = useState(null);
  const [allocation, setAllocation] = useState(null);
  const [risk, setRisk] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [syncing, setSyncing] = useState(false);
  const [syncMessage, setSyncMessage] = useState(null);
  const [lastUpdated, setLastUpdated] = useState(null);
  useEffect(() => {
    loadAnalyticsData();
  }, []);

  const syncPortfolio = async () => {
    setSyncing(true);
    setError(null);
    
    try {
      await portfolioService.syncPortfolio();
      // Después de sincronizar, recargar los datos de analytics
      await loadAnalyticsData();
      setSyncMessage('Datos sincronizados exitosamente');
      setTimeout(() => setSyncMessage(null), 3000);
    } catch (err) {
      let errorMessage = 'Error sincronizando datos';
      
      if (err.response?.status === 429) {
        errorMessage = 'Límite de API excedido. Inténtalo de nuevo en unos minutos.';
      } else if (err.response?.status === 401) {
        errorMessage = 'API Key inválida. Verifica tu configuración.';
      } else if (err.response?.status >= 500) {
        errorMessage = 'Error del servidor durante la sincronización.';
      }
      
      setError(errorMessage);
      console.error('Sync error:', err);
    } finally {
      setSyncing(false);
    }
  };
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
      setLastUpdated(new Date());
      setError(null);
    } catch (err) {
      let errorMessage = 'Error cargando datos de analytics';
      
      if (err.response?.status === 404) {
        errorMessage = 'No se encontraron datos del portafolio. Sincroniza tu cuenta de Trading212 primero.';
      } else if (err.response?.status === 429) {
        errorMessage = 'Límite de solicitudes excedido. Inténtalo de nuevo en unos minutos.';
      } else if (err.response?.status >= 500) {
        errorMessage = 'Error del servidor. Verifica que el backend esté funcionando.';
      } else if (err.code === 'NETWORK_ERROR' || err.message?.includes('Network Error')) {
        errorMessage = 'Error de conexión. Verifica que el backend esté corriendo en localhost:5000.';
      }
      
      setError(errorMessage);
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
        <div className="text-red-600 mb-4 text-lg">{error}</div>
        <div className="space-x-4">
          <button onClick={loadAnalyticsData} className="btn-primary">
            Reintentar
          </button>
          {error.includes('portafolio') && (
            <button onClick={syncPortfolio} disabled={syncing} className="btn-secondary">
              {syncing ? 'Sincronizando...' : 'Sincronizar Datos'}
            </button>
          )}
        </div>
      </div>
    );
  }
  return (
    <div className="space-y-6">
      {/* Mensaje de éxito de sincronización */}
      {syncMessage && (
        <div className="bg-green-50 border border-green-200 rounded-md p-4">
          <div className="flex">
            <div className="flex-shrink-0">
              <CheckCircleIcon className="h-5 w-5 text-green-400" />
            </div>
            <div className="ml-3">
              <p className="text-sm font-medium text-green-800">{syncMessage}</p>
            </div>
          </div>
        </div>
      )}

      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Analytics</h1>
          <p className="mt-1 text-sm text-gray-600">
            Análisis detallado de tu portafolio
            {lastUpdated && (
              <span className="ml-2 text-gray-400">
                • Actualizado: {lastUpdated.toLocaleTimeString()}
              </span>
            )}
          </p>
        </div>
        <div className="mt-4 sm:mt-0 flex flex-col sm:flex-row gap-3">
          <button
            onClick={syncPortfolio}
            disabled={syncing || loading}
            className="btn-secondary flex items-center space-x-2"
          >
            <ArrowPathIcon className={`h-4 w-4 ${syncing ? 'animate-spin' : ''}`} />
            <span>{syncing ? 'Sincronizando...' : 'Sincronizar'}</span>
          </button>
          <button
            onClick={loadAnalyticsData}
            disabled={loading || syncing}
            className="btn-primary flex items-center space-x-2"
          >
            <DocumentChartBarIcon className="h-4 w-4" />
            <span>Actualizar</span>
          </button>
        </div>
      </div>

      {/* Resumen Ejecutivo */}
      {(performance || allocation || risk) && (
        <div className="card bg-gradient-to-r from-trading-blue to-blue-600 text-white">
          <h3 className="text-lg font-medium mb-4">Resumen Ejecutivo</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div>
              <div className="text-sm opacity-90 mb-1">Estado del Portafolio</div>
              <div className="text-xl font-bold">
                {(performance?.total_return_pct || 0) >= 0 ? '📈 Positivo' : '📉 Negativo'}
              </div>
              <div className="text-sm opacity-75">
                {formatPercentage(performance?.total_return_pct || 0)} rendimiento total
              </div>
            </div>
            <div>
              <div className="text-sm opacity-90 mb-1">Nivel de Riesgo</div>
              <div className="text-xl font-bold">
                {risk?.risk_level === 'HIGH' ? '🔴 Alto' : 
                 risk?.risk_level === 'MEDIUM' ? '🟡 Medio' : 
                 risk?.risk_level === 'LOW' ? '🟢 Bajo' : '⚪ N/A'}
              </div>
              <div className="text-sm opacity-75">
                {(performance?.positions_count || 0)} posiciones activas
              </div>
            </div>
            <div>
              <div className="text-sm opacity-90 mb-1">Próxima Acción</div>
              <div className="text-xl font-bold">
                {(performance?.cash_percentage || 0) > 30 ? '💰 Invertir' :
                 (risk?.concentration_index || 0) > 5000 ? '🎯 Diversificar' :
                 (performance?.win_rate || 0) === 0 && (performance?.positions_count || 0) > 0 ? '⚖️ Rebalancear' :
                 '✅ Mantener'}
              </div>
              <div className="text-sm opacity-75">
                Basado en el análisis actual
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Métricas de rendimiento */}
      <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
        <div className="card">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <TrendingUpIcon className="h-8 w-8 text-trading-blue" />
            </div>
            <div className="ml-4">
              <div className="text-sm font-medium text-gray-500">Rendimiento Total</div>
              <div className={`text-2xl font-bold ${getValueColor(performance?.total_return_pct || 0)}`}>
                {formatPercentage(performance?.total_return_pct || 0)}
              </div>
              <div className="text-xs text-gray-500">
                {formatCurrency(performance?.total_pnl || 0)}
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
                {formatPercentage(performance?.win_rate || 0)}
              </div>
              <div className="text-xs text-gray-500">
                {(performance?.winning_positions || 0)} de {(performance?.positions_count || 0)} posiciones
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
              <div className="text-xs text-gray-500">
                HHI: {risk?.concentration_index?.toFixed(0) || 'N/A'}
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
              <div className="text-xs text-gray-500">
                Total: {formatCurrency(performance?.total_value || 0)}
              </div>
            </div>
          </div>
        </div>
      </div>      {/* Gráficos de asignación */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="card">
          <h3 className="text-lg font-medium text-gray-900 mb-4">
            Asignación por Posición
          </h3>
          {allocation?.top_holdings && allocation.top_holdings.length > 0 ? (
            <PortfolioChart data={allocation.top_holdings} />
          ) : (
            <div className="flex items-center justify-center h-48 text-gray-500">
              <div className="text-center">
                <ChartPieIcon className="h-12 w-12 mx-auto mb-2 text-gray-300" />
                <p>No hay datos de asignación disponibles</p>
                <button onClick={syncPortfolio} className="mt-2 text-sm text-trading-blue hover:underline">
                  Sincronizar datos
                </button>
              </div>
            </div>
          )}
        </div>

        <div className="card">
          <h3 className="text-lg font-medium text-gray-900 mb-4">
            Asignación por Sector
          </h3>
          {allocation?.sector_allocation && Object.keys(allocation.sector_allocation).length > 0 ? (
            <PortfolioChart data={Object.entries(allocation.sector_allocation).map(([name, value]) => ({ name, value }))} />
          ) : (
            <div className="flex items-center justify-center h-48 text-gray-500">
              <div className="text-center">
                <DocumentChartBarIcon className="h-12 w-12 mx-auto mb-2 text-gray-300" />
                <p>No hay datos de sector disponibles</p>
                <button onClick={syncPortfolio} className="mt-2 text-sm text-trading-blue hover:underline">
                  Sincronizar datos
                </button>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Análisis de riesgo */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">        <div className="card">
          <h3 className="text-lg font-medium text-gray-900 mb-4">
            Métricas de Riesgo
          </h3>
          <div className="space-y-4">
            <div className="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
              <div>
                <span className="text-gray-600">Concentración (HHI)</span>
                <div className="text-xs text-gray-400">Índice Herfindahl-Hirschman</div>
              </div>
              <span className="font-medium text-gray-900">
                {risk?.concentration_index?.toFixed(0) || 0}
              </span>
            </div>
            <div className="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
              <div>
                <span className="text-gray-600">Posición Más Grande</span>
                <div className="text-xs text-gray-400">% del portafolio total</div>
              </div>
              <span className="font-medium text-gray-900">
                {formatPercentage(risk?.largest_position_pct || 0)}
              </span>
            </div>
            <div className="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
              <div>
                <span className="text-gray-600">Top 5 Concentración</span>
                <div className="text-xs text-gray-400">5 posiciones más grandes</div>
              </div>
              <span className="font-medium text-gray-900">
                {formatPercentage(risk?.top_5_concentration || 0)}
              </span>
            </div>
            <div className="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
              <div>
                <span className="text-gray-600">Total Posiciones</span>
                <div className="text-xs text-gray-400">Número de posiciones activas</div>
              </div>
              <span className="font-medium text-gray-900">
                {risk?.total_positions || 0}
              </span>
            </div>
            <div className="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
              <div>
                <span className="text-gray-600">Beta del Portafolio</span>
                <div className="text-xs text-gray-400">Volatilidad vs mercado</div>
              </div>
              <span className="font-medium text-gray-900">
                {performance?.portfolio_beta?.toFixed(2) || 'N/A'}
              </span>
            </div>
          </div>
        </div>        <div className="card">
          <h3 className="text-lg font-medium text-gray-900 mb-4">
            Recomendaciones y Alertas
          </h3>
          <div className="space-y-3">
            {/* Alertas automáticas basadas en datos */}
            {risk?.concentration_index > 5000 && (
              <div className="flex items-start space-x-3 p-3 bg-red-50 border border-red-200 rounded-lg">
                <ExclamationTriangleIcon className="h-5 w-5 text-red-500 mt-0.5" />
                <div className="text-sm text-red-800">
                  <strong>Alta concentración:</strong> Tu portafolio está muy concentrado (HHI: {risk.concentration_index.toFixed(0)}). 
                  Considera diversificar para reducir el riesgo.
                </div>
              </div>
            )}
            
            {(performance?.cash_percentage || 0) > 30 && (
              <div className="flex items-start space-x-3 p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
                <ExclamationTriangleIcon className="h-5 w-5 text-yellow-500 mt-0.5" />
                <div className="text-sm text-yellow-800">
                  <strong>Alto porcentaje de efectivo:</strong> Tienes {formatPercentage(performance.cash_percentage)} en efectivo. 
                  Considera invertir más para maximizar el potencial de crecimiento.
                </div>
              </div>
            )}
            
            {(performance?.positions_count || 0) < 5 && (
              <div className="flex items-start space-x-3 p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
                <ExclamationTriangleIcon className="h-5 w-5 text-yellow-500 mt-0.5" />
                <div className="text-sm text-yellow-800">
                  <strong>Poca diversificación:</strong> Solo tienes {performance?.positions_count || 0} posiciones. 
                  Considera aumentar la diversificación para reducir el riesgo.
                </div>
              </div>
            )}
            
            {(performance?.win_rate || 0) === 0 && (performance?.positions_count || 0) > 0 && (
              <div className="flex items-start space-x-3 p-3 bg-red-50 border border-red-200 rounded-lg">
                <ExclamationTriangleIcon className="h-5 w-5 text-red-500 mt-0.5" />
                <div className="text-sm text-red-800">
                  <strong>Todas las posiciones en pérdida:</strong> Tu tasa de éxito es 0%. 
                  Revisa tu estrategia de inversión y considera el rebalanceamiento.
                </div>
              </div>
            )}
            
            {/* Recomendaciones del backend */}
            {risk?.recommendations?.map((recommendation, index) => (
              <div key={index} className="flex items-start space-x-3 p-3 bg-blue-50 border border-blue-200 rounded-lg">
                <div className="flex-shrink-0 mt-1">
                  <div className="h-2 w-2 bg-trading-blue rounded-full"></div>
                </div>
                <div className="text-sm text-blue-800">
                  {recommendation}
                </div>
              </div>
            ))}
            
            {/* Estado cuando no hay alertas */}
            {(!risk?.recommendations || risk.recommendations.length === 0) && 
             (risk?.concentration_index <= 5000) && 
             ((performance?.cash_percentage || 0) <= 30) && 
             ((performance?.positions_count || 0) >= 5) && 
             ((performance?.win_rate || 0) > 0 || (performance?.positions_count || 0) === 0) && (
              <div className="flex items-start space-x-3 p-3 bg-green-50 border border-green-200 rounded-lg">
                <CheckCircleIcon className="h-5 w-5 text-green-500 mt-0.5" />
                <div className="text-sm text-green-800">
                  <strong>¡Buen trabajo!</strong> Tu portafolio muestra una estructura saludable sin alertas críticas.
                </div>
              </div>
            )}
          </div>
        </div>
      </div>      {/* Detalles de rendimiento */}
      <div className="card">
        <h3 className="text-lg font-medium text-gray-900 mb-4">
          Desglose de Rendimiento
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <div className="text-center">
            <div className="text-sm text-gray-500 mb-2">P&L No Realizado</div>
            <div className={`text-2xl font-bold ${getValueColor(performance?.unrealized_pnl || 0)}`}>
              {formatCurrency(performance?.unrealized_pnl || 0)}
            </div>
          </div>
          <div className="text-center">
            <div className="text-sm text-gray-500 mb-2">P&L Realizado</div>
            <div className={`text-2xl font-bold ${getValueColor(performance?.realized_pnl || 0)}`}>
              {formatCurrency(performance?.realized_pnl || 0)}
            </div>
          </div>
          <div className="text-center">
            <div className="text-sm text-gray-500 mb-2">Total P&L</div>
            <div className={`text-2xl font-bold ${getValueColor(performance?.total_pnl || 0)}`}>
              {formatCurrency(performance?.total_pnl || 0)}
            </div>
          </div>
          <div className="text-center">
            <div className="text-sm text-gray-500 mb-2">Valor Total</div>
            <div className="text-2xl font-bold text-gray-900">
              {formatCurrency(performance?.total_value || 0)}
            </div>
          </div>
        </div>
        
        {/* Métricas adicionales */}
        <div className="mt-6 pt-6 border-t border-gray-200">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="text-center">
              <div className="text-sm text-gray-500 mb-2">Efectivo</div>
              <div className="text-lg font-medium text-gray-900">
                {formatPercentage(performance?.cash_percentage || 0)}
              </div>
              <div className="text-xs text-gray-500">del portafolio</div>
            </div>
            <div className="text-center">
              <div className="text-sm text-gray-500 mb-2">Posiciones Ganadoras</div>
              <div className="text-lg font-medium text-green-600">
                {performance?.winning_positions || 0}
              </div>
              <div className="text-xs text-gray-500">
                {formatPercentage((performance?.winning_positions || 0) / Math.max(performance?.positions_count || 1, 1) * 100)}
              </div>
            </div>
            <div className="text-center">
              <div className="text-sm text-gray-500 mb-2">Posiciones Perdedoras</div>
              <div className="text-lg font-medium text-red-600">
                {performance?.losing_positions || 0}
              </div>
              <div className="text-xs text-gray-500">
                {formatPercentage((performance?.losing_positions || 0) / Math.max(performance?.positions_count || 1, 1) * 100)}
              </div>
            </div>
          </div>
        </div>
      </div>      {/* Concentración por sector */}
      <div className="card">
        <h3 className="text-lg font-medium text-gray-900 mb-4">
          Concentración por Sector
        </h3>
        {allocation?.sector_allocation && Object.keys(allocation.sector_allocation).length > 0 ? (
          <div className="space-y-3">
            {Object.entries(allocation.sector_allocation).map(([sector, percentage]) => (
              <div key={sector} className="flex justify-between items-center">
                <span className="text-gray-600 font-medium">{sector}</span>
                <div className="flex items-center space-x-3">
                  <div className="w-32 bg-gray-200 rounded-full h-2">
                    <div 
                      className="bg-trading-blue h-2 rounded-full transition-all duration-300" 
                      style={{ width: `${Math.min(percentage, 100)}%` }}
                    ></div>
                  </div>
                  <span className="text-sm font-medium text-gray-900 w-12 text-right">
                    {formatPercentage(percentage)}
                  </span>
                  <span className="text-xs text-gray-500 w-20 text-right">
                    {formatCurrency(percentage / 100 * (performance?.total_value || 0))}
                  </span>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-8 text-gray-500">
            <DocumentChartBarIcon className="h-12 w-12 mx-auto mb-2 text-gray-300" />
            <p>No hay datos de sectores disponibles</p>
            <p className="text-sm text-gray-400 mt-1">
              Los datos de sector se mostrarán una vez que sincronices tu portafolio
            </p>
            <button 
              onClick={syncPortfolio} 
              disabled={syncing}
              className="mt-3 text-sm text-trading-blue hover:underline"
            >
              {syncing ? 'Sincronizando...' : 'Sincronizar ahora'}
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
