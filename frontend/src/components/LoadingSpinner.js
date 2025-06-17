import React from 'react';

export default function LoadingSpinner({ size = 'large' }) {
  const sizeClasses = {
    small: 'h-4 w-4',
    medium: 'h-8 w-8',
    large: 'h-12 w-12'
  };

  return (
    <div className="flex items-center justify-center p-8">
      <div
        className={`${sizeClasses[size]} border-4 border-gray-200 border-t-trading-blue rounded-full animate-spin`}
      />
    </div>
  );
}
