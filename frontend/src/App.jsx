import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';

// Theme
import theme from './theme';

// Context Providers
import { AuthProvider } from './context/AuthContext';
import { ConfigProvider } from './context/ConfigContext';

// Components
import Layout from './components/Layout';
import ProtectedRoute from './components/ProtectedRoute';

// Pages
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import Customers from './pages/Customers';
import CustomerDetail from './pages/CustomerDetail';
import ServiceRequests from './pages/ServiceRequests';
import ServiceRequestDetail from './pages/ServiceRequestDetail';
import Integrations from './pages/Integrations';
import Settings from './pages/Settings';
import NotFound from './pages/NotFound';

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <AuthProvider>
        <ConfigProvider>
          <Router>
            <Routes>
              <Route path="/login" element={<Login />} />
              
              <Route path="/" element={<ProtectedRoute><Layout /></ProtectedRoute>}>
                <Route index element={<Navigate to="/dashboard" replace />} />
                <Route path="dashboard" element={<Dashboard />} />
                <Route path="customers" element={<Customers />} />
                <Route path="customers/:id" element={<CustomerDetail />} />
                <Route path="service-requests" element={<ServiceRequests />} />
                <Route path="service-requests/:id" element={<ServiceRequestDetail />} />
                <Route path="integrations" element={<Integrations />} />
                <Route path="settings" element={<Settings />} />
              </Route>
              
              <Route path="*" element={<NotFound />} />
            </Routes>
          </Router>
        </ConfigProvider>
      </AuthProvider>
    </ThemeProvider>
  );
}

export default App; 