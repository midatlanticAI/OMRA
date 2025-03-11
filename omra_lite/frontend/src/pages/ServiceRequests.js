import React, { useState, useEffect } from 'react';
import {
  Typography,
  Box,
  Paper,
  Button,
  Grid,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Chip,
  IconButton,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TablePagination,
  Alert,
  CircularProgress,
  Checkbox,
  Menu,
  ListItemIcon,
  ListItemText,
  Tooltip,
  Snackbar
} from '@mui/material';
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  MoreVert as MoreVertIcon,
  DeleteSweep as DeleteSweepIcon,
  Edit as BulkEditIcon,
  FileUpload as FileUploadIcon,
  FileDownload as FileDownloadIcon
} from '@mui/icons-material';
import { format } from 'date-fns';
import axios from 'axios';

const ServiceRequests = () => {
  const [serviceRequests, setServiceRequests] = useState([]);
  const [customers, setCustomers] = useState([]);
  const [technicians, setTechnicians] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [openDialog, setOpenDialog] = useState(false);
  const [editingRequest, setEditingRequest] = useState(null);
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [formData, setFormData] = useState({
    customer_id: '',
    appliance_type: '',
    issue_description: '',
    priority: 'medium',
    status: 'pending',
    scheduled_date: '',
    technician_id: '',
    notes: ''
  });

  // New state variables for bulk actions and import/export
  const [selectedRequests, setSelectedRequests] = useState([]);
  const [bulkActionMenuAnchor, setBulkActionMenuAnchor] = useState(null);
  const [openBulkEditDialog, setOpenBulkEditDialog] = useState(false);
  const [bulkEditData, setBulkEditData] = useState({});
  const [importFile, setImportFile] = useState(null);
  const [openImportDialog, setOpenImportDialog] = useState(false);
  const [importErrors, setImportErrors] = useState([]);
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'info' });
  const [openDeleteConfirmation, setOpenDeleteConfirmation] = useState(false);

  // Fetch data on component mount
  useEffect(() => {
    fetchServiceRequests();
    fetchCustomers();
    fetchTechnicians();
  }, []);

  const fetchServiceRequests = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await axios.get('/api/service-requests');
      setServiceRequests(response.data);
    } catch (err) {
      console.error('Error fetching service requests:', err);
      setError('Failed to load service requests. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const fetchCustomers = async () => {
    try {
      const response = await axios.get('/api/customers');
      setCustomers(response.data);
    } catch (err) {
      console.error('Error fetching customers:', err);
    }
  };

  const fetchTechnicians = async () => {
    try {
      const response = await axios.get('/api/technicians');
      setTechnicians(response.data);
    } catch (err) {
      console.error('Error fetching technicians:', err);
    }
  };

  const handleOpenDialog = (request = null) => {
    if (request) {
      // Edit mode
      setEditingRequest(request);
      setFormData({
        customer_id: request.customer_id,
        appliance_type: request.appliance_type,
        issue_description: request.issue_description,
        priority: request.priority,
        status: request.status,
        scheduled_date: request.scheduled_date ? request.scheduled_date.substring(0, 16) : '',
        technician_id: request.technician_id || '',
        notes: request.notes || ''
      });
    } else {
      // Create mode
      setEditingRequest(null);
      setFormData({
        customer_id: '',
        appliance_type: '',
        issue_description: '',
        priority: 'medium',
        status: 'pending',
        scheduled_date: '',
        technician_id: '',
        notes: ''
      });
    }
    setOpenDialog(true);
  };

  const handleCloseDialog = () => {
    setOpenDialog(false);
    setEditingRequest(null);
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      [name]: value
    });
  };

  const validateForm = () => {
    if (!formData.customer_id) {
      return 'Customer is required';
    }
    if (!formData.appliance_type) {
      return 'Appliance type is required';
    }
    if (!formData.issue_description.trim()) {
      return 'Issue description is required';
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
      if (editingRequest) {
        // Update existing service request
        response = await axios.put(`/api/service-requests/${editingRequest._id}`, formData);
        
        // Update the service requests array with the updated item
        setServiceRequests(serviceRequests.map(item => 
          item._id === editingRequest._id ? response.data : item
        ));
      } else {
        // Create new service request
        response = await axios.post('/api/service-requests', formData);
        
        // Add the new service request to the array
        setServiceRequests([response.data, ...serviceRequests]);
      }

      handleCloseDialog();
    } catch (err) {
      console.error('Error saving service request:', err);
      setError(err.response?.data?.detail || 'Failed to save service request. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Are you sure you want to delete this service request?')) {
      return;
    }

    setLoading(true);
    setError(null);

    try {
      await axios.delete(`/api/service-requests/${id}`);
      
      // Remove the deleted service request from the array
      setServiceRequests(serviceRequests.filter(item => item._id !== id));
    } catch (err) {
      console.error('Error deleting service request:', err);
      setError(err.response?.data?.detail || 'Failed to delete service request. Please try again.');
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

  const getCustomerName = (customerId) => {
    const customer = customers.find(c => c._id === customerId);
    return customer ? `${customer.first_name} ${customer.last_name}` : 'Unknown';
  };

  const getTechnicianName = (technicianId) => {
    if (!technicianId) return 'Not assigned';
    const technician = technicians.find(t => t._id === technicianId);
    return technician ? `${technician.first_name} ${technician.last_name}` : 'Unknown';
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'pending':
        return 'warning';
      case 'scheduled':
        return 'info';
      case 'in_progress':
        return 'primary';
      case 'completed':
        return 'success';
      case 'cancelled':
        return 'error';
      default:
        return 'default';
    }
  };

  const getPriorityColor = (priority) => {
    switch (priority) {
      case 'low':
        return 'success';
      case 'medium':
        return 'info';
      case 'high':
        return 'warning';
      case 'urgent':
        return 'error';
      default:
        return 'default';
    }
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'Not scheduled';
    try {
      return format(new Date(dateString), 'MMM d, yyyy h:mm a');
    } catch (err) {
      return dateString;
    }
  };

  // Bulk action functions
  const handleSelectAll = (event) => {
    if (event.target.checked) {
      setSelectedRequests(serviceRequests.map(request => request._id));
    } else {
      setSelectedRequests([]);
    }
  };

  const handleSelectRequest = (id) => {
    const selectedIndex = selectedRequests.indexOf(id);
    let newSelected = [];

    if (selectedIndex === -1) {
      newSelected = [...selectedRequests, id];
    } else {
      newSelected = selectedRequests.filter(requestId => requestId !== id);
    }

    setSelectedRequests(newSelected);
  };

  const isSelected = (id) => selectedRequests.indexOf(id) !== -1;

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
      const response = await axios.post('/service-requests/bulk-delete', { ids: selectedRequests });
      setSnackbar({
        open: true,
        message: response.data.message,
        severity: 'success'
      });
      setSelectedRequests([]);
      fetchServiceRequests();
    } catch (err) {
      setSnackbar({
        open: true,
        message: err.response?.data?.detail || 'An error occurred while deleting service requests',
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
      const response = await axios.post('/service-requests/bulk-update', {
        updates: bulkEditData,
        ids: selectedRequests
      });
      setSnackbar({
        open: true,
        message: response.data.message,
        severity: 'success'
      });
      setSelectedRequests([]);
      setBulkEditData({});
      setOpenBulkEditDialog(false);
      fetchServiceRequests();
    } catch (err) {
      setSnackbar({
        open: true,
        message: err.response?.data?.detail || 'An error occurred while updating service requests',
        severity: 'error'
      });
    }
  };

  // Import/Export functions
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
        const serviceRequests = JSON.parse(e.target.result);
        
        const response = await axios.post('/service-requests/import', { service_requests: serviceRequests });
        setSnackbar({
          open: true,
          message: response.data.message,
          severity: 'success'
        });
        setOpenImportDialog(false);
        setImportFile(null);
        fetchServiceRequests();
      } catch (err) {
        setImportErrors(['Invalid JSON format or error processing the file']);
        setSnackbar({
          open: true,
          message: 'Error importing service requests',
          severity: 'error'
        });
      }
    };
    reader.readAsText(importFile);
  };

  const handleExport = async () => {
    try {
      const response = await axios.get('/service-requests/export');
      const data = response.data;
      const jsonString = JSON.stringify(data, null, 2);
      const blob = new Blob([jsonString], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      
      const link = document.createElement('a');
      link.href = url;
      link.download = 'service_requests_export.json';
      link.click();
      
      URL.revokeObjectURL(url);
      
      setSnackbar({
        open: true,
        message: 'Service requests exported successfully',
        severity: 'success'
      });
      handleBulkActionClose();
    } catch (err) {
      setSnackbar({
        open: true,
        message: 'Error exporting service requests',
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
          Service Requests
        </Typography>
        <Box>
          {selectedRequests.length > 0 ? (
            <Button 
              variant="contained" 
              color="primary"
              startIcon={<MoreVertIcon />}
              onClick={handleBulkActionClick}
              sx={{ mr: 1 }}
            >
              Bulk Actions ({selectedRequests.length})
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
            New Request
          </Button>
        </Box>
      </Box>

      {/* Bulk Actions Menu */}
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

      {/* Main Content */}
      {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
      
      {loading ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
          <CircularProgress />
        </Box>
      ) : (
        <Paper sx={{ width: '100%', overflow: 'hidden' }}>
          <TableContainer sx={{ maxHeight: 'calc(100vh - 250px)' }}>
            <Table stickyHeader>
              <TableHead>
                <TableRow>
                  <TableCell padding="checkbox">
                    <Checkbox
                      indeterminate={selectedRequests.length > 0 && selectedRequests.length < serviceRequests.length}
                      checked={serviceRequests.length > 0 && selectedRequests.length === serviceRequests.length}
                      onChange={handleSelectAll}
                    />
                  </TableCell>
                  <TableCell>Customer</TableCell>
                  <TableCell>Appliance</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell>Priority</TableCell>
                  <TableCell>Created</TableCell>
                  <TableCell>Scheduled</TableCell>
                  <TableCell>Technician</TableCell>
                  <TableCell>Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {serviceRequests
                  .slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage)
                  .map((request) => {
                    const isItemSelected = isSelected(request._id);
                    return (
                      <TableRow 
                        hover 
                        key={request._id}
                        selected={isItemSelected}
                        sx={{ '&.Mui-selected, &.Mui-selected:hover': { backgroundColor: 'rgba(25, 118, 210, 0.08)' } }}
                      >
                        <TableCell padding="checkbox">
                          <Checkbox
                            checked={isItemSelected}
                            onClick={() => handleSelectRequest(request._id)}
                          />
                        </TableCell>
                        <TableCell>{getCustomerName(request.customer_id)}</TableCell>
                        <TableCell>{request.appliance_type}</TableCell>
                        <TableCell>
                          <Chip 
                            label={request.status} 
                            sx={{ 
                              backgroundColor: getStatusColor(request.status),
                              color: 'white',
                              textTransform: 'capitalize'
                            }} 
                          />
                        </TableCell>
                        <TableCell>
                          <Chip 
                            label={request.priority} 
                            sx={{ 
                              backgroundColor: getPriorityColor(request.priority),
                              color: 'white',
                              textTransform: 'capitalize'
                            }} 
                          />
                        </TableCell>
                        <TableCell>{formatDate(request.created_at)}</TableCell>
                        <TableCell>{request.scheduled_date ? formatDate(request.scheduled_date) : 'Not scheduled'}</TableCell>
                        <TableCell>{request.technician_id ? getTechnicianName(request.technician_id) : 'Unassigned'}</TableCell>
                        <TableCell>
                          <Tooltip title="Edit">
                            <IconButton size="small" onClick={() => handleOpenDialog(request)}>
                              <EditIcon />
                            </IconButton>
                          </Tooltip>
                          <Tooltip title="Delete">
                            <IconButton size="small" color="error" onClick={() => handleDelete(request._id)}>
                              <DeleteIcon />
                            </IconButton>
                          </Tooltip>
                        </TableCell>
                      </TableRow>
                    );
                  })}
              </TableBody>
            </Table>
          </TableContainer>
          <TablePagination
            component="div"
            count={serviceRequests.length}
            page={page}
            onPageChange={handleChangePage}
            rowsPerPage={rowsPerPage}
            onRowsPerPageChange={handleChangeRowsPerPage}
            rowsPerPageOptions={[5, 10, 25, 50]}
          />
        </Paper>
      )}

      {/* Bulk Edit Dialog */}
      <Dialog open={openBulkEditDialog} onClose={() => setOpenBulkEditDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Bulk Edit Service Requests</DialogTitle>
        <DialogContent>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            Fields left blank will not be updated. You are editing {selectedRequests.length} service requests.
          </Typography>
          
          <Grid container spacing={2}>
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth margin="dense">
                <InputLabel>Status</InputLabel>
                <Select
                  name="status"
                  value={bulkEditData.status || ''}
                  onChange={handleBulkEditInputChange}
                  label="Status"
                >
                  <MenuItem value="pending">Pending</MenuItem>
                  <MenuItem value="scheduled">Scheduled</MenuItem>
                  <MenuItem value="in_progress">In Progress</MenuItem>
                  <MenuItem value="completed">Completed</MenuItem>
                  <MenuItem value="cancelled">Cancelled</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth margin="dense">
                <InputLabel>Priority</InputLabel>
                <Select
                  name="priority"
                  value={bulkEditData.priority || ''}
                  onChange={handleBulkEditInputChange}
                  label="Priority"
                >
                  <MenuItem value="low">Low</MenuItem>
                  <MenuItem value="medium">Medium</MenuItem>
                  <MenuItem value="high">High</MenuItem>
                  <MenuItem value="urgent">Urgent</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth margin="dense">
                <InputLabel>Technician</InputLabel>
                <Select
                  name="technician_id"
                  value={bulkEditData.technician_id || ''}
                  onChange={handleBulkEditInputChange}
                  label="Technician"
                >
                  <MenuItem value="">Unassigned</MenuItem>
                  {technicians.map(tech => (
                    <MenuItem key={tech._id} value={tech._id}>
                      {tech.first_name} {tech.last_name}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
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
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenBulkEditDialog(false)}>Cancel</Button>
          <Button onClick={handleBulkEditSubmit} variant="contained" color="primary">Update</Button>
        </DialogActions>
      </Dialog>

      {/* Import Dialog */}
      <Dialog open={openImportDialog} onClose={() => setOpenImportDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Import Service Requests</DialogTitle>
        <DialogContent>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            Upload a JSON file with service request data to import. The file should contain an array of service request objects.
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

      {/* Delete Confirmation Dialog */}
      <Dialog
        open={openDeleteConfirmation}
        onClose={() => setOpenDeleteConfirmation(false)}
      >
        <DialogTitle>Delete {selectedRequests.length} Service Requests?</DialogTitle>
        <DialogContent>
          <Typography>
            Are you sure you want to delete {selectedRequests.length} service requests? This action cannot be undone.
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenDeleteConfirmation(false)}>Cancel</Button>
          <Button onClick={confirmBulkDelete} color="error" variant="contained">
            Delete
          </Button>
        </DialogActions>
      </Dialog>

      {/* Create/Edit Dialog */}
      <Dialog open={openDialog} onClose={handleCloseDialog} maxWidth="md" fullWidth>
        <DialogTitle>
          {editingRequest ? 'Edit Service Request' : 'Create Service Request'}
        </DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 0.5 }}>
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth>
                <InputLabel>Customer</InputLabel>
                <Select
                  name="customer_id"
                  value={formData.customer_id}
                  onChange={handleInputChange}
                  label="Customer"
                  required
                >
                  {customers.map(customer => (
                    <MenuItem key={customer._id} value={customer._id}>
                      {customer.first_name} {customer.last_name}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth>
                <InputLabel>Appliance Type</InputLabel>
                <Select
                  name="appliance_type"
                  value={formData.appliance_type}
                  onChange={handleInputChange}
                  label="Appliance Type"
                  required
                >
                  <MenuItem value="refrigerator">Refrigerator</MenuItem>
                  <MenuItem value="washer">Washer</MenuItem>
                  <MenuItem value="dryer">Dryer</MenuItem>
                  <MenuItem value="dishwasher">Dishwasher</MenuItem>
                  <MenuItem value="stove">Stove</MenuItem>
                  <MenuItem value="oven">Oven</MenuItem>
                  <MenuItem value="microwave">Microwave</MenuItem>
                  <MenuItem value="other">Other</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12}>
              <TextField
                name="issue_description"
                label="Issue Description"
                fullWidth
                multiline
                rows={3}
                value={formData.issue_description}
                onChange={handleInputChange}
                required
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth>
                <InputLabel>Priority</InputLabel>
                <Select
                  name="priority"
                  value={formData.priority}
                  onChange={handleInputChange}
                  label="Priority"
                >
                  <MenuItem value="low">Low</MenuItem>
                  <MenuItem value="medium">Medium</MenuItem>
                  <MenuItem value="high">High</MenuItem>
                  <MenuItem value="urgent">Urgent</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth>
                <InputLabel>Status</InputLabel>
                <Select
                  name="status"
                  value={formData.status}
                  onChange={handleInputChange}
                  label="Status"
                >
                  <MenuItem value="pending">Pending</MenuItem>
                  <MenuItem value="scheduled">Scheduled</MenuItem>
                  <MenuItem value="in_progress">In Progress</MenuItem>
                  <MenuItem value="completed">Completed</MenuItem>
                  <MenuItem value="cancelled">Cancelled</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                name="scheduled_date"
                label="Scheduled Date"
                type="datetime-local"
                fullWidth
                value={formData.scheduled_date}
                onChange={handleInputChange}
                InputLabelProps={{
                  shrink: true,
                }}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth>
                <InputLabel>Technician</InputLabel>
                <Select
                  name="technician_id"
                  value={formData.technician_id}
                  onChange={handleInputChange}
                  label="Technician"
                >
                  <MenuItem value="">Not assigned</MenuItem>
                  {technicians.map(technician => (
                    <MenuItem key={technician._id} value={technician._id}>
                      {technician.first_name} {technician.last_name}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12}>
              <TextField
                name="notes"
                label="Notes"
                fullWidth
                multiline
                rows={2}
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

      {/* Snackbar for notifications */}
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

export default ServiceRequests; 