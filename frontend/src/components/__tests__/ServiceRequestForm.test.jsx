import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { vi } from 'vitest';
import ServiceRequestForm from '../ServiceRequestForm';

describe('ServiceRequestForm Component', () => {
  beforeEach(() => {
    // Mock implementations if needed
    vi.spyOn(console, 'error').mockImplementation(() => {});
    global.fetch = vi.fn();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  test('renders form elements correctly', () => {
    render(<ServiceRequestForm />);
    
    // Check for form header
    expect(screen.getByText('Create Service Request')).toBeInTheDocument();
    
    // Check for key form elements
    expect(screen.getByLabelText(/Customer/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Appliance Type/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Brand/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Priority/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Problem Description/i)).toBeInTheDocument();
    
    // Check for buttons
    expect(screen.getByRole('button', { name: /Clear Form/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Create Service Request/i })).toBeInTheDocument();
  });

  test('shows validation errors when submitting empty form', async () => {
    const user = userEvent.setup();
    render(<ServiceRequestForm />);
    
    // Submit the form without filling it
    await user.click(screen.getByRole('button', { name: /Create Service Request/i }));
    
    // Check for validation errors
    await waitFor(() => {
      expect(screen.getByText(/Please select a customer/i)).toBeInTheDocument();
      expect(screen.getByText(/Appliance type is required/i)).toBeInTheDocument();
      expect(screen.getByText(/Brand is required/i)).toBeInTheDocument();
      expect(screen.getByText(/Description is required/i)).toBeInTheDocument();
      expect(screen.getByText(/Select at least one symptom/i)).toBeInTheDocument();
    });
  });

  test('enables symptom selection when appliance type is selected', async () => {
    const user = userEvent.setup();
    render(<ServiceRequestForm />);
    
    // Initially, the symptoms field should be disabled
    expect(screen.getByLabelText(/Symptoms/i)).toBeDisabled();
    
    // Select an appliance type
    await user.click(screen.getByLabelText(/Appliance Type/i));
    await user.click(screen.getByText('Refrigerator'));
    
    // Symptoms field should now be enabled
    await waitFor(() => {
      expect(screen.getByLabelText(/Symptoms/i)).not.toBeDisabled();
    });
  });

  test('clears form when Clear Form button is clicked', async () => {
    const user = userEvent.setup();
    render(<ServiceRequestForm />);
    
    // Fill some form fields
    await user.click(screen.getByLabelText(/Appliance Type/i));
    await user.click(screen.getByText('Refrigerator'));
    
    await user.type(screen.getByLabelText(/Brand/i), 'Samsung');
    await user.type(screen.getByLabelText(/Problem Description/i), 'Not cooling properly');
    
    // Click Clear Form button
    await user.click(screen.getByRole('button', { name: /Clear Form/i }));
    
    // Check if form is cleared
    await waitFor(() => {
      expect(screen.getByLabelText(/Brand/i)).toHaveValue('');
      expect(screen.getByLabelText(/Problem Description/i)).toHaveValue('');
    });
  });
}); 