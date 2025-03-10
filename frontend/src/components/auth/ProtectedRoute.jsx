import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';

/**
 * ProtectedRoute Component - Secures routes by checking authentication status.
 * 
 * Features:
 * - Redirects unauthenticated users to login
 * - Preserves the original requested URL for redirect after login
 * - Supports role-based access control
 * 
 * @param {Object} props Component props
 * @param {Function} props.authCheck Function that returns whether user is authenticated
 * @param {React.ReactNode} props.children Children components to render if authenticated
 * @param {string[]} [props.requiredRoles] Optional array of roles allowed to access this route
 * @param {Function} [props.hasRole] Optional function to check if user has the required role
 */
const ProtectedRoute = ({ 
  authCheck,
  children, 
  requiredRoles,
  hasRole
}) => {
  const location = useLocation();
  
  // Get authentication status
  const isAuthenticated = authCheck();
  
  // If not authenticated, redirect to login
  if (!isAuthenticated) {
    // Redirect to login, preserving the intended destination
    return <Navigate to="/login" state={{ from: location }} replace />;
  }
  
  // Check role-based access if requiredRoles is provided
  if (requiredRoles && requiredRoles.length > 0) {
    // Make sure we have a role-checking function
    if (!hasRole || typeof hasRole !== 'function') {
      console.error('hasRole function is required when using requiredRoles');
      return <Navigate to="/unauthorized" replace />;
    }
    
    // Check if user has at least one of the required roles
    const hasRequiredRole = requiredRoles.some(role => hasRole(role));
    
    if (!hasRequiredRole) {
      return <Navigate to="/unauthorized" replace />;
    }
  }
  
  // User is authenticated and has required role (if specified)
  return children;
};

export default ProtectedRoute; 