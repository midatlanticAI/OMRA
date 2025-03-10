import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import { vi } from 'vitest';
import Dashboard from '../Dashboard';

// Mock the recharts components since they use canvas which isn't available in jsdom
vi.mock('recharts', () => {
  const OriginalModule = vi.importActual('recharts');
  return {
    ...OriginalModule,
    ResponsiveContainer: ({ children }) => (
      <div data-testid="responsive-container">{children}</div>
    ),
    BarChart: ({ children }) => <div data-testid="bar-chart">{children}</div>,
    Bar: ({ dataKey }) => <div data-testid={`bar-${dataKey}`} />,
    XAxis: () => <div data-testid="x-axis" />,
    YAxis: () => <div data-testid="y-axis" />,
    CartesianGrid: () => <div data-testid="cartesian-grid" />,
    Tooltip: () => <div data-testid="tooltip" />,
    Legend: () => <div data-testid="legend" />
  };
});

describe('Dashboard Component', () => {
  beforeEach(() => {
    // Mock fetch or axios calls if needed
    global.fetch = vi.fn();
  });

  afterEach(() => {
    vi.resetAllMocks();
  });

  test('renders loading state initially', () => {
    render(<Dashboard />);
    expect(screen.getByRole('progressbar')).toBeInTheDocument();
  });

  test('renders dashboard content after loading', async () => {
    render(<Dashboard />);
    
    // Wait for loading to complete
    await waitFor(() => {
      expect(screen.queryByRole('progressbar')).not.toBeInTheDocument();
    });
    
    // Check for main dashboard elements
    expect(screen.getByText('Dashboard')).toBeInTheDocument();
    expect(screen.getByText('Monthly Revenue')).toBeInTheDocument();
    expect(screen.getByText('Upcoming Appointments')).toBeInTheDocument();
    
    // Check for summary cards
    expect(screen.getByText('Pending Service Requests')).toBeInTheDocument();
    expect(screen.getByText("Today's Appointments")).toBeInTheDocument();
    expect(screen.getByText('Active Workflows')).toBeInTheDocument();
    expect(screen.getByText("This Month's Revenue")).toBeInTheDocument();
  });

  test('renders chart components', async () => {
    render(<Dashboard />);
    
    await waitFor(() => {
      expect(screen.queryByRole('progressbar')).not.toBeInTheDocument();
    });
    
    expect(screen.getByTestId('responsive-container')).toBeInTheDocument();
    expect(screen.getByTestId('bar-chart')).toBeInTheDocument();
    expect(screen.getByTestId('bar-amount')).toBeInTheDocument();
  });
}); 