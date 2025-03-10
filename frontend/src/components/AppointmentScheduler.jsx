import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Paper,
  Grid,
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogContentText,
  DialogTitle,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Snackbar,
  Alert,
  CircularProgress,
  IconButton,
  Chip,
  Divider,
  FormHelperText,
  Stack
} from '@mui/material';
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Event as EventIcon,
  AccessTime as TimeIcon,
  Person as PersonIcon,
  Sync as SyncIcon
} from '@mui/icons-material';
import { useFormik } from 'formik';
import * as Yup from 'yup';
import { styled } from '@mui/material/styles';

// Styled components for calendar view
const DayHeader = styled(Box)(({ theme }) => ({
  backgroundColor: theme.palette.primary.main,
  color: theme.palette.primary.contrastText,
  padding: theme.spacing(1),
  textAlign: 'center',
  borderRadius: theme.shape.borderRadius,
  marginBottom: theme.spacing(1)
}));

const TimeSlot = styled(Box)(({ theme, isOccupied }) => ({
  padding: theme.spacing(1),
  marginBottom: theme.spacing(1),
  backgroundColor: isOccupied ? theme.palette.grey[100] : 'transparent',
  border: `1px solid ${isOccupied ? theme.palette.primary.main : theme.palette.divider}`,
  borderRadius: theme.shape.borderRadius,
  cursor: isOccupied ? 'pointer' : 'default',
  '&:hover': {
    backgroundColor: isOccupied ? theme.palette.action.hover : 'transparent',
  }
}));

const AppointmentCard = styled(Paper)(({ theme, status }) => {
  const getStatusColor = () => {
    switch (status) {
      case 'pending':
        return theme.palette.warning.light;
      case 'confirmed':
        return theme.palette.success.light;
      case 'in_progress':
        return theme.palette.info.light;
      case 'completed':
        return theme.palette.success.light;
      case 'cancelled':
        return theme.palette.error.light;
      default:
        return theme.palette.grey[300];
    }
  };

  return {
    padding: theme.spacing(2),
    margin: theme.spacing(1, 0),
    borderLeft: `4px solid ${getStatusColor()}`,
    '&:hover': {
      boxShadow: theme.shadows[3],
    }
  };
});

// Mock data for appointments
const mockAppointments = [
  {
    id: 1,
    service_request_id: 1,
    technician_id: 2,
    technician_name: 'Michael Rodriguez',
    customer_name: 'John Doe',
    customer_address: '123 Main St, Anytown, CA 94568',
    service_type: 'Refrigerator Repair',
    start_time: '2023-05-15T10:00:00',
    end_time: '2023-05-15T12:00:00',
    status: 'confirmed',
    notes: 'Customer reported ice maker not working',
    ghl_appointment_id: 'ghl_123456'
  },
  {
    id: 2,
    service_request_id: 2,
    technician_id: 1,
    technician_name: 'Sarah Johnson',
    customer_name: 'Jane Smith',
    customer_address: '456 Oak Ave, Somewhere, CA 94123',
    service_type: 'Washing Machine Repair',
    start_time: '2023-05-15T14:30:00',
    end_time: '2023-05-15T16:30:00',
    status: 'pending',
    notes: 'Washing machine leaking during rinse cycle',
    ghl_appointment_id: null
  },
  {
    id: 3,
    service_request_id: 3,
    technician_id: 2,
    technician_name: 'Michael Rodriguez',
    customer_name: 'Robert Johnson',
    customer_address: '789 Pine St, Nowhere, CA 95123',
    service_type: 'Dishwasher Installation',
    start_time: '2023-05-16T09:00:00',
    end_time: '2023-05-16T11:30:00',
    status: 'confirmed',
    notes: 'New installation, needs water line connection',
    ghl_appointment_id: 'ghl_789012'
  },
  {
    id: 4,
    service_request_id: 4,
    technician_id: 3,
    technician_name: 'David Wilson',
    customer_name: 'Emily Davis',
    customer_address: '321 Elm Dr, Elsewhere, CA 93456',
    service_type: 'Dryer Repair',
    start_time: '2023-05-16T13:00:00',
    end_time: '2023-05-16T15:00:00',
    status: 'in_progress',
    notes: 'Dryer not heating up properly',
    ghl_appointment_id: 'ghl_345678'
  },
  {
    id: 5,
    service_request_id: 5,
    technician_id: 1,
    technician_name: 'Sarah Johnson',
    customer_name: 'Michael Wilson',
    customer_address: '654 Cedar Ln, Anywhere, CA 92789',
    service_type: 'Oven Repair',
    start_time: '2023-05-17T11:00:00',
    end_time: '2023-05-17T13:00:00',
    status: 'pending',
    notes: 'Oven not maintaining temperature',
    ghl_appointment_id: null
  }
];

// Mock technicians data
const mockTechnicians = [
  { id: 1, name: 'Sarah Johnson', specializations: ['Washing Machine', 'Dryer', 'Oven'] },
  { id: 2, name: 'Michael Rodriguez', specializations: ['Refrigerator', 'Dishwasher', 'Freezer'] },
  { id: 3, name: 'David Wilson', specializations: ['Dryer', 'HVAC', 'Water Heater'] }
];

// Mock service requests for dropdown
const mockServiceRequests = [
  { id: 1, customer_name: 'John Doe', service_type: 'Refrigerator Repair', status: 'pending' },
  { id: 2, customer_name: 'Jane Smith', service_type: 'Washing Machine Repair', status: 'pending' },
  { id: 3, customer_name: 'Robert Johnson', service_type: 'Dishwasher Installation', status: 'pending' },
  { id: 4, customer_name: 'Emily Davis', service_type: 'Dryer Repair', status: 'pending' },
  { id: 5, customer_name: 'Michael Wilson', service_type: 'Oven Repair', status: 'pending' }
];

const AppointmentScheduler = () => {
  const [appointments, setAppointments] = useState([]);
  const [filteredAppointments, setFilteredAppointments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedDate, setSelectedDate] = useState(new Date().toISOString().split('T')[0]);
  const [selectedTechnician, setSelectedTechnician] = useState('all');
  const [openCreateDialog, setOpenCreateDialog] = useState(false);
  const [openEditDialog, setOpenEditDialog] = useState(false);
  const [openDeleteDialog, setOpenDeleteDialog] = useState(false);
  const [appointmentToEdit, setAppointmentToEdit] = useState(null);
  const [appointmentToDelete, setAppointmentToDelete] = useState(null);
  const [snackbar, setSnackbar] = useState({
    open: false,
    message: '',
    severity: 'success'
  });

  // Load appointment data
  useEffect(() => {
    const fetchData = async () => {
      try {
        // In a real app, this would be an API call
        await new Promise(resolve => setTimeout(resolve, 1000)); // Simulate API call
        setAppointments(mockAppointments);
      } catch (error) {
        console.error('Error fetching appointments:', error);
        setSnackbar({
          open: true,
          message: 'Failed to load appointments',
          severity: 'error'
        });
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  // Filter appointments based on selected date and technician
  useEffect(() => {
    if (!appointments.length) return;

    let filtered = [...appointments];
    
    // Filter by date
    if (selectedDate) {
      filtered = filtered.filter(apt => 
        new Date(apt.start_time).toISOString().split('T')[0] === selectedDate
      );
    }
    
    // Filter by technician
    if (selectedTechnician !== 'all') {
      filtered = filtered.filter(apt => 
        apt.technician_id === parseInt(selectedTechnician)
      );
    }
    
    // Sort by start time
    filtered.sort((a, b) => new Date(a.start_time) - new Date(b.start_time));
    
    setFilteredAppointments(filtered);
  }, [appointments, selectedDate, selectedTechnician]);

  // Handle date change
  const handleDateChange = (event) => {
    setSelectedDate(event.target.value);
  };

  // Handle technician filter change
  const handleTechnicianChange = (event) => {
    setSelectedTechnician(event.target.value);
  };

  // Open create appointment dialog
  const handleOpenCreateDialog = () => {
    setOpenCreateDialog(true);
  };

  // Close create appointment dialog
  const handleCloseCreateDialog = () => {
    setOpenCreateDialog(false);
    createFormik.resetForm();
  };

  // Open edit appointment dialog
  const handleOpenEditDialog = (appointment) => {
    setAppointmentToEdit(appointment);
    editFormik.setValues({
      service_request_id: appointment.service_request_id.toString(),
      technician_id: appointment.technician_id.toString(),
      start_time: new Date(appointment.start_time).toISOString().slice(0, 16),
      end_time: new Date(appointment.end_time).toISOString().slice(0, 16),
      notes: appointment.notes || '',
      status: appointment.status
    });
    setOpenEditDialog(true);
  };

  // Close edit appointment dialog
  const handleCloseEditDialog = () => {
    setOpenEditDialog(false);
    setAppointmentToEdit(null);
    editFormik.resetForm();
  };

  // Open delete appointment dialog
  const handleOpenDeleteDialog = (appointment) => {
    setAppointmentToDelete(appointment);
    setOpenDeleteDialog(true);
  };

  // Close delete appointment dialog
  const handleCloseDeleteDialog = () => {
    setOpenDeleteDialog(false);
    setAppointmentToDelete(null);
  };

  // Handle appointment deletion
  const handleDeleteAppointment = () => {
    if (appointmentToDelete) {
      // In a real app, this would be an API call
      setAppointments(appointments.filter(a => a.id !== appointmentToDelete.id));
      setSnackbar({
        open: true,
        message: 'Appointment deleted successfully',
        severity: 'success'
      });
    }
    handleCloseDeleteDialog();
  };

  // Handle syncing appointment with GHL
  const handleSyncAppointment = (appointmentId) => {
    // In a real app, this would be an API call to sync with GHL
    setAppointments(appointments.map(apt => 
      apt.id === appointmentId ? { ...apt, ghl_appointment_id: 'ghl_' + Math.random().toString(36).substr(2, 6) } : apt
    ));
    setSnackbar({
      open: true,
      message: 'Appointment synced with Go High Level',
      severity: 'success'
    });
  };

  // Close snackbar
  const handleCloseSnackbar = () => {
    setSnackbar({ ...snackbar, open: false });
  };

  // Create appointment form validation schema
  const createValidationSchema = Yup.object({
    service_request_id: Yup.string().required('Service request is required'),
    technician_id: Yup.string().required('Technician is required'),
    start_time: Yup.date().required('Start time is required'),
    end_time: Yup.date()
      .required('End time is required')
      .min(
        Yup.ref('start_time'),
        'End time must be after start time'
      ),
    notes: Yup.string()
  });

  // Edit appointment form validation schema
  const editValidationSchema = Yup.object({
    service_request_id: Yup.string().required('Service request is required'),
    technician_id: Yup.string().required('Technician is required'),
    start_time: Yup.date().required('Start time is required'),
    end_time: Yup.date()
      .required('End time is required')
      .min(
        Yup.ref('start_time'),
        'End time must be after start time'
      ),
    notes: Yup.string(),
    status: Yup.string().required('Status is required')
  });

  // Create appointment form
  const createFormik = useFormik({
    initialValues: {
      service_request_id: '',
      technician_id: '',
      start_time: '',
      end_time: '',
      notes: ''
    },
    validationSchema: createValidationSchema,
    onSubmit: async (values) => {
      try {
        // In a real app, this would be an API call
        await new Promise(resolve => setTimeout(resolve, 1000)); // Simulate API call
        
        const serviceRequest = mockServiceRequests.find(sr => sr.id === parseInt(values.service_request_id));
        const technician = mockTechnicians.find(t => t.id === parseInt(values.technician_id));
        
        const newAppointment = {
          id: appointments.length + 1,
          service_request_id: parseInt(values.service_request_id),
          technician_id: parseInt(values.technician_id),
          technician_name: technician.name,
          customer_name: serviceRequest.customer_name,
          customer_address: '123 Main St', // This would come from the actual API
          service_type: serviceRequest.service_type,
          start_time: values.start_time,
          end_time: values.end_time,
          status: 'pending',
          notes: values.notes,
          ghl_appointment_id: null
        };
        
        setAppointments([...appointments, newAppointment]);
        setSnackbar({
          open: true,
          message: 'Appointment created successfully',
          severity: 'success'
        });
        handleCloseCreateDialog();
      } catch (error) {
        console.error('Error creating appointment:', error);
        setSnackbar({
          open: true,
          message: 'Failed to create appointment',
          severity: 'error'
        });
      }
    }
  });

  // Edit appointment form
  const editFormik = useFormik({
    initialValues: {
      service_request_id: '',
      technician_id: '',
      start_time: '',
      end_time: '',
      notes: '',
      status: ''
    },
    validationSchema: editValidationSchema,
    onSubmit: async (values) => {
      try {
        // In a real app, this would be an API call
        await new Promise(resolve => setTimeout(resolve, 1000)); // Simulate API call
        
        const serviceRequest = mockServiceRequests.find(sr => sr.id === parseInt(values.service_request_id));
        const technician = mockTechnicians.find(t => t.id === parseInt(values.technician_id));
        
        const updatedAppointment = {
          ...appointmentToEdit,
          service_request_id: parseInt(values.service_request_id),
          technician_id: parseInt(values.technician_id),
          technician_name: technician.name,
          customer_name: serviceRequest.customer_name,
          service_type: serviceRequest.service_type,
          start_time: values.start_time,
          end_time: values.end_time,
          status: values.status,
          notes: values.notes
        };
        
        setAppointments(appointments.map(apt => 
          apt.id === appointmentToEdit.id ? updatedAppointment : apt
        ));
        
        setSnackbar({
          open: true,
          message: 'Appointment updated successfully',
          severity: 'success'
        });
        handleCloseEditDialog();
      } catch (error) {
        console.error('Error updating appointment:', error);
        setSnackbar({
          open: true,
          message: 'Failed to update appointment',
          severity: 'error'
        });
      }
    }
  });

  // Format time for display
  const formatTime = (isoString) => {
    return new Date(isoString).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  // Get status chip color
  const getStatusColor = (status) => {
    switch (status) {
      case 'pending':
        return 'warning';
      case 'confirmed':
        return 'success';
      case 'in_progress':
        return 'info';
      case 'completed':
        return 'success';
      case 'cancelled':
        return 'error';
      default:
        return 'default';
    }
  };

  return (
    <Box sx={{ flexGrow: 1, p: 3 }}>
      <Typography variant="h4" gutterBottom>
        Appointment Scheduler
      </Typography>

      {/* Filters and Actions */}
      <Paper sx={{ p: 2, mb: 3 }}>
        <Grid container spacing={2} alignItems="center">
          <Grid item xs={12} sm={4}>
            <TextField
              fullWidth
              id="appointment-date"
              label="Date"
              type="date"
              value={selectedDate}
              onChange={handleDateChange}
              InputLabelProps={{
                shrink: true,
              }}
            />
          </Grid>
          <Grid item xs={12} sm={4}>
            <FormControl fullWidth>
              <InputLabel id="technician-select-label">Technician</InputLabel>
              <Select
                labelId="technician-select-label"
                id="technician-select"
                value={selectedTechnician}
                label="Technician"
                onChange={handleTechnicianChange}
              >
                <MenuItem value="all">All Technicians</MenuItem>
                {mockTechnicians.map((tech) => (
                  <MenuItem key={tech.id} value={tech.id.toString()}>
                    {tech.name}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={12} sm={4} sx={{ display: 'flex', justifyContent: 'flex-end' }}>
            <Button
              variant="contained"
              startIcon={<AddIcon />}
              onClick={handleOpenCreateDialog}
            >
              New Appointment
            </Button>
          </Grid>
        </Grid>
      </Paper>

      {/* Appointments Display */}
      {loading ? (
        <Box display="flex" justifyContent="center" alignItems="center" minHeight="200px">
          <CircularProgress />
        </Box>
      ) : filteredAppointments.length === 0 ? (
        <Paper sx={{ p: 3, textAlign: 'center' }}>
          <Typography variant="h6" color="textSecondary">
            No appointments found for the selected date and technician.
          </Typography>
          <Button 
            variant="outlined" 
            sx={{ mt: 2 }}
            startIcon={<AddIcon />}
            onClick={handleOpenCreateDialog}
          >
            Schedule an Appointment
          </Button>
        </Paper>
      ) : (
        <Grid container spacing={3}>
          {filteredAppointments.map((appointment) => (
            <Grid item xs={12} md={6} lg={4} key={appointment.id}>
              <AppointmentCard status={appointment.status}>
                <Box display="flex" justifyContent="space-between" alignItems="flex-start">
                  <Typography variant="h6" gutterBottom>
                    {appointment.service_type}
                  </Typography>
                  <Chip 
                    label={appointment.status} 
                    color={getStatusColor(appointment.status)}
                    size="small"
                  />
                </Box>
                
                <Divider sx={{ my: 1 }} />
                
                <Stack spacing={1}>
                  <Box display="flex" alignItems="center" gap={1}>
                    <PersonIcon fontSize="small" color="action" />
                    <Typography variant="body2">
                      Customer: <strong>{appointment.customer_name}</strong>
                    </Typography>
                  </Box>
                  
                  <Box display="flex" alignItems="center" gap={1}>
                    <PersonIcon fontSize="small" color="primary" />
                    <Typography variant="body2">
                      Technician: <strong>{appointment.technician_name}</strong>
                    </Typography>
                  </Box>
                  
                  <Box display="flex" alignItems="center" gap={1}>
                    <EventIcon fontSize="small" color="action" />
                    <Typography variant="body2">
                      {new Date(appointment.start_time).toLocaleDateString()}
                    </Typography>
                  </Box>
                  
                  <Box display="flex" alignItems="center" gap={1}>
                    <TimeIcon fontSize="small" color="action" />
                    <Typography variant="body2">
                      {formatTime(appointment.start_time)} - {formatTime(appointment.end_time)}
                    </Typography>
                  </Box>
                  
                  {appointment.notes && (
                    <Typography variant="body2" color="text.secondary">
                      Notes: {appointment.notes}
                    </Typography>
                  )}
                </Stack>
                
                <Box display="flex" justifyContent="flex-end" mt={2}>
                  {!appointment.ghl_appointment_id && (
                    <IconButton 
                      size="small" 
                      color="secondary"
                      onClick={() => handleSyncAppointment(appointment.id)}
                      title="Sync with Go High Level"
                    >
                      <SyncIcon />
                    </IconButton>
                  )}
                  <IconButton 
                    size="small" 
                    color="primary"
                    onClick={() => handleOpenEditDialog(appointment)}
                    title="Edit Appointment"
                  >
                    <EditIcon />
                  </IconButton>
                  <IconButton 
                    size="small" 
                    color="error"
                    onClick={() => handleOpenDeleteDialog(appointment)}
                    title="Delete Appointment"
                  >
                    <DeleteIcon />
                  </IconButton>
                </Box>
              </AppointmentCard>
            </Grid>
          ))}
        </Grid>
      )}

      {/* Create Appointment Dialog */}
      <Dialog open={openCreateDialog} onClose={handleCloseCreateDialog} maxWidth="sm" fullWidth>
        <form onSubmit={createFormik.handleSubmit}>
          <DialogTitle>Schedule New Appointment</DialogTitle>
          <DialogContent>
            <Grid container spacing={2} sx={{ mt: 1 }}>
              <Grid item xs={12}>
                <FormControl 
                  fullWidth 
                  error={createFormik.touched.service_request_id && Boolean(createFormik.errors.service_request_id)}
                >
                  <InputLabel id="service-request-label">Service Request</InputLabel>
                  <Select
                    labelId="service-request-label"
                    id="service_request_id"
                    name="service_request_id"
                    value={createFormik.values.service_request_id}
                    onChange={createFormik.handleChange}
                    label="Service Request"
                  >
                    {mockServiceRequests.map((sr) => (
                      <MenuItem key={sr.id} value={sr.id.toString()}>
                        {sr.customer_name} - {sr.service_type}
                      </MenuItem>
                    ))}
                  </Select>
                  {createFormik.touched.service_request_id && createFormik.errors.service_request_id && (
                    <FormHelperText>{createFormik.errors.service_request_id}</FormHelperText>
                  )}
                </FormControl>
              </Grid>
              
              <Grid item xs={12}>
                <FormControl 
                  fullWidth 
                  error={createFormik.touched.technician_id && Boolean(createFormik.errors.technician_id)}
                >
                  <InputLabel id="technician-label">Technician</InputLabel>
                  <Select
                    labelId="technician-label"
                    id="technician_id"
                    name="technician_id"
                    value={createFormik.values.technician_id}
                    onChange={createFormik.handleChange}
                    label="Technician"
                  >
                    {mockTechnicians.map((tech) => (
                      <MenuItem key={tech.id} value={tech.id.toString()}>
                        {tech.name} - {tech.specializations.join(', ')}
                      </MenuItem>
                    ))}
                  </Select>
                  {createFormik.touched.technician_id && createFormik.errors.technician_id && (
                    <FormHelperText>{createFormik.errors.technician_id}</FormHelperText>
                  )}
                </FormControl>
              </Grid>
              
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  id="start_time"
                  name="start_time"
                  label="Start Time"
                  type="datetime-local"
                  value={createFormik.values.start_time}
                  onChange={createFormik.handleChange}
                  error={createFormik.touched.start_time && Boolean(createFormik.errors.start_time)}
                  helperText={createFormik.touched.start_time && createFormik.errors.start_time}
                  InputLabelProps={{
                    shrink: true,
                  }}
                />
              </Grid>
              
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  id="end_time"
                  name="end_time"
                  label="End Time"
                  type="datetime-local"
                  value={createFormik.values.end_time}
                  onChange={createFormik.handleChange}
                  error={createFormik.touched.end_time && Boolean(createFormik.errors.end_time)}
                  helperText={createFormik.touched.end_time && createFormik.errors.end_time}
                  InputLabelProps={{
                    shrink: true,
                  }}
                />
              </Grid>
              
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  id="notes"
                  name="notes"
                  label="Notes"
                  multiline
                  rows={3}
                  value={createFormik.values.notes}
                  onChange={createFormik.handleChange}
                  error={createFormik.touched.notes && Boolean(createFormik.errors.notes)}
                  helperText={createFormik.touched.notes && createFormik.errors.notes}
                />
              </Grid>
            </Grid>
          </DialogContent>
          <DialogActions>
            <Button onClick={handleCloseCreateDialog}>Cancel</Button>
            <Button 
              type="submit" 
              variant="contained" 
              disabled={createFormik.isSubmitting}
            >
              {createFormik.isSubmitting ? 'Scheduling...' : 'Schedule Appointment'}
            </Button>
          </DialogActions>
        </form>
      </Dialog>

      {/* Edit Appointment Dialog */}
      <Dialog open={openEditDialog} onClose={handleCloseEditDialog} maxWidth="sm" fullWidth>
        {appointmentToEdit && (
          <form onSubmit={editFormik.handleSubmit}>
            <DialogTitle>Edit Appointment</DialogTitle>
            <DialogContent>
              <Grid container spacing={2} sx={{ mt: 1 }}>
                <Grid item xs={12}>
                  <FormControl 
                    fullWidth 
                    error={editFormik.touched.service_request_id && Boolean(editFormik.errors.service_request_id)}
                  >
                    <InputLabel id="edit-service-request-label">Service Request</InputLabel>
                    <Select
                      labelId="edit-service-request-label"
                      id="service_request_id"
                      name="service_request_id"
                      value={editFormik.values.service_request_id}
                      onChange={editFormik.handleChange}
                      label="Service Request"
                    >
                      {mockServiceRequests.map((sr) => (
                        <MenuItem key={sr.id} value={sr.id.toString()}>
                          {sr.customer_name} - {sr.service_type}
                        </MenuItem>
                      ))}
                    </Select>
                    {editFormik.touched.service_request_id && editFormik.errors.service_request_id && (
                      <FormHelperText>{editFormik.errors.service_request_id}</FormHelperText>
                    )}
                  </FormControl>
                </Grid>
                
                <Grid item xs={12}>
                  <FormControl 
                    fullWidth 
                    error={editFormik.touched.technician_id && Boolean(editFormik.errors.technician_id)}
                  >
                    <InputLabel id="edit-technician-label">Technician</InputLabel>
                    <Select
                      labelId="edit-technician-label"
                      id="technician_id"
                      name="technician_id"
                      value={editFormik.values.technician_id}
                      onChange={editFormik.handleChange}
                      label="Technician"
                    >
                      {mockTechnicians.map((tech) => (
                        <MenuItem key={tech.id} value={tech.id.toString()}>
                          {tech.name} - {tech.specializations.join(', ')}
                        </MenuItem>
                      ))}
                    </Select>
                    {editFormik.touched.technician_id && editFormik.errors.technician_id && (
                      <FormHelperText>{editFormik.errors.technician_id}</FormHelperText>
                    )}
                  </FormControl>
                </Grid>
                
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    id="start_time"
                    name="start_time"
                    label="Start Time"
                    type="datetime-local"
                    value={editFormik.values.start_time}
                    onChange={editFormik.handleChange}
                    error={editFormik.touched.start_time && Boolean(editFormik.errors.start_time)}
                    helperText={editFormik.touched.start_time && editFormik.errors.start_time}
                    InputLabelProps={{
                      shrink: true,
                    }}
                  />
                </Grid>
                
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    id="end_time"
                    name="end_time"
                    label="End Time"
                    type="datetime-local"
                    value={editFormik.values.end_time}
                    onChange={editFormik.handleChange}
                    error={editFormik.touched.end_time && Boolean(editFormik.errors.end_time)}
                    helperText={editFormik.touched.end_time && editFormik.errors.end_time}
                    InputLabelProps={{
                      shrink: true,
                    }}
                  />
                </Grid>
                
                <Grid item xs={12}>
                  <FormControl 
                    fullWidth 
                    error={editFormik.touched.status && Boolean(editFormik.errors.status)}
                  >
                    <InputLabel id="status-label">Status</InputLabel>
                    <Select
                      labelId="status-label"
                      id="status"
                      name="status"
                      value={editFormik.values.status}
                      onChange={editFormik.handleChange}
                      label="Status"
                    >
                      <MenuItem value="pending">Pending</MenuItem>
                      <MenuItem value="confirmed">Confirmed</MenuItem>
                      <MenuItem value="in_progress">In Progress</MenuItem>
                      <MenuItem value="completed">Completed</MenuItem>
                      <MenuItem value="cancelled">Cancelled</MenuItem>
                    </Select>
                    {editFormik.touched.status && editFormik.errors.status && (
                      <FormHelperText>{editFormik.errors.status}</FormHelperText>
                    )}
                  </FormControl>
                </Grid>
                
                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    id="notes"
                    name="notes"
                    label="Notes"
                    multiline
                    rows={3}
                    value={editFormik.values.notes}
                    onChange={editFormik.handleChange}
                    error={editFormik.touched.notes && Boolean(editFormik.errors.notes)}
                    helperText={editFormik.touched.notes && editFormik.errors.notes}
                  />
                </Grid>
              </Grid>
            </DialogContent>
            <DialogActions>
              <Button onClick={handleCloseEditDialog}>Cancel</Button>
              <Button 
                type="submit" 
                variant="contained" 
                disabled={editFormik.isSubmitting}
              >
                {editFormik.isSubmitting ? 'Updating...' : 'Update Appointment'}
              </Button>
            </DialogActions>
          </form>
        )}
      </Dialog>

      {/* Delete Confirmation Dialog */}
      <Dialog open={openDeleteDialog} onClose={handleCloseDeleteDialog}>
        <DialogTitle>Confirm Deletion</DialogTitle>
        <DialogContent>
          <DialogContentText>
            Are you sure you want to delete this appointment for {appointmentToDelete?.customer_name} on {appointmentToDelete && new Date(appointmentToDelete.start_time).toLocaleDateString()}?
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDeleteDialog}>Cancel</Button>
          <Button onClick={handleDeleteAppointment} color="error" variant="contained">
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

export default AppointmentScheduler; 