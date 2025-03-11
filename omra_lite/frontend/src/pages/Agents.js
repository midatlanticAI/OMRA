import React, { useState, useEffect, useContext } from 'react';
import {
  Typography,
  Box,
  Paper,
  CircularProgress,
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  IconButton,
  Chip,
  Grid,
  Divider,
} from '@mui/material';
import {
  Add as AddIcon,
  Delete as DeleteIcon,
  Description as DescriptionIcon,
  Psychology as PsychologyIcon,
  Settings as SettingsIcon,
} from '@mui/icons-material';
import { ApiContext } from '../contexts/ApiContext';
import { useNavigate } from 'react-router-dom';
import { CreateAgentForm } from '../components/agents';

const Agents = () => {
  const [agents, setAgents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [openDialog, setOpenDialog] = useState(false);
  
  const apiContext = useContext(ApiContext);
  const navigate = useNavigate();

  useEffect(() => {
    fetchAgents();
  }, []);

  const fetchAgents = async () => {
    try {
      setLoading(true);
      // In a real app, this would be an API call
      // For now, we'll simulate it with sample data
      setTimeout(() => {
        const sampleAgents = [
          {
            id: 'agent-1',
            name: 'Customer Support Assistant',
            type: 'chat',
            description: 'Virtual assistant for handling customer inquiries',
            model: 'gpt-4o',
            createdAt: '2023-12-15T09:30:00Z',
            ragConfig: { enabled: true, sources: ['kb-1', 'kb-2'] },
            hierarchicalConfig: { isHierarchical: true, role: 'parent', childrenIds: ['agent-3'] }
          },
          {
            id: 'agent-2',
            name: 'Email Response Bot',
            type: 'email',
            description: 'Automated email response system',
            model: 'claude-3-sonnet',
            createdAt: '2024-01-10T14:45:00Z',
            fineTuningConfig: { enabled: true }
          },
          {
            id: 'agent-3',
            name: 'Technical Support Specialist',
            type: 'chat',
            description: 'Specialized agent for technical product questions',
            model: 'gpt-4',
            createdAt: '2024-02-05T11:20:00Z',
            hierarchicalConfig: { isHierarchical: true, role: 'child', parentId: 'agent-1' }
          }
        ];
        setAgents(sampleAgents);
        setLoading(false);
      }, 1000);
    } catch (error) {
      console.error('Error fetching agents:', error);
      setLoading(false);
    }
  };

  const handleOpenDialog = () => {
    setOpenDialog(true);
  };

  const handleCloseDialog = () => {
    setOpenDialog(false);
    // Refresh agent list after creation or editing
    fetchAgents();
  };

  const handleDeleteAgent = async (agentId) => {
    if (window.confirm('Are you sure you want to delete this agent?')) {
      try {
        // In a real app, this would be an API call
        // await api.delete(`/agents/${agentId}`);
        
        // For the demo, just filter it out of state
        setAgents(agents.filter(agent => agent.id !== agentId));
      } catch (error) {
        console.error('Error deleting agent:', error);
      }
    }
  };

  const handleViewAgent = (agentId) => {
    navigate(`/agents/${agentId}`);
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return new Intl.DateTimeFormat('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    }).format(date);
  };

  const getAgentCapabilities = (agent) => {
    const capabilities = [];
    
    if (agent.ragConfig && agent.ragConfig.enabled) {
      capabilities.push('RAG');
    }
    
    if (agent.fineTuningConfig && agent.fineTuningConfig.enabled) {
      capabilities.push('Fine-tuned');
    }
    
    if (agent.hierarchicalConfig && agent.hierarchicalConfig.isHierarchical) {
      capabilities.push(`${agent.hierarchicalConfig.role}`);
    }
    
    return capabilities;
  };

  return (
    <Box p={3}>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4">Agents</Typography>
        <Button
          variant="contained"
          color="primary"
          startIcon={<AddIcon />}
          onClick={handleOpenDialog}
        >
          Create Agent
        </Button>
      </Box>

      <Box mb={4}>
        <Typography variant="subtitle1" gutterBottom>
          Create and manage AI agents with different roles and capabilities
        </Typography>
        <Typography variant="body2" color="textSecondary">
          Configure agents for specific tasks, connect them to knowledge sources, and arrange them in hierarchical structures.
        </Typography>
      </Box>

      {loading ? (
        <Box display="flex" justifyContent="center" mt={4}>
          <CircularProgress />
        </Box>
      ) : (
        <Grid container spacing={3}>
          {agents.length === 0 ? (
            <Grid item xs={12}>
              <Paper sx={{ p: 4, textAlign: 'center' }}>
                <PsychologyIcon sx={{ fontSize: 60, color: 'text.secondary', mb: 2 }} />
                <Typography variant="h6" gutterBottom>
                  No Agents Created Yet
                </Typography>
                <Typography variant="body2" color="textSecondary" paragraph>
                  Get started by creating your first agent using the "Create Agent" button.
                </Typography>
                <Button
                  variant="contained"
                  startIcon={<AddIcon />}
                  onClick={handleOpenDialog}
                >
                  Create Your First Agent
                </Button>
              </Paper>
            </Grid>
          ) : (
            agents.map((agent) => (
              <Grid item xs={12} md={6} lg={4} key={agent.id}>
                <Paper sx={{ p: 0, height: '100%', display: 'flex', flexDirection: 'column' }}>
                  <Box sx={{ 
                    p: 2, 
                    bgcolor: agent.type === 'chat' ? 'primary.light' : 
                              agent.type === 'email' ? 'success.light' : 
                              agent.type === 'voice' ? 'warning.light' : 'secondary.light',
                    color: '#fff',
                    borderTopLeftRadius: 4,
                    borderTopRightRadius: 4
                  }}>
                    <Typography variant="h6" component="h2">
                      {agent.name}
                    </Typography>
                    <Typography variant="caption" sx={{ textTransform: 'capitalize' }}>
                      {agent.type} Agent
                    </Typography>
                  </Box>
                  
                  <Box sx={{ p: 2, flexGrow: 1 }}>
                    <Typography variant="body2" color="textSecondary" paragraph>
                      {agent.description || 'No description provided.'}
                    </Typography>
                    
                    <Typography variant="subtitle2" gutterBottom>
                      Created: {formatDate(agent.createdAt)}
                    </Typography>
                    
                    <Typography variant="subtitle2" gutterBottom>
                      Model: {agent.model}
                    </Typography>
                    
                    {getAgentCapabilities(agent).length > 0 && (
                      <Box mt={1}>
                        {getAgentCapabilities(agent).map((capability, index) => (
                          <Chip 
                            key={index} 
                            label={capability} 
                            size="small" 
                            sx={{ mr: 0.5, mb: 0.5, textTransform: 'capitalize' }} 
                          />
                        ))}
                      </Box>
                    )}
                  </Box>
                  
                  <Divider />
                  
                  <Box sx={{ p: 1, display: 'flex', justifyContent: 'flex-end' }}>
                    <IconButton 
                      aria-label="view agent"
                      onClick={() => handleViewAgent(agent.id)}
                      title="View Agent Details"
                    >
                      <DescriptionIcon />
                    </IconButton>
                    <IconButton 
                      aria-label="edit agent settings"
                      onClick={() => navigate(`/agents/${agent.id}/settings`)}
                      title="Edit Agent Settings"
                    >
                      <SettingsIcon />
                    </IconButton>
                    <IconButton 
                      aria-label="delete agent"
                      onClick={() => handleDeleteAgent(agent.id)}
                      title="Delete Agent"
                    >
                      <DeleteIcon />
                    </IconButton>
                  </Box>
                </Paper>
              </Grid>
            ))
          )}
        </Grid>
      )}
      
      {/* Agent Creation Dialog */}
      <Dialog
        open={openDialog}
        onClose={handleCloseDialog}
        maxWidth="lg"
        fullWidth
      >
        <DialogContent sx={{ p: 0 }}>
          <CreateAgentForm existingAgents={agents} />
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog} color="primary">
            Cancel
          </Button>
        </DialogActions>
      </Dialog>

      {/* Link to Documentation */}
      <Box mt={4} textAlign="center">
        <Button
          variant="outlined"
          color="primary"
          onClick={() => navigate('/agent-docs')}
          startIcon={<DescriptionIcon />}
        >
          View Agent Documentation
        </Button>
      </Box>
    </Box>
  );
};

export default Agents; 