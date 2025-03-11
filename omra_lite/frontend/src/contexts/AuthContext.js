import React, { createContext, useContext, useState, useEffect } from 'react';
import axios from 'axios';

// Set base URL for API requests
axios.defaults.baseURL = 'http://localhost:8000';
console.log('Axios configured with base URL:', axios.defaults.baseURL);

// Create the context
const AuthContext = createContext();

// Custom hook to use the auth context
export const useAuth = () => useContext(AuthContext);

// Provider component
export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(localStorage.getItem('token'));
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Configure axios
  useEffect(() => {
    if (token) {
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
    } else {
      delete axios.defaults.headers.common['Authorization'];
    }
  }, [token]);

  // Check if user is authenticated on initial load
  useEffect(() => {
    const verifyToken = async () => {
      if (!token) {
        setLoading(false);
        return;
      }

      try {
        console.log('Verifying token...');
        
        // Ensure the Authorization header is set
        axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
        
        const response = await axios.get('/users/me');
        console.log('User data received:', response.data);
        
        if (!response.data || !response.data.username) {
          console.error('Invalid user data received:', response.data);
          throw new Error('Invalid user data received');
        }
        
        setUser(response.data);
        setIsAuthenticated(true);
        setError(null);
      } catch (err) {
        console.error('Error verifying token:', err);
        console.error('Error details:', err.response?.data || err.message);
        
        // Clear authentication state
        setUser(null);
        setToken(null);
        setIsAuthenticated(false);
        localStorage.removeItem('token');
        delete axios.defaults.headers.common['Authorization'];
      } finally {
        setLoading(false);
      }
    };

    verifyToken();
  }, [token]);

  // Login function
  const login = async (username, password) => {
    setLoading(true);
    setError(null);

    console.log('Starting login process...');
    console.log('Axios base URL:', axios.defaults.baseURL || 'Not set, using relative URLs');

    try {
      console.log('Preparing login credentials');
      
      // Use URLSearchParams for proper form encoding
      const params = new URLSearchParams();
      params.append('username', username);
      params.append('password', password);
      
      console.log('Sending login request to /token endpoint with credentials:', username);
      
      // Make the token request with explicit debugging
      const response = await axios.post('/token', params, {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded'
        },
        // Add this to see the full request details for debugging
        validateStatus: function (status) {
          console.log('Response status:', status);
          return true; // don't reject any status code
        }
      });
      
      console.log('Login response received:', response.status, response.statusText);
      console.log('Response data:', response.data);
      
      // Handle non-200 responses explicitly
      if (response.status !== 200) {
        console.error('Error response:', response.data);
        throw new Error(`Login failed with status ${response.status}: ${response.statusText}`);
      }
      
      const { access_token } = response.data;
      if (!access_token) {
        console.error('No access token in response:', response.data);
        throw new Error('No access token received');
      }

      console.log('Storing token in localStorage');
      localStorage.setItem('token', access_token);
      setToken(access_token);
      
      // Set the Authorization header for subsequent requests
      axios.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;
      console.log('Set Authorization header for future requests');

      // Fetch user data
      console.log('Fetching user data...');
      const userResponse = await axios.get('/users/me', {
        headers: {
          'Authorization': `Bearer ${access_token}`
        }
      });
      console.log('User data received:', userResponse.data);
      
      setUser(userResponse.data);
      setIsAuthenticated(true);

      return { success: true };
    } catch (err) {
      console.error('Login error:', err);
      console.error('Error message:', err.message);
      
      if (err.response) {
        console.error('Error response status:', err.response.status);
        console.error('Error response data:', err.response.data);
        console.error('Error response headers:', err.response.headers);
      } else if (err.request) {
        console.error('No response received. Request details:', err.request);
      } else {
        console.error('Error setting up request:', err.message);
      }
      
      setError(
        err.response?.data?.detail || 
        err.message || 
        'Failed to login. Please check your credentials.'
      );
      return { 
        success: false, 
        error: err.response?.data?.detail || err.message || 'Login failed'
      };
    } finally {
      setLoading(false);
    }
  };

  // Logout function
  const logout = () => {
    localStorage.removeItem('token');
    setToken(null);
    setUser(null);
    setIsAuthenticated(false);
    delete axios.defaults.headers.common['Authorization'];
  };

  // Context value
  const value = {
    user,
    token,
    isAuthenticated,
    loading,
    error,
    login,
    logout
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}; 