import React, { useState, useEffect } from 'react';
import { positionsService, portfolioService } from '../services/api';
import { formatCurrency, formatPercentage, getValueColor, debounce } from '../utils/formatters';
import { MagnifyingGlassIcon, ArrowUpIcon, ArrowDownIcon, ArrowPathIcon, CheckCircleIcon } from '../utils/icons';
import LoadingSpinner from '../components/LoadingSpinner';

export default function Portfolio() {
  const [positions, setPositions] = useState([]);
  const [filteredPositions, setFilteredPositions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);  const [searchQuery, setSearchQuery] = useState('');
  const [sortBy, setSortBy] = useState('value');  const [sortDirection, setSortDirection] = useState('desc');
  const [syncing, setSyncing] = useState(false);
  const [selectedPosition, setSelectedPosition] = useState(null);
  const [syncMessage, setSyncMessage] = useState(null);

  useEffect(() => {
    loadPositions();
  }, []);
  useEffect(() => {
    const handleSearch = debounce((query) => {
      if (!query.trim()) {
        setFilteredPositions(positions);
        return;
      }

      const filtered = positions.filter(position =>
        position.ticker.toLowerCase().includes(query.toLowerCase()) ||
        (position.company_name && position.company_name.toLowerCase().includes(query.toLowerCase()))
      );
      setFilteredPositions(filtered);
    }, 300);

    handleSearch(searchQuery);
  }, [searchQuery, positions]);

  const syncPortfolio = async () => {
    setSyncing(true);
    setError(null);
      try {
      await portfolioService.syncPortfolio();
      // Después de sincronizar, recargar las posiciones
      await loadPositions();
      setSyncMessage('Datos sincronizados exitosamente');
      setTimeout(() => setSyncMessage(null), 3000); // Ocultar mensaje después de 3 segundos
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

  const loadPositions = async () => {
    setLoading(true);
    setError(null);
      try {
      const response = await positionsService.getPositions();
      if (response.data && Array.isArray(response.data)) {
        setPositions(response.data);
        setFilteredPositions(response.data);
        setError(null);
      } else {
        throw new Error('Invalid data format received from server');
      }
    } catch (err) {
      let errorMessage = 'Error cargando posiciones';
      
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
      console.error('Positions error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleSort = (field) => {
    const direction = sortBy === field && sortDirection === 'desc' ? 'asc' : 'desc';
    setSortBy(field);
    setSortDirection(direction);

    const sorted = [...filteredPositions].sort((a, b) => {
      let aVal = a[field];
      let bVal = b[field];

      if (typeof aVal === 'string') {
        aVal = aVal.toLowerCase();
        bVal = bVal.toLowerCase();
      }

      if (direction === 'asc') {
        return aVal > bVal ? 1 : -1;
      } else {
        return aVal < bVal ? 1 : -1;
      }
    });

    setFilteredPositions(sorted);
  };

  const getSortIcon = (field) => {
    if (sortBy !== field) return null;
    return sortDirection === 'desc' ? 
      <ArrowDownIcon className="h-4 w-4" /> : 
      <ArrowUpIcon className="h-4 w-4" />;
  };

  if (loading) {
    return <LoadingSpinner />;
  }
  if (error) {
    return (
      <div className="text-center py-12">
        <div className="text-red-600 mb-4 text-lg">{error}</div>
        <div className="space-x-4">
          <button onClick={loadPositions} className="btn-primary">
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
          <h1 className="text-3xl font-bold text-gray-900">Portafolio</h1>
          <p className="mt-1 text-sm text-gray-600">
            Todas tus posiciones de Trading212
          </p>
        </div>
        <div className="mt-4 sm:mt-0 flex flex-col sm:flex-row gap-4">
          <button
            onClick={syncPortfolio}
            disabled={syncing || loading}
            className="btn-secondary flex items-center space-x-2"
          >
            <ArrowPathIcon className={`h-4 w-4 ${syncing ? 'animate-spin' : ''}`} />
            <span>{syncing ? 'Sincronizando...' : 'Sincronizar'}</span>
          </button>
          <div className="relative">
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <MagnifyingGlassIcon className="h-5 w-5 text-gray-400" />
            </div>
            <input
              type="text"
              className="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md leading-5 bg-white placeholder-gray-500 focus:outline-none focus:placeholder-gray-400 focus:ring-1 focus:ring-trading-blue focus:border-trading-blue"
              placeholder="Buscar posiciones..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
          </div>
        </div>
      </div>{/* Resumen Extendido */}
      <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
        <div className="card">
          <div className="text-sm font-medium text-gray-500">Total Posiciones</div>
          <div className="text-2xl font-bold text-gray-900">{positions.length}</div>
        </div>
        <div className="card">
          <div className="text-sm font-medium text-gray-500">Valor Total</div>
          <div className="text-2xl font-bold text-gray-900">
            {formatCurrency(positions.reduce((sum, pos) => sum + pos.market_value, 0))}
          </div>
        </div>
        <div className="card">
          <div className="text-sm font-medium text-gray-500">P&L Total</div>
          <div className={`text-2xl font-bold ${getValueColor(positions.reduce((sum, pos) => sum + pos.unrealized_pnl, 0))}`}>
            {formatCurrency(positions.reduce((sum, pos) => sum + pos.unrealized_pnl, 0))}
          </div>
        </div>
        <div className="card">
          <div className="text-sm font-medium text-gray-500">P&L Promedio</div>
          <div className={`text-2xl font-bold ${getValueColor(positions.length > 0 ? positions.reduce((sum, pos) => sum + pos.unrealized_pnl_pct, 0) / positions.length : 0)}`}>
            {positions.length > 0 
              ? formatPercentage(positions.reduce((sum, pos) => sum + pos.unrealized_pnl_pct, 0) / positions.length)
              : '0.00%'
            }
          </div>
        </div>
      </div>

      {/* Estadísticas Adicionales */}
      {positions.length > 0 && (
        <div className="grid grid-cols-1 gap-6 sm:grid-cols-3">
          <div className="card">
            <div className="text-sm font-medium text-gray-500">Posiciones Ganadoras</div>
            <div className="text-lg font-bold text-green-600">
              {positions.filter(pos => pos.unrealized_pnl > 0).length}
            </div>
            <div className="text-xs text-gray-500">
              {positions.length > 0 
                ? `${((positions.filter(pos => pos.unrealized_pnl > 0).length / positions.length) * 100).toFixed(1)}%`
                : '0%'
              } del total
            </div>
          </div>
          <div className="card">
            <div className="text-sm font-medium text-gray-500">Posiciones Perdedoras</div>
            <div className="text-lg font-bold text-red-600">
              {positions.filter(pos => pos.unrealized_pnl < 0).length}
            </div>
            <div className="text-xs text-gray-500">
              {positions.length > 0 
                ? `${((positions.filter(pos => pos.unrealized_pnl < 0).length / positions.length) * 100).toFixed(1)}%`
                : '0%'
              } del total
            </div>
          </div>
          <div className="card">
            <div className="text-sm font-medium text-gray-500">Posiciones Neutras</div>
            <div className="text-lg font-bold text-gray-600">
              {positions.filter(pos => pos.unrealized_pnl === 0).length}
            </div>
            <div className="text-xs text-gray-500">
              {positions.length > 0 
                ? `${((positions.filter(pos => pos.unrealized_pnl === 0).length / positions.length) * 100).toFixed(1)}%`
                : '0%'
              } del total
            </div>
          </div>
        </div>
      )}

      {/* Tabla de posiciones */}
      <div className="card overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th 
                  className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                  onClick={() => handleSort('ticker')}
                >
                  <div className="flex items-center space-x-1">
                    <span>Símbolo</span>
                    {getSortIcon('ticker')}
                  </div>
                </th>
                <th 
                  className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                  onClick={() => handleSort('quantity')}
                >
                  <div className="flex items-center space-x-1">
                    <span>Cantidad</span>
                    {getSortIcon('quantity')}
                  </div>
                </th>
                <th 
                  className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                  onClick={() => handleSort('average_price')}
                >
                  <div className="flex items-center space-x-1">
                    <span>Precio Promedio</span>
                    {getSortIcon('average_price')}
                  </div>
                </th>
                <th 
                  className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                  onClick={() => handleSort('current_price')}
                >
                  <div className="flex items-center space-x-1">
                    <span>Precio Actual</span>
                    {getSortIcon('current_price')}
                  </div>
                </th>
                <th 
                  className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                  onClick={() => handleSort('market_value')}
                >
                  <div className="flex items-center space-x-1">
                    <span>Valor de Mercado</span>
                    {getSortIcon('market_value')}
                  </div>
                </th>
                <th 
                  className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                  onClick={() => handleSort('unrealized_pnl')}
                >
                  <div className="flex items-center space-x-1">
                    <span>P&L</span>
                    {getSortIcon('unrealized_pnl')}
                  </div>
                </th>
                <th 
                  className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                  onClick={() => handleSort('unrealized_pnl_pct')}
                >
                  <div className="flex items-center space-x-1">
                    <span>P&L %</span>
                    {getSortIcon('unrealized_pnl_pct')}
                  </div>
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {filteredPositions.map((position) => (
                <tr 
                  key={position.id} 
                  className="hover:bg-gray-50 cursor-pointer transition-colors duration-200"
                  onClick={() => setSelectedPosition(selectedPosition?.id === position.id ? null : position)}
                >                  <td className="px-6 py-4 whitespace-nowrap">
                    <div>
                      <div className="text-sm font-medium text-gray-900">
                        {position.ticker}
                      </div>
                      {position.company_name && position.company_name !== position.ticker && (
                        <div className="text-sm text-gray-500">
                          {position.company_name.length > 30 
                            ? position.company_name.substring(0, 30) + '...'
                            : position.company_name}
                        </div>
                      )}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {position.quantity.toLocaleString()}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {formatCurrency(position.average_price)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {formatCurrency(position.current_price)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                    {formatCurrency(position.market_value)}
                  </td>
                  <td className={`px-6 py-4 whitespace-nowrap text-sm font-medium ${getValueColor(position.unrealized_pnl)}`}>
                    {formatCurrency(position.unrealized_pnl)}
                  </td>
                  <td className={`px-6 py-4 whitespace-nowrap text-sm font-medium ${getValueColor(position.unrealized_pnl_pct)}`}>
                    <div className="flex items-center">
                      {position.unrealized_pnl_pct > 0 ? (
                        <ArrowUpIcon className="h-4 w-4 mr-1" />
                      ) : position.unrealized_pnl_pct < 0 ? (
                        <ArrowDownIcon className="h-4 w-4 mr-1" />
                      ) : null}
                      {formatPercentage(position.unrealized_pnl_pct)}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>        {filteredPositions.length === 0 && (
          <div className="text-center py-12">
            <div className="text-gray-500 mb-4">
              {searchQuery ? 'No se encontraron posiciones que coincidan con tu búsqueda' : 'No hay posiciones para mostrar'}
            </div>
            {!searchQuery && positions.length === 0 && (
              <div className="space-y-4">
                <p className="text-sm text-gray-400">
                  Tu portafolio parece estar vacío. Sincroniza tus datos de Trading212 para ver tus posiciones.
                </p>
                <button onClick={syncPortfolio} disabled={syncing} className="btn-primary">
                  {syncing ? 'Sincronizando...' : 'Sincronizar Datos'}
                </button>
              </div>            )}
          </div>
        )}
      </div>

      {/* Detalles de posición seleccionada */}
      {selectedPosition && (
        <div className="card">          <div className="border-b border-gray-200 pb-4 mb-4 flex justify-between items-center">
            <h3 className="text-lg font-medium text-gray-900">
              Detalles de {selectedPosition.ticker}
            </h3>
            <button
              onClick={() => setSelectedPosition(null)}
              className="text-sm text-gray-500 hover:text-gray-700 px-3 py-1 rounded border"
            >
              Cerrar
            </button>
          </div>
          
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <div>
              <div className="text-sm font-medium text-gray-500">Cantidad Total</div>
              <div className="text-lg font-bold text-gray-900">
                {selectedPosition.quantity.toLocaleString()} acciones
              </div>
            </div>
            <div>
              <div className="text-sm font-medium text-gray-500">Precio Promedio</div>
              <div className="text-lg font-bold text-gray-900">
                {formatCurrency(selectedPosition.average_price)}
              </div>
            </div>
            <div>
              <div className="text-sm font-medium text-gray-500">Precio Actual</div>
              <div className="text-lg font-bold text-gray-900">
                {formatCurrency(selectedPosition.current_price)}
              </div>
            </div>
            <div>
              <div className="text-sm font-medium text-gray-500">Diferencia de Precio</div>
              <div className={`text-lg font-bold ${getValueColor(selectedPosition.current_price - selectedPosition.average_price)}`}>
                {formatCurrency(selectedPosition.current_price - selectedPosition.average_price)}
              </div>
            </div>            <div>
              <div className="text-sm font-medium text-gray-500">Inversión Total</div>
              <div className="text-lg font-bold text-gray-900">
                {formatCurrency(selectedPosition.cost_basis || selectedPosition.quantity * selectedPosition.average_price)}
              </div>
            </div>
            <div>
              <div className="text-sm font-medium text-gray-500">Valor Actual</div>
              <div className="text-lg font-bold text-gray-900">
                {formatCurrency(selectedPosition.market_value)}
              </div>
            </div>
            <div>
              <div className="text-sm font-medium text-gray-500">Ganancia/Pérdida</div>
              <div className={`text-lg font-bold ${getValueColor(selectedPosition.unrealized_pnl)}`}>
                {formatCurrency(selectedPosition.unrealized_pnl)}
              </div>
            </div>
            <div>
              <div className="text-sm font-medium text-gray-500">Rendimiento %</div>
              <div className={`text-lg font-bold ${getValueColor(selectedPosition.unrealized_pnl_pct)}`}>
                {formatPercentage(selectedPosition.unrealized_pnl_pct)}
              </div>
            </div>
          </div>
          
          {selectedPosition.company_name && selectedPosition.company_name !== selectedPosition.ticker && (
            <div className="mt-4 pt-4 border-t border-gray-200">
              <div className="text-sm font-medium text-gray-500">Nombre de la Empresa</div>
              <div className="text-lg text-gray-900">{selectedPosition.company_name}</div>
            </div>
          )}
        </div>
      )}

    </div>
  );
}
