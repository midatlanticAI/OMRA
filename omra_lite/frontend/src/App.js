import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { Box, CircularProgress } from '@mui/material';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import Customers from './pages/Customers';
import ServiceRequests from './pages/ServiceRequests';
import Technicians from './pages/Technicians';
import Agents from './pages/Agents';
import AgentDocs from './pages/AgentDocs';
import Settings from './pages/Settings';
import Smartlists from './pages/Smartlists';
import Layout from './components/Layout';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import { ApiProvider } from './contexts/ApiContext';
import { AiAssistantProvider } from './contexts/AiAssistantContext';
import AiAssistant from './components/AiAssistant';

// Protected route wrapper
const ProtectedRoute = ({ children }) => {
  const { isAuthenticated, loading } = useAuth();

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>
        <CircularProgress />
      </Box>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" />;
  }

  return children;
};

function AppRoutes() {
  const { isAuthenticated } = useAuth();

  return (
    <Routes>
      <Route path="/login" element={!isAuthenticated ? <Login /> : <Navigate to="/" />} />
      
      <Route path="/" element={<ProtectedRoute><Layout /></ProtectedRoute>}>
        <Route index element={<Dashboard />} />
        <Route path="customers" element={<Customers />} />
        <Route path="service-requests" element={<ServiceRequests />} />
        <Route path="technicians" element={<Technicians />} />
        <Route path="agents" element={<Agents />} />
        <Route path="agent-docs" element={<AgentDocs />} />
        <Route path="smartlists" element={<Smartlists />} />
        <Route path="settings" element={<Settings />} />
      </Route>
      
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

// Wrapper to add the AI Assistant in protected routes only
const ProtectedContent = ({ children }) => {
  const { isAuthenticated } = useAuth();
  
  return (
    <>
      {children}
      {isAuthenticated && <AiAssistant />}
    </>
  );
};

function App() {
  return (
    <AuthProvider>
      <ApiProvider>
        <AiAssistantProvider>
          <ProtectedContent>
            <AppRoutes />
          </ProtectedContent>
        </AiAssistantProvider>
      </ApiProvider>
    </AuthProvider>
  );
}

export default App; 