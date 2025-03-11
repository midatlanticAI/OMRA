import React, { useState, useEffect } from 'react';
import {
  Typography,
  Box,
  Paper,
  Button,
  Grid,
  Card,
  CardContent,
  CardActions,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  FormControlLabel,
  Switch,
  Chip,
  Divider,
  Alert,
  CircularProgress
} from '@mui/material';
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  FilterList as FilterIcon
} from '@mui/icons-material';
import axios from 'axios';

const Smartlists = () => {
  const [smartlists, setSmartlists] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [openDialog, setOpenDialog] = useState(false);
  const [editingSmartlist, setEditingSmartlist] = useState(null);
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    type: 'service_request',
    filter_criteria: {},
    is_public: false
  });
  const [filterCriteriaText, setFilterCriteriaText] = useState('');

  // Fetch smartlists on component mount
  useEffect(() => {
    fetchSmartlists();
  }, []);

  const fetchSmartlists = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await axios.get('/api/smartlists');
      setSmartlists(response.data);
    } catch (err) {
      console.error('Error fetching smartlists:', err);
      setError('Failed to load smartlists. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleOpenDialog = (smartlist = null) => {
    if (smartlist) {
      // Edit mode
      setEditingSmartlist(smartlist);
      setFormData({
        name: smartlist.name,
        description: smartlist.description || '',
        type: smartlist.type,
        filter_criteria: smartlist.filter_criteria,
        is_public: smartlist.is_public
      });
      setFilterCriteriaText(JSON.stringify(smartlist.filter_criteria, null, 2));
    } else {
      // Create mode
      setEditingSmartlist(null);
      setFormData({
        name: '',
        description: '',
        type: 'service_request',
        filter_criteria: {},
        is_public: false
      });
      setFilterCriteriaText('{}');
    }
    setOpenDialog(true);
  };

  const handleCloseDialog = () => {
    setOpenDialog(false);
    setEditingSmartlist(null);
  };

  const handleInputChange = (e) => {
    const { name, value, checked } = e.target;
    setFormData({
      ...formData,
      [name]: name === 'is_public' ? checked : value
    });
  };

  const handleFilterCriteriaChange = (e) => {
    setFilterCriteriaText(e.target.value);
    try {
      const parsedCriteria = JSON.parse(e.target.value);
      setFormData({
        ...formData,
        filter_criteria: parsedCriteria
      });
    } catch (err) {
      // Invalid JSON, will be caught during validation
    }
  };

  const validateForm = () => {
    if (!formData.name.trim()) {
      return 'Name is required';
    }
    if (!formData.type) {
      return 'Type is required';
    }
    try {
      JSON.parse(filterCriteriaText);
    } catch (err) {
      return 'Filter criteria must be valid JSON';
    }
    return null;
  };

  const handleSubmit = async () => {
    const validationError = validateForm();
    if (validationError) {
      setError(validationError);
      return;
    }

    setLoading(true);
    setError(null);

    try {
      // Parse filter criteria from text
      const parsedFilterCriteria = JSON.parse(filterCriteriaText);
      const dataToSubmit = {
        ...formData,
        filter_criteria: parsedFilterCriteria
      };

      let response;
      if (editingSmartlist) {
        // Update existing smartlist
        response = await axios.put(`/api/smartlists/${editingSmartlist._id}`, dataToSubmit);
        
        // Update the smartlists array with the updated item
        setSmartlists(smartlists.map(item => 
          item._id === editingSmartlist._id ? response.data : item
        ));
      } else {
        // Create new smartlist
        response = await axios.post('/api/smartlists', dataToSubmit);
        
        // Add the new smartlist to the array
        setSmartlists([response.data, ...smartlists]);
      }

      handleCloseDialog();
    } catch (err) {
      console.error('Error saving smartlist:', err);
      setError(err.response?.data?.detail || 'Failed to save smartlist. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Are you sure you want to delete this smartlist?')) {
      return;
    }

    setLoading(true);
    setError(null);

    try {
      await axios.delete(`/api/smartlists/${id}`);
      
      // Remove the deleted smartlist from the array
      setSmartlists(smartlists.filter(item => item._id !== id));
    } catch (err) {
      console.error('Error deleting smartlist:', err);
      setError(err.response?.data?.detail || 'Failed to delete smartlist. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const getTypeLabel = (type) => {
    switch (type) {
      case 'customer':
        return 'Customers';
      case 'service_request':
        return 'Service Requests';
      case 'technician':
        return 'Technicians';
      default:
        return type;
    }
  };

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" component="h1">
          Smartlists
        </Typography>
        <Button 
          variant="contained" 
          startIcon={<AddIcon />}
          onClick={() => handleOpenDialog()}
        >
          Create Smartlist
        </Button>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      {loading && smartlists.length === 0 ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', my: 4 }}>
          <CircularProgress />
        </Box>
      ) : smartlists.length === 0 ? (
        <Paper sx={{ p: 3, textAlign: 'center' }}>
          <Typography variant="body1" sx={{ mb: 2 }}>
            No smartlists found. Create your first smartlist to get started.
          </Typography>
          <Button 
            variant="outlined" 
            startIcon={<AddIcon />}
            onClick={() => handleOpenDialog()}
          >
            Create Smartlist
          </Button>
        </Paper>
      ) : (
        <Grid container spacing={3}>
          {smartlists.map((smartlist) => (
            <Grid item xs={12} md={6} lg={4} key={smartlist._id}>
              <Card>
                <CardContent>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                    <Typography variant="h6" component="h2" gutterBottom>
                      {smartlist.name}
                    </Typography>
                    <Chip 
                      label={getTypeLabel(smartlist.type)} 
                      size="small" 
                      color="primary" 
                      variant="outlined"
                    />
                  </Box>
                  
                  {smartlist.description && (
                    <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                      {smartlist.description}
                    </Typography>
                  )}
                  
                  <Divider sx={{ my: 1 }} />
                  
                  <Typography variant="subtitle2" sx={{ mt: 1, display: 'flex', alignItems: 'center' }}>
                    <FilterIcon fontSize="small" sx={{ mr: 0.5 }} /> Filter Criteria:
                  </Typography>
                  <Box 
                    component="pre" 
                    sx={{ 
                      mt: 1, 
                      p: 1, 
                      bgcolor: 'grey.100', 
                      borderRadius: 1,
                      fontSize: '0.75rem',
                      overflow: 'auto',
                      maxHeight: '100px'
                    }}
                  >
                    {JSON.stringify(smartlist.filter_criteria, null, 2)}
                  </Box>
                  
                  {smartlist.is_public && (
                    <Chip 
                      label="Public" 
                      size="small" 
                      color="success" 
                      sx={{ mt: 1 }}
                    />
                  )}
                </CardContent>
                <CardActions>
                  <Button 
                    size="small" 
                    startIcon={<EditIcon />}
                    onClick={() => handleOpenDialog(smartlist)}
                  >
                    Edit
                  </Button>
                  <Button 
                    size="small" 
                    color="error" 
                    startIcon={<DeleteIcon />}
                    onClick={() => handleDelete(smartlist._id)}
                  >
                    Delete
                  </Button>
                </CardActions>
              </Card>
            </Grid>
          ))}
        </Grid>
      )}

      {/* Create/Edit Dialog */}
      <Dialog open={openDialog} onClose={handleCloseDialog} maxWidth="md" fullWidth>
        <DialogTitle>
          {editingSmartlist ? 'Edit Smartlist' : 'Create Smartlist'}
        </DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 0.5 }}>
            <Grid item xs={12}>
              <TextField
                name="name"
                label="Name"
                fullWidth
                value={formData.name}
                onChange={handleInputChange}
                required
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                name="description"
                label="Description"
                fullWidth
                multiline
                rows={2}
                value={formData.description}
                onChange={handleInputChange}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth>
                <InputLabel>Type</InputLabel>
                <Select
                  name="type"
                  value={formData.type}
                  onChange={handleInputChange}
                  label="Type"
                >
                  <MenuItem value="customer">Customers</MenuItem>
                  <MenuItem value="service_request">Service Requests</MenuItem>
                  <MenuItem value="technician">Technicians</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} sm={6}>
              <FormControlLabel
                control={
                  <Switch
                    name="is_public"
                    checked={formData.is_public}
                    onChange={handleInputChange}
                  />
                }
                label="Public Smartlist"
              />
            </Grid>
            <Grid item xs={12}>
              <Typography variant="subtitle2" gutterBottom>
                Filter Criteria (JSON format)
              </Typography>
              <TextField
                fullWidth
                multiline
                rows={6}
                value={filterCriteriaText}
                onChange={handleFilterCriteriaChange}
                placeholder='{"status": "pending", "priority": ["high", "urgent"]}'
                sx={{ fontFamily: 'monospace' }}
              />
              <Typography variant="caption" color="text.secondary">
                Enter filter criteria in JSON format. For example, to filter service requests with pending status:
                {`{"status": "pending"}`}
              </Typography>
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog}>Cancel</Button>
          <Button 
            onClick={handleSubmit} 
            variant="contained"
            disabled={loading}
          >
            {loading ? <CircularProgress size={24} /> : 'Save'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default Smartlists; 