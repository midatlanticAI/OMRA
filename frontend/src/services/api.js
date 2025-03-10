import axios from 'axios';

// Create an axios instance with default config
const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000/api',
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000, // 10 seconds
});

// Security headers to protect against common attacks
api.interceptors.request.use(config => {
  config.headers['X-Content-Type-Options'] = 'nosniff';
  config.headers['X-Frame-Options'] = 'DENY';
  config.headers['X-XSS-Protection'] = '1; mode=block';
  config.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains';
  return config;
});

// Response interceptor for global error handling
api.interceptors.response.use(
  response => {
    // Sanitize data if needed before returning
    return response;
  },
  error => {
    const { response } = error;
    
    // Log errors but prevent sensitive info from being exposed
    if (response) {
      const sanitizedError = {
        status: response.status,
        statusText: response.statusText,
        url: response.config.url.replace(/\/\/[^\/]+/, ''), // Remove domain for security
        method: response.config.method.toUpperCase(),
      };
      
      // Don't log credentials or tokens
      console.error('API Error:', sanitizedError);
      
      // Handle specific error status codes
      switch (response.status) {
        case 400: // Bad Request
          error.userMessage = 'The request could not be processed. Please check your input.';
          break;
        case 401: // Unauthorized
          error.userMessage = 'Your session has expired. Please log in again.';
          // The auth interceptor will handle token refresh or logout
          break;
        case 403: // Forbidden
          error.userMessage = 'You do not have permission to access this resource.';
          break;
        case 404: // Not Found
          error.userMessage = 'The requested resource was not found.';
          break;
        case 429: // Too Many Requests
          error.userMessage = 'Too many requests. Please try again later.';
          break;
        case 500: // Server Error
        case 502: // Bad Gateway
        case 503: // Service Unavailable
          error.userMessage = 'A server error occurred. Please try again later.';
          break;
        default:
          error.userMessage = 'An unexpected error occurred. Please try again.';
      }
    } else {
      // Network error or CORS issue
      console.error('Network Error:', error.message);
      error.userMessage = 'Unable to connect to the server. Please check your internet connection.';
    }
    
    return Promise.reject(error);
  }
);

// Customer API methods
const customersAPI = {
  getAll: async (params = {}) => {
    return api.get('/customers', { params });
  },
  
  getById: async (id) => {
    return api.get(`/customers/${id}`);
  },
  
  create: async (customerData) => {
    return api.post('/customers', customerData);
  },
  
  update: async (id, customerData) => {
    return api.put(`/customers/${id}`, customerData);
  },
  
  delete: async (id) => {
    return api.delete(`/customers/${id}`);
  },
  
  syncWithGHL: async (customerId) => {
    return api.post(`/integrations/ghl/contacts`, { customer_id: customerId });
  }
};

// Service Requests API methods
const serviceRequestsAPI = {
  getAll: async (params = {}) => {
    return api.get('/service-requests', { params });
  },
  
  getById: async (id) => {
    return api.get(`/service-requests/${id}`);
  },
  
  create: async (requestData) => {
    return api.post('/service-requests', requestData);
  },
  
  update: async (id, requestData) => {
    return api.put(`/service-requests/${id}`, requestData);
  },
  
  delete: async (id) => {
    return api.delete(`/service-requests/${id}`);
  },
  
  createGHLOpportunity: async (serviceRequestId) => {
    return api.post(`/integrations/ghl/opportunities`, { service_request_id: serviceRequestId });
  }
};

// Appointments API methods
const appointmentsAPI = {
  getAll: async (params = {}) => {
    return api.get('/appointments', { params });
  },
  
  getById: async (id) => {
    return api.get(`/appointments/${id}`);
  },
  
  create: async (appointmentData) => {
    return api.post('/appointments', appointmentData);
  },
  
  update: async (id, appointmentData) => {
    return api.put(`/appointments/${id}`, appointmentData);
  },
  
  delete: async (id) => {
    return api.delete(`/appointments/${id}`);
  },
  
  createGHLAppointment: async (appointmentData) => {
    return api.post(`/integrations/ghl/appointments`, appointmentData);
  }
};

// Authentication API methods
const authAPI = {
  login: async (credentials) => {
    return api.post('/auth/token', credentials);
  },
  
  logout: async () => {
    return api.post('/auth/logout');
  },
  
  refreshToken: async () => {
    return api.post('/auth/refresh');
  },
  
  getCurrentUser: async () => {
    return api.get('/auth/me');
  }
};

export { customersAPI, serviceRequestsAPI, appointmentsAPI, authAPI }; 