import React, { useState, useEffect } from 'react';
import { 
  Grid, 
  Card, 
  CardContent, 
  Typography, 
  Box,
  Paper,
  Button,
  Divider,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Avatar,
  IconButton,
  Chip,
  CircularProgress
} from '@mui/material';
import { 
  TrendingUp, 
  Event, 
  Person, 
  Build, 
  Receipt, 
  CheckCircle,
  ErrorOutline,
  MoreVert as MoreIcon
} from '@mui/icons-material';
import axios from 'axios';
import { useAuth } from '../context/AuthContext';
import { useConfig } from '../context/ConfigContext';
import { Chart } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement
} from 'chart.js';

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement
);

const Dashboard = () => {
  const { user } = useAuth();
  const { config } = useConfig();
  const [stats, setStats] = useState({
    totalCustomers: 0,
    activeJobs: 0,
    completedJobs: 0,
    revenueThisMonth: 0,
    revenueLastMonth: 0
  });
  const [recentCustomers, setRecentCustomers] = useState([]);
  const [upcomingJobs, setUpcomingJobs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        setLoading(true);
        const [statsRes, customersRes, jobsRes] = await Promise.all([
          axios.get('/api/dashboard/stats'),
          axios.get('/api/dashboard/recent-customers'),
          axios.get('/api/dashboard/upcoming-jobs')
        ]);
        
        setStats(statsRes.data);
        setRecentCustomers(customersRes.data);
        setUpcomingJobs(jobsRes.data);
        setError(null);
      } catch (err) {
        console.error('Failed to fetch dashboard data:', err);
        setError('Failed to load dashboard information');
      } finally {
        setLoading(false);
      }
    };

    fetchDashboardData();
  }, []);

  // Chart data for revenue
  const revenueData = {
    labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
    datasets: [
      {
        label: 'Revenue',
        data: [12000, 19000, 15000, 21000, 18000, 24000],
        fill: false,
        backgroundColor: 'rgba(75, 192, 192, 0.2)',
        borderColor: 'rgba(75, 192, 192, 1)',
        tension: 0.1
      }
    ]
  };

  // Chart data for job types
  const jobTypeData = {
    labels: ['Repair', 'Installation', 'Maintenance', 'Consultation'],
    datasets: [
      {
        label: 'Job Types',
        data: [25, 35, 20, 15],
        backgroundColor: [
          'rgba(255, 99, 132, 0.6)',
          'rgba(54, 162, 235, 0.6)',
          'rgba(255, 206, 86, 0.6)',
          'rgba(75, 192, 192, 0.6)'
        ],
        borderWidth: 1
      }
    ]
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" height="80vh">
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
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
      <Typography variant="h4" gutterBottom>
        Welcome, {user?.name || 'User'}
      </Typography>
      
      <Typography variant="subtitle1" color="textSecondary" gutterBottom>
        Here's an overview of your business operations
      </Typography>
      
      {/* Stats Cards */}
      <Grid container spacing={3} sx={{ mt: 1, mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ height: '100%' }}>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Total Customers
              </Typography>
              <Box display="flex" alignItems="center">
                <Person sx={{ fontSize: 40, color: 'primary.main', mr: 2 }} />
                <Typography variant="h4" component="div">
                  {stats.totalCustomers}
                </Typography>
              </Box>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ height: '100%' }}>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Active Jobs
              </Typography>
              <Box display="flex" alignItems="center">
                <Build sx={{ fontSize: 40, color: 'info.main', mr: 2 }} />
                <Typography variant="h4" component="div">
                  {stats.activeJobs}
                </Typography>
              </Box>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ height: '100%' }}>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Completed Jobs
              </Typography>
              <Box display="flex" alignItems="center">
                <CheckCircle sx={{ fontSize: 40, color: 'success.main', mr: 2 }} />
                <Typography variant="h4" component="div">
                  {stats.completedJobs}
                </Typography>
              </Box>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ height: '100%' }}>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Revenue This Month
              </Typography>
              <Box display="flex" alignItems="center">
                <Receipt sx={{ fontSize: 40, color: 'secondary.main', mr: 2 }} />
                <Typography variant="h4" component="div">
                  ${stats.revenueThisMonth.toLocaleString()}
                </Typography>
              </Box>
              <Typography variant="body2" color={stats.revenueThisMonth > stats.revenueLastMonth ? 'success.main' : 'error.main'} sx={{ mt: 1 }}>
                <TrendingUp sx={{ fontSize: 16, verticalAlign: 'middle', mr: 0.5 }} />
                {stats.revenueThisMonth > stats.revenueLastMonth ? 'Up' : 'Down'} from last month
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Charts */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} md={8}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Revenue Trend
              </Typography>
              <Box height={300}>
                <Chart type="line" data={revenueData} options={{ maintainAspectRatio: false }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} md={4}>
          <Card sx={{ height: '100%' }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Job Distribution
              </Typography>
              <Box height={300} display="flex" justifyContent="center">
                <Chart type="pie" data={jobTypeData} options={{ maintainAspectRatio: false }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Recent Activity and Upcoming Jobs */}
      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Recent Customers
              </Typography>
              <List>
                {recentCustomers.map((customer) => (
                  <React.Fragment key={customer.id}>
                    <ListItem 
                      secondaryAction={
                        <IconButton edge="end">
                          <MoreIcon />
                        </IconButton>
                      }
                    >
                      <ListItemIcon>
                        <Avatar alt={customer.name} src={customer.avatar} />
                      </ListItemIcon>
                      <ListItemText
                        primary={customer.name}
                        secondary={customer.email}
                      />
                      <Chip 
                        label={`${customer.jobCount} jobs`} 
                        size="small" 
                        variant="outlined"
                        color="primary"
                        sx={{ ml: 2 }}
                      />
                    </ListItem>
                    <Divider variant="inset" component="li" />
                  </React.Fragment>
                ))}
              </List>
              <Box textAlign="center" mt={2}>
                <Button color="primary">View All Customers</Button>
              </Box>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Upcoming Jobs
              </Typography>
              <List>
                {upcomingJobs.map((job) => (
                  <React.Fragment key={job.id}>
                    <ListItem 
                      secondaryAction={
                        <IconButton edge="end">
                          <MoreIcon />
                        </IconButton>
                      }
                    >
                      <ListItemIcon>
                        <Event color="primary" />
                      </ListItemIcon>
                      <ListItemText
                        primary={job.title}
                        secondary={
                          <>
                            <Typography component="span" variant="body2" color="textPrimary">
                              {job.customerName}
                            </Typography>
                            {` — ${new Date(job.scheduledDate).toLocaleDateString()}`}
                          </>
                        }
                      />
                      <Chip 
                        label={job.status} 
                        size="small"
                        color={job.status === 'scheduled' ? 'info' : 'warning'}
                        sx={{ ml: 2 }}
                      />
                    </ListItem>
                    <Divider variant="inset" component="li" />
                  </React.Fragment>
                ))}
              </List>
              <Box textAlign="center" mt={2}>
                <Button color="primary">View All Jobs</Button>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
      
      {/* Integration Status */}
      {(config.integrations.ghl.enabled || config.integrations.kickserv.enabled) && (
        <Card sx={{ mt: 4 }}>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Integration Status
            </Typography>
            <Grid container spacing={2}>
              {config.integrations.ghl.enabled && (
                <Grid item xs={12} sm={6}>
                  <Paper variant="outlined" sx={{ p: 2 }}>
                    <Box display="flex" alignItems="center" justifyContent="space-between">
                      <Box display="flex" alignItems="center">
                        <img 
                          src="/assets/ghl-logo.png" 
                          alt="GHL" 
                          style={{ width: 40, height: 40, marginRight: 16 }} 
                        />
                        <div>
                          <Typography variant="subtitle1">Go High Level</Typography>
                          <Typography variant="body2" color="textSecondary">
                            CRM Integration
                          </Typography>
                        </div>
                      </Box>
                      <Chip 
                        label={config.integrations.ghl.connected ? "Connected" : "Disconnected"} 
                        color={config.integrations.ghl.connected ? "success" : "error"} 
                      />
                    </Box>
                  </Paper>
                </Grid>
              )}
              
              {config.integrations.kickserv.enabled && (
                <Grid item xs={12} sm={6}>
                  <Paper variant="outlined" sx={{ p: 2 }}>
                    <Box display="flex" alignItems="center" justifyContent="space-between">
                      <Box display="flex" alignItems="center">
                        <img 
                          src="/assets/kickserv-logo.png" 
                          alt="Kickserv" 
                          style={{ width: 40, height: 40, marginRight: 16 }} 
                        />
                        <div>
                          <Typography variant="subtitle1">Kickserv</Typography>
                          <Typography variant="body2" color="textSecondary">
                            Service Management
                          </Typography>
                        </div>
                      </Box>
                      <Chip 
                        label={config.integrations.kickserv.connected ? "Connected" : "Disconnected"} 
                        color={config.integrations.kickserv.connected ? "success" : "error"} 
                      />
                    </Box>
                  </Paper>
                </Grid>
              )}
            </Grid>
          </CardContent>
        </Card>
      )}
    </Box>
  );
};

export default Dashboard; 