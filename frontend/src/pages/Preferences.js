import React, { useState, useEffect, useMemo, useCallback, useRef } from 'react';
import { investmentsService } from '../services/api';
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

  // Estados para selección y análisis de sentimientos
  const [selectedCompanies, setSelectedCompanies] = useState(new Set());
  const [sentimentAnalysis, setSentimentAnalysis] = useState({});
  const [analyzingSentiment, setAnalyzingSentiment] = useState(false);
  const [sentimentError, setSentimentError] = useState(null);

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

  // Funciones para manejar selección de empresas
  const handleCompanySelect = (ticker, isSelected) => {
    const newSelected = new Set(selectedCompanies);
    if (isSelected) {
      newSelected.add(ticker);
    } else {
      newSelected.delete(ticker);
    }
    setSelectedCompanies(newSelected);
  };

  const handleSelectAll = (isSelected) => {
    if (isSelected) {
      const allTickers = new Set(filteredInvestments.map(inv => inv.ticker));
      setSelectedCompanies(allTickers);
    } else {
      setSelectedCompanies(new Set());
    }
  };

  // Función para analizar sentimientos
  const analyzeSentiment = async () => {
    if (selectedCompanies.size === 0) {
      setSentimentError('Selecciona al menos una empresa para analizar');
      return;
    }

    try {
      setAnalyzingSentiment(true);
      setSentimentError(null);

      const symbols = Array.from(selectedCompanies);
      console.log('🔍 Analizando sentimientos para:', symbols);

      const response = await investmentsService.analyzeSentiment(symbols, 5);

      // Organizar resultados por símbolo
      const analysisBySymbol = {};
      response.data.results.forEach(result => {
        analysisBySymbol[result.symbol] = result;
      });

      setSentimentAnalysis(analysisBySymbol);
      console.log('✅ Análisis de sentimientos completado');

    } catch (err) {
      console.error('❌ Error analizando sentimientos:', err);
      setSentimentError('Error analizando sentimientos. Verifica tu conexión a internet.');
    } finally {
      setAnalyzingSentiment(false);
    }
  };

  // Función para obtener el color del sentimiento
  const getSentimentColor = (score) => {
    if (score > 0.1) return 'text-green-600 bg-green-50';
    if (score < -0.1) return 'text-red-600 bg-red-50';
    return 'text-gray-600 bg-gray-50';
  };

  // Función para formatear el score de sentimiento
  const formatSentimentScore = (score) => {
    if (score === null || score === undefined) return 'N/A';
    return score.toFixed(3);
  };

  const totalPages = Math.ceil(totalItems / itemsPerPage);

  if (loading && investments.length === 0) {
    return <LoadingSpinner />;
  }

  // No mostrar página de error completa, solo un banner de advertencia
  // if (error) {
  //   return (
  //     <div className="text-center py-12">
  //       <GlobeAltIcon className="h-16 w-16 text-gray-400 mx-auto mb-4" />
  //       <h3 className="text-lg font-medium text-gray-900 mb-2">Error cargando inversiones</h3>
  //       <p className="text-red-600 mb-6">{error}</p>
  //       <button
  //         onClick={debouncedSearchQuery ? () => searchInvestments(debouncedSearchQuery) : loadInvestments}
  //         className="btn-primary flex items-center space-x-2 mx-auto"
  //       >
  //         <RefreshIcon className="h-4 w-4" />
  //         <span>Reintentar</span>
  //       </button>
  //     </div>
  //   );
  // }

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
        <div className="mt-4 sm:mt-0 flex space-x-3">
          {selectedCompanies.size > 0 && (
            <div className="flex items-center space-x-2">
              <span className="text-sm text-gray-600">
                {selectedCompanies.size} empresa{selectedCompanies.size !== 1 ? 's' : ''} seleccionada{selectedCompanies.size !== 1 ? 's' : ''}
              </span>
              <button
                onClick={analyzeSentiment}
                disabled={analyzingSentiment}
                className="btn-primary flex items-center space-x-2 disabled:opacity-50"
              >
                {analyzingSentiment ? (
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                ) : (
                  <ChartBarIcon className="h-4 w-4" />
                )}
                <span>{analyzingSentiment ? 'Analizando...' : 'Analizar Sentimiento'}</span>
              </button>
            </div>
          )}
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

      {/* Banner de error sutil si hay problemas */}
      {error && (
        <div className="bg-yellow-50 border-l-4 border-yellow-400 p-4">
          <div className="flex">
            <div className="flex-shrink-0">
              <svg className="h-5 w-5 text-yellow-400" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
              </svg>
            </div>
            <div className="ml-3">
              <p className="text-sm text-yellow-700">
                {error}
              </p>
            </div>
            <div className="ml-auto pl-3">
              <div className="-mx-1.5 -my-1.5">
                <button
                  onClick={() => setError(null)}
                  className="inline-flex bg-yellow-50 rounded-md p-1.5 text-yellow-500 hover:bg-yellow-100 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-yellow-50 focus:ring-yellow-600"
                >
                  <span className="sr-only">Cerrar</span>
                  <svg className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                    <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
                  </svg>
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Banner de error de análisis de sentimientos */}
      {sentimentError && (
        <div className="bg-red-50 border-l-4 border-red-400 p-4">
          <div className="flex">
            <div className="flex-shrink-0">
              <svg className="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
              </svg>
            </div>
            <div className="ml-3">
              <p className="text-sm text-red-700">
                {sentimentError}
              </p>
            </div>
            <div className="ml-auto pl-3">
              <div className="-mx-1.5 -my-1.5">
                <button
                  onClick={() => setSentimentError(null)}
                  className="inline-flex bg-red-50 rounded-md p-1.5 text-red-500 hover:bg-red-100 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-red-50 focus:ring-red-600"
                >
                  <span className="sr-only">Cerrar</span>
                  <svg className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                    <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
                  </svg>
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

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
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  <input
                    type="checkbox"
                    checked={selectedCompanies.size === filteredInvestments.length && filteredInvestments.length > 0}
                    onChange={(e) => handleSelectAll(e.target.checked)}
                    className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                  />
                </th>
                <th
                  className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                  onClick={() => handleSort('ticker')}
                >
                  Empresa {sortBy === 'ticker' && (sortOrder === 'asc' ? '↑' : '↓')}
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Sentimiento
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Vader
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  TextBlob
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Noticias
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {processedInvestments.map((investment) => {
                const sentiment = sentimentAnalysis[investment.ticker];
                return (
                  <tr key={investment.ticker} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <input
                        type="checkbox"
                        checked={selectedCompanies.has(investment.ticker)}
                        onChange={(e) => handleCompanySelect(investment.ticker, e.target.checked)}
                        className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                      />
                    </td>
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
                      {sentiment ? (
                        <span className={`inline-flex px-2 py-1 text-xs font-medium rounded-full ${getSentimentColor(sentiment.sentiment.overall_score)}`}>
                          {formatSentimentScore(sentiment.sentiment.overall_score)}
                        </span>
                      ) : (
                        <span className="text-gray-400 text-xs">No analizado</span>
                      )}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      {sentiment ? (
                        <span className={`text-sm font-medium ${getSentimentColor(sentiment.sentiment.vader_compound)}`}>
                          {formatSentimentScore(sentiment.sentiment.vader_compound)}
                        </span>
                      ) : (
                        <span className="text-gray-400 text-xs">-</span>
                      )}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      {sentiment ? (
                        <span className={`text-sm font-medium ${getSentimentColor(sentiment.sentiment.textblob_polarity)}`}>
                          {formatSentimentScore(sentiment.sentiment.textblob_polarity)}
                        </span>
                      ) : (
                        <span className="text-gray-400 text-xs">-</span>
                      )}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      {sentiment ? (
                        <span className="text-sm text-gray-900">
                          {sentiment.news_count}
                        </span>
                      ) : (
                        <span className="text-gray-400 text-xs">-</span>
                      )}
                    </td>
                  </tr>
                );
              })}
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
