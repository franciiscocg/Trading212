import React from 'react';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend } from 'recharts';
import { formatCurrency, generateColors } from '../utils/formatters';

export default function PortfolioChart({ data }) {
  if (!data || data.length === 0) {
    return (
      <div className="flex items-center justify-center h-64 text-gray-500">
        No hay datos para mostrar
      </div>
    );
  }

  // Preparar datos para el gráfico
  const chartData = data.slice(0, 8).map(position => ({
    name: position.ticker,
    value: position.market_value || position.value,
    percentage: position.percentage || 0,
    pnl: position.unrealized_pnl || 0
  }));

  const colors = generateColors(chartData.length);

  const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      return (
        <div className="bg-white p-3 border border-gray-200 rounded-lg shadow-lg">
          <p className="font-medium">{data.name}</p>
          <p className="text-sm text-gray-600">
            Valor: {formatCurrency(data.value)}
          </p>
          <p className="text-sm text-gray-600">
            Porcentaje: {data.percentage.toFixed(2)}%
          </p>
          {data.pnl !== 0 && (
            <p className={`text-sm ${data.pnl > 0 ? 'text-green-600' : 'text-red-600'}`}>
              P&L: {formatCurrency(data.pnl)}
            </p>
          )}
        </div>
      );
    }
    return null;
  };

  return (
    <div className="h-64">
      <ResponsiveContainer width="100%" height="100%">
        <PieChart>
          <Pie
            data={chartData}
            cx="50%"
            cy="50%"
            innerRadius={40}
            outerRadius={80}
            paddingAngle={2}
            dataKey="value"
          >
            {chartData.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={colors[index]} />
            ))}
          </Pie>
          <Tooltip content={<CustomTooltip />} />
          <Legend 
            verticalAlign="bottom" 
            height={36}
            formatter={(value, entry) => (
              <span style={{ color: entry.color }}>{value}</span>
            )}
          />
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
}
