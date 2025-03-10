import React, { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import {
  Box,
  Button,
  Card,
  CardContent,
  CircularProgress,
  Container,
  Divider,
  Grid,
  IconButton,
  InputAdornment,
  TextField,
  Typography,
  Alert
} from '@mui/material';
import { 
  Email, 
  Lock, 
  Visibility, 
  VisibilityOff
} from '@mui/icons-material';
import { useAuth } from '../context/AuthContext';
import { useFormik } from 'formik';
import * as Yup from 'yup';

const Login = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { login, error: authError, loading } = useAuth();
  const [showPassword, setShowPassword] = useState(false);
  
  // Get redirect path from location state or default to dashboard
  const from = location.state?.from?.pathname || '/dashboard';

  // Form validation schema
  const validationSchema = Yup.object({
    email: Yup.string()
      .email('Enter a valid email')
      .required('Email is required'),
    password: Yup.string()
      .min(8, 'Password should be of minimum 8 characters length')
      .required('Password is required')
  });

  // Initialize formik
  const formik = useFormik({
    initialValues: {
      email: '',
      password: ''
    },
    validationSchema: validationSchema,
    onSubmit: async (values) => {
      const success = await login(values.email, values.password);
      if (success) {
        navigate(from, { replace: true });
      }
    }
  });

  const handleTogglePasswordVisibility = () => {
    setShowPassword(!showPassword);
  };

  return (
    <Container maxWidth="sm">
      <Box
        sx={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          minHeight: '100vh',
          py: 4
        }}
      >
        <Card sx={{ width: '100%', mb: 4, boxShadow: 3 }}>
          <CardContent sx={{ p: 4 }}>
            <Box
              sx={{
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                mb: 4
              }}
            >
              <img 
                src="/assets/logo.png" 
                alt="OpenManus Logo" 
                style={{ width: 200, marginBottom: 24 }} 
              />
              <Typography component="h1" variant="h4" fontWeight="bold">
                Welcome Back
              </Typography>
              <Typography variant="body1" color="textSecondary" sx={{ mt: 1 }}>
                Sign in to continue to OpenManus
              </Typography>
            </Box>

            {authError && (
              <Alert severity="error" sx={{ mb: 3 }}>
                {authError}
              </Alert>
            )}

            <form onSubmit={formik.handleSubmit}>
              <TextField
                fullWidth
                id="email"
                name="email"
                label="Email Address"
                variant="outlined"
                margin="normal"
                value={formik.values.email}
                onChange={formik.handleChange}
                onBlur={formik.handleBlur}
                error={formik.touched.email && Boolean(formik.errors.email)}
                helperText={formik.touched.email && formik.errors.email}
                InputProps={{
                  startAdornment: (
                    <InputAdornment position="start">
                      <Email color="action" />
                    </InputAdornment>
                  ),
                }}
              />

              <TextField
                fullWidth
                id="password"
                name="password"
                label="Password"
                type={showPassword ? 'text' : 'password'}
                variant="outlined"
                margin="normal"
                value={formik.values.password}
                onChange={formik.handleChange}
                onBlur={formik.handleBlur}
                error={formik.touched.password && Boolean(formik.errors.password)}
                helperText={formik.touched.password && formik.errors.password}
                InputProps={{
                  startAdornment: (
                    <InputAdornment position="start">
                      <Lock color="action" />
                    </InputAdornment>
                  ),
                  endAdornment: (
                    <InputAdornment position="end">
                      <IconButton
                        aria-label="toggle password visibility"
                        onClick={handleTogglePasswordVisibility}
                        edge="end"
                      >
                        {showPassword ? <VisibilityOff /> : <Visibility />}
                      </IconButton>
                    </InputAdornment>
                  ),
                }}
              />

              <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 1, mb: 2 }}>
                <Typography 
                  variant="body2" 
                  color="primary" 
                  sx={{ cursor: 'pointer' }}
                  onClick={() => navigate('/forgot-password')}
                >
                  Forgot password?
                </Typography>
              </Box>

              <Button
                type="submit"
                fullWidth
                variant="contained"
                color="primary"
                size="large"
                disabled={loading}
                sx={{ 
                  py: 1.5,
                  mt: 1, 
                  mb: 3,
                  fontWeight: 'bold'
                }}
              >
                {loading ? <CircularProgress size={24} /> : 'Sign In'}
              </Button>

              <Divider>
                <Typography variant="body2" color="textSecondary">
                  OR
                </Typography>
              </Divider>

              <Box sx={{ mt: 3 }}>
                <Grid container spacing={2}>
                  <Grid item xs={12}>
                    <Button
                      fullWidth
                      variant="outlined"
                      color="primary"
                      size="large"
                      sx={{ py: 1.25 }}
                      onClick={() => navigate('/register')}
                    >
                      Create Account
                    </Button>
                  </Grid>
                </Grid>
              </Box>
            </form>
          </CardContent>
        </Card>

        <Typography variant="body2" color="textSecondary" align="center">
          &copy; {new Date().getFullYear()} OpenManus. All rights reserved.
        </Typography>
      </Box>
    </Container>
  );
};

export default Login; 