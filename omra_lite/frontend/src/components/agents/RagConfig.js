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
  Card,
  CardContent,
  Tab,
  Tabs,
} from '@mui/material';
import HelpOutlineIcon from '@mui/icons-material/HelpOutline';
import DeleteIcon from '@mui/icons-material/Delete';
import UploadFileIcon from '@mui/icons-material/UploadFile';
import LinkIcon from '@mui/icons-material/Link';
import FolderIcon from '@mui/icons-material/Folder';
import DescriptionIcon from '@mui/icons-material/Description';
import WebIcon from '@mui/icons-material/Web';
import StorageIcon from '@mui/icons-material/Storage';

/**
 * TabPanel - Component for displaying tab content
 */
function TabPanel(props) {
  const { children, value, index, ...other } = props;

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`rag-tabpanel-${index}`}
      aria-labelledby={`rag-tab-${index}`}
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
 * RagConfig - Component for configuring RAG (Retrieval-Augmented Generation) settings
 * 
 * @param {Object} props - Component props
 * @param {Object} props.config - Current RAG configuration
 * @param {Function} props.onChange - Function to update configuration
 * @param {Array} props.existingKnowledgeBases - Available knowledge bases
 * @param {Boolean} props.showAdvanced - Whether to show advanced options
 */
const RagConfig = ({
  config,
  onChange,
  existingKnowledgeBases = [],
  showAdvanced = false,
}) => {
  // Default configuration
  const defaultConfig = {
    enabled: false,
    sources: [],
    retrievalStrategy: 'semantic',
    topK: 5,
    similarityThreshold: 0.7,
    useMetadata: true,
    chunkSize: 1000,
    chunkOverlap: 200,
    embeddingModel: 'text-embedding-3-small',
    useHybridSearch: false,
    reranker: 'none',
    customPrompt: '',
  };

  // Merge provided config with defaults
  const currentConfig = { ...defaultConfig, ...config };
  
  // Local state for file uploads and URL inputs
  const [uploadedFiles, setUploadedFiles] = useState([]);
  const [newURL, setNewURL] = useState('');
  const [activeTab, setActiveTab] = useState(0);
  const [newKnowledgeBaseName, setNewKnowledgeBaseName] = useState('');
  const [newKnowledgeBaseDescription, setNewKnowledgeBaseDescription] = useState('');
  
  // Handle changes to any configuration field
  const handleChange = (field, value) => {
    const newConfig = {
      ...currentConfig,
      [field]: value,
    };
    
    onChange(newConfig);
  };
  
  // Handle tab changes
  const handleTabChange = (event, newValue) => {
    setActiveTab(newValue);
  };
  
  // Add a URL to the sources list
  const handleAddURL = () => {
    if (!newURL || !newURL.startsWith('http')) return;
    
    const newSource = {
      id: `url-${Date.now()}`,
      type: 'url',
      url: newURL,
      title: newURL.split('/').pop() || 'Web Page',
      dateAdded: new Date().toISOString(),
    };
    
    handleChange('sources', [...currentConfig.sources, newSource]);
    setNewURL('');
  };
  
  // Handle file uploads
  const handleFileUpload = (event) => {
    const files = event.target.files;
    if (!files || files.length === 0) return;
    
    // Create new sources from files
    const newSources = Array.from(files).map(file => ({
      id: `file-${Date.now()}-${file.name.replace(/\s+/g, '-')}`,
      type: 'file',
      filename: file.name,
      title: file.name,
      size: file.size,
      contentType: file.type,
      dateAdded: new Date().toISOString(),
      // In a real app, you'd upload the file and store a reference
      // For this mock-up, we're just storing file metadata
      file: file, // This would normally be replaced with a URL after upload
    }));
    
    setUploadedFiles([...uploadedFiles, ...Array.from(files)]);
    handleChange('sources', [...currentConfig.sources, ...newSources]);
  };
  
  // Create a new knowledge base from selected sources
  const handleCreateKnowledgeBase = () => {
    if (!newKnowledgeBaseName) return;
    
    // In a real app, this would make an API call to create the knowledge base
    alert(`Created knowledge base: ${newKnowledgeBaseName}`);
    
    setNewKnowledgeBaseName('');
    setNewKnowledgeBaseDescription('');
  };
  
  // Add an existing knowledge base to sources
  const handleAddKnowledgeBase = (kbId) => {
    const kb = existingKnowledgeBases.find(kb => kb.id === kbId);
    if (!kb) return;
    
    const newSource = {
      id: `kb-${kbId}`,
      type: 'knowledge_base',
      knowledgeBaseId: kbId,
      title: kb.name,
      description: kb.description,
      dateAdded: new Date().toISOString(),
    };
    
    handleChange('sources', [...currentConfig.sources, newSource]);
  };
  
  // Remove a source from the list
  const handleRemoveSource = (sourceId) => {
    const newSources = currentConfig.sources.filter(source => source.id !== sourceId);
    handleChange('sources', newSources);
  };
  
  // Get icon based on source type
  const getSourceIcon = (type) => {
    switch (type) {
      case 'url':
        return <WebIcon />;
      case 'file':
        return <DescriptionIcon />;
      case 'knowledge_base':
        return <StorageIcon />;
      default:
        return <FolderIcon />;
    }
  };
  
  return (
    <Box>
      <Typography variant="h6" gutterBottom>
        Retrieval-Augmented Generation (RAG)
        <Tooltip title="RAG enables your agent to retrieve relevant information from documents, websites, and knowledge bases when answering questions.">
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
        label="Enable RAG Capabilities"
      />
      
      {!currentConfig.enabled && (
        <Alert severity="info" sx={{ mt: 2 }}>
          Enable RAG to allow your agent to retrieve and cite knowledge from documents, websites, and databases.
          This significantly improves accuracy for domain-specific questions.
        </Alert>
      )}
      
      {currentConfig.enabled && (
        <>
          {/* Knowledge Sources Tabs */}
          <Box sx={{ mt: 3 }}>
            <Tabs value={activeTab} onChange={handleTabChange} aria-label="RAG source tabs">
              <Tab label="Documents & URLs" />
              <Tab label="Knowledge Bases" />
              {showAdvanced && <Tab label="Advanced Settings" />}
            </Tabs>
            
            {/* Documents & URLs Tab */}
            <TabPanel value={activeTab} index={0}>
              <Grid container spacing={2}>
                {/* File Upload */}
                <Grid item xs={12}>
                  <Paper variant="outlined" sx={{ p: 2 }}>
                    <Typography variant="subtitle2" gutterBottom>
                      Upload Documents
                    </Typography>
                    <Box sx={{ display: 'flex', alignItems: 'center', mt: 1 }}>
                      <Button
                        variant="outlined"
                        component="label"
                        startIcon={<UploadFileIcon />}
                      >
                        Select Files
                        <input
                          type="file"
                          hidden
                          multiple
                          onChange={handleFileUpload}
                        />
                      </Button>
                      <Typography variant="caption" sx={{ ml: 2, color: 'text.secondary' }}>
                        Supported formats: PDF, DOCX, TXT, CSV, PPTX
                      </Typography>
                    </Box>
                  </Paper>
                </Grid>
                
                {/* URL Input */}
                <Grid item xs={12}>
                  <Paper variant="outlined" sx={{ p: 2 }}>
                    <Typography variant="subtitle2" gutterBottom>
                      Add Web Pages
                    </Typography>
                    <Box sx={{ display: 'flex', alignItems: 'center', mt: 1 }}>
                      <TextField
                        fullWidth
                        placeholder="https://example.com/page"
                        value={newURL}
                        onChange={(e) => setNewURL(e.target.value)}
                        onKeyDown={(e) => {
                          if (e.key === 'Enter') handleAddURL();
                        }}
                        size="small"
                      />
                      <Button
                        variant="outlined"
                        sx={{ ml: 1, whiteSpace: 'nowrap' }}
                        startIcon={<LinkIcon />}
                        onClick={handleAddURL}
                        disabled={!newURL || !newURL.startsWith('http')}
                      >
                        Add URL
                      </Button>
                    </Box>
                  </Paper>
                </Grid>
                
                {/* Selected Sources List */}
                <Grid item xs={12}>
                  <Typography variant="subtitle1" gutterBottom>
                    Selected Sources
                    <Tooltip title="These sources will be processed and made available to your agent for retrieving relevant information when answering questions.">
                      <IconButton size="small" sx={{ ml: 1 }}>
                        <HelpOutlineIcon fontSize="small" />
                      </IconButton>
                    </Tooltip>
                  </Typography>
                  
                  <Paper variant="outlined">
                    {currentConfig.sources.length === 0 ? (
                      <Box sx={{ p: 3, textAlign: 'center' }}>
                        <Typography variant="body2" color="text.secondary">
                          No sources added yet. Upload documents or add URLs above.
                        </Typography>
                      </Box>
                    ) : (
                      <List dense>
                        {currentConfig.sources.map((source) => (
                          <ListItem key={source.id} divider>
                            <ListItemIcon>
                              {getSourceIcon(source.type)}
                            </ListItemIcon>
                            <ListItemText
                              primary={source.title}
                              secondary={
                                source.type === 'url' ? source.url :
                                source.type === 'file' ? `File • ${(source.size / 1024 / 1024).toFixed(2)} MB` :
                                source.type === 'knowledge_base' ? 'Knowledge Base' : ''
                              }
                            />
                            <ListItemSecondaryAction>
                              <IconButton
                                edge="end"
                                onClick={() => handleRemoveSource(source.id)}
                              >
                                <DeleteIcon />
                              </IconButton>
                            </ListItemSecondaryAction>
                          </ListItem>
                        ))}
                      </List>
                    )}
                  </Paper>
                </Grid>
                
                {/* Create Knowledge Base Option */}
                {currentConfig.sources.length > 0 && (
                  <Grid item xs={12}>
                    <Paper variant="outlined" sx={{ p: 2, mt: 2 }}>
                      <Typography variant="subtitle2" gutterBottom>
                        Save as Knowledge Base
                      </Typography>
                      <Typography variant="body2" color="text.secondary" paragraph>
                        Save these sources as a reusable knowledge base for this and other agents.
                      </Typography>
                      
                      <Grid container spacing={2}>
                        <Grid item xs={12} sm={6}>
                          <TextField
                            fullWidth
                            label="Knowledge Base Name"
                            value={newKnowledgeBaseName}
                            onChange={(e) => setNewKnowledgeBaseName(e.target.value)}
                            size="small"
                          />
                        </Grid>
                        <Grid item xs={12} sm={6}>
                          <TextField
                            fullWidth
                            label="Description (Optional)"
                            value={newKnowledgeBaseDescription}
                            onChange={(e) => setNewKnowledgeBaseDescription(e.target.value)}
                            size="small"
                          />
                        </Grid>
                        <Grid item xs={12}>
                          <Button
                            variant="contained"
                            disabled={!newKnowledgeBaseName}
                            onClick={handleCreateKnowledgeBase}
                          >
                            Create Knowledge Base
                          </Button>
                        </Grid>
                      </Grid>
                    </Paper>
                  </Grid>
                )}
              </Grid>
            </TabPanel>
            
            {/* Knowledge Bases Tab */}
            <TabPanel value={activeTab} index={1}>
              {existingKnowledgeBases.length === 0 ? (
                <Alert severity="info">
                  No existing knowledge bases found. Create one by adding sources in the Documents & URLs tab.
                </Alert>
              ) : (
                <Grid container spacing={2}>
                  {existingKnowledgeBases.map((kb) => (
                    <Grid item xs={12} sm={6} md={4} key={kb.id}>
                      <Card variant="outlined">
                        <CardContent>
                          <Typography variant="h6" component="div">
                            {kb.name}
                          </Typography>
                          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                            {kb.description || 'No description provided'}
                          </Typography>
                          <Typography variant="caption" display="block">
                            {kb.sourceCount} sources • Created {new Date(kb.createdAt).toLocaleDateString()}
                          </Typography>
                          
                          <Button
                            variant="outlined"
                            size="small"
                            sx={{ mt: 2 }}
                            disabled={currentConfig.sources.some(s => s.type === 'knowledge_base' && s.knowledgeBaseId === kb.id)}
                            onClick={() => handleAddKnowledgeBase(kb.id)}
                          >
                            {currentConfig.sources.some(s => s.type === 'knowledge_base' && s.knowledgeBaseId === kb.id) 
                              ? 'Already Added' 
                              : 'Add to Agent'}
                          </Button>
                        </CardContent>
                      </Card>
                    </Grid>
                  ))}
                </Grid>
              )}
            </TabPanel>
            
            {/* Advanced Settings Tab */}
            {showAdvanced && (
              <TabPanel value={activeTab} index={2}>
                <Grid container spacing={3}>
                  {/* Retrieval Strategy */}
                  <Grid item xs={12} md={6}>
                    <FormControl fullWidth>
                      <InputLabel id="retrieval-strategy-label">Retrieval Strategy</InputLabel>
                      <Select
                        labelId="retrieval-strategy-label"
                        value={currentConfig.retrievalStrategy}
                        onChange={(e) => handleChange('retrievalStrategy', e.target.value)}
                        label="Retrieval Strategy"
                      >
                        <MenuItem value="semantic">Semantic Search (Vector Similarity)</MenuItem>
                        <MenuItem value="keyword">Keyword Search (BM25)</MenuItem>
                        <MenuItem value="hybrid">Hybrid Search (Combined)</MenuItem>
                      </Select>
                      <FormHelperText>
                        How documents are searched and retrieved
                      </FormHelperText>
                    </FormControl>
                  </Grid>
                  
                  {/* Top K */}
                  <Grid item xs={12} md={6}>
                    <Typography id="top-k-slider-label" gutterBottom>
                      Number of Documents to Retrieve (Top K): {currentConfig.topK}
                    </Typography>
                    <Slider
                      value={currentConfig.topK}
                      onChange={(e, value) => handleChange('topK', value)}
                      step={1}
                      marks={[
                        { value: 1, label: '1' },
                        { value: 5, label: '5' },
                        { value: 10, label: '10' },
                        { value: 15, label: '15' },
                      ]}
                      min={1}
                      max={15}
                      valueLabelDisplay="auto"
                      aria-labelledby="top-k-slider-label"
                    />
                    <FormHelperText>
                      Higher values provide more context but may dilute relevance
                    </FormHelperText>
                  </Grid>
                  
                  {/* Chunking Parameters */}
                  <Grid item xs={12}>
                    <Typography variant="subtitle1" gutterBottom>
                      Document Chunking
                      <Tooltip title="Documents are split into smaller chunks for better retrieval. These settings control how documents are divided.">
                        <IconButton size="small" sx={{ ml: 1 }}>
                          <HelpOutlineIcon fontSize="small" />
                        </IconButton>
                      </Tooltip>
                    </Typography>
                    
                    <Grid container spacing={2}>
                      <Grid item xs={12} md={6}>
                        <Typography id="chunk-size-slider-label" gutterBottom>
                          Chunk Size (tokens): {currentConfig.chunkSize}
                        </Typography>
                        <Slider
                          value={currentConfig.chunkSize}
                          onChange={(e, value) => handleChange('chunkSize', value)}
                          step={100}
                          marks={[
                            { value: 500, label: '500' },
                            { value: 1000, label: '1000' },
                            { value: 2000, label: '2000' },
                          ]}
                          min={200}
                          max={2000}
                          valueLabelDisplay="auto"
                          aria-labelledby="chunk-size-slider-label"
                        />
                        <FormHelperText>
                          Larger chunks contain more context but may reduce precision
                        </FormHelperText>
                      </Grid>
                      
                      <Grid item xs={12} md={6}>
                        <Typography id="chunk-overlap-slider-label" gutterBottom>
                          Chunk Overlap (tokens): {currentConfig.chunkOverlap}
                        </Typography>
                        <Slider
                          value={currentConfig.chunkOverlap}
                          onChange={(e, value) => handleChange('chunkOverlap', value)}
                          step={50}
                          marks={[
                            { value: 0, label: '0' },
                            { value: 200, label: '200' },
                            { value: 400, label: '400' },
                          ]}
                          min={0}
                          max={400}
                          valueLabelDisplay="auto"
                          aria-labelledby="chunk-overlap-slider-label"
                        />
                        <FormHelperText>
                          Overlap prevents context loss between chunks
                        </FormHelperText>
                      </Grid>
                    </Grid>
                  </Grid>
                  
                  {/* Embedding Model */}
                  <Grid item xs={12} md={6}>
                    <FormControl fullWidth>
                      <InputLabel id="embedding-model-label">Embedding Model</InputLabel>
                      <Select
                        labelId="embedding-model-label"
                        value={currentConfig.embeddingModel}
                        onChange={(e) => handleChange('embeddingModel', e.target.value)}
                        label="Embedding Model"
                      >
                        <MenuItem value="text-embedding-3-small">OpenAI Text Embedding 3 Small</MenuItem>
                        <MenuItem value="text-embedding-3-large">OpenAI Text Embedding 3 Large</MenuItem>
                        <MenuItem value="text-embedding-ada-002">OpenAI Ada 002 (Legacy)</MenuItem>
                        <MenuItem value="cohere-embed-english">Cohere Embed English</MenuItem>
                        <MenuItem value="local-e5-small">Local E5-small (Free)</MenuItem>
                        <MenuItem value="local-bge-small">Local BGE-small (Free)</MenuItem>
                      </Select>
                      <FormHelperText>
                        Model used to convert text into vector representations
                      </FormHelperText>
                    </FormControl>
                  </Grid>
                  
                  {/* Reranker Model */}
                  <Grid item xs={12} md={6}>
                    <FormControl fullWidth>
                      <InputLabel id="reranker-label">Reranker</InputLabel>
                      <Select
                        labelId="reranker-label"
                        value={currentConfig.reranker}
                        onChange={(e) => handleChange('reranker', e.target.value)}
                        label="Reranker"
                      >
                        <MenuItem value="none">None (Use raw retrieval results)</MenuItem>
                        <MenuItem value="cohere-rerank">Cohere Rerank</MenuItem>
                        <MenuItem value="bge-reranker">BGE Reranker (Free)</MenuItem>
                      </Select>
                      <FormHelperText>
                        Optional second-stage ranking to improve result relevance
                      </FormHelperText>
                    </FormControl>
                  </Grid>
                  
                  {/* Custom Retrieval Prompt */}
                  <Grid item xs={12}>
                    <Typography variant="subtitle1" gutterBottom>
                      Custom Retrieval Prompt
                      <Tooltip title="Customize how retrieved information is presented to the model. Leave empty to use the system default.">
                        <IconButton size="small" sx={{ ml: 1 }}>
                          <HelpOutlineIcon fontSize="small" />
                        </IconButton>
                      </Tooltip>
                    </Typography>
                    
                    <TextField
                      fullWidth
                      multiline
                      rows={4}
                      placeholder="Use the following pieces of retrieved context to answer the user's question. If you don't know the answer based on the context, say that you don't know..."
                      value={currentConfig.customPrompt}
                      onChange={(e) => handleChange('customPrompt', e.target.value)}
                    />
                    <FormHelperText>
                      Advanced: Customize how retrieved information is presented to the model
                    </FormHelperText>
                  </Grid>
                  
                  {/* Advanced Options */}
                  <Grid item xs={12}>
                    <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                      <FormControlLabel
                        control={
                          <Switch
                            checked={currentConfig.useMetadata}
                            onChange={(e) => handleChange('useMetadata', e.target.checked)}
                          />
                        }
                        label="Include document metadata in context"
                      />
                      
                      <FormControlLabel
                        control={
                          <Switch
                            checked={currentConfig.useHybridSearch}
                            onChange={(e) => handleChange('useHybridSearch', e.target.checked)}
                            disabled={currentConfig.retrievalStrategy !== 'semantic'}
                          />
                        }
                        label="Fall back to keyword search when semantic results are low confidence"
                      />
                    </Box>
                  </Grid>
                </Grid>
              </TabPanel>
            )}
          </Box>
        </>
      )}
    </Box>
  );
};

export default RagConfig; 