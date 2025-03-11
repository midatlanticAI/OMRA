import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Paper,
  TextField,
  Button,
  List,
  ListItem,
  ListItemText,
  Divider,
  IconButton,
  Dialog,
  DialogActions,
  DialogContent,
  DialogContentText,
  DialogTitle,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Grid,
  CircularProgress,
  Snackbar,
  Alert,
  InputAdornment,
  Tooltip
} from '@mui/material';
import {
  Add as AddIcon,
  Delete as DeleteIcon,
  Visibility as VisibilityIcon,
  VisibilityOff as VisibilityOffIcon,
  Key as KeyIcon,
  Refresh as RefreshIcon
} from '@mui/icons-material';
import axios from 'axios';

const Settings = () => {
  const [apiKeys, setApiKeys] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [openDialog, setOpenDialog] = useState(false);
  const [newKeyName, setNewKeyName] = useState('');
  const [newKeyValue, setNewKeyValue] = useState('');
  const [showValues, setShowValues] = useState({});
  const [snackbar, setSnackbar] = useState({
    open: false,
    message: '',
    severity: 'info'
  });

  // Fetch API keys on component mount
  useEffect(() => {
    fetchApiKeys();
  }, []);

  const fetchApiKeys = async () => {
    try {
      setLoading(true);
      const response = await axios.get('/api/settings/api-keys');
      setApiKeys(response.data);
      setError(null);
    } catch (err) {
      console.error('Error fetching API keys:', err);
      setError('Failed to load API keys. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleOpenDialog = () => {
    setOpenDialog(true);
    setNewKeyName('');
    setNewKeyValue('');
  };

  const handleCloseDialog = () => {
    setOpenDialog(false);
  };

  const handleShowValue = (keyId) => {
    setShowValues(prev => ({
      ...prev,
      [keyId]: !prev[keyId]
    }));
  };

  const handleAddKey = async () => {
    if (!newKeyName || !newKeyValue) {
      setSnackbar({
        open: true,
        message: 'Key name and value are required',
        severity: 'error'
      });
      return;
    }

    try {
      await axios.post('/api/settings/api-keys', {
        key_name: newKeyName,
        key_value: newKeyValue
      });
      
      await fetchApiKeys();
      handleCloseDialog();
      
      setSnackbar({
        open: true,
        message: 'API key added successfully',
        severity: 'success'
      });
    } catch (err) {
      console.error('Error adding API key:', err);
      setSnackbar({
        open: true,
        message: 'Failed to add API key. Please try again.',
        severity: 'error'
      });
    }
  };

  const handleDeleteKey = async (keyName) => {
    try {
      await axios.delete(`/api/settings/api-keys/${keyName}`);
      await fetchApiKeys();
      setSnackbar({
        open: true,
        message: `API key '${keyName}' deleted successfully`,
        severity: 'success'
      });
    } catch (err) {
      console.error('Error deleting API key:', err);
      setSnackbar({
        open: true,
        message: 'Failed to delete API key. Please try again.',
        severity: 'error'
      });
    }
  };

  const handleCloseSnackbar = () => {
    setSnackbar({
      ...snackbar,
      open: false
    });
  };

  // Predefined API key options
  const apiKeyOptions = [
    { name: "ANTHROPIC_API_KEY", description: "API key for Claude (Anthropic)" },
    { name: "OPENAI_API_KEY", description: "API key for GPT models (OpenAI)" },
    { name: "SERPAPI_API_KEY", description: "API key for search engines" },
    { name: "GOOGLE_MAPS_API_KEY", description: "API key for Google Maps integration" },
    { name: "TWILIO_API_KEY", description: "API key for SMS notifications" },
    { name: "SENDGRID_API_KEY", description: "API key for email notifications" }
  ];

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '50vh' }}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" component="h1">
          Settings
        </Typography>
        <Button 
          variant="contained" 
          startIcon={<RefreshIcon />}
          onClick={fetchApiKeys}
        >
          Refresh
        </Button>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      <Paper sx={{ p: 3, mb: 4 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
          <Typography variant="h5" component="h2">
            API Keys
          </Typography>
          <Button 
            variant="contained" 
            startIcon={<AddIcon />}
            onClick={handleOpenDialog}
          >
            Add API Key
          </Button>
        </Box>

        <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
          Manage API keys for integration with external services. These keys are stored securely and used by the agent system.
        </Typography>

        {apiKeys.length === 0 ? (
          <Paper elevation={0} sx={{ p: 3, bgcolor: 'background.default', textAlign: 'center' }}>
            <Typography variant="body1" color="text.secondary">
              No API keys found. Add your first API key using the button above.
            </Typography>
          </Paper>
        ) : (
          <List>
            {apiKeys.map((key, index) => (
              <React.Fragment key={key._id}>
                <ListItem>
                  <ListItemText
                    primary={
                      <Box sx={{ display: 'flex', alignItems: 'center' }}>
                        <KeyIcon color="primary" sx={{ mr: 1 }} />
                        <Typography variant="subtitle1">
                          {key.key_name}
                        </Typography>
                      </Box>
                    }
                    secondary={
                      <Box sx={{ mt: 1 }}>
                        <Typography variant="body2" color="text.secondary">
                          Value: 
                          <Box component="span" sx={{ 
                            fontFamily: 'monospace', 
                            ml: 1, 
                            p: 0.5, 
                            bgcolor: 'background.default',
                            borderRadius: 1
                          }}>
                            {showValues[key._id] 
                              ? key.key_value 
                              : '••••••••••••••••••••••••••••••'}
                          </Box>
                          <IconButton 
                            size="small" 
                            onClick={() => handleShowValue(key._id)}
                            sx={{ ml: 1 }}
                          >
                            {showValues[key._id] ? <VisibilityOffIcon fontSize="small" /> : <VisibilityIcon fontSize="small" />}
                          </IconButton>
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          Last updated: {new Date(key.updated_at).toLocaleString()}
                        </Typography>
                      </Box>
                    }
                  />
                  <IconButton 
                    edge="end" 
                    color="error"
                    onClick={() => handleDeleteKey(key.key_name)}
                  >
                    <DeleteIcon />
                  </IconButton>
                </ListItem>
                {index < apiKeys.length - 1 && <Divider />}
              </React.Fragment>
            ))}
          </List>
        )}
      </Paper>

      {/* Add API Key Dialog */}
      <Dialog open={openDialog} onClose={handleCloseDialog} maxWidth="sm" fullWidth>
        <DialogTitle>Add API Key</DialogTitle>
        <DialogContent>
          <DialogContentText sx={{ mb: 2 }}>
            Add a new API key to integrate with external services. These keys are used by the agent system.
          </DialogContentText>
          
          <Grid container spacing={2}>
            <Grid item xs={12}>
              <FormControl fullWidth margin="normal">
                <InputLabel id="key-name-label">Key Name</InputLabel>
                <Select
                  labelId="key-name-label"
                  id="key-name"
                  value={newKeyName}
                  onChange={(e) => setNewKeyName(e.target.value)}
                  label="Key Name"
                >
                  {apiKeyOptions.map((option) => (
                    <MenuItem key={option.name} value={option.name}>
                      <Tooltip title={option.description} placement="right">
                        <Box>
                          {option.name}
                        </Box>
                      </Tooltip>
                    </MenuItem>
                  ))}
                  <MenuItem value="CUSTOM">
                    <em>Custom Key Name...</em>
                  </MenuItem>
                </Select>
              </FormControl>
            </Grid>
            
            {newKeyName === 'CUSTOM' && (
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Custom Key Name"
                  variant="outlined"
                  value={newKeyName === 'CUSTOM' ? '' : newKeyName}
                  onChange={(e) => setNewKeyName(e.target.value)}
                  helperText="Enter a custom key name (e.g. MY_SERVICE_API_KEY)"
                />
              </Grid>
            )}
            
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="API Key Value"
                type={showValues.newKey ? "text" : "password"}
                variant="outlined"
                value={newKeyValue}
                onChange={(e) => setNewKeyValue(e.target.value)}
                helperText="Enter the API key value provided by the service"
                InputProps={{
                  endAdornment: (
                    <InputAdornment position="end">
                      <IconButton
                        onClick={() => handleShowValue('newKey')}
                        edge="end"
                      >
                        {showValues.newKey ? <VisibilityOffIcon /> : <VisibilityIcon />}
                      </IconButton>
                    </InputAdornment>
                  ),
                }}
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog}>Cancel</Button>
          <Button 
            onClick={handleAddKey} 
            variant="contained"
            disabled={!newKeyName || !newKeyValue || newKeyName === 'CUSTOM'}
          >
            Add Key
          </Button>
        </DialogActions>
      </Dialog>

      {/* Snackbar for notifications */}
      <Snackbar
        open={snackbar.open}
        autoHideDuration={6000}
        onClose={handleCloseSnackbar}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
      >
        <Alert onClose={handleCloseSnackbar} severity={snackbar.severity} sx={{ width: '100%' }}>
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Box>
  );
};

export default Settings; 