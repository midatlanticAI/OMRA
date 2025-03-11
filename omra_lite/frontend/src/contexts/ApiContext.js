import React, { createContext, useState, useEffect } from 'react';
import axios from 'axios';

// Create a context with default values
export const ApiContext = createContext({
  api: null,
  isAuthenticated: false,
  user: null,
  login: () => {},
  logout: () => {},
});

export const ApiProvider = ({ children }) => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [user, setUser] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  // Create an axios instance with consistent configuration
  const api = axios.create({
    baseURL: '/api',
    headers: {
      'Content-Type': 'application/json',
    },
  });

  // Add authentication interceptor
  api.interceptors.request.use(
    (config) => {
      const token = localStorage.getItem('token');
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    },
    (error) => Promise.reject(error)
  );

  // Authentication functions
  const login = async (username, password) => {
    try {
      const response = await axios.post('/token', new URLSearchParams({
        username,
        password,
      }), {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
      });

      const { access_token } = response.data;
      localStorage.setItem('token', access_token);
      setIsAuthenticated(true);
      
      // Get user info
      await getCurrentUser();
      
      return { success: true };
    } catch (error) {
      console.error('Login failed', error);
      return {
        success: false,
        error: error.response?.data?.detail || 'Login failed',
      };
    }
  };

  const logout = () => {
    localStorage.removeItem('token');
    setIsAuthenticated(false);
    setUser(null);
  };

  const getCurrentUser = async () => {
    try {
      const response = await api.get('/users/me');
      setUser(response.data);
      setIsAuthenticated(true);
      return response.data;
    } catch (error) {
      console.error('Failed to get current user', error);
      setIsAuthenticated(false);
      setUser(null);
      return null;
    }
  };

  // Check authentication status on initial load
  useEffect(() => {
    const checkAuth = async () => {
      setIsLoading(true);
      
      const token = localStorage.getItem('token');
      if (token) {
        try {
          await getCurrentUser();
        } catch (error) {
          console.error('Token validation failed', error);
          logout();
        }
      }
      
      setIsLoading(false);
    };

    checkAuth();
  }, [getCurrentUser]);

  // Context value
  const contextValue = {
    api,
    isAuthenticated,
    user,
    login,
    logout,
    isLoading,
  };

  return (
    <ApiContext.Provider value={contextValue}>
      {children}
    </ApiContext.Provider>
  );
}; 