import React, { useState, useEffect, useContext, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Paper,
  Stepper,
  Step,
  StepLabel,
  Button,
  Typography,
  Alert,
  Divider,
  TextField,
  Grid,
  CircularProgress,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
} from '@mui/material';
import AgentTypeSelector from './AgentTypeSelector';
import ModelSelector from './ModelSelector';
import ChannelConfig from './ChannelConfig';
import RagConfig from './RagConfig';
import FineTuningConfig from './FineTuningConfig';
import HierarchicalConfig from './HierarchicalConfig';
import { ApiContext } from '../../contexts/ApiContext';

// Stepper steps
const steps = [
  { label: 'Agent Type', optional: false },
  { label: 'Basic Settings', optional: false },
  { label: 'Model Selection', optional: false },
  { label: 'Channel Configuration', optional: false },
  { label: 'Knowledge Sources', optional: true },
  { label: 'Fine-Tuning', optional: true },
  { label: 'Hierarchical Setup', optional: true },
  { label: 'Review & Create', optional: false },
];

/**
 * CreateAgentForm - Main form component for creating a new agent
 * 
 * Combines all sub-components in a step-by-step workflow
 */
const CreateAgentForm = ({ existingAgents = [] }) => {
  const navigate = useNavigate();
  // Remove unused API context reference entirely
  const apiContext = useContext(ApiContext);
  
  // Form state
  const [activeStep, setActiveStep] = useState(0);
  const [agentData, setAgentData] = useState({
    name: '',
    description: '',
    type: 'chat',
    modelId: 'gpt-4o',
    channelConfig: null,
    ragConfig: {
      enabled: false,
      sources: []
    },
    fineTuningConfig: {
      enabled: false,
      method: 'existing'
    },
    hierarchicalConfig: {
      isHierarchical: false,
      role: 'standalone',
      parentId: null,
      childrenIds: []
    },
    isPublic: false,
    tags: [],
  });
  
  // UI state
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [successDialogOpen, setSuccessDialogOpen] = useState(false);
  const [createdAgent, setCreatedAgent] = useState(null);
  
  // Navigation
  const handleNext = () => {
    if (activeStep === steps.length - 1) {
      handleCreateAgent();
    } else {
      setActiveStep((prevStep) => prevStep + 1);
    }
  };
  
  const handleBack = () => {
    setActiveStep((prevStep) => prevStep - 1);
  };
  
  // Form field updates
  const handleFieldChange = (field, value) => {
    setAgentData(prevData => ({
      ...prevData,
      [field]: value
    }));
  };
  
  // Skip optional steps that are disabled
  const isStepSkippable = useCallback((stepIndex) => {
    if (!steps[stepIndex].optional) return false;
    
    switch (stepIndex) {
      case 3: // Channel Configuration
        return agentData.type === 'general';
      case 4: // Knowledge Sources (RAG)
        return !agentData.ragConfig.enabled;
      case 5: // Fine-Tuning
        return !agentData.fineTuningConfig.enabled;
      case 6: // Hierarchical Setup
        return !agentData.hierarchicalConfig.isHierarchical;
      default:
        return false;
    }
  }, [agentData.type, agentData.ragConfig.enabled, agentData.fineTuningConfig.enabled, agentData.hierarchicalConfig.isHierarchical, steps]);
  
  // Check if current step is complete and can proceed
  const canProceed = () => {
    switch (activeStep) {
      case 0: // Agent Type
        return !!agentData.type;
      case 1: // Basic Settings
        return !!agentData.name && agentData.name.length >= 3;
      case 2: // Model Selection
        return !!agentData.modelId;
      case 3: // Channel Configuration
        return agentData.type === 'general' || !!agentData.channelConfig;
      case 4: // Knowledge Sources
        return !agentData.ragConfig.enabled || agentData.ragConfig.sources.length > 0;
      case 5: // Fine-Tuning
        if (!agentData.fineTuningConfig.enabled) return true;
        if (agentData.fineTuningConfig.method === 'existing') return !!agentData.fineTuningConfig.fineTunedModelId;
        return agentData.fineTuningConfig.trainingDataset.examples.length > 0;
      case 6: // Hierarchical Setup
        if (!agentData.hierarchicalConfig.isHierarchical) return true;
        if (agentData.hierarchicalConfig.role === 'child' || agentData.hierarchicalConfig.role === 'hybrid') {
          return !!agentData.hierarchicalConfig.parentId;
        }
        if (agentData.hierarchicalConfig.role === 'parent' || agentData.hierarchicalConfig.role === 'hybrid') {
          return agentData.hierarchicalConfig.childrenIds.length > 0;
        }
        return true;
      case 7: // Review & Create
        return true;
      default:
        return false;
    }
  };
  
  // Effect to potentially skip steps when transitioning
  useEffect(() => {
    if (isStepSkippable(activeStep)) {
      // Determine direction based on previous step
      const direction = activeStep > 0 ? 1 : -1;
      setActiveStep(prevStep => prevStep + direction);
    }
  }, [activeStep, isStepSkippable]);
  
  // Create the agent
  const handleCreateAgent = async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      // In a real app, this would be an API call
      console.log('Creating agent with data:', agentData);
      
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      // Simulate successful creation
      const createdAgentData = {
        ...agentData,
        id: `agent-${Date.now()}`,
        createdAt: new Date().toISOString(),
      };
      
      setCreatedAgent(createdAgentData);
      setSuccessDialogOpen(true);
    } catch (err) {
      console.error('Error creating agent:', err);
      setError('Failed to create agent. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };
  
  // Navigate to the new agent after creation
  const handleViewAgent = () => {
    setSuccessDialogOpen(false);
    navigate(`/agents/${createdAgent.id}`);
  };
  
  // Render step content based on active step
  const renderStepContent = () => {
    switch (activeStep) {
      case 0: // Agent Type
        return (
          <AgentTypeSelector
            selectedType={agentData.type}
            onTypeChange={(type) => handleFieldChange('type', type)}
          />
        );
      
      case 1: // Basic Settings
        return (
          <Box>
            <Typography variant="h6" gutterBottom>
              Basic Settings
            </Typography>
            
            <Grid container spacing={3}>
              <Grid item xs={12}>
                <TextField
                  required
                  fullWidth
                  label="Agent Name"
                  value={agentData.name}
                  onChange={(e) => handleFieldChange('name', e.target.value)}
                  helperText="Give your agent a descriptive name"
                />
              </Grid>
              
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  multiline
                  rows={3}
                  label="Description"
                  value={agentData.description}
                  onChange={(e) => handleFieldChange('description', e.target.value)}
                  helperText="Describe what this agent does and its purpose"
                />
              </Grid>
            </Grid>
          </Box>
        );
      
      case 2: // Model Selection
        return (
          <ModelSelector
            selectedModel={agentData.modelId}
            onModelChange={(modelId) => handleFieldChange('modelId', modelId)}
            showLocalModels={true}
            allowCustomEndpoint={true}
          />
        );
      
      case 3: // Channel Configuration
        return (
          <ChannelConfig
            channelType={agentData.type}
            config={agentData.channelConfig}
            onChange={(config) => handleFieldChange('channelConfig', config)}
          />
        );
      
      case 4: // Knowledge Sources (RAG)
        return (
          <RagConfig
            config={agentData.ragConfig}
            onChange={(config) => handleFieldChange('ragConfig', config)}
            existingKnowledgeBases={[]}
            showAdvanced={true}
          />
        );
      
      case 5: // Fine-Tuning
        return (
          <FineTuningConfig
            config={agentData.fineTuningConfig}
            onChange={(config) => handleFieldChange('fineTuningConfig', config)}
            existingFineTunedModels={[]}
          />
        );
      
      case 6: // Hierarchical Setup
        return (
          <HierarchicalConfig
            config={agentData.hierarchicalConfig}
            onChange={(config) => handleFieldChange('hierarchicalConfig', config)}
            availableAgents={existingAgents}
          />
        );
      
      case 7: // Review & Create
        return (
          <Box>
            <Typography variant="h6" gutterBottom>
              Review Agent Configuration
            </Typography>
            
            <Paper variant="outlined" sx={{ p: 2, mb: 2 }}>
              <Grid container spacing={2}>
                <Grid item xs={12} sm={6}>
                  <Typography variant="subtitle2">Agent Name</Typography>
                  <Typography variant="body1">{agentData.name}</Typography>
                </Grid>
                
                <Grid item xs={12} sm={6}>
                  <Typography variant="subtitle2">Agent Type</Typography>
                  <Typography variant="body1" sx={{ textTransform: 'capitalize' }}>
                    {agentData.type} Agent
                  </Typography>
                </Grid>
                
                <Grid item xs={12}>
                  <Typography variant="subtitle2">Description</Typography>
                  <Typography variant="body1">
                    {agentData.description || 'No description provided'}
                  </Typography>
                </Grid>
                
                <Grid item xs={12}>
                  <Divider sx={{ my: 1 }} />
                </Grid>
                
                <Grid item xs={12} sm={6}>
                  <Typography variant="subtitle2">Model</Typography>
                  <Typography variant="body1">{agentData.modelId}</Typography>
                </Grid>
                
                <Grid item xs={12} sm={6}>
                  <Typography variant="subtitle2">Capabilities</Typography>
                  <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                    {agentData.ragConfig.enabled && (
                      <Typography variant="body2" component="span" sx={{ mr: 1 }}>
                        RAG Enabled ({agentData.ragConfig.sources.length} sources)
                      </Typography>
                    )}
                    
                    {agentData.fineTuningConfig.enabled && (
                      <Typography variant="body2" component="span" sx={{ mr: 1 }}>
                        Fine-Tuned
                      </Typography>
                    )}
                    
                    {agentData.hierarchicalConfig.isHierarchical && (
                      <Typography variant="body2" component="span" sx={{ mr: 1 }}>
                        Hierarchical ({agentData.hierarchicalConfig.role})
                      </Typography>
                    )}
                  </Box>
                </Grid>
              </Grid>
            </Paper>
            
            <Alert severity="info" sx={{ mb: 2 }}>
              Review the configuration above. When you're ready, click Create Agent to finalize.
            </Alert>
          </Box>
        );
      
      default:
        return null;
    }
  };
  
  return (
    <Box sx={{ width: '100%', mb: 4 }}>
      <Paper sx={{ p: 3 }}>
        <Typography variant="h5" gutterBottom>
          Create New Agent
        </Typography>
        
        <Stepper activeStep={activeStep} alternativeLabel sx={{ mb: 4 }}>
          {steps.map((step, index) => (
            <Step key={step.label}>
              <StepLabel optional={step.optional ? <Typography variant="caption">Optional</Typography> : null}>
                {step.label}
              </StepLabel>
            </Step>
          ))}
        </Stepper>
        
        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}
        
        <Box sx={{ minHeight: '320px' }}>
          {renderStepContent()}
        </Box>
        
        <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 3 }}>
          <Button
            variant="outlined"
            onClick={handleBack}
            disabled={activeStep === 0 || isLoading}
          >
            Back
          </Button>
          
          <Button
            variant="contained"
            onClick={handleNext}
            disabled={!canProceed() || isLoading}
          >
            {isLoading ? (
              <CircularProgress size={24} sx={{ mr: 1 }} />
            ) : null}
            {activeStep === steps.length - 1 ? 'Create Agent' : 'Next'}
          </Button>
        </Box>
      </Paper>
      
      {/* Success Dialog */}
      <Dialog open={successDialogOpen} onClose={() => setSuccessDialogOpen(false)}>
        <DialogTitle>Agent Created Successfully</DialogTitle>
        <DialogContent>
          <Alert severity="success" sx={{ mb: 2 }}>
            Your agent "{createdAgent?.name}" has been created successfully!
          </Alert>
          <Typography variant="body1">
            You can now start using your agent or continue configuring additional settings.
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setSuccessDialogOpen(false)}>Close</Button>
          <Button variant="contained" onClick={handleViewAgent}>
            View Agent
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default CreateAgentForm; 