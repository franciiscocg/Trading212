/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'trading-blue': '#1e40af',
        'trading-green': '#059669',
        'trading-red': '#dc2626',
        'trading-gray': '#6b7280'
      }
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
  ],
}
