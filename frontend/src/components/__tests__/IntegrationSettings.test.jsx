import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import IntegrationSettings from '../IntegrationSettings';
import { ConfigContext } from '../../context/ConfigContext';

// Mock API service
vi.mock('../../services/api', () => ({
  updateIntegrationConfig: vi.fn(() => Promise.resolve({ success: true })),
  getIntegrationConfig: vi.fn(() => Promise.resolve({
    ghl: {
      enabled: true,
      api_key: 'test-api-key',
      location_id: 'test-location-id',
      base_url: 'https://rest.gohighlevel.com/v1/'
    },
    kickserv: {
      enabled: false,
      api_key: '',
      account_name: ''
    }
  }))
}));

describe('IntegrationSettings', () => {
  const mockSetConfig = vi.fn();
  const mockConfig = {
    integrations: {
      ghl: {
        enabled: true,
        api_key: 'test-api-key',
        location_id: 'test-location-id',
        base_url: 'https://rest.gohighlevel.com/v1/'
      },
      kickserv: {
        enabled: false,
        api_key: '',
        account_name: ''
      }
    }
  };

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders integration settings correctly', () => {
    render(
      <ConfigContext.Provider value={{ config: mockConfig, setConfig: mockSetConfig }}>
        <IntegrationSettings />
      </ConfigContext.Provider>
    );

    // Check if the component renders the integration sections
    expect(screen.getByText('Integration Settings')).toBeInTheDocument();
    expect(screen.getByText('Go High Level (GHL)')).toBeInTheDocument();
    expect(screen.getByText('Kickserv')).toBeInTheDocument();
    
    // Check if GHL settings are displayed correctly
    expect(screen.getByLabelText('Enable GHL Integration')).toBeChecked();
    expect(screen.getByLabelText('API Key')).toHaveValue('test-api-key');
    expect(screen.getByLabelText('Location ID')).toHaveValue('test-location-id');
    
    // Check if Kickserv settings are displayed correctly
    expect(screen.getByLabelText('Enable Kickserv Integration')).not.toBeChecked();
  });

  it('handles form input changes', async () => {
    render(
      <ConfigContext.Provider value={{ config: mockConfig, setConfig: mockSetConfig }}>
        <IntegrationSettings />
      </ConfigContext.Provider>
    );

    // Change GHL API Key
    const apiKeyInput = screen.getByLabelText('API Key');
    fireEvent.change(apiKeyInput, { target: { value: 'new-api-key' } });
    expect(apiKeyInput).toHaveValue('new-api-key');
    
    // Toggle Kickserv integration
    const kickservToggle = screen.getByLabelText('Enable Kickserv Integration');
    fireEvent.click(kickservToggle);
    expect(kickservToggle).toBeChecked();
    
    // Fill in Kickserv fields that should now be enabled
    const accountNameInput = screen.getByLabelText('Account Name');
    fireEvent.change(accountNameInput, { target: { value: 'test-account' } });
    expect(accountNameInput).toHaveValue('test-account');
  });

  it('submits the form with updated values', async () => {
    const { getByTestId } = render(
      <ConfigContext.Provider value={{ config: mockConfig, setConfig: mockSetConfig }}>
        <IntegrationSettings />
      </ConfigContext.Provider>
    );

    // Change GHL API Key
    const apiKeyInput = screen.getByLabelText('API Key');
    fireEvent.change(apiKeyInput, { target: { value: 'new-api-key' } });
    
    // Submit the form
    const saveButton = getByTestId('save-integration-settings');
    fireEvent.click(saveButton);
    
    // Wait for the form submission to complete
    await waitFor(() => {
      expect(mockSetConfig).toHaveBeenCalled();
    });
    
    // Check if the success message is displayed
    expect(screen.getByText('Settings saved successfully!')).toBeInTheDocument();
  });

  it('displays error message on form submission failure', async () => {
    // Mock API to return an error
    const apiModule = await import('../../services/api');
    apiModule.updateIntegrationConfig.mockRejectedValueOnce(new Error('API Error'));
    
    const { getByTestId } = render(
      <ConfigContext.Provider value={{ config: mockConfig, setConfig: mockSetConfig }}>
        <IntegrationSettings />
      </ConfigContext.Provider>
    );
    
    // Submit the form
    const saveButton = getByTestId('save-integration-settings');
    fireEvent.click(saveButton);
    
    // Wait for the form submission to complete
    await waitFor(() => {
      expect(screen.getByText('Error saving settings: API Error')).toBeInTheDocument();
    });
  });

  it('disables form fields when integration is disabled', () => {
    render(
      <ConfigContext.Provider value={{ config: mockConfig, setConfig: mockSetConfig }}>
        <IntegrationSettings />
      </ConfigContext.Provider>
    );
    
    // Kickserv is disabled by default, so its fields should be disabled
    expect(screen.getByLabelText('Account Name')).toBeDisabled();
    expect(screen.getByLabelText('Kickserv API Key')).toBeDisabled();
    
    // Disable GHL integration
    const ghlToggle = screen.getByLabelText('Enable GHL Integration');
    fireEvent.click(ghlToggle);
    
    // GHL fields should now be disabled
    expect(screen.getByLabelText('API Key')).toBeDisabled();
    expect(screen.getByLabelText('Location ID')).toBeDisabled();
  });
}); 