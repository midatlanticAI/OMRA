import React, { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import {
  Box,
  Button,
  TextField,
  Typography,
  Link,
  Paper,
  CircularProgress,
  Alert,
  InputAdornment,
  IconButton,
  Container
} from '@mui/material';
import {
  Visibility as VisibilityIcon,
  VisibilityOff as VisibilityOffIcon,
  LockOutlined as LockIcon
} from '@mui/icons-material';
import { useFormik } from 'formik';
import * as Yup from 'yup';
import axios from 'axios';

// Simulate a basic CSRF token - In a real app, this would be provided by the server
const getCsrfToken = () => {
  return Math.random().toString(36).substring(2);
};

const LoginForm = ({ onLogin }) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [csrfToken] = useState(getCsrfToken());
  const [loginAttempts, setLoginAttempts] = useState(0);
  const [isLocked, setIsLocked] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();

  // Max login attempts before temporary lockout
  const MAX_LOGIN_ATTEMPTS = 5;
  
  // Validation schema with strong password requirements
  const validationSchema = Yup.object({
    username: Yup.string()
      .required('Username is required')
      .min(4, 'Username must be at least 4 characters')
      .max(30, 'Username must be at most 30 characters')
      .matches(/^[a-zA-Z0-9_.-]+$/, 'Username can only contain letters, numbers, and the characters _.-'),
    password: Yup.string()
      .required('Password is required')
      .min(8, 'Password must be at least 8 characters')
  });

  const formik = useFormik({
    initialValues: {
      username: '',
      password: ''
    },
    validationSchema,
    onSubmit: async (values) => {
      if (isLocked) {
        setError('Account is temporarily locked. Please try again later.');
        return;
      }

      setError('');
      setLoading(true);

      try {
        // In a real app, this would be an API call
        const response = await mockLoginAPI(values.username, values.password, csrfToken);
        
        if (response.success) {
          // Reset login attempts on successful login
          setLoginAttempts(0);
          
          // Store the token in a secure, HttpOnly cookie (handled by backend)
          // Store only non-sensitive user data in localStorage
          localStorage.setItem('user', JSON.stringify({
            username: response.user.username,
            fullName: response.user.fullName,
            role: response.user.role
          }));
          
          // Call the onLogin callback
          if (onLogin) onLogin(response.user);
          
          // Redirect to the intended page or dashboard
          const from = location.state?.from?.pathname || '/';
          navigate(from, { replace: true });
        } else {
          throw new Error(response.message);
        }
      } catch (err) {
        const newAttempts = loginAttempts + 1;
        setLoginAttempts(newAttempts);
        
        // Lock account temporarily after too many failed attempts
        if (newAttempts >= MAX_LOGIN_ATTEMPTS) {
          setIsLocked(true);
          setError('Too many failed login attempts. Account is temporarily locked for 15 minutes.');
          
          // Unlock after 15 minutes
          setTimeout(() => {
            setIsLocked(false);
            setLoginAttempts(0);
          }, 15 * 60 * 1000);
        } else {
          setError(err.message || 'Failed to login. Please check your credentials.');
        }
      } finally {
        setLoading(false);
      }
    }
  });

  const handleTogglePasswordVisibility = () => {
    setShowPassword(!showPassword);
  };

  // Mock API function - in a real app, this would be an actual API call
  const mockLoginAPI = async (username, password, csrf) => {
    // Simulate network delay
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    // Demo credentials for testing
    if (username === 'admin' && password === 'Password123!') {
      return {
        success: true,
        user: {
          id: 1,
          username: 'admin',
          fullName: 'Admin User',
          role: 'admin'
        },
        token: 'mock-jwt-token'
      };
    } else {
      return {
        success: false,
        message: 'Invalid username or password'
      };
    }
  };

  return (
    <Container maxWidth="sm">
      <Box sx={{ mt: 8, display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
        <Paper elevation={3} sx={{ p: 4, width: '100%' }}>
          <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', mb: 3 }}>
            <LockIcon color="primary" sx={{ fontSize: 40, mb: 1 }} />
            <Typography component="h1" variant="h5">
              Sign in to OpenManus
            </Typography>
          </Box>

          {error && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {error}
            </Alert>
          )}

          <form onSubmit={formik.handleSubmit} noValidate>
            {/* Hidden CSRF token field */}
            <input type="hidden" name="csrf_token" value={csrfToken} />
            
            <TextField
              margin="normal"
              required
              fullWidth
              id="username"
              label="Username"
              name="username"
              autoComplete="username"
              autoFocus
              value={formik.values.username}
              onChange={formik.handleChange}
              onBlur={formik.handleBlur}
              error={formik.touched.username && Boolean(formik.errors.username)}
              helperText={formik.touched.username && formik.errors.username}
              disabled={loading || isLocked}
            />
            
            <TextField
              margin="normal"
              required
              fullWidth
              name="password"
              label="Password"
              type={showPassword ? 'text' : 'password'}
              id="password"
              autoComplete="current-password"
              value={formik.values.password}
              onChange={formik.handleChange}
              onBlur={formik.handleBlur}
              error={formik.touched.password && Boolean(formik.errors.password)}
              helperText={formik.touched.password && formik.errors.password}
              disabled={loading || isLocked}
              InputProps={{
                endAdornment: (
                  <InputAdornment position="end">
                    <IconButton
                      aria-label="toggle password visibility"
                      onClick={handleTogglePasswordVisibility}
                      edge="end"
                    >
                      {showPassword ? <VisibilityOffIcon /> : <VisibilityIcon />}
                    </IconButton>
                  </InputAdornment>
                )
              }}
            />
            
            <Button
              type="submit"
              fullWidth
              variant="contained"
              sx={{ mt: 3, mb: 2, py: 1.5 }}
              disabled={loading || isLocked}
            >
              {loading ? <CircularProgress size={24} /> : 'Sign In'}
            </Button>
            
            <Box sx={{ mt: 2, textAlign: 'center' }}>
              <Link href="#" variant="body2" underline="hover">
                Forgot password?
              </Link>
            </Box>
          </form>
        </Paper>
        
        <Typography variant="body2" color="text.secondary" align="center" sx={{ mt: 3 }}>
          &copy; {new Date().getFullYear()} OpenManus Appliance Repair
        </Typography>
      </Box>
    </Container>
  );
};

export default LoginForm; 