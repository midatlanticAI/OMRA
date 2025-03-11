import React, { useState, useEffect } from 'react';
import {
  Box,
  Grid,
  Paper,
  Typography,
  Card,
  CardContent,
  CircularProgress,
  Button,
  List,
  ListItem,
  ListItemText,
  Divider,
} from '@mui/material';
import {
  People as PeopleIcon,
  Assignment as AssignmentIcon,
  Engineering as TechnicianIcon,
  SmartToy as AgentIcon,
} from '@mui/icons-material';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';

const StatCard = ({ title, value, icon, color, onClick }) => {
  return (
    <Card 
      sx={{ 
        height: '100%', 
        display: 'flex', 
        flexDirection: 'column',
        cursor: onClick ? 'pointer' : 'default',
        '&:hover': onClick ? { boxShadow: 6 } : {}
      }}
      onClick={onClick}
    >
      <CardContent>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
          <Typography variant="h6" component="div" gutterBottom>
            {title}
          </Typography>
          <Box sx={{ color }}>
            {icon}
          </Box>
        </Box>
        <Typography variant="h3" component="div">
          {value}
        </Typography>
      </CardContent>
    </Card>
  );
};

const Dashboard = () => {
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchSummary = async () => {
      try {
        setLoading(true);
        const response = await axios.get('/api/dashboard/summary');
        setSummary(response.data);
        setError(null);
      } catch (err) {
        console.error('Error fetching dashboard summary:', err);
        setError('Failed to load dashboard data. Please try again later.');
      } finally {
        setLoading(false);
      }
    };

    fetchSummary();
  }, []);

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '50vh' }}>
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Box sx={{ mt: 4 }}>
        <Typography color="error" align="center" gutterBottom>
          {error}
        </Typography>
        <Box sx={{ display: 'flex', justifyContent: 'center', mt: 2 }}>
          <Button variant="contained" onClick={() => window.location.reload()}>
            Retry
          </Button>
        </Box>
      </Box>
    );
  }

  return (
    <Box>
      <Typography variant="h4" component="h1" gutterBottom>
        Dashboard
      </Typography>

      {/* Stats cards */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard 
            title="Customers" 
            value={summary?.counts.customers || 0} 
            icon={<PeopleIcon />} 
            color="primary.main" 
            onClick={() => navigate('/customers')}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard 
            title="Service Requests" 
            value={summary?.counts.service_requests.total || 0} 
            icon={<AssignmentIcon />} 
            color="secondary.main" 
            onClick={() => navigate('/service-requests')}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard 
            title="Technicians" 
            value={summary?.counts.technicians || 0} 
            icon={<TechnicianIcon />} 
            color="success.main" 
            onClick={() => navigate('/technicians')}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard 
            title="Agents" 
            value={summary?.counts.agents || 0} 
            icon={<AgentIcon />} 
            color="info.main" 
            onClick={() => navigate('/agents')}
          />
        </Grid>
      </Grid>

      {/* Detail sections */}
      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2, height: '100%' }}>
            <Typography variant="h6" gutterBottom>
              Service Request Status
            </Typography>
            <Grid container spacing={2} sx={{ mt: 1 }}>
              <Grid item xs={6}>
                <Paper sx={{ p: 2, bgcolor: 'warning.light' }}>
                  <Typography variant="body2">Pending</Typography>
                  <Typography variant="h4">{summary?.counts.service_requests.pending || 0}</Typography>
                </Paper>
              </Grid>
              <Grid item xs={6}>
                <Paper sx={{ p: 2, bgcolor: 'info.light' }}>
                  <Typography variant="body2">Scheduled</Typography>
                  <Typography variant="h4">{summary?.counts.service_requests.scheduled || 0}</Typography>
                </Paper>
              </Grid>
              <Grid item xs={6}>
                <Paper sx={{ p: 2, bgcolor: 'primary.light' }}>
                  <Typography variant="body2">In Progress</Typography>
                  <Typography variant="h4">{summary?.counts.service_requests.in_progress || 0}</Typography>
                </Paper>
              </Grid>
              <Grid item xs={6}>
                <Paper sx={{ p: 2, bgcolor: 'success.light' }}>
                  <Typography variant="body2">Completed</Typography>
                  <Typography variant="h4">{summary?.counts.service_requests.completed || 0}</Typography>
                </Paper>
              </Grid>
            </Grid>
          </Paper>
        </Grid>

        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2, height: '100%' }}>
            <Typography variant="h6" gutterBottom sx={{ mb: 2 }}>
              Recent Service Requests
            </Typography>
            {summary?.recent_requests && summary.recent_requests.length > 0 ? (
              <List>
                {summary.recent_requests.map((request, index) => (
                  <React.Fragment key={request._id}>
                    <ListItem 
                      button 
                      onClick={() => navigate(`/service-requests/${request._id}`)}
                      sx={{ 
                        bgcolor: index % 2 === 0 ? 'background.default' : 'transparent',
                        borderRadius: 1
                      }}
                    >
                      <ListItemText
                        primary={`${request.appliance_type} - ${request.issue_description}`}
                        secondary={`Status: ${request.status} | Priority: ${request.priority}`}
                      />
                    </ListItem>
                    {index < summary.recent_requests.length - 1 && <Divider />}
                  </React.Fragment>
                ))}
              </List>
            ) : (
              <Typography variant="body2" color="text.secondary" align="center">
                No recent service requests
              </Typography>
            )}
            <Box sx={{ mt: 2, display: 'flex', justifyContent: 'flex-end' }}>
              <Button 
                variant="outlined" 
                size="small"
                onClick={() => navigate('/service-requests')}
              >
                View All
              </Button>
            </Box>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};

export default Dashboard; 