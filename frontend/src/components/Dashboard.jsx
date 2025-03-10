import React, { useState, useEffect } from 'react';
import { 
  Grid, 
  Paper, 
  Typography, 
  Box, 
  Card, 
  CardContent, 
  Button,
  CircularProgress,
  List,
  ListItem,
  ListItemText,
  Divider,
  Chip
} from '@mui/material';
import { 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  Legend, 
  ResponsiveContainer 
} from 'recharts';

// Mock data - in a real implementation, this would come from the API
const mockDashboardData = {
  pendingRequests: 5,
  upcomingAppointments: [
    { id: 1, customerName: 'John Doe', date: '2023-05-15', time: '10:00 AM', serviceType: 'Refrigerator Repair' },
    { id: 2, customerName: 'Jane Smith', date: '2023-05-16', time: '2:30 PM', serviceType: 'Dishwasher Installation' },
    { id: 3, customerName: 'Bob Johnson', date: '2023-05-17', time: '9:00 AM', serviceType: 'Washing Machine Repair' }
  ],
  monthlyRevenue: [
    { month: 'Jan', amount: 4500 },
    { month: 'Feb', amount: 5200 },
    { month: 'Mar', amount: 4900 },
    { month: 'Apr', amount: 6100 },
    { month: 'May', amount: 5800 }
  ],
  agentActivity: [
    { id: 'wf_123', status: 'active', description: 'Customer response generation' },
    { id: 'wf_124', status: 'active', description: 'Service scheduling' },
    { id: 'wf_125', status: 'completed', description: 'Invoice generation' }
  ]
};

const Dashboard = () => {
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    // In a real app, this would fetch data from the API
    const loadDashboardData = async () => {
      try {
        setLoading(true);
        // Simulate API call
        await new Promise(resolve => setTimeout(resolve, 1000));
        setDashboardData(mockDashboardData);
        setError(null);
      } catch (error) {
        console.error('Error fetching dashboard data:', error);
        setError('Failed to load dashboard data. Please try again.');
      } finally {
        setLoading(false);
      }
    };

    loadDashboardData();
  }, []);

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '80vh' }}>
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Box sx={{ p: 3 }}>
        <Typography color="error" variant="h6">{error}</Typography>
        <Button variant="contained" sx={{ mt: 2 }} onClick={() => window.location.reload()}>
          Retry
        </Button>
      </Box>
    );
  }

  return (
    <Box sx={{ flexGrow: 1, p: 3 }}>
      <Typography variant="h4" gutterBottom>
        Dashboard
      </Typography>

      {/* Summary Cards */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ height: '100%' }}>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Pending Service Requests
              </Typography>
              <Typography variant="h3">
                {dashboardData.pendingRequests}
              </Typography>
              <Button size="small" color="primary" sx={{ mt: 2 }}>
                View All
              </Button>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ height: '100%' }}>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Today's Appointments
              </Typography>
              <Typography variant="h3">
                {dashboardData.upcomingAppointments.filter(a => 
                  new Date(a.date).toDateString() === new Date().toDateString()
                ).length}
              </Typography>
              <Button size="small" color="primary" sx={{ mt: 2 }}>
                View Schedule
              </Button>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ height: '100%' }}>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Active Workflows
              </Typography>
              <Typography variant="h3">
                {dashboardData.agentActivity.filter(a => a.status === 'active').length}
              </Typography>
              <Button size="small" color="primary" sx={{ mt: 2 }}>
                View Workflows
              </Button>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ height: '100%' }}>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                This Month's Revenue
              </Typography>
              <Typography variant="h3">
                ${dashboardData.monthlyRevenue.reduce((sum, item) => sum + item.amount, 0).toLocaleString()}
              </Typography>
              <Button size="small" color="primary" sx={{ mt: 2 }}>
                Financial Reports
              </Button>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Revenue Chart and Upcoming Appointments */}
      <Grid container spacing={3}>
        <Grid item xs={12} md={8}>
          <Paper sx={{ p: 2, display: 'flex', flexDirection: 'column' }}>
            <Typography variant="h6" gutterBottom>
              Monthly Revenue
            </Typography>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart
                data={dashboardData.monthlyRevenue}
                margin={{
                  top: 5,
                  right: 30,
                  left: 20,
                  bottom: 5,
                }}
              >
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="month" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Bar dataKey="amount" fill="#8884d8" name="Revenue ($)" />
              </BarChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>

        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 2, display: 'flex', flexDirection: 'column' }}>
            <Typography variant="h6" gutterBottom>
              Upcoming Appointments
            </Typography>
            <List sx={{ overflow: 'auto', maxHeight: 300 }}>
              {dashboardData.upcomingAppointments.map((appointment, index) => (
                <React.Fragment key={appointment.id}>
                  {index > 0 && <Divider />}
                  <ListItem>
                    <ListItemText
                      primary={appointment.customerName}
                      secondary={
                        <>
                          <Typography component="span" variant="body2" color="text.primary">
                            {new Date(appointment.date).toLocaleDateString()} - {appointment.time}
                          </Typography>
                          <br />
                          {appointment.serviceType}
                        </>
                      }
                    />
                  </ListItem>
                </React.Fragment>
              ))}
            </List>
            <Button color="primary" sx={{ mt: 1 }}>
              View All Appointments
            </Button>
          </Paper>
        </Grid>
      </Grid>

      {/* Agent Activity */}
      <Grid container spacing={3} sx={{ mt: 2 }}>
        <Grid item xs={12}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Agent Activity
            </Typography>
            <List>
              {dashboardData.agentActivity.map((activity, index) => (
                <React.Fragment key={activity.id}>
                  {index > 0 && <Divider />}
                  <ListItem>
                    <ListItemText
                      primary={activity.description}
                      secondary={`Workflow ID: ${activity.id}`}
                    />
                    <Chip
                      label={activity.status}
                      color={activity.status === 'active' ? 'primary' : 'success'}
                      size="small"
                    />
                  </ListItem>
                </React.Fragment>
              ))}
            </List>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};

export default Dashboard; 