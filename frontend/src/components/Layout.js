import React, { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { 
  HomeIcon, 
  ChartBarIcon, 
  CogIcon, 
  DocumentChartBarIcon,
  LightBulbIcon,
  Bars3Icon,
  XMarkIcon
} from '../utils/icons';

const navigation = [
  { name: 'Dashboard', href: '/', icon: HomeIcon },
  { name: 'Portafolio', href: '/portfolio', icon: ChartBarIcon },
  { name: 'Analytics', href: '/analytics', icon: DocumentChartBarIcon },
  { name: 'Investment Advisor', href: '/investment-advisor', icon: LightBulbIcon },
  { name: 'Configuración', href: '/settings', icon: CogIcon },
];

export default function Layout({ children }) {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const location = useLocation();

  return (
    <div className="h-screen flex bg-gray-50">
      {/* Sidebar móvil */}
      <div className={`${sidebarOpen ? 'block' : 'hidden'} fixed inset-0 z-40 lg:hidden`}>
        <div className="fixed inset-0 bg-gray-600 bg-opacity-75" onClick={() => setSidebarOpen(false)} />
        <div className="fixed inset-y-0 left-0 flex flex-col w-64 bg-white shadow-xl">
          <div className="flex items-center justify-between h-16 px-4 bg-trading-blue">
            <h1 className="text-xl font-bold text-white">Trading212</h1>
            <button onClick={() => setSidebarOpen(false)} className="text-white">
              <XMarkIcon className="h-6 w-6" />
            </button>
          </div>
          <nav className="flex-1 px-4 py-4 space-y-2">
            {navigation.map((item) => {
              const isActive = location.pathname === item.href;
              return (
                <Link
                  key={item.name}
                  to={item.href}
                  className={`${
                    isActive
                      ? 'bg-trading-blue text-white'
                      : 'text-gray-600 hover:bg-gray-100'
                  } group flex items-center px-3 py-2 text-sm font-medium rounded-md`}
                  onClick={() => setSidebarOpen(false)}
                >
                  <item.icon className="mr-3 h-5 w-5" />
                  {item.name}
                </Link>
              );
            })}
          </nav>
        </div>
      </div>

      {/* Sidebar desktop */}
      <div className="hidden lg:flex lg:flex-shrink-0">
        <div className="flex flex-col w-64 bg-white border-r border-gray-200">
          <div className="flex items-center h-16 px-4 bg-trading-blue">
            <h1 className="text-xl font-bold text-white">Trading212</h1>
          </div>
          <nav className="flex-1 px-4 py-4 space-y-2">
            {navigation.map((item) => {
              const isActive = location.pathname === item.href;
              return (
                <Link
                  key={item.name}
                  to={item.href}
                  className={`${
                    isActive
                      ? 'bg-trading-blue text-white'
                      : 'text-gray-600 hover:bg-gray-100'
                  } group flex items-center px-3 py-2 text-sm font-medium rounded-md`}
                >
                  <item.icon className="mr-3 h-5 w-5" />
                  {item.name}
                </Link>
              );
            })}
          </nav>
        </div>
      </div>

      {/* Contenido principal */}
      <div className="flex flex-col flex-1 overflow-hidden">
        {/* Header móvil */}
        <div className="lg:hidden bg-white border-b border-gray-200 px-4 py-3">
          <div className="flex items-center justify-between">
            <button
              onClick={() => setSidebarOpen(true)}
              className="text-gray-600"
            >
              <Bars3Icon className="h-6 w-6" />
            </button>
            <h1 className="text-lg font-semibold text-gray-900">Trading212</h1>
            <div></div>
          </div>
        </div>

        {/* Contenido */}
        <main className="flex-1 overflow-y-auto">
          <div className="p-6">
            {children}
          </div>
        </main>
      </div>
    </div>
  );
}
