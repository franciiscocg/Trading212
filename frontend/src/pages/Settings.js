import React, { useState, useEffect } from 'react';
import { authService } from '../services/api';
import { CheckCircleIcon, XCircleIcon, CogIcon } from '../utils/icons';

export default function Settings() {
  const [apiKey, setApiKey] = useState('');
  const [connectionStatus, setConnectionStatus] = useState(null);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');

  useEffect(() => {
    checkConnectionStatus();
  }, []);

  const checkConnectionStatus = async () => {
    try {
      const response = await authService.getConnectionStatus();
      setConnectionStatus(response.data);
    } catch (err) {
      console.error('Error checking connection status:', err);
    }
  };

  const handleValidateApiKey = async (e) => {
    e.preventDefault();
    setLoading(true);
    setMessage('');

    try {
      const response = await authService.validateApiKey(apiKey);
      if (response.data.valid) {
        setMessage('API Key válida y configurada correctamente');
        localStorage.setItem('trading212_api_key', apiKey);
        await checkConnectionStatus();
      }
    } catch (err) {
      setMessage('Error: API Key inválida o no tiene permisos suficientes');
    } finally {
      setLoading(false);
    }
  };

  const handleClearApiKey = () => {
    setApiKey('');
    localStorage.removeItem('trading212_api_key');
    setConnectionStatus(null);
    setMessage('API Key eliminada');
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Configuración</h1>
        <p className="mt-1 text-sm text-gray-600">
          Configura tu conexión con Trading212
        </p>
      </div>

      {/* Estado de conexión */}
      {connectionStatus && (
        <div className="card">
          <h3 className="text-lg font-medium text-gray-900 mb-4">
            Estado de Conexión
          </h3>
          <div className="flex items-center space-x-3">
            {connectionStatus.connected ? (
              <CheckCircleIcon className="h-5 w-5 text-green-500" />
            ) : (
              <XCircleIcon className="h-5 w-5 text-red-500" />
            )}
            <span className={connectionStatus.connected ? 'text-green-600' : 'text-red-600'}>
              {connectionStatus.connected ? 'Conectado' : 'Desconectado'}
            </span>
          </div>
          {connectionStatus.last_sync && (
            <p className="text-sm text-gray-500 mt-2">
              Última sincronización: {new Date(connectionStatus.last_sync).toLocaleString()}
            </p>
          )}
        </div>
      )}

      {/* Configuración de API Key */}
      <div className="card">
        <div className="flex items-center mb-4">
          <CogIcon className="h-6 w-6 text-gray-400 mr-3" />
          <h3 className="text-lg font-medium text-gray-900">
            API Key de Trading212
          </h3>
        </div>
        
        <div className="space-y-4">
          <div>
            <p className="text-sm text-gray-600 mb-4">
              Para conectar con tu cuenta de Trading212, necesitas una API Key. 
              Puedes obtenerla desde tu cuenta de Trading212 en la sección de configuración.
            </p>
            
            <div className="bg-yellow-50 border border-yellow-200 rounded-md p-4 mb-4">
              <div className="flex">
                <div className="flex-shrink-0">
                  <CogIcon className="h-5 w-5 text-yellow-400" />
                </div>
                <div className="ml-3">
                  <h3 className="text-sm font-medium text-yellow-800">
                    Importante
                  </h3>
                  <div className="mt-2 text-sm text-yellow-700">
                    <ul className="list-disc pl-5 space-y-1">
                      <li>Nunca compartas tu API Key con nadie</li>
                      <li>La API Key se almacena solo en tu navegador</li>
                      <li>Asegúrate de que tu API Key tenga permisos de lectura</li>
                    </ul>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <form onSubmit={handleValidateApiKey} className="space-y-4">
            <div>
              <label htmlFor="apiKey" className="block text-sm font-medium text-gray-700">
                API Key
              </label>
              <input
                type="password"
                id="apiKey"
                value={apiKey}
                onChange={(e) => setApiKey(e.target.value)}
                className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-trading-blue focus:border-trading-blue"
                placeholder="Ingresa tu API Key de Trading212"
                required
              />
            </div>

            <div className="flex space-x-3">
              <button
                type="submit"
                disabled={loading || !apiKey}
                className="btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {loading ? 'Validando...' : 'Validar y Guardar'}
              </button>
              
              {apiKey && (
                <button
                  type="button"
                  onClick={handleClearApiKey}
                  className="btn-secondary"
                >
                  Limpiar
                </button>
              )}
            </div>
          </form>

          {message && (
            <div className={`text-sm p-3 rounded-md ${
              message.includes('Error') 
                ? 'bg-red-50 text-red-600' 
                : 'bg-green-50 text-green-600'
            }`}>
              {message}
            </div>
          )}
        </div>
      </div>

      {/* Instrucciones para obtener API Key */}
      <div className="card">
        <h3 className="text-lg font-medium text-gray-900 mb-4">
          ¿Cómo obtener tu API Key?
        </h3>
        <div className="space-y-3 text-sm text-gray-600">
          <div className="flex items-start space-x-3">
            <div className="flex-shrink-0 w-6 h-6 bg-trading-blue text-white rounded-full flex items-center justify-center text-xs font-medium">
              1
            </div>
            <div>
              <p className="font-medium text-gray-900">Accede a Trading212</p>
              <p>Inicia sesión en tu cuenta de Trading212</p>
            </div>
          </div>
          
          <div className="flex items-start space-x-3">
            <div className="flex-shrink-0 w-6 h-6 bg-trading-blue text-white rounded-full flex items-center justify-center text-xs font-medium">
              2
            </div>
            <div>
              <p className="font-medium text-gray-900">Ve a Configuración</p>
              <p>Busca la sección de API o configuración avanzada</p>
            </div>
          </div>
          
          <div className="flex items-start space-x-3">
            <div className="flex-shrink-0 w-6 h-6 bg-trading-blue text-white rounded-full flex items-center justify-center text-xs font-medium">
              3
            </div>
            <div>
              <p className="font-medium text-gray-900">Genera una API Key</p>
              <p>Crea una nueva API Key con permisos de lectura para tu portafolio</p>
            </div>
          </div>
          
          <div className="flex items-start space-x-3">
            <div className="flex-shrink-0 w-6 h-6 bg-trading-blue text-white rounded-full flex items-center justify-center text-xs font-medium">
              4
            </div>
            <div>
              <p className="font-medium text-gray-900">Copia y pega</p>
              <p>Copia la API Key y pégala en el campo de arriba</p>
            </div>
          </div>
        </div>
      </div>

      {/* Información adicional */}
      <div className="card">
        <h3 className="text-lg font-medium text-gray-900 mb-4">
          Información de la Aplicación
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
          <div>
            <span className="font-medium text-gray-900">Versión:</span>
            <span className="ml-2 text-gray-600">1.0.0</span>
          </div>
          <div>
            <span className="font-medium text-gray-900">Última actualización:</span>
            <span className="ml-2 text-gray-600">Enero 2024</span>
          </div>
          <div>
            <span className="font-medium text-gray-900">Backend:</span>
            <span className="ml-2 text-gray-600">Python/Flask</span>
          </div>
          <div>
            <span className="font-medium text-gray-900">Frontend:</span>
            <span className="ml-2 text-gray-600">React 18</span>
          </div>
        </div>
      </div>
    </div>
  );
}
