import React, { useState, useEffect, useMemo, useCallback, useRef } from 'react';
import { investmentsService } from '../services/api';
import { formatCurrency } from '../utils/formatters';
import {
  GlobeAltIcon,
  BuildingOfficeIcon,
  ChartBarIcon,
  RefreshIcon,
  MagnifyingGlassIcon,
  ChevronLeftIcon,
  ChevronRightIcon
} from '../utils/icons';
import LoadingSpinner from '../components/LoadingSpinner';

export default function Preferences() {
  const [investments, setInvestments] = useState([]);
  const [filteredInvestments, setFilteredInvestments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [debouncedSearchQuery, setDebouncedSearchQuery] = useState('');
  const [selectedExchange, setSelectedExchange] = useState('');
  const [exchanges, setExchanges] = useState([]);
  const [sortBy, setSortBy] = useState('name');
  const [sortOrder, setSortOrder] = useState('asc');
  const [currentPage, setCurrentPage] = useState(1);
  const [totalItems, setTotalItems] = useState(0);
  const [hasMore, setHasMore] = useState(false);
  const [isSearching, setIsSearching] = useState(false);

  const itemsPerPage = 50;

  // Debounced search effect
  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedSearchQuery(searchQuery);
      setCurrentPage(1); // Reset to first page when searching
    }, 300);

    return () => clearTimeout(timer);
  }, [searchQuery]);

  // Load exchanges on mount
  useEffect(() => {
    loadExchanges();
  }, []);

  const loadInvestments = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      setIsSearching(false);

      const offset = (currentPage - 1) * itemsPerPage;
      const params = {
        limit: itemsPerPage,
        offset
      };

      // Solo incluir exchange si tiene un valor válido
      if (selectedExchange && selectedExchange.trim() !== '') {
        params.exchange = selectedExchange;
      }

      console.log('Loading investments with params:', params);
      const response = await investmentsService.getAvailable(params);

      // Manejar respuesta especial de rate limit
      if (response.data.error === 'RATE_LIMIT') {
        console.warn('Rate limit alcanzado al cargar inversiones');
        setError('Se ha alcanzado el límite de velocidad de la API. Los datos se mostrarán desde el caché cuando estén disponibles.');
        setInvestments([]);
        setFilteredInvestments([]);
        setTotalItems(0);
        setHasMore(false);
        return;
      }

      setInvestments(response.data.instruments || []);
      setFilteredInvestments(response.data.instruments || []);
      setTotalItems(response.data.total || 0);
      setHasMore(response.data.has_more || false);
    } catch (err) {
      console.error('Error loading investments:', err);
      setError('Error cargando inversiones disponibles.');
    } finally {
      setLoading(false);
    }
  }, [currentPage, selectedExchange, itemsPerPage]);

  const loadExchanges = async () => {
    try {
      const response = await investmentsService.getExchanges();

      if (response.data.error === 'RATE_LIMIT') {
        console.warn('Rate limit alcanzado al cargar exchanges');
        setExchanges([
          { code: 'NASDAQ', name: 'NASDAQ' },
          { code: 'NYSE', name: 'NYSE' }
        ]);
        return;
      }

      setExchanges(response.data.exchanges || []);
    } catch (err) {
      console.error('Error loading exchanges:', err);
      setExchanges([
        { code: 'NASDAQ', name: 'NASDAQ' },
        { code: 'NYSE', name: 'NYSE' }
      ]);
    }
  };

  const searchInvestments = useCallback(async (query) => {
    if (!query.trim()) {
      setFilteredInvestments(investments);
      setIsSearching(false);
      return;
    }

    try {
      setIsSearching(true);
      setLoading(true);
      const response = await investmentsService.search(query, itemsPerPage);
      setFilteredInvestments(response.data.instruments || []);
      setTotalItems(response.data.total || 0);
      setHasMore(false);
    } catch (err) {
      console.error('Error searching investments:', err);
      setError('Error buscando inversiones.');
    } finally {
      setLoading(false);
    }
  }, [investments, itemsPerPage]);

  const loadInvestmentsRef = useRef();
  const searchInvestmentsRef = useRef();

  // Update refs when functions change
  useEffect(() => {
    loadInvestmentsRef.current = loadInvestments;
    searchInvestmentsRef.current = searchInvestments;
  }, [loadInvestments, searchInvestments]);

  // Load investments when filters change
  useEffect(() => {
    const loadData = async () => {
      if (debouncedSearchQuery) {
        await searchInvestmentsRef.current(debouncedSearchQuery);
      } else {
        await loadInvestmentsRef.current();
      }
    };

    loadData();
  }, [debouncedSearchQuery, selectedExchange, currentPage]);

  // Memoized sorted investments
  const processedInvestments = useMemo(() => {
    let processed = [...filteredInvestments];

    // Sort
    processed.sort((a, b) => {
      let aValue = a[sortBy];
      let bValue = b[sortBy];

      if (typeof aValue === 'string') {
        aValue = aValue.toLowerCase();
        bValue = bValue.toLowerCase();
      }

      if (sortOrder === 'asc') {
        return aValue > bValue ? 1 : -1;
      } else {
        return aValue < bValue ? 1 : -1;
      }
    });

    return processed;
  }, [filteredInvestments, sortBy, sortOrder]);

  // Memoized statistics
  const statistics = useMemo(() => {
    const total = processedInvestments.length;
    const exchangesCount = new Set(processedInvestments.map(i => i.exchange).filter(Boolean)).size;
    const sectorsCount = new Set(processedInvestments.map(i => i.sector).filter(Boolean)).size;

    return {
      total,
      exchangesCount,
      sectorsCount
    };
  }, [processedInvestments]);

  const handleSort = (field) => {
    if (sortBy === field) {
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc');
    } else {
      setSortBy(field);
      setSortOrder('asc');
    }
  };

  const handlePageChange = (page) => {
    setCurrentPage(page);
  };

  const totalPages = Math.ceil(totalItems / itemsPerPage);

  if (loading && investments.length === 0) {
    return <LoadingSpinner />;
  }

  if (error) {
    return (
      <div className="text-center py-12">
        <GlobeAltIcon className="h-16 w-16 text-gray-400 mx-auto mb-4" />
        <h3 className="text-lg font-medium text-gray-900 mb-2">Error cargando inversiones</h3>
        <p className="text-red-600 mb-6">{error}</p>
        <button
          onClick={debouncedSearchQuery ? () => searchInvestments(debouncedSearchQuery) : loadInvestments}
          className="btn-primary flex items-center space-x-2 mx-auto"
        >
          <RefreshIcon className="h-4 w-4" />
          <span>Reintentar</span>
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Mis Preferencias</h1>
          <p className="mt-1 text-sm text-gray-600">
            Explora todas las empresas disponibles con sus logos y detalles completos
          </p>
        </div>
        <div className="mt-4 sm:mt-0">
          <button
            onClick={loadInvestments}
            className="btn-primary flex items-center space-x-2"
            disabled={loading}
          >
            <RefreshIcon className="h-4 w-4" />
            <span>Actualizar</span>
          </button>
        </div>
      </div>

      {/* Filtros y búsqueda */}
      <div className="card">
        <div className="flex flex-col sm:flex-row gap-4">
          {/* Búsqueda */}
          <div className="flex-1 relative">
            <MagnifyingGlassIcon className="absolute left-3 top-3 h-5 w-5 text-gray-400" />
            <input
              type="text"
              placeholder="Buscar por nombre o ticker..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="input-field pl-10 w-full"
            />
            {isSearching && (
              <div className="absolute right-3 top-3">
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600"></div>
              </div>
            )}
          </div>

          {/* Filtro por exchange */}
          <div className="sm:w-48">
            <select
              value={selectedExchange}
              onChange={(e) => {
                setSelectedExchange(e.target.value);
                setCurrentPage(1);
              }}
              className="input-field w-full"
            >
              <option value="">Todos los exchanges</option>
              {exchanges.map((exchange) => (
                <option key={exchange.code} value={exchange.code}>
                  {exchange.name}
                </option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* Estadísticas */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-6">
        <div className="card">
          <div className="flex items-center">
            <ChartBarIcon className="h-8 w-8 text-blue-600" />
            <div className="ml-4">
              <div className="text-sm font-medium text-gray-500">Total de Empresas</div>
              <div className="text-2xl font-bold text-gray-900">{statistics.total}</div>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center">
            <GlobeAltIcon className="h-8 w-8 text-green-600" />
            <div className="ml-4">
              <div className="text-sm font-medium text-gray-500">Exchanges</div>
              <div className="text-2xl font-bold text-gray-900">{statistics.exchangesCount}</div>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center">
            <BuildingOfficeIcon className="h-8 w-8 text-purple-600" />
            <div className="ml-4">
              <div className="text-sm font-medium text-gray-500">Sectores</div>
              <div className="text-2xl font-bold text-gray-900">{statistics.sectorsCount}</div>
            </div>
          </div>
        </div>
      </div>

      {/* Tabla de empresas */}
      <div className="card">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th
                  className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                  onClick={() => handleSort('ticker')}
                >
                  Empresa {sortBy === 'ticker' && (sortOrder === 'asc' ? '↑' : '↓')}
                </th>
                <th
                  className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                  onClick={() => handleSort('current_price_eur')}
                >
                  Precio {sortBy === 'current_price_eur' && (sortOrder === 'asc' ? '↑' : '↓')}
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Exchange
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Sector
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  País
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {processedInvestments.map((investment) => (
                <tr key={investment.ticker} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      {/* Logo de la empresa */}
                      <div className="h-10 w-10 rounded-full mr-3 bg-gray-100 flex items-center justify-center overflow-hidden">
                        {investment.logo_url ? (
                          <img
                            src={investment.logo_url}
                            alt={`${investment.name} logo`}
                            className="h-10 w-10 object-contain"
                            onError={(e) => {
                              e.target.style.display = 'none';
                              e.target.nextElementSibling.style.display = 'flex';
                            }}
                          />
                        ) : null}
                        {/* Placeholder cuando no hay logo */}
                        <div className="h-10 w-10 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-white font-bold text-sm" style={{ display: investment.logo_url ? 'none' : 'flex' }}>
                          {investment.ticker.charAt(0).toUpperCase()}
                        </div>
                      </div>
                      <div>
                        <div className="font-medium text-gray-900">{investment.ticker}</div>
                        <div className="text-sm text-gray-500">{investment.name}</div>
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm font-medium text-gray-900">
                      {formatCurrency(investment.current_price_eur)}
                    </div>
                    <div className="text-xs text-gray-500">
                      {investment.currency} {formatCurrency(investment.current_price)}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className="inline-flex px-2 py-1 text-xs font-medium bg-blue-100 text-blue-800 rounded-full">
                      {investment.exchange}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm text-gray-900">{investment.sector || 'N/A'}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm text-gray-900">{investment.country || 'N/A'}</div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {processedInvestments.length === 0 && !loading && (
          <div className="text-center py-12">
            <ChartBarIcon className="h-16 w-16 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">
              {debouncedSearchQuery ? 'No se encontraron resultados' : 'No hay empresas disponibles'}
            </h3>
            <p className="text-gray-600">
              {debouncedSearchQuery ? 'Prueba con otros términos de búsqueda' : 'Los datos se están cargando...'}
            </p>
          </div>
        )}

        {/* Paginación */}
        {!debouncedSearchQuery && totalPages > 1 && (
          <div className="flex items-center justify-between px-6 py-3 bg-gray-50">
            <div className="text-sm text-gray-700">
              Mostrando {((currentPage - 1) * itemsPerPage) + 1} a {Math.min(currentPage * itemsPerPage, totalItems)} de {totalItems} resultados
            </div>
            <div className="flex items-center space-x-2">
              <button
                onClick={() => handlePageChange(currentPage - 1)}
                disabled={currentPage === 1 || loading}
                className="btn-secondary p-2 disabled:opacity-50"
              >
                <ChevronLeftIcon className="h-4 w-4" />
              </button>

              <span className="text-sm text-gray-700">
                Página {currentPage} de {totalPages}
              </span>

              <button
                onClick={() => handlePageChange(currentPage + 1)}
                disabled={!hasMore || loading}
                className="btn-secondary p-2 disabled:opacity-50"
              >
                <ChevronRightIcon className="h-4 w-4" />
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
