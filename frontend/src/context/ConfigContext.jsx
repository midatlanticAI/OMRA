import React, { createContext, useState, useContext, useEffect } from 'react';
import axios from 'axios';

const ConfigContext = createContext(null);

export const useConfig = () => {
  const context = useContext(ConfigContext);
  if (!context) {
    throw new Error('useConfig must be used within a ConfigProvider');
  }
  return context;
};

export const ConfigProvider = ({ children }) => {
  const [config, setConfig] = useState({
    integrations: {
      ghl: {
        enabled: false,
        connected: false
      },
      kickserv: {
        enabled: false,
        connected: false
      }
    },
    notifications: {
      email: true,
      sms: false,
      pushNotifications: false
    },
    theme: {
      mode: 'light',
      primaryColor: '#1976d2'
    }
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchConfig = async () => {
      try {
        const response = await axios.get('/api/config');
        setConfig(response.data);
        setError(null);
      } catch (err) {
        console.error('Failed to fetch configuration:', err);
        setError('Failed to load application configuration');
      } finally {
        setLoading(false);
      }
    };

    fetchConfig();
  }, []);

  const updateConfig = async (newConfig) => {
    try {
      setLoading(true);
      const response = await axios.put('/api/config', newConfig);
      setConfig(response.data);
      setError(null);
      return true;
    } catch (err) {
      console.error('Failed to update configuration:', err);
      setError('Failed to update application configuration');
      return false;
    } finally {
      setLoading(false);
    }
  };

  const updateIntegrationStatus = async (integration, status) => {
    try {
      setLoading(true);
      const response = await axios.put(`/api/integrations/${integration}/status`, { status });
      
      // Update only the relevant integration in the config
      setConfig(prevConfig => ({
        ...prevConfig,
        integrations: {
          ...prevConfig.integrations,
          [integration]: response.data
        }
      }));
      
      setError(null);
      return true;
    } catch (err) {
      console.error(`Failed to update ${integration} status:`, err);
      setError(`Failed to update ${integration} integration status`);
      return false;
    } finally {
      setLoading(false);
    }
  };

  const value = {
    config,
    loading,
    error,
    updateConfig,
    updateIntegrationStatus
  };

  return <ConfigContext.Provider value={value}>{children}</ConfigContext.Provider>;
};

export default ConfigContext; 