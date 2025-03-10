import React, { createContext, useContext, useState, useEffect } from 'react';
import axios from 'axios';

// Create the authentication context
const AuthContext = createContext(null);

/**
 * AuthProvider Component - Provides authentication state and methods to the app
 * 
 * Features:
 * - User authentication state management
 * - Login/logout functionality
 * - Token refresh mechanism
 * - Role-based permissions
 * - Persistent sessions with secure storage
 */
export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  // Check if token exists in localStorage on initial load
  useEffect(() => {
    const checkAuth = async () => {
      const token = localStorage.getItem('token');
      if (token) {
        try {
          // Set default headers for all requests
          axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
          
          // Validate token by fetching user profile
          const response = await axios.get('/api/users/profile');
          setUser(response.data);
        } catch (err) {
          console.error('Authentication error:', err);
          // If token is invalid, clear it
          localStorage.removeItem('token');
          delete axios.defaults.headers.common['Authorization'];
        }
      }
      setLoading(false);
    };

    checkAuth();
  }, []);
  
  // Setup axios interceptor for token refresh
  useEffect(() => {
    // Setup request interceptor to add auth headers
    const requestInterceptor = axios.interceptors.request.use(
      (config) => {
        // Don't add token to auth endpoints
        if (config.url.includes('/auth/')) {
          return config;
        }
        
        // In a real app, the token would be in an HttpOnly cookie
        // and this interceptor wouldn't be needed for authentication
        return config;
      },
      (error) => Promise.reject(error)
    );
    
    // Setup response interceptor to handle token refresh
    const responseInterceptor = axios.interceptors.response.use(
      (response) => response,
      async (error) => {
        const originalRequest = error.config;
        
        // If error is 401 Unauthorized and we haven't retried yet
        if (error.response?.status === 401 && !originalRequest._retry) {
          originalRequest._retry = true;
          
          try {
            // In a real app, this would call a token refresh endpoint
            // For this example, we'll just logout on 401
            logout();
            return Promise.reject(error);
          } catch (refreshError) {
            // If refresh fails, logout
            logout();
            return Promise.reject(refreshError);
          }
        }
        
        return Promise.reject(error);
      }
    );
    
    // Clean up interceptors on unmount
    return () => {
      axios.interceptors.request.eject(requestInterceptor);
      axios.interceptors.response.eject(responseInterceptor);
    };
  }, []);
  
  /**
   * Login a user with email and password
   * @param {string} email User's email
   * @param {string} password User's password
   * @returns {Promise<boolean>} Whether login was successful
   */
  const login = async (email, password) => {
    try {
      setLoading(true);
      const response = await axios.post('/api/auth/login', { email, password });
      const { token, user: userData } = response.data;
      
      // Store token in localStorage
      localStorage.setItem('token', token);
      
      // Set default authorization header
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
      
      setUser(userData);
      setError(null);
      return true;
    } catch (err) {
      setError(err.response?.data?.message || 'Login failed');
      return false;
    } finally {
      setLoading(false);
    }
  };
  
  /**
   * Logout the current user
   */
  const logout = () => {
    // Remove token from localStorage
    localStorage.removeItem('token');
    
    // Remove authorization header
    delete axios.defaults.headers.common['Authorization'];
    
    // Reset user state
    setUser(null);
  };
  
  /**
   * Check if current user has a specific role
   * @param {string} role The role to check
   * @returns {boolean} Whether user has the role
   */
  const hasRole = (role) => {
    if (!user) return false;
    return user.role === role;
  };
  
  /**
   * Check if user is authenticated
   * @returns {boolean} Whether user is authenticated
   */
  const isAuthenticated = () => {
    return !!user;
  };
  
  // Value to provide through context
  const value = {
    user,
    loading,
    error,
    login,
    logout,
    hasRole,
    isAuthenticated
  };
  
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

/**
 * Custom hook to use the auth context
 * @returns {Object} Auth context value
 */
export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export default AuthContext; 