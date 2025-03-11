import React, { useState, useEffect } from 'react';
import {
  Typography,
  Box,
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
  TablePagination,
  Alert,
  CircularProgress,
  Divider,
  Chip,
  Checkbox,
  Menu,
  ListItemIcon,
  ListItemText,
  Snackbar
} from '@mui/material';
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Phone as PhoneIcon,
  Email as EmailIcon,
  LocationOn as LocationIcon,
  MoreVert as MoreVertIcon,
  DeleteSweep as DeleteSweepIcon,
  Edit as BulkEditIcon,
  FileUpload as FileUploadIcon,
  FileDownload as FileDownloadIcon
} from '@mui/icons-material';
import axios from 'axios';

const Customers = () => {
  const [customers, setCustomers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [openDialog, setOpenDialog] = useState(false);
  const [editingCustomer, setEditingCustomer] = useState(null);
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [selectedCustomers, setSelectedCustomers] = useState([]);
  const [bulkActionMenuAnchor, setBulkActionMenuAnchor] = useState(null);
  const [openBulkEditDialog, setOpenBulkEditDialog] = useState(false);
  const [bulkEditData, setBulkEditData] = useState({});
  const [importFile, setImportFile] = useState(null);
  const [openImportDialog, setOpenImportDialog] = useState(false);
  const [importErrors, setImportErrors] = useState([]);
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'info' });
  const [openDeleteConfirmation, setOpenDeleteConfirmation] = useState(false);
  const [formData, setFormData] = useState({
    first_name: '',
    last_name: '',
    contact_info: {
      phone: '',
      email: '',
      preferred_contact: 'phone'
    },
    address: {
      street: '',
      city: '',
      state: '',
      zip_code: '',
      country: 'USA'
    },
    notes: ''
  });

  useEffect(() => {
    fetchCustomers();
  }, []);

  const fetchCustomers = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await axios.get('/api/customers');
      setCustomers(response.data);
    } catch (err) {
      console.error('Error fetching customers:', err);
      setError('Failed to load customers. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleOpenDialog = (customer = null) => {
    if (customer) {
      setEditingCustomer(customer);
      setFormData({
        first_name: customer.first_name,
        last_name: customer.last_name,
        contact_info: {
          phone: customer.contact_info.phone || '',
          email: customer.contact_info.email || '',
          preferred_contact: customer.contact_info.preferred_contact || 'phone'
        },
        address: customer.address ? {
          street: customer.address.street || '',
          city: customer.address.city || '',
          state: customer.address.state || '',
          zip_code: customer.address.zip_code || '',
          country: customer.address.country || 'USA'
        } : {
          street: '',
          city: '',
          state: '',
          zip_code: '',
          country: 'USA'
        },
        notes: customer.notes || ''
      });
    } else {
      setEditingCustomer(null);
      setFormData({
        first_name: '',
        last_name: '',
        contact_info: {
          phone: '',
          email: '',
          preferred_contact: 'phone'
        },
        address: {
          street: '',
          city: '',
          state: '',
          zip_code: '',
          country: 'USA'
        },
        notes: ''
      });
    }
    setOpenDialog(true);
  };

  const handleCloseDialog = () => {
    setOpenDialog(false);
    setEditingCustomer(null);
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    
    if (name.includes('.')) {
      const [parent, child] = name.split('.');
      setFormData({
        ...formData,
        [parent]: {
          ...formData[parent],
          [child]: value
        }
      });
    } else {
      setFormData({
        ...formData,
        [name]: value
      });
    }
  };

  const validateForm = () => {
    if (!formData.first_name.trim()) {
      return 'First name is required';
    }
    if (!formData.last_name.trim()) {
      return 'Last name is required';
    }
    if (!formData.contact_info.phone && !formData.contact_info.email) {
      return 'At least one contact method (phone or email) is required';
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
      let response;
      if (editingCustomer) {
        response = await axios.put(`/api/customers/${editingCustomer._id}`, formData);
        
        setCustomers(customers.map(item => 
          item._id === editingCustomer._id ? response.data : item
        ));
      } else {
        response = await axios.post('/api/customers', formData);
        
        setCustomers([response.data, ...customers]);
      }

      handleCloseDialog();
    } catch (err) {
      console.error('Error saving customer:', err);
      setError(err.response?.data?.detail || 'Failed to save customer. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Are you sure you want to delete this customer?')) {
      return;
    }

    setLoading(true);
    setError(null);

    try {
      await axios.delete(`/api/customers/${id}`);
      
      setCustomers(customers.filter(item => item._id !== id));
    } catch (err) {
      console.error('Error deleting customer:', err);
      setError(err.response?.data?.detail || 'Failed to delete customer. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleChangePage = (event, newPage) => {
    setPage(newPage);
  };

  const handleChangeRowsPerPage = (event) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };

  // Unused function - keeping commented for future reference
  // const handleSelectAll = (event) => {
  //   if (event.target.checked) {
  //     setSelectedCustomers(customers.map(customer => customer._id));
  //   } else {
  //     setSelectedCustomers([]);
  //   }
  // };

  const handleSelectCustomer = (id) => {
    const selectedIndex = selectedCustomers.indexOf(id);
    let newSelected = [];

    if (selectedIndex === -1) {
      newSelected = [...selectedCustomers, id];
    } else {
      newSelected = selectedCustomers.filter(customerId => customerId !== id);
    }

    setSelectedCustomers(newSelected);
  };

  const isSelected = (id) => selectedCustomers.indexOf(id) !== -1;

  const handleBulkActionClick = (event) => {
    setBulkActionMenuAnchor(event.currentTarget);
  };

  const handleBulkActionClose = () => {
    setBulkActionMenuAnchor(null);
  };

  const handleBulkDelete = () => {
    setOpenDeleteConfirmation(true);
    handleBulkActionClose();
  };

  const confirmBulkDelete = async () => {
    try {
      const response = await axios.post('/customers/bulk-delete', { ids: selectedCustomers });
      setSnackbar({
        open: true,
        message: response.data.message,
        severity: 'success'
      });
      setSelectedCustomers([]);
      fetchCustomers();
    } catch (err) {
      setSnackbar({
        open: true,
        message: err.response?.data?.detail || 'An error occurred while deleting customers',
        severity: 'error'
      });
    }
    setOpenDeleteConfirmation(false);
  };

  const handleBulkEdit = () => {
    setOpenBulkEditDialog(true);
    handleBulkActionClose();
  };

  const handleBulkEditInputChange = (e) => {
    setBulkEditData({
      ...bulkEditData,
      [e.target.name]: e.target.value
    });
  };

  const handleBulkEditSubmit = async () => {
    try {
      const response = await axios.post('/customers/bulk-update', {
        updates: bulkEditData,
        ids: selectedCustomers
      });
      setSnackbar({
        open: true,
        message: response.data.message,
        severity: 'success'
      });
      setSelectedCustomers([]);
      setBulkEditData({});
      setOpenBulkEditDialog(false);
      fetchCustomers();
    } catch (err) {
      setSnackbar({
        open: true,
        message: err.response?.data?.detail || 'An error occurred while updating customers',
        severity: 'error'
      });
    }
  };

  const handleImportClick = () => {
    setOpenImportDialog(true);
    handleBulkActionClose();
  };

  const handleFileChange = (e) => {
    setImportFile(e.target.files[0]);
  };

  const handleImportSubmit = async () => {
    if (!importFile) {
      setSnackbar({
        open: true,
        message: 'Please select a file to import',
        severity: 'error'
      });
      return;
    }

    const reader = new FileReader();
    reader.onload = async (e) => {
      try {
        const customers = JSON.parse(e.target.result);
        
        const response = await axios.post('/customers/import', { customers });
        setSnackbar({
          open: true,
          message: response.data.message,
          severity: 'success'
        });
        setOpenImportDialog(false);
        setImportFile(null);
        fetchCustomers();
      } catch (err) {
        setImportErrors(['Invalid JSON format or error processing the file']);
        setSnackbar({
          open: true,
          message: 'Error importing customers',
          severity: 'error'
        });
      }
    };
    reader.readAsText(importFile);
  };

  const handleExport = async () => {
    try {
      const response = await axios.get('/customers/export');
      const data = response.data;
      const jsonString = JSON.stringify(data, null, 2);
      const blob = new Blob([jsonString], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      
      const link = document.createElement('a');
      link.href = url;
      link.download = 'customers_export.json';
      link.click();
      
      URL.revokeObjectURL(url);
      
      setSnackbar({
        open: true,
        message: 'Customers exported successfully',
        severity: 'success'
      });
      handleBulkActionClose();
    } catch (err) {
      setSnackbar({
        open: true,
        message: 'Error exporting customers',
        severity: 'error'
      });
    }
  };

  const handleSnackbarClose = () => {
    setSnackbar({ ...snackbar, open: false });
  };

  return (
    <Box sx={{ p: 3 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 3 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Customers
        </Typography>
        <Box>
          {selectedCustomers.length > 0 ? (
            <Button 
              variant="contained" 
              color="primary"
              startIcon={<MoreVertIcon />}
              onClick={handleBulkActionClick}
              sx={{ mr: 1 }}
            >
              Bulk Actions ({selectedCustomers.length})
            </Button>
          ) : (
            <Button
              variant="outlined"
              startIcon={<FileUploadIcon />}
              onClick={handleImportClick}
              sx={{ mr: 1 }}
            >
              Import
            </Button>
          )}
          <Button
            variant="outlined"
            startIcon={<FileDownloadIcon />}
            onClick={handleExport}
            sx={{ mr: 1 }}
          >
            Export
          </Button>
          <Button
            variant="contained"
            color="primary"
            startIcon={<AddIcon />}
            onClick={() => handleOpenDialog()}
          >
            Add Customer
          </Button>
        </Box>
      </Box>

      <Menu
        anchorEl={bulkActionMenuAnchor}
        open={Boolean(bulkActionMenuAnchor)}
        onClose={handleBulkActionClose}
      >
        <MenuItem onClick={handleBulkEdit}>
          <ListItemIcon>
            <BulkEditIcon fontSize="small" />
          </ListItemIcon>
          <ListItemText>Edit Selected</ListItemText>
        </MenuItem>
        <MenuItem onClick={handleBulkDelete}>
          <ListItemIcon>
            <DeleteSweepIcon fontSize="small" />
          </ListItemIcon>
          <ListItemText>Delete Selected</ListItemText>
        </MenuItem>
      </Menu>

      {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
      
      {loading ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
          <CircularProgress />
        </Box>
      ) : (
        <Box>
          <Grid container spacing={3}>
            {customers.slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage).map((customer) => (
              <Grid item xs={12} sm={6} md={4} key={customer._id}>
                <Card variant="outlined" sx={{ 
                  height: '100%', 
                  display: 'flex', 
                  flexDirection: 'column',
                  border: isSelected(customer._id) ? '2px solid #1976d2' : '1px solid rgba(0, 0, 0, 0.12)'
                }}>
                  <CardContent sx={{ flexGrow: 1, position: 'relative' }}>
                    <Checkbox
                      checked={isSelected(customer._id)}
                      onChange={() => handleSelectCustomer(customer._id)}
                      sx={{ position: 'absolute', top: 0, right: 0 }}
                    />
                    
                    <Typography variant="h6" component="div">
                      {customer.first_name} {customer.last_name}
                    </Typography>
                    
                    <Box sx={{ mt: 2 }}>
                      {customer.contact_info.phone && (
                        <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                          <PhoneIcon fontSize="small" sx={{ mr: 1, color: 'text.secondary' }} />
                          <Typography variant="body2">
                            {customer.contact_info.phone}
                            {customer.contact_info.preferred_contact === 'phone' && (
                              <Chip 
                                label="Preferred" 
                                size="small" 
                                color="primary" 
                                sx={{ ml: 1 }}
                              />
                            )}
                          </Typography>
                        </Box>
                      )}
                      
                      {customer.contact_info.email && (
                        <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                          <EmailIcon fontSize="small" sx={{ mr: 1, color: 'text.secondary' }} />
                          <Typography variant="body2">
                            {customer.contact_info.email}
                            {customer.contact_info.preferred_contact === 'email' && (
                              <Chip 
                                label="Preferred" 
                                size="small" 
                                color="primary" 
                                sx={{ ml: 1 }}
                              />
                            )}
                          </Typography>
                        </Box>
                      )}
                    </Box>
                    
                    {customer.address && (
                      <>
                        <Divider sx={{ my: 1.5 }} />
                        <Box sx={{ display: 'flex', alignItems: 'flex-start' }}>
                          <LocationIcon fontSize="small" sx={{ mr: 1, mt: 0.5, color: 'text.secondary' }} />
                          <Typography variant="body2" component="div">
                            {customer.address.street && (
                              <Box>{customer.address.street}</Box>
                            )}
                            {(customer.address.city || customer.address.state || customer.address.zip_code) && (
                              <Box>
                                {customer.address.city && `${customer.address.city}, `}
                                {customer.address.state && `${customer.address.state} `}
                                {customer.address.zip_code}
                              </Box>
                            )}
                            {customer.address.country && customer.address.country !== 'USA' && (
                              <Box>{customer.address.country}</Box>
                            )}
                          </Typography>
                        </Box>
                      </>
                    )}
                    
                    {customer.notes && (
                      <>
                        <Divider sx={{ my: 1.5 }} />
                        <Typography variant="body2" color="text.secondary">
                          <strong>Notes:</strong> {customer.notes}
                        </Typography>
                      </>
                    )}
                  </CardContent>
                  <CardActions>
                    <Button 
                      size="small" 
                      startIcon={<EditIcon />}
                      onClick={() => handleOpenDialog(customer)}
                    >
                      Edit
                    </Button>
                    <Button 
                      size="small" 
                      color="error" 
                      startIcon={<DeleteIcon />}
                      onClick={() => handleDelete(customer._id)}
                    >
                      Delete
                    </Button>
                  </CardActions>
                </Card>
              </Grid>
            ))}
          </Grid>
          
          <TablePagination
            component="div"
            count={customers.length}
            page={page}
            onPageChange={handleChangePage}
            rowsPerPage={rowsPerPage}
            onRowsPerPageChange={handleChangeRowsPerPage}
            rowsPerPageOptions={[9, 18, 36]}
            sx={{ mt: 2 }}
          />
        </Box>
      )}

      <Dialog open={openBulkEditDialog} onClose={() => setOpenBulkEditDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Bulk Edit Customers</DialogTitle>
        <DialogContent>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            Fields left blank will not be updated. You are editing {selectedCustomers.length} customers.
          </Typography>
          
          <Grid container spacing={2}>
            <Grid item xs={12} sm={6}>
              <TextField
                margin="dense"
                name="notes"
                label="Notes"
                fullWidth
                multiline
                rows={3}
                variant="outlined"
                value={bulkEditData.notes || ''}
                onChange={handleBulkEditInputChange}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth margin="dense">
                <InputLabel>Preferred Contact Method</InputLabel>
                <Select
                  name="contact_info.preferred_contact"
                  value={bulkEditData?.contact_info?.preferred_contact || ''}
                  onChange={(e) => setBulkEditData({
                    ...bulkEditData,
                    contact_info: {
                      ...bulkEditData.contact_info,
                      preferred_contact: e.target.value
                    }
                  })}
                  label="Preferred Contact Method"
                >
                  <MenuItem value="phone">Phone</MenuItem>
                  <MenuItem value="email">Email</MenuItem>
                </Select>
              </FormControl>
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenBulkEditDialog(false)}>Cancel</Button>
          <Button onClick={handleBulkEditSubmit} variant="contained" color="primary">Update</Button>
        </DialogActions>
      </Dialog>

      <Dialog open={openImportDialog} onClose={() => setOpenImportDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Import Customers</DialogTitle>
        <DialogContent>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            Upload a JSON file with customer data to import. The file should contain an array of customer objects.
          </Typography>
          
          <Button
            variant="outlined"
            component="label"
            fullWidth
            sx={{ mt: 2, height: 100, borderStyle: 'dashed' }}
          >
            {importFile ? importFile.name : 'Select JSON File'}
            <input
              type="file"
              accept=".json"
              hidden
              onChange={handleFileChange}
            />
          </Button>
          
          {importErrors.length > 0 && (
            <Alert severity="error" sx={{ mt: 2 }}>
              {importErrors.map((error, index) => (
                <Typography key={index} variant="body2">{error}</Typography>
              ))}
            </Alert>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenImportDialog(false)}>Cancel</Button>
          <Button 
            onClick={handleImportSubmit} 
            variant="contained" 
            color="primary"
            disabled={!importFile}
          >
            Import
          </Button>
        </DialogActions>
      </Dialog>

      <Dialog
        open={openDeleteConfirmation}
        onClose={() => setOpenDeleteConfirmation(false)}
      >
        <DialogTitle>Delete {selectedCustomers.length} Customers?</DialogTitle>
        <DialogContent>
          <Typography>
            Are you sure you want to delete {selectedCustomers.length} customers? This action cannot be undone.
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenDeleteConfirmation(false)}>Cancel</Button>
          <Button onClick={confirmBulkDelete} color="error" variant="contained">
            Delete
          </Button>
        </DialogActions>
      </Dialog>

      <Dialog open={openDialog} onClose={handleCloseDialog} maxWidth="md" fullWidth>
        <DialogTitle>
          {editingCustomer ? 'Edit Customer' : 'Add Customer'}
        </DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 0.5 }}>
            <Grid item xs={12} sm={6}>
              <TextField
                name="first_name"
                label="First Name"
                fullWidth
                value={formData.first_name}
                onChange={handleInputChange}
                required
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                name="last_name"
                label="Last Name"
                fullWidth
                value={formData.last_name}
                onChange={handleInputChange}
                required
              />
            </Grid>
            
            <Grid item xs={12}>
              <Typography variant="subtitle1" sx={{ mt: 1 }}>
                Contact Information
              </Typography>
              <Divider />
            </Grid>
            
            <Grid item xs={12} sm={6}>
              <TextField
                name="contact_info.phone"
                label="Phone Number"
                fullWidth
                value={formData.contact_info.phone}
                onChange={handleInputChange}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                name="contact_info.email"
                label="Email"
                type="email"
                fullWidth
                value={formData.contact_info.email}
                onChange={handleInputChange}
              />
            </Grid>
            <Grid item xs={12}>
              <FormControl fullWidth>
                <InputLabel>Preferred Contact Method</InputLabel>
                <Select
                  name="contact_info.preferred_contact"
                  value={formData.contact_info.preferred_contact}
                  onChange={handleInputChange}
                  label="Preferred Contact Method"
                >
                  <MenuItem value="phone">Phone</MenuItem>
                  <MenuItem value="email">Email</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            
            <Grid item xs={12}>
              <Typography variant="subtitle1" sx={{ mt: 1 }}>
                Address
              </Typography>
              <Divider />
            </Grid>
            
            <Grid item xs={12}>
              <TextField
                name="address.street"
                label="Street Address"
                fullWidth
                value={formData.address.street}
                onChange={handleInputChange}
              />
            </Grid>
            <Grid item xs={12} sm={4}>
              <TextField
                name="address.city"
                label="City"
                fullWidth
                value={formData.address.city}
                onChange={handleInputChange}
              />
            </Grid>
            <Grid item xs={12} sm={4}>
              <TextField
                name="address.state"
                label="State"
                fullWidth
                value={formData.address.state}
                onChange={handleInputChange}
              />
            </Grid>
            <Grid item xs={12} sm={4}>
              <TextField
                name="address.zip_code"
                label="ZIP Code"
                fullWidth
                value={formData.address.zip_code}
                onChange={handleInputChange}
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                name="address.country"
                label="Country"
                fullWidth
                value={formData.address.country}
                onChange={handleInputChange}
              />
            </Grid>
            
            <Grid item xs={12}>
              <Typography variant="subtitle1" sx={{ mt: 1 }}>
                Additional Information
              </Typography>
              <Divider />
            </Grid>
            
            <Grid item xs={12}>
              <TextField
                name="notes"
                label="Notes"
                fullWidth
                multiline
                rows={3}
                value={formData.notes}
                onChange={handleInputChange}
              />
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

      <Snackbar
        open={snackbar.open}
        autoHideDuration={6000}
        onClose={handleSnackbarClose}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
      >
        <Alert onClose={handleSnackbarClose} severity={snackbar.severity}>
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Box>
  );
};

export default Customers; 