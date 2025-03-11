import React, { useState } from 'react';
import {
  Box,
  Typography,
  FormControl,
  FormControlLabel,
  FormHelperText,
  Switch,
  Select,
  MenuItem,
  InputLabel,
  TextField,
  Paper,
  Divider,
  Chip,
  IconButton,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  ListItemSecondaryAction,
  Button,
  Alert,
  Tooltip,
  Grid,
  Slider,
  LinearProgress,
  Tab,
  Tabs,
} from '@mui/material';
import HelpOutlineIcon from '@mui/icons-material/HelpOutline';
import DeleteIcon from '@mui/icons-material/Delete';
import AddIcon from '@mui/icons-material/Add';
import UploadFileIcon from '@mui/icons-material/UploadFile';
import DatasetIcon from '@mui/icons-material/Dataset';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';
import DescriptionIcon from '@mui/icons-material/Description';
import MoneyOffIcon from '@mui/icons-material/MoneyOff';

/**
 * TabPanel - Component for displaying tab content
 */
function TabPanel(props) {
  const { children, value, index, ...other } = props;

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`finetuning-tabpanel-${index}`}
      aria-labelledby={`finetuning-tab-${index}`}
      {...other}
    >
      {value === index && (
        <Box sx={{ p: 2 }}>
          {children}
        </Box>
      )}
    </div>
  );
}

/**
 * FineTuningConfig - Component for configuring model fine-tuning settings
 * 
 * @param {Object} props - Component props
 * @param {Object} props.config - Current fine-tuning configuration
 * @param {Function} props.onChange - Function to update configuration
 * @param {Array} props.existingFineTunedModels - List of already fine-tuned models available
 * @param {Object} props.baseModel - The base model selected for the agent
 */
const FineTuningConfig = ({
  config,
  onChange,
  existingFineTunedModels = [],
  baseModel = {},
}) => {
  // Default configuration
  const defaultConfig = {
    enabled: false,
    method: 'existing', // 'existing', 'dataset', or 'synthetic'
    fineTunedModelId: null,
    trainingDataset: {
      id: null,
      name: '',
      examples: [],
    },
    hyperParams: {
      epochs: 3,
      batchSize: 4,
      learningRate: 0.0001,
    },
    useLoRA: true,
    estimatedCost: 0,
  };

  // Merge provided config with defaults
  const currentConfig = { ...defaultConfig, ...config };
  
  // Local state
  const [activeTab, setActiveTab] = useState(0);
  const [uploadedExamplesFile, setUploadedExamplesFile] = useState(null);
  const [newExample, setNewExample] = useState({ user: '', assistant: '' });
  const [fineTuningInProgress, setFineTuningInProgress] = useState(false);
  const [progress, setProgress] = useState(0);
  const [newDatasetName, setNewDatasetName] = useState('');
  
  // Handle changes to any configuration field
  const handleChange = (field, value) => {
    const newConfig = {
      ...currentConfig,
      [field]: value,
    };
    
    // Calculate estimated cost whenever key parameters change
    if (field === 'method' || field === 'hyperParams' || field === 'useLoRA') {
      newConfig.estimatedCost = calculateEstimatedCost(newConfig);
    }
    
    onChange(newConfig);
  };
  
  // Calculate estimated fine-tuning cost based on configuration
  const calculateEstimatedCost = (config) => {
    if (!config.enabled) return 0;
    if (config.method === 'existing') return 0;
    
    // This is a simplified cost estimation
    // In a real app, you'd use a more accurate model based on token count
    const baseTokenCost = config.useLoRA ? 0.0075 : 0.015; // per 1K tokens
    const exampleCount = config.trainingDataset.examples.length || 100; // approximate if no examples yet
    const avgTokensPerExample = 750; // rough estimate
    const totalTokens = exampleCount * avgTokensPerExample;
    const epochMultiplier = config.hyperParams.epochs;
    
    return ((totalTokens / 1000) * baseTokenCost * epochMultiplier).toFixed(2);
  };
  
  // Handle tab changes
  const handleTabChange = (event, newValue) => {
    setActiveTab(newValue);
  };
  
  // Add a manually entered example to the training dataset
  const handleAddExample = () => {
    if (!newExample.user.trim() || !newExample.assistant.trim()) return;
    
    const examples = [...(currentConfig.trainingDataset.examples || [])];
    examples.push({
      id: `example-${Date.now()}`,
      user: newExample.user,
      assistant: newExample.assistant,
    });
    
    const newDataset = {
      ...currentConfig.trainingDataset,
      examples: examples,
    };
    
    handleChange('trainingDataset', newDataset);
    setNewExample({ user: '', assistant: '' });
    
    // Update cost estimation
    handleChange('estimatedCost', calculateEstimatedCost({
      ...currentConfig,
      trainingDataset: newDataset,
    }));
  };
  
  // Handle file uploads for examples
  const handleFileUpload = (event) => {
    const file = event.target.files && event.target.files[0];
    if (!file) return;
    
    setUploadedExamplesFile(file);
    
    // In a real app, you'd parse the file and extract examples
    // For this prototype, we'll simulate adding 50 examples
    const simulatedExamples = Array(50).fill().map((_, index) => ({
      id: `file-example-${Date.now()}-${index}`,
      user: `This is a simulated user query from file ${index + 1}`,
      assistant: `This is a simulated assistant response from file ${index + 1}`,
    }));
    
    const newDataset = {
      ...currentConfig.trainingDataset,
      examples: [...(currentConfig.trainingDataset.examples || []), ...simulatedExamples],
    };
    
    handleChange('trainingDataset', newDataset);
    
    // Update cost estimation
    handleChange('estimatedCost', calculateEstimatedCost({
      ...currentConfig,
      trainingDataset: newDataset,
    }));
  };
  
  // Remove an example from the dataset
  const handleRemoveExample = (exampleId) => {
    const examples = currentConfig.trainingDataset.examples.filter(
      example => example.id !== exampleId
    );
    
    const newDataset = {
      ...currentConfig.trainingDataset,
      examples: examples,
    };
    
    handleChange('trainingDataset', newDataset);
    
    // Update cost estimation
    handleChange('estimatedCost', calculateEstimatedCost({
      ...currentConfig,
      trainingDataset: newDataset,
    }));
  };
  
  // Start fine-tuning process
  const handleStartFineTuning = () => {
    if (fineTuningInProgress) return;
    
    // In a real app, this would initiate an API call to start fine-tuning
    setFineTuningInProgress(true);
    setProgress(0);
    
    // Simulate progress updates
    const interval = setInterval(() => {
      setProgress(prev => {
        const newProgress = prev + Math.random() * 5;
        if (newProgress >= 100) {
          clearInterval(interval);
          setTimeout(() => {
            setFineTuningInProgress(false);
            // Add to existing models (in a real app, this would come from the API)
            alert('Fine-tuning completed! The model is now available in your fine-tuned models list.');
          }, 500);
          return 100;
        }
        return newProgress;
      });
    }, 1000);
  };
  
  // Create and save a new dataset
  const handleSaveDataset = () => {
    if (!newDatasetName || currentConfig.trainingDataset.examples.length === 0) return;
    
    // In a real app, this would make an API call to save the dataset
    alert(`Dataset "${newDatasetName}" saved with ${currentConfig.trainingDataset.examples.length} examples`);
    setNewDatasetName('');
  };
  
  return (
    <Box>
      <Typography variant="h6" gutterBottom>
        Model Fine-Tuning
        <Tooltip title="Fine-tuning allows you to customize a model for your specific use case, improving performance on domain-specific tasks.">
          <IconButton size="small" sx={{ ml: 1 }}>
            <HelpOutlineIcon fontSize="small" />
          </IconButton>
        </Tooltip>
      </Typography>
      
      <FormControlLabel
        control={
          <Switch
            checked={currentConfig.enabled}
            onChange={(e) => handleChange('enabled', e.target.checked)}
          />
        }
        label="Enable Fine-Tuning"
      />
      
      {!currentConfig.enabled && (
        <Alert severity="info" sx={{ mt: 2 }}>
          Enable fine-tuning to customize the model for your specific use case. Fine-tuning improves your agent's
          ability to follow specific formats, use domain-specific knowledge, and maintain a consistent style.
        </Alert>
      )}
      
      {currentConfig.enabled && (
        <>
          {/* Fine-tuning Tabs */}
          <Box sx={{ mt: 3 }}>
            <Tabs value={activeTab} onChange={handleTabChange} aria-label="Fine-tuning tabs">
              <Tab label="Method" />
              <Tab label="Training Data" disabled={currentConfig.method === 'existing'} />
              <Tab label="Parameters" disabled={currentConfig.method === 'existing'} />
            </Tabs>
            
            {/* Method Tab */}
            <TabPanel value={activeTab} index={0}>
              <Typography variant="subtitle1" gutterBottom>
                Select Fine-Tuning Method
              </Typography>
              
              <Grid container spacing={3}>
                <Grid item xs={12}>
                  <FormControl fullWidth>
                    <InputLabel id="finetuning-method-label">Fine-Tuning Method</InputLabel>
                    <Select
                      labelId="finetuning-method-label"
                      value={currentConfig.method}
                      onChange={(e) => handleChange('method', e.target.value)}
                      label="Fine-Tuning Method"
                    >
                      <MenuItem value="existing">Use Existing Fine-Tuned Model</MenuItem>
                      <MenuItem value="dataset">Fine-Tune With Custom Dataset</MenuItem>
                      <MenuItem value="synthetic">Generate Synthetic Training Data</MenuItem>
                    </Select>
                    <FormHelperText>
                      Choose how you want to customize your model
                    </FormHelperText>
                  </FormControl>
                </Grid>
                
                {currentConfig.method === 'existing' && (
                  <Grid item xs={12}>
                    {existingFineTunedModels.length === 0 ? (
                      <Alert severity="info" sx={{ mt: 1 }}>
                        You don't have any fine-tuned models yet. Choose another method to create one.
                      </Alert>
                    ) : (
                      <FormControl fullWidth>
                        <InputLabel id="finetuned-model-label">Fine-Tuned Model</InputLabel>
                        <Select
                          labelId="finetuned-model-label"
                          value={currentConfig.fineTunedModelId || ''}
                          onChange={(e) => handleChange('fineTunedModelId', e.target.value)}
                          label="Fine-Tuned Model"
                        >
                          {existingFineTunedModels.map(model => (
                            <MenuItem key={model.id} value={model.id}>
                              {model.name}
                            </MenuItem>
                          ))}
                        </Select>
                        <FormHelperText>
                          Select a previously fine-tuned model to use
                        </FormHelperText>
                      </FormControl>
                    )}
                  </Grid>
                )}
                
                {currentConfig.method === 'synthetic' && (
                  <Grid item xs={12}>
                    <Alert severity="info">
                      Synthetic data generation will automatically create training examples based on your agent's
                      purpose, description, and knowledge sources. This requires minimal setup but may be less
                      precise than using custom examples.
                    </Alert>
                    
                    <Typography variant="subtitle2" sx={{ mt: 2 }}>
                      Training Data Generation Options
                    </Typography>
                    
                    <TextField
                      fullWidth
                      multiline
                      rows={3}
                      margin="normal"
                      label="Additional Instructions (Optional)"
                      placeholder="Describe specific formats, tone, or behaviors you want the fine-tuned model to learn..."
                      helperText="Any special instructions to guide the synthetic data generation process"
                    />
                    
                    <FormControlLabel
                      control={
                        <Switch defaultChecked />
                      }
                      label="Include examples from knowledge sources"
                      sx={{ mt: 1, display: 'block' }}
                    />
                    
                    <FormControlLabel
                      control={
                        <Switch defaultChecked />
                      }
                      label="Generate examples covering edge cases and error handling"
                      sx={{ display: 'block' }}
                    />
                  </Grid>
                )}
                
                {currentConfig.method !== 'existing' && (
                  <>
                    <Grid item xs={12}>
                      <FormControlLabel
                        control={
                          <Switch
                            checked={currentConfig.useLoRA}
                            onChange={(e) => handleChange('useLoRA', e.target.checked)}
                          />
                        }
                        label={
                          <Box sx={{ display: 'flex', alignItems: 'center' }}>
                            Use LoRA (Low-Rank Adaptation)
                            <Tooltip title="LoRA is a parameter-efficient fine-tuning technique that significantly reduces computational requirements and cost. Recommended for most use cases.">
                              <IconButton size="small">
                                <HelpOutlineIcon fontSize="small" />
                              </IconButton>
                            </Tooltip>
                            <Chip 
                              icon={<MoneyOffIcon />} 
                              label="Cost-Effective" 
                              size="small" 
                              color="success" 
                              variant="outlined"
                              sx={{ ml: 1 }}
                            />
                          </Box>
                        }
                      />
                    </Grid>
                    
                    <Grid item xs={12}>
                      <Paper variant="outlined" sx={{ p: 2, bgcolor: 'background.default' }}>
                        <Typography variant="subtitle2" gutterBottom>
                          Estimated Cost
                        </Typography>
                        
                        <Typography variant="h4" color={parseFloat(currentConfig.estimatedCost) > 0 ? 'primary' : 'text.secondary'}>
                          ${currentConfig.estimatedCost}
                        </Typography>
                        
                        <Typography variant="body2" color="text.secondary">
                          {parseFloat(currentConfig.estimatedCost) === 0 
                            ? 'No cost estimate available yet' 
                            : `Based on current settings and ${currentConfig.trainingDataset.examples.length || 'estimated'} training examples`}
                        </Typography>
                      </Paper>
                    </Grid>
                  </>
                )}
              </Grid>
            </TabPanel>
            
            {/* Training Data Tab */}
            <TabPanel value={activeTab} index={1}>
              <Typography variant="subtitle1" gutterBottom>
                Training Examples
                <Tooltip title="Provide examples of interactions that demonstrate how your agent should respond. Higher quality and quantity of examples leads to better fine-tuning results.">
                  <IconButton size="small" sx={{ ml: 1 }}>
                    <HelpOutlineIcon fontSize="small" />
                  </IconButton>
                </Tooltip>
              </Typography>
              
              <Grid container spacing={3}>
                {/* File Upload */}
                <Grid item xs={12}>
                  <Paper variant="outlined" sx={{ p: 2 }}>
                    <Typography variant="subtitle2" gutterBottom>
                      Upload Examples File
                    </Typography>
                    <Box sx={{ display: 'flex', alignItems: 'center', mt: 1 }}>
                      <Button
                        variant="outlined"
                        component="label"
                        startIcon={<UploadFileIcon />}
                      >
                        Select File
                        <input
                          type="file"
                          hidden
                          accept=".jsonl,.csv,.xlsx"
                          onChange={handleFileUpload}
                        />
                      </Button>
                      <Typography variant="caption" sx={{ ml: 2, color: 'text.secondary' }}>
                        Supported formats: JSONL, CSV, Excel
                      </Typography>
                    </Box>
                    {uploadedExamplesFile && (
                      <Typography variant="body2" sx={{ mt: 1 }}>
                        Uploaded: {uploadedExamplesFile.name}
                      </Typography>
                    )}
                  </Paper>
                </Grid>
                
                {/* Manual Example Entry */}
                <Grid item xs={12}>
                  <Paper variant="outlined" sx={{ p: 2 }}>
                    <Typography variant="subtitle2" gutterBottom>
                      Add Example Manually
                    </Typography>
                    
                    <Grid container spacing={2}>
                      <Grid item xs={12}>
                        <TextField
                          fullWidth
                          label="User Message"
                          multiline
                          rows={2}
                          value={newExample.user}
                          onChange={(e) => setNewExample({...newExample, user: e.target.value})}
                          placeholder="Enter what the user would say..."
                        />
                      </Grid>
                      <Grid item xs={12}>
                        <TextField
                          fullWidth
                          label="Assistant Response"
                          multiline
                          rows={3}
                          value={newExample.assistant}
                          onChange={(e) => setNewExample({...newExample, assistant: e.target.value})}
                          placeholder="Enter how the assistant should respond..."
                        />
                      </Grid>
                      <Grid item xs={12}>
                        <Button
                          variant="contained"
                          startIcon={<AddIcon />}
                          onClick={handleAddExample}
                          disabled={!newExample.user.trim() || !newExample.assistant.trim()}
                        >
                          Add Example
                        </Button>
                      </Grid>
                    </Grid>
                  </Paper>
                </Grid>
                
                {/* Examples List */}
                <Grid item xs={12}>
                  <Typography variant="subtitle2" gutterBottom>
                    Training Examples ({currentConfig.trainingDataset.examples.length})
                  </Typography>
                  
                  <Paper variant="outlined">
                    {currentConfig.trainingDataset.examples.length === 0 ? (
                      <Box sx={{ p: 3, textAlign: 'center' }}>
                        <Typography variant="body2" color="text.secondary">
                          No examples added yet. Upload a file or add examples manually.
                        </Typography>
                      </Box>
                    ) : (
                      <List>
                        {currentConfig.trainingDataset.examples.slice(0, 5).map((example) => (
                          <ListItem key={example.id} divider alignItems="flex-start">
                            <ListItemIcon>
                              <DescriptionIcon />
                            </ListItemIcon>
                            <ListItemText
                              primary={<Typography noWrap>{example.user}</Typography>}
                              secondary={
                                <Typography 
                                  noWrap 
                                  variant="body2" 
                                  color="text.secondary"
                                  sx={{ maxWidth: '500px' }}
                                >
                                  {example.assistant}
                                </Typography>
                              }
                            />
                            <ListItemSecondaryAction>
                              <IconButton edge="end" onClick={() => handleRemoveExample(example.id)}>
                                <DeleteIcon />
                              </IconButton>
                            </ListItemSecondaryAction>
                          </ListItem>
                        ))}
                        
                        {currentConfig.trainingDataset.examples.length > 5 && (
                          <ListItem>
                            <ListItemText
                              primary={
                                <Typography color="text.secondary">
                                  +{currentConfig.trainingDataset.examples.length - 5} more examples
                                </Typography>
                              }
                            />
                          </ListItem>
                        )}
                      </List>
                    )}
                  </Paper>
                </Grid>
                
                {/* Save Dataset */}
                {currentConfig.trainingDataset.examples.length > 0 && (
                  <Grid item xs={12}>
                    <Box sx={{ display: 'flex', alignItems: 'center', mt: 1 }}>
                      <TextField
                        label="Dataset Name"
                        size="small"
                        value={newDatasetName}
                        onChange={(e) => setNewDatasetName(e.target.value)}
                        sx={{ mr: 2 }}
                      />
                      <Button
                        variant="outlined"
                        startIcon={<DatasetIcon />}
                        onClick={handleSaveDataset}
                        disabled={!newDatasetName}
                      >
                        Save Dataset for Reuse
                      </Button>
                    </Box>
                  </Grid>
                )}
              </Grid>
            </TabPanel>
            
            {/* Parameters Tab */}
            <TabPanel value={activeTab} index={2}>
              <Typography variant="subtitle1" gutterBottom>
                Training Parameters
                <Tooltip title="Adjust training parameters to control the fine-tuning process. Default values work well for most use cases.">
                  <IconButton size="small" sx={{ ml: 1 }}>
                    <HelpOutlineIcon fontSize="small" />
                  </IconButton>
                </Tooltip>
              </Typography>
              
              <Grid container spacing={3}>
                {/* Epochs */}
                <Grid item xs={12} md={4}>
                  <Typography id="epochs-slider-label" gutterBottom>
                    Epochs: {currentConfig.hyperParams.epochs}
                  </Typography>
                  <Slider
                    value={currentConfig.hyperParams.epochs}
                    onChange={(e, value) => handleChange('hyperParams', {
                      ...currentConfig.hyperParams,
                      epochs: value
                    })}
                    step={1}
                    marks={[
                      { value: 1, label: '1' },
                      { value: 3, label: '3' },
                      { value: 5, label: '5' },
                    ]}
                    min={1}
                    max={5}
                    valueLabelDisplay="auto"
                    aria-labelledby="epochs-slider-label"
                  />
                  <FormHelperText>
                    Number of training passes through the data
                  </FormHelperText>
                </Grid>
                
                {/* Batch Size */}
                <Grid item xs={12} md={4}>
                  <Typography id="batch-slider-label" gutterBottom>
                    Batch Size: {currentConfig.hyperParams.batchSize}
                  </Typography>
                  <Slider
                    value={currentConfig.hyperParams.batchSize}
                    onChange={(e, value) => handleChange('hyperParams', {
                      ...currentConfig.hyperParams,
                      batchSize: value
                    })}
                    step={1}
                    marks={[
                      { value: 1, label: '1' },
                      { value: 4, label: '4' },
                      { value: 8, label: '8' },
                    ]}
                    min={1}
                    max={8}
                    valueLabelDisplay="auto"
                    aria-labelledby="batch-slider-label"
                  />
                  <FormHelperText>
                    Number of examples processed together
                  </FormHelperText>
                </Grid>
                
                {/* Learning Rate */}
                <Grid item xs={12} md={4}>
                  <Typography id="lr-slider-label" gutterBottom>
                    Learning Rate: {currentConfig.hyperParams.learningRate.toExponential(2)}
                  </Typography>
                  <Slider
                    value={Math.log10(currentConfig.hyperParams.learningRate) + 5}  // Transform for UI
                    onChange={(e, value) => handleChange('hyperParams', {
                      ...currentConfig.hyperParams,
                      learningRate: Math.pow(10, value - 5)  // Transform back
                    })}
                    step={0.5}
                    marks={[
                      { value: 0, label: '1e-5' },
                      { value: 1, label: '1e-4' },
                      { value: 2, label: '1e-3' },
                    ]}
                    min={0}
                    max={2}
                    valueLabelDisplay="auto"
                    aria-labelledby="lr-slider-label"
                    valueLabelFormat={(value) => Math.pow(10, value - 5).toExponential(1)}
                  />
                  <FormHelperText>
                    Controls how quickly the model adapts
                  </FormHelperText>
                </Grid>
                
                {/* Advanced Settings */}
                <Grid item xs={12}>
                  <Divider sx={{ my: 2 }} />
                  <Typography variant="subtitle2" gutterBottom>
                    Additional Settings
                  </Typography>
                  
                  <FormControlLabel
                    control={<Switch defaultChecked />}
                    label="Enable early stopping"
                  />
                  
                  <FormControlLabel
                    control={<Switch defaultChecked />}
                    label="Save checkpoints during training"
                  />
                </Grid>
                
                {/* Training Controls */}
                <Grid item xs={12}>
                  <Paper variant="outlined" sx={{ p: 2, mt: 2 }}>
                    <Grid container spacing={2} alignItems="center">
                      <Grid item xs={12} md={6}>
                        <Typography variant="subtitle2" gutterBottom>
                          Start Fine-Tuning Process
                        </Typography>
                        <Typography variant="body2" color="text.secondary" paragraph>
                          Fine-tuning typically takes 30-60 minutes depending on data size and parameters.
                        </Typography>
                        
                        <Button
                          variant="contained"
                          startIcon={<CloudUploadIcon />}
                          onClick={handleStartFineTuning}
                          disabled={
                            fineTuningInProgress || 
                            currentConfig.trainingDataset.examples.length === 0
                          }
                        >
                          {fineTuningInProgress ? 'Fine-Tuning in Progress...' : 'Start Fine-Tuning'}
                        </Button>
                      </Grid>
                      
                      {fineTuningInProgress && (
                        <Grid item xs={12} md={6}>
                          <Typography variant="body2" gutterBottom>
                            Progress: {Math.round(progress)}%
                          </Typography>
                          <LinearProgress variant="determinate" value={progress} sx={{ height: 10, borderRadius: 5 }} />
                          <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block' }}>
                            Estimated time remaining: {Math.round((100 - progress) / 5)} minutes
                          </Typography>
                        </Grid>
                      )}
                    </Grid>
                  </Paper>
                </Grid>
              </Grid>
            </TabPanel>
          </Box>
        </>
      )}
    </Box>
  );
};

export default FineTuningConfig; 