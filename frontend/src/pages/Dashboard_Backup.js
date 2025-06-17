import React, { useState, useEffect } from 'react';
import { portfolioService, analyticsService } from '../services/api';
import { formatCurrency, formatPercentage, getValueColor } from '../utils/formatters';
import { 
  ArrowUpIcon, 
  ArrowDownIcon, 
  TrendingUpIcon,
  CurrencyEuroIcon,
  ChartBarIcon,
  BanknotesIcon
} from '../utils/icons';
import LoadingSpinner from '../components/LoadingSpinner';
import PortfolioChart from '../components/Charts';

export default function Dashboard() {
  const [portfolio, setPortfolio] = useState(null);
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadDashboardData();
  }, []);  const loadDashboardData = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const [portfolioResponse, analyticsResponse] = await Promise.all([
        portfolioService.getPortfolioSummary(),
        analyticsService.getPerformanceMetrics()
      ]);
      
      setPortfolio(portfolioResponse.data);
      setAnalytics(analyticsResponse.data);
      
    } catch (err) {
      console.error('Dashboard error:', err);
      
      if (err.response?.status === 404) {
        setError('No se encontraron datos del portafolio. Necesitas sincronizar tus datos de Trading212 primero.');
      } else {
        setError('Error cargando datos del dashboard. Verifica tu conexión y configuración.');
      }
    } finally {
      setLoading(false);
    }
  };
  const handleSync = async () => {
    try {
      setLoading(true);
      setError(null);
      
      console.log('🔄 Sincronizando datos con Trading212...');
      const syncResponse = await portfolioService.syncPortfolio();
      console.log('✅ Sincronización completada:', syncResponse.data);
      
      // Recargar datos después de la sincronización
      await loadDashboardData();
      
    } catch (err) {      console.error('Sync error:', err);
      
      if (err.response?.data?.error?.includes('rate limit')) {
        setError('Trading212 API rate limit alcanzado. Espera unos minutos antes de sincronizar de nuevo.');
      } else if (err.response?.status === 500) {
        setError('Error al conectar con Trading212. Verifica tu API key en Settings.');
      } else {
        setError('Error sincronizando datos. Verifica tu configuración.');
      }
      setLoading(false);
    }
  };

  if (loading) {
    return <LoadingSpinner />;
  }
  if (error) {
    return (
      <div className="text-center py-12">
        <div className="mb-6">
          <ChartBarIcon className="h-16 w-16 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">No hay datos del portafolio</h3>
          <p className="text-red-600 mb-6">{error}</p>
        </div>
        
        <div className="space-y-4">
          <button 
            onClick={handleSync} 
            className="btn-primary flex items-center space-x-2 mx-auto"
            disabled={loading}
          >
            <ArrowUpIcon className="h-4 w-4" />
            <span>Sincronizar con Trading212</span>
          </button>
          
          <button 
            onClick={loadDashboardData} 
            className="btn-secondary flex items-center space-x-2 mx-auto"
          >
            <span>Reintentar carga</span>
          </button>
        </div>
        
        <div className="mt-8 text-sm text-gray-600">
          <p>Para usar datos reales:</p>
          <ol className="list-decimal list-inside mt-2 space-y-1">
            <li>Ve a Settings y configura tu API key de Trading212</li>
            <li>Haz clic en "Sincronizar con Trading212"</li>
            <li>Tus datos reales aparecerán aquí</li>
          </ol>
        </div>
      </div>
    );
  }  const portfolioData = portfolio || {};
  const metrics = analytics || {};
  const positions = portfolio?.positions || [];
  
  // Calcular métricas adicionales basadas en posiciones reales
  const calculatedMetrics = {
    positions_count: positions.length,
    winning_positions: positions.filter(p => p.unrealized_pnl > 0).length,
    losing_positions: positions.filter(p => p.unrealized_pnl < 0).length,
    cash_percentage: portfolioData.total_value > 0 ? (portfolioData.cash_balance / portfolioData.total_value * 100) : 0,
    win_rate: positions.length > 0 ? (positions.filter(p => p.unrealized_pnl > 0).length / positions.length * 100) : 0,
    ...metrics
  };

  return (
    <div className="space-y-6">
      {/* Demo Banner */}
      {isDemo && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <ChartBarIcon className="h-5 w-5 text-blue-600" />
            </div>
            <div className="ml-3">
              <h3 className="text-sm font-medium text-blue-800">
                Modo Demostración
              </h3>
              <div className="mt-1 text-sm text-blue-700">
                Mostrando datos de ejemplo. Configura tu API key en Settings para ver datos reales.
              </div>
            </div>
          </div>        </div>
      )}

      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
          <p className="mt-1 text-sm text-gray-600">
            Resumen de tu portafolio de Trading212
          </p>
          {portfolioData.updated_at && (
            <p className="text-xs text-gray-500">
              Última actualización: {new Date(portfolioData.updated_at).toLocaleString('es-ES')}
            </p>
          )}
        </div>
        <div className="mt-4 sm:mt-0">
          <button 
            onClick={handleSync}
            className="btn-primary flex items-center space-x-2"
          >
            <ArrowUpIcon className="h-4 w-4" />
            <span>Sincronizar</span>
          </button>
        </div>
      </div>

      {/* Métricas principales */}
      <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
        <div className="card">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <CurrencyEuroIcon className="h-8 w-8 text-trading-blue" />
            </div>
            <div className="ml-4">
              <div className="text-sm font-medium text-gray-500">Valor Total</div>
              <div className="text-2xl font-bold text-gray-900">
                {formatCurrency(portfolioData.total_value)}
              </div>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <TrendingUpIcon className={`h-8 w-8 ${getValueColor(portfolioData.total_pnl)}`} />
            </div>
            <div className="ml-4">
              <div className="text-sm font-medium text-gray-500">P&L Total</div>
              <div className={`text-2xl font-bold ${getValueColor(portfolioData.total_pnl)}`}>
                {formatCurrency(portfolioData.total_pnl)}
              </div>
              <div className={`text-sm ${getValueColor(portfolioData.total_return_pct)}`}>
                {formatPercentage(portfolioData.total_return_pct)}
              </div>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <BanknotesIcon className="h-8 w-8 text-green-600" />
            </div>
            <div className="ml-4">
              <div className="text-sm font-medium text-gray-500">Efectivo</div>
              <div className="text-2xl font-bold text-gray-900">
                {formatCurrency(portfolioData.cash_balance)}
              </div>              <div className="text-sm text-gray-600">
                {formatPercentage(calculatedMetrics.cash_percentage)}
              </div>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <ChartBarIcon className="h-8 w-8 text-purple-600" />
            </div>
            <div className="ml-4">
              <div className="text-sm font-medium text-gray-500">Posiciones</div>              <div className="text-2xl font-bold text-gray-900">
                {calculatedMetrics.positions_count || 0}
              </div>
              <div className="text-sm text-gray-600">
                Win Rate: {formatPercentage(calculatedMetrics.win_rate)}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Gráfico del portafolio */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="card">
          <h3 className="text-lg font-medium text-gray-900 mb-4">
            Asignación del Portafolio
          </h3>
          <PortfolioChart data={positions.map(p => ({
            name: p.ticker,
            value: p.market_value,
            percentage: portfolioData.total_value > 0 ? (p.market_value / portfolioData.total_value * 100) : 0
          }))} />
        </div>

        <div className="card">
          <h3 className="text-lg font-medium text-gray-900 mb-4">
            Top Posiciones
          </h3>
          <div className="space-y-3">
            {positions.slice(0, 5).map((position, index) => (
              <div key={position.ticker} className="flex items-center justify-between py-2">
                <div>
                  <div className="font-medium text-gray-900">{position.ticker}</div>
                  <div className="text-sm text-gray-500">
                    {position.company_name || position.ticker}
                  </div>
                </div>
                <div className="text-right">
                  <div className="font-medium text-gray-900">
                    {formatCurrency(position.market_value)}
                  </div>
                  <div className={`text-sm flex items-center ${getValueColor(position.unrealized_pnl)}`}>
                    {position.unrealized_pnl > 0 ? (
                      <ArrowUpIcon className="h-3 w-3 mr-1" />
                    ) : (
                      <ArrowDownIcon className="h-3 w-3 mr-1" />
                    )}
                    {formatPercentage(position.unrealized_pnl_pct)}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Métricas adicionales */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="card">
          <h3 className="text-lg font-medium text-gray-900 mb-4">
            Rendimiento
          </h3>
          <div className="space-y-3">
            <div className="flex justify-between">
              <span className="text-gray-600">P&L No Realizado</span>
              <span className={getValueColor(portfolioData.unrealized_pnl)}>
                {formatCurrency(portfolioData.unrealized_pnl)}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">P&L Realizado</span>
              <span className={getValueColor(portfolioData.realized_pnl)}>
                {formatCurrency(portfolioData.realized_pnl)}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Capital Invertido</span>
              <span className="text-gray-900">
                {formatCurrency(portfolioData.invested_amount)}
              </span>
            </div>
          </div>
        </div>        <div className="card">
          <h3 className="text-lg font-medium text-gray-900 mb-4">
            Detalle de Posiciones
          </h3>
          <div className="space-y-3">
            {positions.map((position) => (
              <div key={position.ticker} className="flex justify-between">
                <span className="text-gray-600">{position.ticker}</span>
                <span className="text-gray-900">
                  {formatCurrency(position.market_value)}
                </span>
              </div>
            ))}
            {positions.length === 0 && (
              <div className="text-center text-gray-500 py-4">
                No hay posiciones para mostrar
              </div>
            )}
          </div>
        </div>

        <div className="card">
          <h3 className="text-lg font-medium text-gray-900 mb-4">
            Estado de Posiciones
          </h3>
          <div className="space-y-3">
            <div className="flex justify-between">
              <span className="text-gray-600">Posiciones Ganadoras</span>              <span className="text-trading-green font-medium">
                {calculatedMetrics.winning_positions || 0}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Posiciones Perdedoras</span>
              <span className="text-trading-red font-medium">
                {calculatedMetrics.losing_positions || 0}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Tasa de Éxito</span>
              <span className="text-gray-900 font-medium">
                {formatPercentage(calculatedMetrics.win_rate)}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
