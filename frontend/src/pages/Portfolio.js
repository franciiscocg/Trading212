import React, { useState, useEffect } from 'react';
import { positionsService } from '../services/api';
import { formatCurrency, formatPercentage, getValueColor, debounce } from '../utils/formatters';
import { MagnifyingGlassIcon, ArrowUpIcon, ArrowDownIcon } from '../utils/icons';
import LoadingSpinner from '../components/LoadingSpinner';

export default function Portfolio() {
  const [positions, setPositions] = useState([]);
  const [filteredPositions, setFilteredPositions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [sortBy, setSortBy] = useState('value');
  const [sortDirection, setSortDirection] = useState('desc');

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

  const loadPositions = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await positionsService.getPositions();
      setPositions(response.data);
      setFilteredPositions(response.data);
    } catch (err) {      setError('Error cargando posiciones');
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
        <div className="text-red-600 mb-4">{error}</div>
        <button onClick={loadPositions} className="btn-primary">
          Reintentar
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Portafolio</h1>
          <p className="mt-1 text-sm text-gray-600">
            Todas tus posiciones de Trading212
          </p>
        </div>
        <div className="mt-4 sm:mt-0">
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
      </div>

      {/* Resumen */}
      <div className="grid grid-cols-1 gap-6 sm:grid-cols-3">
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
      </div>

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
                <tr key={position.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div>
                      <div className="text-sm font-medium text-gray-900">
                        {position.ticker}
                      </div>
                      {position.company_name && (
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
        </div>

        {filteredPositions.length === 0 && (
          <div className="text-center py-12">
            <div className="text-gray-500">
              {searchQuery ? 'No se encontraron posiciones' : 'No hay posiciones para mostrar'}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
