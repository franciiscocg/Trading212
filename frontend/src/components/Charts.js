import React from 'react';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend } from 'recharts';
import { formatCurrency, formatPercentage, generateColors } from '../utils/formatters';

export default function PortfolioChart({ data, type = 'pie' }) {
  if (!data || data.length === 0) {
    return (
      <div className="flex items-center justify-center h-64 text-gray-500">
        No hay datos para mostrar
      </div>
    );
  }

  // Preparar datos para el gráfico
  const chartData = data.slice(0, 8).map((item, index) => ({
    name: item.ticker || item.sector || item.name || `Item ${index + 1}`,
    value: item.value || item.market_value || item.percentage || 0,
    percentage: item.percentage || 0,
    color: generateColors(data.length)[index]
  }));

  // Añadir "Otros" si hay más de 8 elementos
  if (data.length > 8) {
    const othersValue = data.slice(8).reduce((sum, item) => 
      sum + (item.value || item.market_value || item.percentage || 0), 0
    );
    
    if (othersValue > 0) {
      chartData.push({
        name: 'Otros',
        value: othersValue,
        percentage: 0,
        color: '#9CA3AF'
      });
    }
  }

  const renderTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      return (
        <div className="bg-white p-3 border border-gray-200 rounded-lg shadow-lg">
          <p className="font-medium text-gray-900">{data.name}</p>
          <p className="text-sm text-gray-600">
            Valor: {formatCurrency(data.value)}
          </p>
          {data.percentage > 0 && (
            <p className="text-sm text-gray-600">
              Porcentaje: {formatPercentage(data.percentage)}
            </p>
          )}
        </div>
      );
    }
    return null;
  };

  const renderLabel = ({ name, percent }) => {
    if (percent < 0.05) return ''; // No mostrar labels para segmentos muy pequeños
    return `${(percent * 100).toFixed(1)}%`;
  };

  return (
    <div className="w-full">
      <ResponsiveContainer width="100%" height={300}>
        <PieChart>
          <Pie
            data={chartData}
            cx="50%"
            cy="50%"
            labelLine={false}
            label={renderLabel}
            outerRadius={100}
            fill="#8884d8"
            dataKey="value"
          >
            {chartData.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={entry.color} />
            ))}
          </Pie>
          <Tooltip content={renderTooltip} />
          <Legend 
            verticalAlign="bottom" 
            height={36}
            formatter={(value, entry) => (
              <span style={{ color: entry.color }}>
                {value}
              </span>
            )}
          />
        </PieChart>
      </ResponsiveContainer>

      {/* Lista de elementos */}
      <div className="mt-4 space-y-2 max-h-40 overflow-y-auto">
        {chartData.map((item, index) => (
          <div key={index} className="flex items-center justify-between text-sm">
            <div className="flex items-center space-x-2">
              <div 
                className="w-3 h-3 rounded-full" 
                style={{ backgroundColor: item.color }}
              />
              <span className="text-gray-700 truncate max-w-32">
                {item.name}
              </span>
            </div>
            <span className="font-medium text-gray-900">
              {formatCurrency(item.value)}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
