import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Button,
  Card,
  CardContent,
  Chip,
  CircularProgress,
  Dialog,
  DialogActions,
  DialogContent,
  DialogContentText,
  DialogTitle,
  Divider,
  Grid,
  IconButton,
  InputAdornment,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TablePagination,
  TableRow,
  TextField,
  Tooltip,
  Typography
} from '@mui/material';
import {
  Add as AddIcon,
  Delete as DeleteIcon,
  Edit as EditIcon,
  ErrorOutline,
  FilterList as FilterIcon,
  PersonAdd,
  Search as SearchIcon,
  SyncAlt,
  Visibility
} from '@mui/icons-material';
import axios from 'axios';
import { useConfig } from '../context/ConfigContext';

const Customers = () => {
  const navigate = useNavigate();
  const { config } = useConfig();
  
  // State for customer data
  const [customers, setCustomers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  // State for pagination
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  
  // State for search and filters
  const [searchTerm, setSearchTerm] = useState('');
  const [filterStatus, setFilterStatus] = useState('all');
  
  // State for dialogs
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [customerToDelete, setCustomerToDelete] = useState(null);
  const [syncDialogOpen, setSyncDialogOpen] = useState(false);
  
  // Fetch customers data
  useEffect(() => {
    const fetchCustomers = async () => {
      try {
        setLoading(true);
        const response = await axios.get('/api/customers', {
          params: {
            search: searchTerm,
            status: filterStatus !== 'all' ? filterStatus : undefined
          }
        });
        setCustomers(response.data);
        setError(null);
      } catch (err) {
        console.error('Failed to fetch customers:', err);
        setError('Failed to load customers. Please try again later.');
      } finally {
        setLoading(false);
      }
    };

    fetchCustomers();
  }, [searchTerm, filterStatus]);

  // Handle search input change
  const handleSearchChange = (event) => {
    setSearchTerm(event.target.value);
    setPage(0); // Reset to first page when searching
  };

  // Handle filter change
  const handleFilterChange = (status) => {
    setFilterStatus(status);
    setPage(0); // Reset to first page when filtering
  };

  // Handle pagination changes
  const handleChangePage = (event, newPage) => {
    setPage(newPage);
  };

  const handleChangeRowsPerPage = (event) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };

  // Dialog handlers
  const handleOpenDeleteDialog = (customer) => {
    setCustomerToDelete(customer);
    setDeleteDialogOpen(true);
  };

  const handleCloseDeleteDialog = () => {
    setDeleteDialogOpen(false);
    setCustomerToDelete(null);
  };

  const handleConfirmDelete = async () => {
    try {
      await axios.delete(`/api/customers/${customerToDelete.id}`);
      
      // Remove the deleted customer from state
      setCustomers(customers.filter(c => c.id !== customerToDelete.id));
      
      handleCloseDeleteDialog();
    } catch (err) {
      console.error('Failed to delete customer:', err);
      setError('Failed to delete customer. Please try again.');
      handleCloseDeleteDialog();
    }
  };

  const handleOpenSyncDialog = () => {
    setSyncDialogOpen(true);
  };

  const handleCloseSyncDialog = () => {
    setSyncDialogOpen(false);
  };

  const handleSyncCustomers = async () => {
    try {
      setLoading(true);
      const response = await axios.post('/api/integrations/sync-customers');
      
      if (response.data.success) {
        // Refresh customer list after sync
        const customerResponse = await axios.get('/api/customers');
        setCustomers(customerResponse.data);
      }
      
      handleCloseSyncDialog();
    } catch (err) {
      console.error('Failed to sync customers:', err);
      setError('Failed to sync customers. Please try again.');
      handleCloseSyncDialog();
    } finally {
      setLoading(false);
    }
  };

  // Navigate to customer details
  const handleViewCustomer = (customerId) => {
    navigate(`/customers/${customerId}`);
  };

  // Navigate to edit customer
  const handleEditCustomer = (customerId) => {
    navigate(`/customers/${customerId}/edit`);
  };

  // Navigate to add new customer
  const handleAddCustomer = () => {
    navigate('/customers/new');
  };

  // Render loading state
  if (loading && customers.length === 0) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" height="80vh">
        <CircularProgress />
      </Box>
    );
  }

  // Render error state
  if (error && customers.length === 0) {
    return (
      <Paper sx={{ p: 3, m: 2, textAlign: 'center', color: 'error.main' }}>
        <ErrorOutline sx={{ fontSize: 60, mb: 2 }} />
        <Typography variant="h6">{error}</Typography>
        <Button
          variant="contained"
          color="primary"
          sx={{ mt: 2 }}
          onClick={() => window.location.reload()}
        >
          Retry
        </Button>
      </Paper>
    );
  }

  return (
    <Box p={3}>
      <Grid container spacing={3}>
        <Grid item xs={12}>
          <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
            <Typography variant="h4">Customers</Typography>
            <Box>
              {(config.integrations.ghl.enabled || config.integrations.kickserv.enabled) && (
                <Button
                  variant="outlined"
                  color="primary"
                  startIcon={<SyncAlt />}
                  onClick={handleOpenSyncDialog}
                  sx={{ mr: 1 }}
                >
                  Sync
                </Button>
              )}
              <Button
                variant="contained"
                color="primary"
                startIcon={<AddIcon />}
                onClick={handleAddCustomer}
              >
                Add Customer
              </Button>
            </Box>
          </Box>
        </Grid>

        <Grid item xs={12}>
          <Card sx={{ mb: 3 }}>
            <CardContent>
              <Grid container spacing={2} alignItems="center">
                <Grid item xs={12} sm={6} md={8}>
                  <TextField
                    fullWidth
                    placeholder="Search customers by name, email, or phone"
                    value={searchTerm}
                    onChange={handleSearchChange}
                    InputProps={{
                      startAdornment: (
                        <InputAdornment position="start">
                          <SearchIcon />
                        </InputAdornment>
                      ),
                    }}
                  />
                </Grid>
                <Grid item xs={12} sm={6} md={4}>
                  <Box display="flex" justifyContent={{ xs: 'flex-start', sm: 'flex-end' }}>
                    <Button
                      color={filterStatus === 'all' ? 'primary' : 'inherit'}
                      onClick={() => handleFilterChange('all')}
                      sx={{ mr: 1 }}
                    >
                      All
                    </Button>
                    <Button
                      color={filterStatus === 'active' ? 'primary' : 'inherit'}
                      onClick={() => handleFilterChange('active')}
                      sx={{ mr: 1 }}
                    >
                      Active
                    </Button>
                    <Button
                      color={filterStatus === 'inactive' ? 'primary' : 'inherit'}
                      onClick={() => handleFilterChange('inactive')}
                    >
                      Inactive
                    </Button>
                    <Tooltip title="More filters">
                      <IconButton>
                        <FilterIcon />
                      </IconButton>
                    </Tooltip>
                  </Box>
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12}>
          <TableContainer component={Paper}>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Name</TableCell>
                  <TableCell>Email</TableCell>
                  <TableCell>Phone</TableCell>
                  <TableCell>Jobs</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell>Source</TableCell>
                  <TableCell align="right">Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {customers.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={7} align="center">
                      <Box py={3}>
                        <PersonAdd sx={{ fontSize: 60, color: 'text.secondary', mb: 2 }} />
                        <Typography variant="h6" gutterBottom>No customers found</Typography>
                        <Typography variant="body2" color="textSecondary" gutterBottom>
                          Get started by adding your first customer
                        </Typography>
                        <Button
                          variant="contained"
                          color="primary"
                          startIcon={<AddIcon />}
                          onClick={handleAddCustomer}
                          sx={{ mt: 2 }}
                        >
                          Add Customer
                        </Button>
                      </Box>
                    </TableCell>
                  </TableRow>
                ) : (
                  customers
                    .slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage)
                    .map((customer) => (
                      <TableRow key={customer.id} hover>
                        <TableCell>
                          <Box display="flex" alignItems="center">
                            <Typography variant="body1" fontWeight="medium">
                              {customer.name}
                            </Typography>
                          </Box>
                        </TableCell>
                        <TableCell>{customer.email}</TableCell>
                        <TableCell>{customer.phone}</TableCell>
                        <TableCell>{customer.jobCount || 0}</TableCell>
                        <TableCell>
                          <Chip
                            label={customer.status}
                            color={customer.status === 'active' ? 'success' : 'default'}
                            size="small"
                          />
                        </TableCell>
                        <TableCell>
                          {customer.source && (
                            <Chip
                              label={customer.source}
                              variant="outlined"
                              size="small"
                            />
                          )}
                        </TableCell>
                        <TableCell align="right">
                          <Tooltip title="View details">
                            <IconButton
                              size="small"
                              onClick={() => handleViewCustomer(customer.id)}
                            >
                              <Visibility />
                            </IconButton>
                          </Tooltip>
                          <Tooltip title="Edit customer">
                            <IconButton
                              size="small"
                              onClick={() => handleEditCustomer(customer.id)}
                            >
                              <EditIcon />
                            </IconButton>
                          </Tooltip>
                          <Tooltip title="Delete customer">
                            <IconButton
                              size="small"
                              color="error"
                              onClick={() => handleOpenDeleteDialog(customer)}
                            >
                              <DeleteIcon />
                            </IconButton>
                          </Tooltip>
                        </TableCell>
                      </TableRow>
                    ))
                )}
              </TableBody>
            </Table>
            {customers.length > 0 && (
              <TablePagination
                rowsPerPageOptions={[5, 10, 25]}
                component="div"
                count={customers.length}
                rowsPerPage={rowsPerPage}
                page={page}
                onPageChange={handleChangePage}
                onRowsPerPageChange={handleChangeRowsPerPage}
              />
            )}
          </TableContainer>
        </Grid>
      </Grid>

      {/* Delete Confirmation Dialog */}
      <Dialog
        open={deleteDialogOpen}
        onClose={handleCloseDeleteDialog}
      >
        <DialogTitle>Delete Customer</DialogTitle>
        <DialogContent>
          <DialogContentText>
            Are you sure you want to delete {customerToDelete?.name}? This action cannot be undone.
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDeleteDialog}>Cancel</Button>
          <Button onClick={handleConfirmDelete} color="error" autoFocus>
            Delete
          </Button>
        </DialogActions>
      </Dialog>

      {/* Sync Confirmation Dialog */}
      <Dialog
        open={syncDialogOpen}
        onClose={handleCloseSyncDialog}
      >
        <DialogTitle>Sync Customers</DialogTitle>
        <DialogContent>
          <DialogContentText>
            This will synchronize customers with your connected integration(s):
            <Box component="ul" sx={{ mt: 1 }}>
              {config.integrations.ghl.enabled && (
                <li>Go High Level {config.integrations.ghl.connected ? '(Connected)' : '(Disconnected)'}</li>
              )}
              {config.integrations.kickserv.enabled && (
                <li>Kickserv {config.integrations.kickserv.connected ? '(Connected)' : '(Disconnected)'}</li>
              )}
            </Box>
            Do you want to continue?
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseSyncDialog}>Cancel</Button>
          <Button onClick={handleSyncCustomers} color="primary" autoFocus>
            Sync Now
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default Customers; 