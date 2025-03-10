import React, { useState } from 'react';
import {
  Box,
  Button,
  Card,
  CardActions,
  CardContent,
  CircularProgress,
  Dialog,
  DialogActions,
  DialogContent,
  DialogContentText,
  DialogTitle,
  Divider,
  Grid,
  Paper,
  Switch,
  TextField,
  Typography
} from '@mui/material';
import {
  Check as CheckIcon,
  ErrorOutline,
  LinkOff,
  Settings as SettingsIcon
} from '@mui/icons-material';
import axios from 'axios';
import { useConfig } from '../context/ConfigContext';

const Integrations = () => {
  const { config, loading: configLoading, updateIntegrationStatus } = useConfig();
  
  // State for API key dialogs
  const [ghlDialogOpen, setGhlDialogOpen] = useState(false);
  const [kickservDialogOpen, setKickservDialogOpen] = useState(false);
  
  // State for API keys
  const [ghlApiKey, setGhlApiKey] = useState('');
  const [kickservApiKey, setKickservApiKey] = useState('');
  const [kickservCompanyId, setKickservCompanyId] = useState('');
  
  // State for loading states
  const [ghlLoading, setGhlLoading] = useState(false);
  const [kickservLoading, setKickservLoading] = useState(false);
  
  // State for error messages
  const [ghlError, setGhlError] = useState(null);
  const [kickservError, setKickservError] = useState(null);

  // Handle integration toggle
  const handleToggleIntegration = async (integration, enabled) => {
    try {
      await updateIntegrationStatus(integration, { enabled });
    } catch (err) {
      console.error(`Failed to update ${integration} status:`, err);
    }
  };

  // GHL Dialog handlers
  const handleOpenGhlDialog = () => {
    setGhlDialogOpen(true);
    setGhlError(null);
  };

  const handleCloseGhlDialog = () => {
    setGhlDialogOpen(false);
    setGhlApiKey('');
  };

  const handleConnectGhl = async () => {
    try {
      setGhlLoading(true);
      setGhlError(null);
      
      const response = await axios.post('/api/integrations/ghl/connect', {
        apiKey: ghlApiKey
      });
      
      if (response.data.success) {
        await updateIntegrationStatus('ghl', { connected: true });
        handleCloseGhlDialog();
      } else {
        setGhlError(response.data.message || 'Failed to connect to Go High Level');
      }
    } catch (err) {
      console.error('Failed to connect to GHL:', err);
      setGhlError(err.response?.data?.message || 'Failed to connect to Go High Level');
    } finally {
      setGhlLoading(false);
    }
  };

  const handleDisconnectGhl = async () => {
    try {
      setGhlLoading(true);
      
      const response = await axios.post('/api/integrations/ghl/disconnect');
      
      if (response.data.success) {
        await updateIntegrationStatus('ghl', { connected: false });
      }
    } catch (err) {
      console.error('Failed to disconnect from GHL:', err);
    } finally {
      setGhlLoading(false);
    }
  };

  // Kickserv Dialog handlers
  const handleOpenKickservDialog = () => {
    setKickservDialogOpen(true);
    setKickservError(null);
  };

  const handleCloseKickservDialog = () => {
    setKickservDialogOpen(false);
    setKickservApiKey('');
    setKickservCompanyId('');
  };

  const handleConnectKickserv = async () => {
    try {
      setKickservLoading(true);
      setKickservError(null);
      
      const response = await axios.post('/api/integrations/kickserv/connect', {
        apiKey: kickservApiKey,
        companyId: kickservCompanyId
      });
      
      if (response.data.success) {
        await updateIntegrationStatus('kickserv', { connected: true });
        handleCloseKickservDialog();
      } else {
        setKickservError(response.data.message || 'Failed to connect to Kickserv');
      }
    } catch (err) {
      console.error('Failed to connect to Kickserv:', err);
      setKickservError(err.response?.data?.message || 'Failed to connect to Kickserv');
    } finally {
      setKickservLoading(false);
    }
  };

  const handleDisconnectKickserv = async () => {
    try {
      setKickservLoading(true);
      
      const response = await axios.post('/api/integrations/kickserv/disconnect');
      
      if (response.data.success) {
        await updateIntegrationStatus('kickserv', { connected: false });
      }
    } catch (err) {
      console.error('Failed to disconnect from Kickserv:', err);
    } finally {
      setKickservLoading(false);
    }
  };

  if (configLoading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" height="80vh">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box p={3}>
      <Typography variant="h4" gutterBottom>
        Integrations
      </Typography>
      
      <Typography variant="subtitle1" color="textSecondary" gutterBottom>
        Connect your OpenManus system with external services
      </Typography>
      
      <Grid container spacing={3} sx={{ mt: 2 }}>
        {/* Go High Level Integration */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Box display="flex" justifyContent="space-between" alignItems="flex-start">
                <Box>
                  <Box display="flex" alignItems="center">
                    <img 
                      src="/assets/ghl-logo.png" 
                      alt="Go High Level" 
                      style={{ width: 50, height: 50, marginRight: 16 }} 
                    />
                    <div>
                      <Typography variant="h6">Go High Level</Typography>
                      <Typography variant="body2" color="textSecondary">
                        CRM and Marketing Automation
                      </Typography>
                    </div>
                  </Box>
                  
                  <Box mt={2}>
                    <Typography variant="body2">
                      Go High Level provides powerful CRM, marketing automation, and 
                      client management tools. Connect to sync your customers and leads.
                    </Typography>
                  </Box>
                </Box>
                
                <Switch
                  checked={config.integrations.ghl.enabled}
                  onChange={(e) => handleToggleIntegration('ghl', e.target.checked)}
                  color="primary"
                />
              </Box>
              
              {config.integrations.ghl.enabled && (
                <>
                  <Divider sx={{ my: 2 }} />
                  
                  <Box display="flex" alignItems="center" justifyContent="space-between">
                    <Typography>
                      {config.integrations.ghl.connected ? (
                        <Box display="flex" alignItems="center" color="success.main">
                          <CheckIcon fontSize="small" sx={{ mr: 0.5 }} />
                          Connected
                        </Box>
                      ) : (
                        <Box display="flex" alignItems="center" color="text.secondary">
                          <LinkOff fontSize="small" sx={{ mr: 0.5 }} />
                          Disconnected
                        </Box>
                      )}
                    </Typography>
                    
                    {ghlLoading ? (
                      <CircularProgress size={24} />
                    ) : config.integrations.ghl.connected ? (
                      <Button 
                        variant="outlined"
                        color="primary"
                        onClick={handleDisconnectGhl}
                        startIcon={<LinkOff />}
                      >
                        Disconnect
                      </Button>
                    ) : (
                      <Button 
                        variant="contained"
                        color="primary"
                        onClick={handleOpenGhlDialog}
                      >
                        Connect
                      </Button>
                    )}
                  </Box>
                </>
              )}
            </CardContent>
            
            {config.integrations.ghl.enabled && config.integrations.ghl.connected && (
              <CardActions>
                <Button 
                  size="small" 
                  startIcon={<SettingsIcon />}
                >
                  Configure
                </Button>
              </CardActions>
            )}
          </Card>
        </Grid>
        
        {/* Kickserv Integration */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Box display="flex" justifyContent="space-between" alignItems="flex-start">
                <Box>
                  <Box display="flex" alignItems="center">
                    <img 
                      src="/assets/kickserv-logo.png" 
                      alt="Kickserv" 
                      style={{ width: 50, height: 50, marginRight: 16 }} 
                    />
                    <div>
                      <Typography variant="h6">Kickserv</Typography>
                      <Typography variant="body2" color="textSecondary">
                        Field Service Management
                      </Typography>
                    </div>
                  </Box>
                  
                  <Box mt={2}>
                    <Typography variant="body2">
                      Kickserv helps manage service requests, scheduling, invoicing, and 
                      payments. Connect to sync jobs and customer data.
                    </Typography>
                  </Box>
                </Box>
                
                <Switch
                  checked={config.integrations.kickserv.enabled}
                  onChange={(e) => handleToggleIntegration('kickserv', e.target.checked)}
                  color="primary"
                />
              </Box>
              
              {config.integrations.kickserv.enabled && (
                <>
                  <Divider sx={{ my: 2 }} />
                  
                  <Box display="flex" alignItems="center" justifyContent="space-between">
                    <Typography>
                      {config.integrations.kickserv.connected ? (
                        <Box display="flex" alignItems="center" color="success.main">
                          <CheckIcon fontSize="small" sx={{ mr: 0.5 }} />
                          Connected
                        </Box>
                      ) : (
                        <Box display="flex" alignItems="center" color="text.secondary">
                          <LinkOff fontSize="small" sx={{ mr: 0.5 }} />
                          Disconnected
                        </Box>
                      )}
                    </Typography>
                    
                    {kickservLoading ? (
                      <CircularProgress size={24} />
                    ) : config.integrations.kickserv.connected ? (
                      <Button 
                        variant="outlined"
                        color="primary"
                        onClick={handleDisconnectKickserv}
                        startIcon={<LinkOff />}
                      >
                        Disconnect
                      </Button>
                    ) : (
                      <Button 
                        variant="contained"
                        color="primary"
                        onClick={handleOpenKickservDialog}
                      >
                        Connect
                      </Button>
                    )}
                  </Box>
                </>
              )}
            </CardContent>
            
            {config.integrations.kickserv.enabled && config.integrations.kickserv.connected && (
              <CardActions>
                <Button 
                  size="small" 
                  startIcon={<SettingsIcon />}
                >
                  Configure
                </Button>
              </CardActions>
            )}
          </Card>
        </Grid>
        
        {/* Integration Sync Card */}
        <Grid item xs={12}>
          <Paper sx={{ p: 3, mt: 2 }}>
            <Typography variant="h6" gutterBottom>
              Data Synchronization
            </Typography>
            
            <Typography variant="body2" color="textSecondary" paragraph>
              Configure how your data is synchronized between OpenManus and connected integrations.
            </Typography>
            
            <Grid container spacing={3}>
              <Grid item xs={12} md={4}>
                <Card variant="outlined">
                  <CardContent>
                    <Typography variant="subtitle1" gutterBottom>
                      Customer Sync
                    </Typography>
                    <Typography variant="body2" color="textSecondary">
                      Determine how customer data is synchronized between systems
                    </Typography>
                  </CardContent>
                  <CardActions>
                    <Button size="small" color="primary">
                      Configure
                    </Button>
                  </CardActions>
                </Card>
              </Grid>
              
              <Grid item xs={12} md={4}>
                <Card variant="outlined">
                  <CardContent>
                    <Typography variant="subtitle1" gutterBottom>
                      Job Sync
                    </Typography>
                    <Typography variant="body2" color="textSecondary">
                      Configure how service jobs are synchronized with Kickserv
                    </Typography>
                  </CardContent>
                  <CardActions>
                    <Button size="small" color="primary">
                      Configure
                    </Button>
                  </CardActions>
                </Card>
              </Grid>
              
              <Grid item xs={12} md={4}>
                <Card variant="outlined">
                  <CardContent>
                    <Typography variant="subtitle1" gutterBottom>
                      Sync Schedule
                    </Typography>
                    <Typography variant="body2" color="textSecondary">
                      Set up automatic synchronization schedules
                    </Typography>
                  </CardContent>
                  <CardActions>
                    <Button size="small" color="primary">
                      Configure
                    </Button>
                  </CardActions>
                </Card>
              </Grid>
            </Grid>
          </Paper>
        </Grid>
      </Grid>
      
      {/* Go High Level Connection Dialog */}
      <Dialog open={ghlDialogOpen} onClose={handleCloseGhlDialog}>
        <DialogTitle>Connect to Go High Level</DialogTitle>
        <DialogContent>
          <DialogContentText>
            Enter your Go High Level API Key to connect your account.
            You can find your API key in the Go High Level dashboard under Settings &gt; API.
          </DialogContentText>
          
          {ghlError && (
            <Box 
              sx={{ 
                display: 'flex', 
                alignItems: 'center',
                color: 'error.main',
                mt: 2,
                mb: 1,
                p: 1,
                backgroundColor: 'error.light',
                borderRadius: 1
              }}
            >
              <ErrorOutline sx={{ mr: 1 }} />
              <Typography variant="body2">{ghlError}</Typography>
            </Box>
          )}
          
          <TextField
            autoFocus
            margin="dense"
            id="ghl-api-key"
            label="API Key"
            type="password"
            fullWidth
            variant="outlined"
            value={ghlApiKey}
            onChange={(e) => setGhlApiKey(e.target.value)}
            sx={{ mt: 2 }}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseGhlDialog}>Cancel</Button>
          <Button 
            onClick={handleConnectGhl} 
            color="primary"
            disabled={!ghlApiKey || ghlLoading}
          >
            {ghlLoading ? <CircularProgress size={24} /> : 'Connect'}
          </Button>
        </DialogActions>
      </Dialog>
      
      {/* Kickserv Connection Dialog */}
      <Dialog open={kickservDialogOpen} onClose={handleCloseKickservDialog}>
        <DialogTitle>Connect to Kickserv</DialogTitle>
        <DialogContent>
          <DialogContentText>
            Enter your Kickserv API credentials to connect your account.
            You can find your API key in the Kickserv dashboard under Settings &gt; API.
          </DialogContentText>
          
          {kickservError && (
            <Box 
              sx={{ 
                display: 'flex', 
                alignItems: 'center',
                color: 'error.main',
                mt: 2,
                mb: 1,
                p: 1,
                backgroundColor: 'error.light',
                borderRadius: 1
              }}
            >
              <ErrorOutline sx={{ mr: 1 }} />
              <Typography variant="body2">{kickservError}</Typography>
            </Box>
          )}
          
          <TextField
            autoFocus
            margin="dense"
            id="kickserv-company-id"
            label="Company ID"
            fullWidth
            variant="outlined"
            value={kickservCompanyId}
            onChange={(e) => setKickservCompanyId(e.target.value)}
            sx={{ mt: 2 }}
          />
          
          <TextField
            margin="dense"
            id="kickserv-api-key"
            label="API Key"
            type="password"
            fullWidth
            variant="outlined"
            value={kickservApiKey}
            onChange={(e) => setKickservApiKey(e.target.value)}
            sx={{ mt: 2 }}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseKickservDialog}>Cancel</Button>
          <Button 
            onClick={handleConnectKickserv} 
            color="primary"
            disabled={!kickservApiKey || !kickservCompanyId || kickservLoading}
          >
            {kickservLoading ? <CircularProgress size={24} /> : 'Connect'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default Integrations; 