import React, { useState } from 'react';
import {
  Box,
  Typography,
  FormControl,
  FormHelperText,
  InputLabel,
  Select,
  MenuItem,
  TextField,
  Grid,
  Switch,
  FormControlLabel,
  Tooltip,
  IconButton,
  Paper,
  Chip,
  Stack,
} from '@mui/material';
import HelpOutlineIcon from '@mui/icons-material/HelpOutline';

// Model category definitions
const MODEL_CATEGORIES = {
  PROPRIETARY: 'proprietary',
  LOCAL: 'local',
  OPEN_SOURCE: 'open_source',
  CUSTOM: 'custom',
};

// Model provider definitions
const MODEL_PROVIDERS = {
  OPENAI: 'openai',
  GOOGLE: 'google',
  ANTHROPIC: 'anthropic',
  META: 'meta',
  MISTRAL: 'mistral',
  COHERE: 'cohere',
  OLLAMA: 'ollama',
  HUGGINGFACE: 'huggingface',
  CUSTOM: 'custom',
};

// Default models with their details
const DEFAULT_MODELS = [
  // OpenAI Models
  {
    id: 'gpt-4o',
    name: 'GPT-4o',
    provider: MODEL_PROVIDERS.OPENAI,
    category: MODEL_CATEGORIES.PROPRIETARY,
    contextWindow: 128000,
    costPer1kTokensInput: 0.005,
    costPer1kTokensOutput: 0.015,
    description: 'OpenAI\'s most advanced model with vision capabilities, optimal for complex reasoning and multimodal tasks.',
    tags: ['multimodal', 'vision', 'reasoning', 'recommended'],
    released: '2024-05',
  },
  {
    id: 'gpt-4-1106-preview',
    name: 'GPT-4 Turbo',
    provider: MODEL_PROVIDERS.OPENAI,
    category: MODEL_CATEGORIES.PROPRIETARY,
    contextWindow: 128000,
    costPer1kTokensInput: 0.01,
    costPer1kTokensOutput: 0.03,
    description: 'OpenAI\'s advanced model with extended context window and improved instruction following.',
    tags: ['reasoning', 'long-context'],
    released: '2023-11',
  },
  {
    id: 'gpt-3.5-turbo',
    name: 'GPT-3.5 Turbo',
    provider: MODEL_PROVIDERS.OPENAI,
    category: MODEL_CATEGORIES.PROPRIETARY,
    contextWindow: 16385,
    costPer1kTokensInput: 0.0005,
    costPer1kTokensOutput: 0.0015,
    description: 'Cost-effective model for simpler tasks and general content generation.',
    tags: ['fast', 'cost-effective'],
    released: '2023-01',
  },
  
  // Anthropic Models
  {
    id: 'claude-3-opus',
    name: 'Claude 3 Opus',
    provider: MODEL_PROVIDERS.ANTHROPIC,
    category: MODEL_CATEGORIES.PROPRIETARY,
    contextWindow: 200000,
    costPer1kTokensInput: 0.015,
    costPer1kTokensOutput: 0.075,
    description: 'Anthropic\'s most capable model, exceptional at complex reasoning, creativity, and instruction following.',
    tags: ['multimodal', 'vision', 'reasoning'],
    released: '2024-03',
  },
  {
    id: 'claude-3-sonnet',
    name: 'Claude 3 Sonnet',
    provider: MODEL_PROVIDERS.ANTHROPIC,
    category: MODEL_CATEGORIES.PROPRIETARY,
    contextWindow: 200000,
    costPer1kTokensInput: 0.003,
    costPer1kTokensOutput: 0.015,
    description: 'Balanced model with strong reasoning and creativity at a lower cost than Opus.',
    tags: ['multimodal', 'balanced', 'recommended'],
    released: '2024-03',
  },
  {
    id: 'claude-3-haiku',
    name: 'Claude 3 Haiku',
    provider: MODEL_PROVIDERS.ANTHROPIC,
    category: MODEL_CATEGORIES.PROPRIETARY,
    contextWindow: 200000,
    costPer1kTokensInput: 0.00025,
    costPer1kTokensOutput: 0.00125,
    description: 'Fast, cost-effective model for simpler tasks while maintaining accuracy.',
    tags: ['fast', 'cost-effective'],
    released: '2024-03',
  },
  
  // Google Models
  {
    id: 'gemini-1.5-pro',
    name: 'Gemini 1.5 Pro',
    provider: MODEL_PROVIDERS.GOOGLE,
    category: MODEL_CATEGORIES.PROPRIETARY,
    contextWindow: 1000000,
    costPer1kTokensInput: 0.00035,
    costPer1kTokensOutput: 0.00175,
    description: 'Google\'s premier model with million-token context window and strong multimodal capabilities.',
    tags: ['multimodal', 'vision', 'long-context', 'recommended'],
    released: '2024-03',
  },
  {
    id: 'gemini-1.0-pro',
    name: 'Gemini 1.0 Pro',
    provider: MODEL_PROVIDERS.GOOGLE,
    category: MODEL_CATEGORIES.PROPRIETARY,
    contextWindow: 32768,
    costPer1kTokensInput: 0.00025,
    costPer1kTokensOutput: 0.0005,
    description: 'Cost-effective model with solid reasoning and multimodal capabilities.',
    tags: ['multimodal', 'cost-effective'],
    released: '2023-12',
  },
  
  // Mistral Models
  {
    id: 'mistral-large',
    name: 'Mistral Large',
    provider: MODEL_PROVIDERS.MISTRAL,
    category: MODEL_CATEGORIES.PROPRIETARY,
    contextWindow: 32768,
    costPer1kTokensInput: 0.0008,
    costPer1kTokensOutput: 0.0024,
    description: 'Mistral\'s most powerful model with strong reasoning capabilities.',
    tags: ['reasoning', 'instruction'],
    released: '2024-02',
  },
  {
    id: 'mistral-small',
    name: 'Mistral Small',
    provider: MODEL_PROVIDERS.MISTRAL,
    category: MODEL_CATEGORIES.PROPRIETARY,
    contextWindow: 32768,
    costPer1kTokensInput: 0.0002,
    costPer1kTokensOutput: 0.0006,
    description: 'Efficient, cost-effective model with good performance on general tasks.',
    tags: ['cost-effective', 'fast'],
    released: '2024-02',
  },
  
  // Cohere Models
  {
    id: 'command-r',
    name: 'Command R',
    provider: MODEL_PROVIDERS.COHERE,
    category: MODEL_CATEGORIES.PROPRIETARY,
    contextWindow: 128000,
    costPer1kTokensInput: 0.0005,
    costPer1kTokensOutput: 0.0015,
    description: 'Cohere\'s reliable model optimized for enterprise use cases.',
    tags: ['enterprise', 'grounding'],
    released: '2024-02',
  },
  
  // Local/Open Source Models
  {
    id: 'ollama:llama3-70b',
    name: 'Llama 3 70B',
    provider: MODEL_PROVIDERS.OLLAMA,
    category: MODEL_CATEGORIES.LOCAL,
    contextWindow: 8192,
    costPer1kTokensInput: 0,
    costPer1kTokensOutput: 0,
    description: 'Meta\'s most powerful open model, comparable to proprietary alternatives.',
    tags: ['free', 'local', 'powerful'],
    released: '2024-04',
  },
  {
    id: 'ollama:llama3-8b',
    name: 'Llama 3 8B',
    provider: MODEL_PROVIDERS.OLLAMA,
    category: MODEL_CATEGORIES.LOCAL,
    contextWindow: 8192,
    costPer1kTokensInput: 0,
    costPer1kTokensOutput: 0,
    description: 'Smaller, efficient Meta model that runs well on consumer hardware.',
    tags: ['free', 'local', 'efficient'],
    released: '2024-04',
  },
  {
    id: 'ollama:mistral-7b',
    name: 'Mistral 7B',
    provider: MODEL_PROVIDERS.OLLAMA,
    category: MODEL_CATEGORIES.LOCAL,
    contextWindow: 8192,
    costPer1kTokensInput: 0,
    costPer1kTokensOutput: 0,
    description: 'Efficient open source model with strong instruction following.',
    tags: ['free', 'local', 'instruction'],
    released: '2023-09',
  },
];

/**
 * ModelSelector - Component for selecting LLM models with detailed information
 * 
 * @param {Object} props - Component props
 * @param {string} props.selectedModel - Currently selected model ID
 * @param {Function} props.onModelChange - Function to call when model selection changes
 * @param {Array} props.customModels - Additional custom models to include in the list
 * @param {boolean} props.showCost - Whether to display cost information (default: true)
 * @param {boolean} props.showLocalModels - Whether to display local models (default: true)
 * @param {boolean} props.allowCustomEndpoint - Whether to allow custom API endpoint configuration (default: false)
 */
const ModelSelector = ({
  selectedModel = 'gpt-4o',
  onModelChange,
  customModels = [],
  showCost = true,
  showLocalModels = true,
  allowCustomEndpoint = false,
}) => {
  // Combine default models with any custom models
  const allModels = [...DEFAULT_MODELS, ...customModels]
    .filter(model => showLocalModels || model.category !== MODEL_CATEGORIES.LOCAL);
  
  // State for custom endpoint configuration
  const [useCustomEndpoint, setUseCustomEndpoint] = useState(false);
  const [customEndpoint, setCustomEndpoint] = useState({
    url: '',
    apiKey: '',
    modelName: '',
  });
  
  // Group models by provider for easier selection
  const modelsByProvider = allModels.reduce((acc, model) => {
    if (!acc[model.provider]) {
      acc[model.provider] = [];
    }
    acc[model.provider].push(model);
    return acc;
  }, {});
  
  // Find the currently selected model object
  const currentModel = allModels.find(model => model.id === selectedModel) || allModels[0];
  
  // Handle model change
  const handleModelChange = (event) => {
    const modelId = event.target.value;
    onModelChange(modelId);
  };
  
  // Handle custom endpoint toggle
  const handleCustomEndpointToggle = (event) => {
    setUseCustomEndpoint(event.target.checked);
    if (!event.target.checked) {
      onModelChange(currentModel.id);
    } else {
      onModelChange('custom');
    }
  };
  
  // Handle custom endpoint field changes
  const handleCustomEndpointChange = (field, value) => {
    const newEndpoint = {
      ...customEndpoint,
      [field]: value,
    };
    setCustomEndpoint(newEndpoint);
    
    // Only update the model if all required fields are filled
    if (newEndpoint.url && newEndpoint.modelName) {
      onModelChange('custom', newEndpoint);
    }
  };
  
  return (
    <Box>
      <Typography variant="h6" gutterBottom>
        Model Selection
        <Tooltip title="Choose the AI model that will power your agent's abilities. Different models have different capabilities, costs, and performance characteristics.">
          <IconButton size="small" sx={{ ml: 1 }}>
            <HelpOutlineIcon fontSize="small" />
          </IconButton>
        </Tooltip>
      </Typography>
      
      {allowCustomEndpoint && (
        <FormControlLabel
          control={
            <Switch
              checked={useCustomEndpoint}
              onChange={handleCustomEndpointToggle}
            />
          }
          label="Use Custom API Endpoint"
          sx={{ mb: 2 }}
        />
      )}
      
      {!useCustomEndpoint ? (
        <>
          <FormControl fullWidth margin="normal">
            <InputLabel id="model-select-label">AI Model</InputLabel>
            <Select
              labelId="model-select-label"
              value={selectedModel}
              onChange={handleModelChange}
              label="AI Model"
            >
              {Object.entries(modelsByProvider).map(([provider, models]) => [
                <MenuItem 
                  key={`provider-${provider}`} 
                  value="" 
                  disabled 
                  sx={{ opacity: 0.7, fontWeight: 'bold' }}
                >
                  {provider.toUpperCase()}
                </MenuItem>,
                ...models.map(model => (
                  <MenuItem key={model.id} value={model.id}>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', width: '100%', alignItems: 'center' }}>
                      <span>{model.name}</span>
                      {model.tags && model.tags.includes('recommended') && (
                        <Chip size="small" color="primary" label="Recommended" sx={{ ml: 1 }} />
                      )}
                    </Box>
                  </MenuItem>
                ))
              ]).flat()}
            </Select>
          </FormControl>

          {currentModel && (
            <Paper variant="outlined" sx={{ mt: 2, p: 2 }}>
              <Typography variant="subtitle1" gutterBottom>
                {currentModel.name}
                <Box component="span" sx={{ ml: 1 }}>
                  {currentModel.tags && (
                    <Stack direction="row" spacing={1} sx={{ display: 'inline-flex', ml: 1 }}>
                      {currentModel.tags.map(tag => (
                        <Chip 
                          key={tag} 
                          label={tag} 
                          size="small"
                          color={tag === 'recommended' ? 'primary' : 'default'}
                          variant={tag === 'free' || tag === 'local' ? 'outlined' : 'filled'}
                        />
                      ))}
                    </Stack>
                  )}
                </Box>
              </Typography>
              
              <Typography variant="body2" color="text.secondary" paragraph>
                {currentModel.description}
              </Typography>
              
              <Grid container spacing={2} sx={{ mt: 1 }}>
                <Grid item xs={12} sm={6}>
                  <Typography variant="body2">
                    <strong>Context Window:</strong> {currentModel.contextWindow.toLocaleString()} tokens
                  </Typography>
                </Grid>
                
                {showCost && currentModel.category !== MODEL_CATEGORIES.LOCAL && (
                  <>
                    <Grid item xs={12} sm={6}>
                      <Typography variant="body2">
                        <strong>Provider:</strong> {currentModel.provider.charAt(0).toUpperCase() + currentModel.provider.slice(1)}
                      </Typography>
                    </Grid>
                    <Grid item xs={12} sm={6}>
                      <Typography variant="body2">
                        <strong>Input Cost:</strong> ${currentModel.costPer1kTokensInput.toFixed(5)} per 1K tokens
                      </Typography>
                    </Grid>
                    <Grid item xs={12} sm={6}>
                      <Typography variant="body2">
                        <strong>Output Cost:</strong> ${currentModel.costPer1kTokensOutput.toFixed(5)} per 1K tokens
                      </Typography>
                    </Grid>
                  </>
                )}
                
                {currentModel.category === MODEL_CATEGORIES.LOCAL && (
                  <Grid item xs={12}>
                    <Typography variant="body2" color="success.main">
                      <strong>Free:</strong> This model runs locally on your hardware
                    </Typography>
                  </Grid>
                )}
              </Grid>
            </Paper>
          )}
        </>
      ) : (
        // Custom endpoint configuration
        <Box sx={{ mt: 2 }}>
          <Typography variant="subtitle1" gutterBottom>
            Custom API Endpoint
          </Typography>
          
          <Grid container spacing={2}>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="API Endpoint URL"
                value={customEndpoint.url}
                onChange={(e) => handleCustomEndpointChange('url', e.target.value)}
                placeholder="https://api.example.com/v1/chat/completions"
                margin="normal"
              />
              <FormHelperText>
                The complete URL to the API endpoint
              </FormHelperText>
            </Grid>
            
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="API Key"
                type="password"
                value={customEndpoint.apiKey}
                onChange={(e) => handleCustomEndpointChange('apiKey', e.target.value)}
                margin="normal"
              />
              <FormHelperText>
                Your API key for this service (stored securely)
              </FormHelperText>
            </Grid>
            
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Model Name"
                value={customEndpoint.modelName}
                onChange={(e) => handleCustomEndpointChange('modelName', e.target.value)}
                placeholder="gpt-4o"
                margin="normal"
              />
              <FormHelperText>
                The model identifier accepted by this API
              </FormHelperText>
            </Grid>
            
            <Grid item xs={12}>
              <FormHelperText>
                <strong>Note:</strong> Custom endpoints require compatible APIs that follow OpenAI's chat completion format
              </FormHelperText>
            </Grid>
          </Grid>
        </Box>
      )}
    </Box>
  );
};

export default ModelSelector; 