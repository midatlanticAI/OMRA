import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import axios from 'axios';
import * as api from '../api';

// Mock axios
vi.mock('axios');

describe('API Service', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  afterEach(() => {
    localStorage.clear();
  });

  describe('Authentication', () => {
    it('login should make a POST request and store token', async () => {
      const mockResponse = {
        data: {
          access_token: 'test-token',
          token_type: 'bearer',
          user: { id: 1, username: 'testuser', role: 'admin' }
        }
      };
      axios.post.mockResolvedValueOnce(mockResponse);

      const credentials = { username: 'testuser', password: 'password' };
      const result = await api.login(credentials);

      expect(axios.post).toHaveBeenCalledWith('/api/auth/login', credentials);
      expect(result).toEqual(mockResponse.data);
      expect(localStorage.getItem('token')).toBe('test-token');
      expect(localStorage.getItem('user')).toBe(JSON.stringify(mockResponse.data.user));
    });

    it('logout should clear localStorage', async () => {
      // Setup localStorage with token and user
      localStorage.setItem('token', 'test-token');
      localStorage.setItem('user', JSON.stringify({ id: 1, username: 'testuser' }));

      await api.logout();

      expect(localStorage.getItem('token')).toBeNull();
      expect(localStorage.getItem('user')).toBeNull();
    });

    it('getCurrentUser should return user from localStorage', () => {
      const mockUser = { id: 1, username: 'testuser', role: 'admin' };
      localStorage.setItem('user', JSON.stringify(mockUser));

      const result = api.getCurrentUser();

      expect(result).toEqual(mockUser);
    });

    it('getCurrentUser should return null if no user in localStorage', () => {
      const result = api.getCurrentUser();
      expect(result).toBeNull();
    });

    it('isAuthenticated should return true if token exists', () => {
      localStorage.setItem('token', 'test-token');
      expect(api.isAuthenticated()).toBe(true);
    });

    it('isAuthenticated should return false if no token exists', () => {
      expect(api.isAuthenticated()).toBe(false);
    });
  });

  describe('Customers API', () => {
    it('getCustomers should make a GET request', async () => {
      const mockCustomers = [
        { id: 1, first_name: 'John', last_name: 'Doe' },
        { id: 2, first_name: 'Jane', last_name: 'Smith' }
      ];
      axios.get.mockResolvedValueOnce({ data: mockCustomers });

      const result = await api.getCustomers();

      expect(axios.get).toHaveBeenCalledWith('/api/customers/');
      expect(result).toEqual(mockCustomers);
    });

    it('getCustomer should make a GET request with ID', async () => {
      const mockCustomer = { id: 1, first_name: 'John', last_name: 'Doe' };
      axios.get.mockResolvedValueOnce({ data: mockCustomer });

      const result = await api.getCustomer(1);

      expect(axios.get).toHaveBeenCalledWith('/api/customers/1');
      expect(result).toEqual(mockCustomer);
    });

    it('createCustomer should make a POST request', async () => {
      const newCustomer = { first_name: 'New', last_name: 'Customer' };
      const mockResponse = { id: 3, ...newCustomer };
      axios.post.mockResolvedValueOnce({ data: mockResponse });

      const result = await api.createCustomer(newCustomer);

      expect(axios.post).toHaveBeenCalledWith('/api/customers/', newCustomer);
      expect(result).toEqual(mockResponse);
    });

    it('updateCustomer should make a PATCH request', async () => {
      const updatedData = { first_name: 'Updated' };
      const mockResponse = { id: 1, first_name: 'Updated', last_name: 'Doe' };
      axios.patch.mockResolvedValueOnce({ data: mockResponse });

      const result = await api.updateCustomer(1, updatedData);

      expect(axios.patch).toHaveBeenCalledWith('/api/customers/1', updatedData);
      expect(result).toEqual(mockResponse);
    });

    it('deleteCustomer should make a DELETE request', async () => {
      axios.delete.mockResolvedValueOnce({ status: 204 });

      await api.deleteCustomer(1);

      expect(axios.delete).toHaveBeenCalledWith('/api/customers/1');
    });
  });

  describe('Service Requests API', () => {
    it('getServiceRequests should make a GET request', async () => {
      const mockRequests = [
        { id: 1, customer_id: 1, appliance_type: 'Refrigerator' },
        { id: 2, customer_id: 2, appliance_type: 'Dishwasher' }
      ];
      axios.get.mockResolvedValueOnce({ data: mockRequests });

      const result = await api.getServiceRequests();

      expect(axios.get).toHaveBeenCalledWith('/api/service-requests/');
      expect(result).toEqual(mockRequests);
    });

    it('getCustomerServiceRequests should make a GET request with customer ID', async () => {
      const mockRequests = [
        { id: 1, customer_id: 1, appliance_type: 'Refrigerator' }
      ];
      axios.get.mockResolvedValueOnce({ data: mockRequests });

      const result = await api.getCustomerServiceRequests(1);

      expect(axios.get).toHaveBeenCalledWith('/api/customers/1/service-requests');
      expect(result).toEqual(mockRequests);
    });
  });

  describe('Integration API', () => {
    it('syncCustomerWithGHL should make a POST request', async () => {
      const mockResponse = { success: true, ghl_contact_id: 'ghl_123' };
      axios.post.mockResolvedValueOnce({ data: mockResponse });

      const result = await api.syncCustomerWithGHL(1);

      expect(axios.post).toHaveBeenCalledWith('/api/integrations/ghl/sync-contact/1');
      expect(result).toEqual(mockResponse);
    });

    it('createGHLOpportunity should make a POST request with data', async () => {
      const opportunityData = { pipeline_id: 'pipe_123', stage_id: 'stage_456' };
      const mockResponse = { success: true, opportunity_id: 'opp_123' };
      axios.post.mockResolvedValueOnce({ data: mockResponse });

      const result = await api.createGHLOpportunity(1, opportunityData);

      expect(axios.post).toHaveBeenCalledWith('/api/integrations/ghl/create-opportunity/1', opportunityData);
      expect(result).toEqual(mockResponse);
    });

    it('getIntegrationConfig should make a GET request', async () => {
      const mockConfig = {
        ghl: { enabled: true, api_key: 'test-key' },
        kickserv: { enabled: false }
      };
      axios.get.mockResolvedValueOnce({ data: mockConfig });

      const result = await api.getIntegrationConfig();

      expect(axios.get).toHaveBeenCalledWith('/api/config/integrations');
      expect(result).toEqual(mockConfig);
    });

    it('updateIntegrationConfig should make a PUT request with config data', async () => {
      const configData = {
        ghl: { enabled: true, api_key: 'new-key' },
        kickserv: { enabled: true, api_key: 'kickserv-key' }
      };
      const mockResponse = { success: true };
      axios.put.mockResolvedValueOnce({ data: mockResponse });

      const result = await api.updateIntegrationConfig(configData);

      expect(axios.put).toHaveBeenCalledWith('/api/config/integrations', configData);
      expect(result).toEqual(mockResponse);
    });
  });

  describe('Error handling', () => {
    it('should handle API errors', async () => {
      const errorResponse = {
        response: {
          status: 400,
          data: { detail: 'Bad request' }
        }
      };
      axios.get.mockRejectedValueOnce(errorResponse);

      await expect(api.getCustomers()).rejects.toThrow('Bad request');
    });

    it('should handle network errors', async () => {
      axios.get.mockRejectedValueOnce(new Error('Network Error'));

      await expect(api.getCustomers()).rejects.toThrow('Network Error');
    });
  });
}); 