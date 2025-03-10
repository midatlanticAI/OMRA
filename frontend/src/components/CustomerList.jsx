import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TablePagination,
  Button,
  IconButton,
  TextField,
  InputAdornment,
  Chip,
  Dialog,
  DialogActions,
  DialogContent,
  DialogContentText,
  DialogTitle,
  Snackbar,
  Alert,
  Tooltip,
  Grid
} from '@mui/material';
import {
  Search as SearchIcon,
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Visibility as ViewIcon,
  Sync as SyncIcon,
  FilterList as FilterIcon
} from '@mui/icons-material';

// Mock customer data
const mockCustomers = [
  {
    id: '1001',
    name: 'John Doe',
    email: 'john.doe@example.com',
    phone: '(555) 123-4567',
    address: '123 Main St, Anytown, CA 94568',
    status: 'active',
    synced: true,
    lastServiceDate: '2023-04-10'
  },
  {
    id: '1002',
    name: 'Jane Smith',
    email: 'jane.smith@example.com',
    phone: '(555) 987-6543',
    address: '456 Oak Ave, Somewhere, CA 94123',
    status: 'active',
    synced: true,
    lastServiceDate: '2023-03-22'
  },
  {
    id: '1003',
    name: 'Robert Johnson',
    email: 'robert.johnson@example.com',
    phone: '(555) 456-7890',
    address: '789 Pine St, Nowhere, CA 95123',
    status: 'inactive',
    synced: false,
    lastServiceDate: '2022-11-15'
  },
  {
    id: '1004',
    name: 'Emily Davis',
    email: 'emily.davis@example.com',
    phone: '(555) 789-0123',
    address: '321 Elm Dr, Elsewhere, CA 93456',
    status: 'active',
    synced: true,
    lastServiceDate: '2023-04-28'
  },
  {
    id: '1005',
    name: 'Michael Wilson',
    email: 'michael.wilson@example.com',
    phone: '(555) 234-5678',
    address: '654 Cedar Ln, Anywhere, CA 92789',
    status: 'active',
    synced: false,
    lastServiceDate: '2023-02-05'
  }
];

const CustomerList = () => {
  const [customers, setCustomers] = useState([]);
  const [filteredCustomers, setFilteredCustomers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [searchTerm, setSearchTerm] = useState('');
  const [openDeleteDialog, setOpenDeleteDialog] = useState(false);
  const [customerToDelete, setCustomerToDelete] = useState(null);
  const [snackbar, setSnackbar] = useState({
    open: false,
    message: '',
    severity: 'success'
  });

  // Load customer data
  useEffect(() => {
    const fetchData = async () => {
      try {
        // In a real app, this would be an API call
        await new Promise(resolve => setTimeout(resolve, 1000));
        setCustomers(mockCustomers);
        setFilteredCustomers(mockCustomers);
      } catch (error) {
        console.error('Error fetching customers:', error);
        setSnackbar({
          open: true,
          message: 'Failed to load customers',
          severity: 'error'
        });
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  // Handle search
  useEffect(() => {
    if (searchTerm.trim() === '') {
      setFilteredCustomers(customers);
    } else {
      const filtered = customers.filter(customer => 
        customer.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        customer.email.toLowerCase().includes(searchTerm.toLowerCase()) ||
        customer.phone.includes(searchTerm) ||
        customer.address.toLowerCase().includes(searchTerm.toLowerCase())
      );
      setFilteredCustomers(filtered);
    }
    setPage(0); // Reset to first page when searching
  }, [searchTerm, customers]);

  // Handle pagination
  const handleChangePage = (event, newPage) => {
    setPage(newPage);
  };

  const handleChangeRowsPerPage = (event) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };

  // Handle delete
  const handleOpenDeleteDialog = (customer) => {
    setCustomerToDelete(customer);
    setOpenDeleteDialog(true);
  };

  const handleCloseDeleteDialog = () => {
    setOpenDeleteDialog(false);
    setCustomerToDelete(null);
  };

  const handleDeleteCustomer = () => {
    if (customerToDelete) {
      // In a real app, this would be an API call
      setCustomers(customers.filter(c => c.id !== customerToDelete.id));
      setFilteredCustomers(filteredCustomers.filter(c => c.id !== customerToDelete.id));
      setSnackbar({
        open: true,
        message: `Customer ${customerToDelete.name} has been deleted`,
        severity: 'success'
      });
    }
    handleCloseDeleteDialog();
  };

  // Handle sync with CRM
  const handleSyncCustomer = (customerId) => {
    // In a real app, this would be an API call to sync with GHL
    setCustomers(customers.map(c => 
      c.id === customerId ? { ...c, synced: true } : c
    ));
    setFilteredCustomers(filteredCustomers.map(c => 
      c.id === customerId ? { ...c, synced: true } : c
    ));
    setSnackbar({
      open: true,
      message: 'Customer synced with CRM',
      severity: 'success'
    });
  };

  const handleCloseSnackbar = () => {
    setSnackbar({ ...snackbar, open: false });
  };

  return (
    <Box sx={{ flexGrow: 1, p: 3 }}>
      <Typography variant="h4" gutterBottom>
        Customers
      </Typography>

      {/* Search and Actions Toolbar */}
      <Grid container spacing={2} sx={{ mb: 3 }} alignItems="center">
        <Grid item xs={12} md={6}>
          <TextField
            fullWidth
            variant="outlined"
            placeholder="Search customers..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <SearchIcon />
                </InputAdornment>
              ),
            }}
          />
        </Grid>
        <Grid item xs={12} md={6} sx={{ display: 'flex', justifyContent: { xs: 'flex-start', md: 'flex-end' } }}>
          <Button 
            variant="outlined" 
            startIcon={<FilterIcon />} 
            sx={{ mr: 1 }}
          >
            Filter
          </Button>
          <Button 
            variant="contained" 
            startIcon={<AddIcon />}
          >
            Add Customer
          </Button>
        </Grid>
      </Grid>

      {/* Customers Table */}
      <TableContainer component={Paper}>
        <Table size="medium">
          <TableHead>
            <TableRow>
              <TableCell>Name</TableCell>
              <TableCell>Email</TableCell>
              <TableCell>Phone</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>Last Service</TableCell>
              <TableCell align="center">Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {loading ? (
              <TableRow>
                <TableCell colSpan={6} align="center">
                  <Typography variant="body1">Loading customers...</Typography>
                </TableCell>
              </TableRow>
            ) : filteredCustomers.length === 0 ? (
              <TableRow>
                <TableCell colSpan={6} align="center">
                  <Typography variant="body1">No customers found</Typography>
                </TableCell>
              </TableRow>
            ) : (
              filteredCustomers
                .slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage)
                .map((customer) => (
                  <TableRow key={customer.id}>
                    <TableCell>{customer.name}</TableCell>
                    <TableCell>{customer.email}</TableCell>
                    <TableCell>{customer.phone}</TableCell>
                    <TableCell>
                      <Chip 
                        label={customer.status} 
                        color={customer.status === 'active' ? 'success' : 'default'}
                        size="small"
                      />
                    </TableCell>
                    <TableCell>{new Date(customer.lastServiceDate).toLocaleDateString()}</TableCell>
                    <TableCell align="center">
                      <Tooltip title="View Details">
                        <IconButton size="small" color="primary">
                          <ViewIcon />
                        </IconButton>
                      </Tooltip>
                      <Tooltip title="Edit Customer">
                        <IconButton size="small" color="primary">
                          <EditIcon />
                        </IconButton>
                      </Tooltip>
                      {!customer.synced && (
                        <Tooltip title="Sync with CRM">
                          <IconButton 
                            size="small" 
                            color="secondary"
                            onClick={() => handleSyncCustomer(customer.id)}
                          >
                            <SyncIcon />
                          </IconButton>
                        </Tooltip>
                      )}
                      <Tooltip title="Delete Customer">
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
        <TablePagination
          rowsPerPageOptions={[5, 10, 25]}
          component="div"
          count={filteredCustomers.length}
          rowsPerPage={rowsPerPage}
          page={page}
          onPageChange={handleChangePage}
          onRowsPerPageChange={handleChangeRowsPerPage}
        />
      </TableContainer>

      {/* Delete Confirmation Dialog */}
      <Dialog
        open={openDeleteDialog}
        onClose={handleCloseDeleteDialog}
      >
        <DialogTitle>Confirm Deletion</DialogTitle>
        <DialogContent>
          <DialogContentText>
            Are you sure you want to delete customer {customerToDelete?.name}? This action cannot be undone.
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDeleteDialog}>Cancel</Button>
          <Button onClick={handleDeleteCustomer} color="error" variant="contained">
            Delete
          </Button>
        </DialogActions>
      </Dialog>

      {/* Snackbar for notifications */}
      <Snackbar
        open={snackbar.open}
        autoHideDuration={6000}
        onClose={handleCloseSnackbar}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
      >
        <Alert 
          onClose={handleCloseSnackbar} 
          severity={snackbar.severity} 
          sx={{ width: '100%' }}
        >
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Box>
  );
};

export default CustomerList; 