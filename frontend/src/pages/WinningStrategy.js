import React, { useState, useEffect } from 'react';
import { strategyService, portfolioService } from '../services/api';
import { formatCurrency, formatPercentage } from '../utils/formatters';
import {
  LightBulbIcon,
  ArrowPathIcon,
  CheckCircleIcon,
  XCircleIcon,
  ClockIcon,
  ChartBarIcon,
  ArrowTrendingUpIcon,
  ShieldCheckIcon,
  InformationCircleIcon
} from '../utils/icons';
import LoadingSpinner from '../components/LoadingSpinner';
import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from 'recharts';

const COLORS = ['#10b981', '#3b82f6', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899', '#14b8a6'];

export default function WinningStrategy() {
  const [strategy, setStrategy] = useState(null);
  const [loading, setLoading] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [error, setError] = useState(null);
  const [portfolio, setPortfolio] = useState(null);
  const [historyExpanded, setHistoryExpanded] = useState(false);
  const [strategyHistory, setStrategyHistory] = useState([]);
  
  // Parámetros de configuración
  const [timeframeWeeks, setTimeframeWeeks] = useState(2);
  const [riskTolerance, setRiskTolerance] = useState('MODERATE');

  useEffect(() => {
    loadActiveStrategy();
    loadPortfolioData();
  }, []);

  const loadPortfolioData = async () => {
    try {
      const response = await portfolioService.getPortfolioSummary();
      setPortfolio(response.data);
    } catch (err) {
      console.error('Error loading portfolio:', err);
    }
  };

  const loadActiveStrategy = async () => {
    try {
      setLoading(true);
      
      // Primero buscar estrategias PENDING (recién generadas)
      const pendingResponse = await strategyService.getHistory('default', 'PENDING', 1);
      if (pendingResponse.data.strategies && pendingResponse.data.strategies.length > 0) {
        setStrategy(pendingResponse.data.strategies[0]);
        setLoading(false);
        return;
      }
      
      // Si no hay PENDING, buscar ACTIVE
      const activeResponse = await strategyService.getActive();
      if (activeResponse.data.strategy) {
        setStrategy(activeResponse.data.strategy);
      }
    } catch (err) {
      console.error('Error loading active strategy:', err);
      setError('No se pudo conectar con el servidor. Verifica que el backend esté corriendo.');
    } finally {
      setLoading(false);
    }
  };

  const loadStrategyHistory = async () => {
    try {
      const response = await strategyService.getHistory('default', null, 10);
      setStrategyHistory(response.data.strategies || []);
    } catch (err) {
      console.error('Error loading strategy history:', err);
    }
  };

  const handleGenerateStrategy = async () => {
    try {
      setGenerating(true);
      setError(null);
      
      const response = await strategyService.generate({
        user_id: 'default',
        timeframe_weeks: timeframeWeeks,
        risk_tolerance: riskTolerance
      });
      
      setStrategy(response.data.strategy);
      
    } catch (err) {
      console.error('Error generating strategy:', err);
      const errorMessage = err.userMessage || 
                          err.response?.data?.error || 
                          'Error generando estrategia. Intenta nuevamente.';
      setError(errorMessage);
    } finally {
      setGenerating(false);
    }
  };

  const handleAcceptStrategy = async () => {
    if (!strategy) return;
    
    try {
      await strategyService.updateStatus(strategy.id, 'ACTIVE');
      await loadActiveStrategy();
      alert('✅ Estrategia activada exitosamente');
    } catch (err) {
      console.error('Error accepting strategy:', err);
      alert('Error activando estrategia');
    }
  };

  const handleRejectStrategy = async () => {
    if (!strategy) return;
    
    if (!window.confirm('¿Estás seguro de rechazar esta estrategia?')) return;
    
    try {
      await strategyService.updateStatus(strategy.id, 'CANCELLED');
      setStrategy(null);
      alert('Estrategia rechazada');
    } catch (err) {
      console.error('Error rejecting strategy:', err);
      alert('Error rechazando estrategia');
    }
  };

  const renderPositionCard = (position, index) => {
    const expectedGain = position.investment_amount * (position.expected_return_pct / 100);
    const maxLoss = position.entry_price * position.quantity - position.stop_loss * position.quantity;
    
    return (
      <div key={index} className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
        <div className="flex justify-between items-start mb-3">
          <div>
            <h4 className="text-lg font-semibold text-gray-900">{position.ticker}</h4>
            <span className={`inline-block px-2 py-1 text-xs rounded-full mt-1 ${
              position.risk_rating === 'HIGH' ? 'bg-red-100 text-red-800' :
              position.risk_rating === 'MEDIUM' ? 'bg-yellow-100 text-yellow-800' :
              'bg-green-100 text-green-800'
            }`}>
              {position.risk_rating} Risk
            </span>
          </div>
          <div className="text-right">
            <div className="text-2xl font-bold text-gray-900">
              {formatCurrency(position.investment_amount)}
            </div>
            <div className="text-sm text-gray-500">{position.allocation_pct}% del cash</div>
          </div>
        </div>

        <div className="grid grid-cols-2 gap-3 mb-3">
          <div>
            <div className="text-xs text-gray-500">Acción</div>
            <div className="font-medium text-green-600">{position.action}</div>
          </div>
          <div>
            <div className="text-xs text-gray-500">Cantidad</div>
            <div className="font-medium">{position.quantity} unidades</div>
          </div>
          <div>
            <div className="text-xs text-gray-500">Precio Entrada</div>
            <div className="font-medium">{formatCurrency(position.entry_price)}</div>
          </div>
          <div>
            <div className="text-xs text-gray-500">Retorno Esperado</div>
            <div className="font-medium text-green-600">+{formatPercentage(position.expected_return_pct)}</div>
          </div>
        </div>

        <div className="border-t border-gray-200 pt-3 mb-3">
          <div className="grid grid-cols-2 gap-3">
            <div>
              <div className="text-xs text-gray-500 mb-1">🎯 Take Profit</div>
              <div className="font-semibold text-green-600">{formatCurrency(position.take_profit)}</div>
              <div className="text-xs text-gray-500">
                +{formatCurrency(expectedGain)} ganancia
              </div>
            </div>
            <div>
              <div className="text-xs text-gray-500 mb-1">🛡️ Stop Loss</div>
              <div className="font-semibold text-red-600">{formatCurrency(position.stop_loss)}</div>
              <div className="text-xs text-gray-500">
                -{formatCurrency(maxLoss)} máx pérdida
              </div>
            </div>
          </div>
        </div>

        <div className="bg-blue-50 rounded p-3">
          <div className="text-xs text-blue-900 font-medium mb-1">💡 Razonamiento</div>
          <div className="text-sm text-blue-800">{position.reasoning}</div>
        </div>
      </div>
    );
  };

  const renderAllocationChart = () => {
    if (!strategy?.strategy?.recommended_positions) return null;

    const chartData = strategy.strategy.recommended_positions.map(pos => ({
      name: pos.ticker,
      value: pos.allocation_pct,
      amount: pos.investment_amount
    }));

    return (
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold mb-4">Distribución de Capital</h3>
        <ResponsiveContainer width="100%" height={300}>
          <PieChart>
            <Pie
              data={chartData}
              cx="50%"
              cy="50%"
              labelLine={false}
              label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
              outerRadius={100}
              fill="#8884d8"
              dataKey="value"
            >
              {chartData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
              ))}
            </Pie>
            <Tooltip formatter={(value, name, props) => [
              `${value}% (${formatCurrency(props.payload.amount)})`,
              name
            ]} />
            <Legend />
          </PieChart>
        </ResponsiveContainer>
      </div>
    );
  };

  if (loading) {
    return <LoadingSpinner />;
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 flex items-center space-x-3">
          <LightBulbIcon className="h-8 w-8 text-yellow-500" />
          <span>Estrategia Ganadora</span>
        </h1>
        <p className="mt-2 text-gray-600">
          Genera estrategias automatizadas optimizadas con IA para 1-2 semanas
        </p>
      </div>

      {/* Portfolio Summary */}
      {portfolio && (
        <div className="bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg shadow-lg p-6 mb-6 text-white">
          <div className="grid grid-cols-3 gap-4">
            <div>
              <div className="text-sm opacity-90">Cash Disponible</div>
              <div className="text-2xl font-bold">{formatCurrency(portfolio.cash_balance)}</div>
            </div>
            <div>
              <div className="text-sm opacity-90">Valor Total</div>
              <div className="text-2xl font-bold">{formatCurrency(portfolio.total_value)}</div>
            </div>
            <div>
              <div className="text-sm opacity-90">P&L Total</div>
              <div className="text-2xl font-bold">{formatCurrency(portfolio.unrealized_pnl)}</div>
            </div>
          </div>
        </div>
      )}

      {/* Configuration Panel */}
      <div className="bg-white rounded-lg shadow p-6 mb-6">
        <h2 className="text-xl font-semibold mb-4">Configuración de Estrategia</h2>
        
        <div className="grid grid-cols-2 gap-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Horizonte Temporal
            </label>
            <select
              value={timeframeWeeks}
              onChange={(e) => setTimeframeWeeks(parseInt(e.target.value))}
              className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
              disabled={generating}
            >
              <option value={1}>1 semana</option>
              <option value={2}>2 semanas</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Tolerancia al Riesgo
            </label>
            <select
              value={riskTolerance}
              onChange={(e) => setRiskTolerance(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
              disabled={generating}
            >
              <option value="CONSERVATIVE">Conservador</option>
              <option value="MODERATE">Moderado</option>
              <option value="AGGRESSIVE">Agresivo</option>
            </select>
          </div>
        </div>

        <button
          onClick={handleGenerateStrategy}
          disabled={generating}
          className="mt-6 w-full btn-primary flex items-center justify-center space-x-2"
        >
          {generating ? (
            <>
              <ArrowPathIcon className="h-5 w-5 animate-spin" />
              <span>Generando Estrategia...</span>
            </>
          ) : (
            <>
              <LightBulbIcon className="h-5 w-5" />
              <span>Generar Estrategia Ganadora</span>
            </>
          )}
        </button>
      </div>

      {/* Error Message */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
          <div className="flex items-center space-x-2">
            <XCircleIcon className="h-5 w-5 text-red-600" />
            <span className="text-red-800">{error}</span>
          </div>
        </div>
      )}

      {/* Strategy Display */}
      {strategy?.strategy && (
        <div className="space-y-6">
          {/* Strategy Overview */}
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex justify-between items-start mb-4">
              <div>
                <h2 className="text-2xl font-bold text-gray-900 mb-2">Estrategia Actual</h2>
                <p className="text-gray-600">{strategy.strategy.overall_strategy}</p>
              </div>
              <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                strategy.status === 'ACTIVE' ? 'bg-green-100 text-green-800' :
                strategy.status === 'PENDING' ? 'bg-yellow-100 text-yellow-800' :
                'bg-gray-100 text-gray-800'
              }`}>
                {strategy.status}
              </span>
            </div>

            <div className="grid grid-cols-4 gap-4 mb-6">
              <div className="bg-blue-50 rounded-lg p-4">
                <div className="text-sm text-blue-600 mb-1">Inversión Total</div>
                <div className="text-2xl font-bold text-blue-900">
                  {formatCurrency(strategy.strategy.total_investment)}
                </div>
              </div>
              <div className="bg-green-50 rounded-lg p-4">
                <div className="text-sm text-green-600 mb-1">Retorno Esperado</div>
                <div className="text-2xl font-bold text-green-900">
                  {strategy.strategy.expected_return_range?.[0]}-{strategy.strategy.expected_return_range?.[1]}%
                </div>
              </div>
              <div className="bg-purple-50 rounded-lg p-4">
                <div className="text-sm text-purple-600 mb-1">Nivel de Riesgo</div>
                <div className="text-2xl font-bold text-purple-900">
                  {strategy.risk_level}
                </div>
              </div>
              <div className="bg-orange-50 rounded-lg p-4">
                <div className="text-sm text-orange-600 mb-1">Duración</div>
                <div className="text-2xl font-bold text-orange-900">
                  {strategy.timeframe_weeks} semanas
                </div>
              </div>
            </div>

            {/* Action Buttons */}
            {strategy.status === 'PENDING' && (
              <div className="flex space-x-4">
                <button
                  onClick={handleAcceptStrategy}
                  className="flex-1 bg-green-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-green-700 flex items-center justify-center space-x-2"
                >
                  <CheckCircleIcon className="h-5 w-5" />
                  <span>Aceptar Estrategia</span>
                </button>
                <button
                  onClick={handleRejectStrategy}
                  className="flex-1 bg-red-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-red-700 flex items-center justify-center space-x-2"
                >
                  <XCircleIcon className="h-5 w-5" />
                  <span>Rechazar</span>
                </button>
              </div>
            )}
          </div>

          {/* Allocation Chart */}
          {renderAllocationChart()}

          {/* Positions Table */}
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-xl font-semibold mb-4">Posiciones Recomendadas</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {strategy.strategy.recommended_positions?.map((position, index) => 
                renderPositionCard(position, index)
              )}
            </div>
          </div>

          {/* Risk Management */}
          {strategy.strategy.risk_management && (
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-xl font-semibold mb-4 flex items-center space-x-2">
                <ShieldCheckIcon className="h-6 w-6 text-blue-600" />
                <span>Gestión de Riesgos</span>
              </h3>
              <div className="grid grid-cols-3 gap-4">
                <div>
                  <div className="text-sm text-gray-500">Pérdida Máxima del Portfolio</div>
                  <div className="font-semibold text-red-600">
                    {strategy.strategy.risk_management.max_portfolio_loss}
                  </div>
                </div>
                <div>
                  <div className="text-sm text-gray-500">Método de Posicionamiento</div>
                  <div className="font-semibold">
                    {strategy.strategy.risk_management.position_sizing_method}
                  </div>
                </div>
                <div>
                  <div className="text-sm text-gray-500">Score de Diversificación</div>
                  <div className="font-semibold text-blue-600">
                    {strategy.strategy.risk_management.diversification_score}
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Execution Plan */}
          {strategy.strategy.execution_plan && (
            <div className="bg-gradient-to-r from-purple-50 to-blue-50 rounded-lg p-6">
              <h3 className="text-xl font-semibold mb-4 flex items-center space-x-2">
                <ClockIcon className="h-6 w-6 text-purple-600" />
                <span>Plan de Ejecución</span>
              </h3>
              <div className="space-y-3">
                <div>
                  <div className="text-sm font-medium text-gray-700">Orden de Ejecución:</div>
                  <div className="text-gray-900">{strategy.strategy.execution_plan.order}</div>
                </div>
                <div>
                  <div className="text-sm font-medium text-gray-700">Mejor Momento:</div>
                  <div className="text-gray-900">{strategy.strategy.execution_plan.timing}</div>
                </div>
                <div>
                  <div className="text-sm font-medium text-gray-700">Monitoreo:</div>
                  <div className="text-gray-900">{strategy.strategy.execution_plan.monitoring}</div>
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Empty State */}
      {!strategy && !generating && (
        <div className="text-center py-12 bg-white rounded-lg shadow">
          <LightBulbIcon className="h-16 w-16 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">
            No hay estrategia activa
          </h3>
          <p className="text-gray-600">
            Genera una nueva estrategia usando los parámetros de configuración
          </p>
        </div>
      )}
    </div>
  );
}
