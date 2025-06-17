// Utilidades para formatear valores monetarios
export const formatCurrency = (value, currency = 'EUR', decimals = 2) => {
  if (value === null || value === undefined) return '-';
  
  return new Intl.NumberFormat('es-ES', {
    style: 'currency',
    currency: currency,
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  }).format(value);
};

// Formatear porcentajes
export const formatPercentage = (value, decimals = 2) => {
  if (value === null || value === undefined) return '-';
  
  return new Intl.NumberFormat('es-ES', {
    style: 'percent',
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  }).format(value / 100);
};

// Formatear números grandes
export const formatNumber = (value, decimals = 0) => {
  if (value === null || value === undefined) return '-';
  
  return new Intl.NumberFormat('es-ES', {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  }).format(value);
};

// Determinar el color basado en el valor (positivo/negativo)
export const getValueColor = (value) => {
  if (value > 0) return 'text-trading-green';
  if (value < 0) return 'text-trading-red';
  return 'text-gray-600';
};

// Obtener clase CSS para background basado en valor
export const getValueBackground = (value) => {
  if (value > 0) return 'bg-green-50 text-trading-green';
  if (value < 0) return 'bg-red-50 text-trading-red';
  return 'bg-gray-50 text-gray-600';
};

// Formatear fecha
export const formatDate = (dateString) => {
  if (!dateString) return '-';
  
  const date = new Date(dateString);
  return new Intl.DateTimeFormat('es-ES', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  }).format(date);
};

// Formatear solo fecha
export const formatDateOnly = (dateString) => {
  if (!dateString) return '-';
  
  const date = new Date(dateString);
  return new Intl.DateTimeFormat('es-ES', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  }).format(date);
};

// Calcular el cambio porcentual
export const calculatePercentageChange = (current, previous) => {
  if (!previous || previous === 0) return 0;
  return ((current - previous) / previous) * 100;
};

// Truncar texto
export const truncateText = (text, maxLength = 20) => {
  if (!text) return '';
  if (text.length <= maxLength) return text;
  return text.substring(0, maxLength) + '...';
};

// Generar colores para gráficos
export const generateColors = (count) => {
  const colors = [
    '#3B82F6', '#EF4444', '#10B981', '#F59E0B', '#8B5CF6',
    '#EC4899', '#14B8A6', '#F97316', '#6366F1', '#84CC16'
  ];
  
  const result = [];
  for (let i = 0; i < count; i++) {
    result.push(colors[i % colors.length]);
  }
  return result;
};

// Debounce para búsquedas
export const debounce = (func, wait) => {
  let timeout;
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
};
