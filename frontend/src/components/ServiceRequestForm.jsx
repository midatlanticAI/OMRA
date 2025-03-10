import React, { useState } from 'react';
import { 
  Box, 
  Typography, 
  TextField, 
  Button, 
  Grid, 
  Paper, 
  MenuItem,
  FormControl,
  FormHelperText,
  InputLabel,
  Select,
  Divider,
  Stack,
  Autocomplete,
  Chip,
  FormControlLabel,
  Checkbox,
  CircularProgress,
  Snackbar,
  Alert
} from '@mui/material';
import { useFormik } from 'formik';
import * as Yup from 'yup';

// Mock customer data for dropdown
const mockCustomers = [
  { id: '1001', name: 'John Doe', email: 'john.doe@example.com', phone: '(555) 123-4567' },
  { id: '1002', name: 'Jane Smith', email: 'jane.smith@example.com', phone: '(555) 987-6543' },
  { id: '1003', name: 'Robert Johnson', email: 'robert.johnson@example.com', phone: '(555) 456-7890' },
  { id: '1004', name: 'Emily Davis', email: 'emily.davis@example.com', phone: '(555) 789-0123' },
  { id: '1005', name: 'Michael Wilson', email: 'michael.wilson@example.com', phone: '(555) 234-5678' }
];

// Appliance types
const applianceTypes = [
  'Refrigerator',
  'Freezer',
  'Washing Machine',
  'Dryer',
  'Dishwasher',
  'Oven',
  'Stove',
  'Microwave',
  'Garbage Disposal',
  'Water Heater',
  'Air Conditioner',
  'Furnace',
  'Other'
];

// Service priorities
const servicePriorities = [
  { value: 'low', label: 'Low - Schedule in the next week' },
  { value: 'medium', label: 'Medium - Schedule in the next 2-3 days' },
  { value: 'high', label: 'High - Schedule within 24 hours' },
  { value: 'emergency', label: 'Emergency - Schedule ASAP' }
];

// Common symptoms by appliance type
const commonSymptoms = {
  'Refrigerator': [
    'Not cooling', 
    'Making noise', 
    'Leaking water', 
    'Ice maker not working',
    'Temperature inconsistent'
  ],
  'Washing Machine': [
    'Won\'t start', 
    'Leaking', 
    'Drum not spinning', 
    'Making loud noise',
    'Not draining'
  ],
  'Dryer': [
    'Not heating', 
    'Not spinning', 
    'Making noise', 
    'Takes too long to dry',
    'Stops mid-cycle'
  ],
  // Add more for other appliance types
};

const ServiceRequestForm = () => {
  const [loading, setLoading] = useState(false);
  const [snackbar, setSnackbar] = useState({
    open: false,
    message: '',
    severity: 'success'
  });
  const [availableSymptoms, setAvailableSymptoms] = useState([]);

  // Form validation schema using Yup
  const validationSchema = Yup.object({
    customerId: Yup.string().required('Please select a customer'),
    applianceType: Yup.string().required('Appliance type is required'),
    brand: Yup.string().required('Brand is required'),
    model: Yup.string(),
    priority: Yup.string().required('Priority is required'),
    description: Yup.string().required('Description is required').min(10, 'Description must be at least 10 characters'),
    preferredDate: Yup.date().min(new Date(), 'Date cannot be in the past'),
    symptoms: Yup.array().min(1, 'Select at least one symptom'),
    createGhlOpportunity: Yup.boolean()
  });

  // Initialize formik
  const formik = useFormik({
    initialValues: {
      customerId: '',
      applianceType: '',
      brand: '',
      model: '',
      serialNumber: '',
      priority: 'medium',
      description: '',
      preferredDate: '',
      preferredTimeSlot: '',
      symptoms: [],
      createGhlOpportunity: true
    },
    validationSchema,
    onSubmit: async (values) => {
      setLoading(true);
      try {
        // In a real app, this would be an API call
        console.log('Form values submitted:', values);
        await new Promise(resolve => setTimeout(resolve, 1500)); // Simulate API call
        
        setSnackbar({
          open: true,
          message: 'Service request created successfully!',
          severity: 'success'
        });
        
        // Reset form after successful submission
        formik.resetForm();
      } catch (error) {
        console.error('Error submitting form:', error);
        setSnackbar({
          open: true,
          message: 'Failed to create service request. Please try again.',
          severity: 'error'
        });
      } finally {
        setLoading(false);
      }
    }
  });

  // Update available symptoms when appliance type changes
  React.useEffect(() => {
    const applianceType = formik.values.applianceType;
    if (applianceType && commonSymptoms[applianceType]) {
      setAvailableSymptoms(commonSymptoms[applianceType]);
    } else {
      setAvailableSymptoms([]);
    }
    
    // Reset symptoms when appliance type changes
    if (formik.values.symptoms.length > 0) {
      formik.setFieldValue('symptoms', []);
    }
  }, [formik.values.applianceType]);

  const handleCloseSnackbar = () => {
    setSnackbar({ ...snackbar, open: false });
  };

  // Get customer details by ID
  const getSelectedCustomer = () => {
    return mockCustomers.find(c => c.id === formik.values.customerId) || null;
  };

  return (
    <Box sx={{ flexGrow: 1, p: 3 }}>
      <Typography variant="h4" gutterBottom>
        Create Service Request
      </Typography>
      
      <Paper sx={{ p: 3, mb: 4 }}>
        <form onSubmit={formik.handleSubmit}>
          <Grid container spacing={3}>
            {/* Customer Selection */}
            <Grid item xs={12} md={6}>
              <FormControl fullWidth error={formik.touched.customerId && Boolean(formik.errors.customerId)}>
                <InputLabel id="customer-select-label">Customer</InputLabel>
                <Select
                  labelId="customer-select-label"
                  id="customerId"
                  name="customerId"
                  value={formik.values.customerId}
                  onChange={formik.handleChange}
                  onBlur={formik.handleBlur}
                  label="Customer"
                >
                  {mockCustomers.map((customer) => (
                    <MenuItem key={customer.id} value={customer.id}>
                      {customer.name} - {customer.phone}
                    </MenuItem>
                  ))}
                </Select>
                {formik.touched.customerId && formik.errors.customerId && (
                  <FormHelperText>{formik.errors.customerId}</FormHelperText>
                )}
              </FormControl>
            </Grid>

            {/* Selected Customer Details */}
            <Grid item xs={12} md={6}>
              {formik.values.customerId && (
                <Box sx={{ p: 2, border: '1px solid #eee', borderRadius: 1 }}>
                  <Typography variant="subtitle2" gutterBottom>
                    Selected Customer:
                  </Typography>
                  <Typography variant="body2">
                    {getSelectedCustomer()?.name}
                  </Typography>
                  <Typography variant="body2">
                    {getSelectedCustomer()?.email}
                  </Typography>
                  <Typography variant="body2">
                    {getSelectedCustomer()?.phone}
                  </Typography>
                </Box>
              )}
            </Grid>

            <Grid item xs={12}>
              <Divider sx={{ my: 2 }}>Appliance Information</Divider>
            </Grid>

            {/* Appliance Type */}
            <Grid item xs={12} md={6}>
              <FormControl fullWidth error={formik.touched.applianceType && Boolean(formik.errors.applianceType)}>
                <InputLabel id="appliance-type-label">Appliance Type</InputLabel>
                <Select
                  labelId="appliance-type-label"
                  id="applianceType"
                  name="applianceType"
                  value={formik.values.applianceType}
                  onChange={formik.handleChange}
                  onBlur={formik.handleBlur}
                  label="Appliance Type"
                >
                  {applianceTypes.map((type) => (
                    <MenuItem key={type} value={type}>
                      {type}
                    </MenuItem>
                  ))}
                </Select>
                {formik.touched.applianceType && formik.errors.applianceType && (
                  <FormHelperText>{formik.errors.applianceType}</FormHelperText>
                )}
              </FormControl>
            </Grid>

            {/* Brand */}
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                id="brand"
                name="brand"
                label="Brand"
                value={formik.values.brand}
                onChange={formik.handleChange}
                onBlur={formik.handleBlur}
                error={formik.touched.brand && Boolean(formik.errors.brand)}
                helperText={formik.touched.brand && formik.errors.brand}
              />
            </Grid>

            {/* Model */}
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                id="model"
                name="model"
                label="Model Number (if known)"
                value={formik.values.model}
                onChange={formik.handleChange}
                onBlur={formik.handleBlur}
                error={formik.touched.model && Boolean(formik.errors.model)}
                helperText={formik.touched.model && formik.errors.model}
              />
            </Grid>

            {/* Serial Number */}
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                id="serialNumber"
                name="serialNumber"
                label="Serial Number (if known)"
                value={formik.values.serialNumber}
                onChange={formik.handleChange}
                onBlur={formik.handleBlur}
              />
            </Grid>

            <Grid item xs={12}>
              <Divider sx={{ my: 2 }}>Service Details</Divider>
            </Grid>

            {/* Priority */}
            <Grid item xs={12} md={6}>
              <FormControl fullWidth error={formik.touched.priority && Boolean(formik.errors.priority)}>
                <InputLabel id="priority-label">Service Priority</InputLabel>
                <Select
                  labelId="priority-label"
                  id="priority"
                  name="priority"
                  value={formik.values.priority}
                  onChange={formik.handleChange}
                  onBlur={formik.handleBlur}
                  label="Service Priority"
                >
                  {servicePriorities.map((priority) => (
                    <MenuItem key={priority.value} value={priority.value}>
                      {priority.label}
                    </MenuItem>
                  ))}
                </Select>
                {formik.touched.priority && formik.errors.priority && (
                  <FormHelperText>{formik.errors.priority}</FormHelperText>
                )}
              </FormControl>
            </Grid>

            {/* Preferred Date */}
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                id="preferredDate"
                name="preferredDate"
                label="Preferred Service Date"
                type="date"
                value={formik.values.preferredDate}
                onChange={formik.handleChange}
                onBlur={formik.handleBlur}
                error={formik.touched.preferredDate && Boolean(formik.errors.preferredDate)}
                helperText={formik.touched.preferredDate && formik.errors.preferredDate}
                InputLabelProps={{
                  shrink: true,
                }}
              />
            </Grid>

            {/* Preferred Time Slot */}
            <Grid item xs={12} md={6}>
              <FormControl fullWidth>
                <InputLabel id="time-slot-label">Preferred Time Slot</InputLabel>
                <Select
                  labelId="time-slot-label"
                  id="preferredTimeSlot"
                  name="preferredTimeSlot"
                  value={formik.values.preferredTimeSlot}
                  onChange={formik.handleChange}
                  label="Preferred Time Slot"
                >
                  <MenuItem value="morning">Morning (8AM - 12PM)</MenuItem>
                  <MenuItem value="afternoon">Afternoon (12PM - 4PM)</MenuItem>
                  <MenuItem value="evening">Evening (4PM - 8PM)</MenuItem>
                </Select>
              </FormControl>
            </Grid>

            {/* Symptoms */}
            <Grid item xs={12}>
              <Autocomplete
                multiple
                id="symptoms"
                options={availableSymptoms}
                value={formik.values.symptoms}
                onChange={(event, newValue) => {
                  formik.setFieldValue('symptoms', newValue);
                }}
                renderTags={(value, getTagProps) =>
                  value.map((option, index) => (
                    <Chip 
                      label={option} 
                      {...getTagProps({ index })} 
                      color="primary" 
                      variant="outlined"
                    />
                  ))
                }
                renderInput={(params) => (
                  <TextField
                    {...params}
                    label="Symptoms"
                    placeholder="Select symptoms"
                    error={formik.touched.symptoms && Boolean(formik.errors.symptoms)}
                    helperText={formik.touched.symptoms && formik.errors.symptoms}
                  />
                )}
                disabled={!formik.values.applianceType}
              />
              {!formik.values.applianceType && (
                <FormHelperText>Select an appliance type to see common symptoms</FormHelperText>
              )}
            </Grid>

            {/* Description */}
            <Grid item xs={12}>
              <TextField
                fullWidth
                id="description"
                name="description"
                label="Problem Description"
                multiline
                rows={4}
                value={formik.values.description}
                onChange={formik.handleChange}
                onBlur={formik.handleBlur}
                error={formik.touched.description && Boolean(formik.errors.description)}
                helperText={formik.touched.description && formik.errors.description}
              />
            </Grid>

            {/* Integration Options */}
            <Grid item xs={12}>
              <FormControlLabel
                control={
                  <Checkbox
                    id="createGhlOpportunity"
                    name="createGhlOpportunity"
                    checked={formik.values.createGhlOpportunity}
                    onChange={formik.handleChange}
                  />
                }
                label="Create opportunity in Go High Level CRM"
              />
            </Grid>

            {/* Submit Button */}
            <Grid item xs={12}>
              <Stack direction="row" spacing={2} justifyContent="flex-end">
                <Button variant="outlined" onClick={formik.handleReset}>
                  Clear Form
                </Button>
                <Button 
                  type="submit" 
                  variant="contained" 
                  disabled={loading}
                  startIcon={loading && <CircularProgress size={20} />}
                >
                  {loading ? 'Creating Request...' : 'Create Service Request'}
                </Button>
              </Stack>
            </Grid>
          </Grid>
        </form>
      </Paper>

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

export default ServiceRequestForm; 