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
  Chip,
  Stack,
  IconButton,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  ListItemSecondaryAction,
  Button,
  Alert,
  Tooltip,
} from '@mui/material';
import HelpOutlineIcon from '@mui/icons-material/HelpOutline';
import DeleteIcon from '@mui/icons-material/Delete';
import AddIcon from '@mui/icons-material/Add';
import SubdirectoryArrowRightIcon from '@mui/icons-material/SubdirectoryArrowRight';
import ArrowUpwardIcon from '@mui/icons-material/ArrowUpward';
import ArrowDownwardIcon from '@mui/icons-material/ArrowDownward';

/**
 * HierarchicalConfig - Component for configuring hierarchical agent relationships
 * 
 * @param {Object} props - Component props
 * @param {Object} props.config - Current hierarchical configuration
 * @param {Function} props.onChange - Function to update the configuration
 * @param {Array} props.availableAgents - List of existing agents that can be parents/children
 */
const HierarchicalConfig = ({ 
  config, 
  onChange, 
  availableAgents = [] 
}) => {
  // Default configuration structure
  const defaultConfig = {
    isHierarchical: false,
    role: 'standalone', // standalone, parent, child, or hybrid (both parent and child)
    parentId: null,
    childrenIds: [],
    routingStrategy: 'round-robin', // round-robin, skill-based, or priority
    skillMapping: {}
  };

  // Use provided config or default
  const currentConfig = config || defaultConfig;

  // State to track whether to show advanced options
  const [showAdvanced, setShowAdvanced] = useState(false);

  // Handle changes to any field in the configuration
  const handleChange = (field, value) => {
    const newConfig = {
      ...currentConfig,
      [field]: value
    };

    // Auto-set the role based on parent/children relationships
    if (field === 'parentId' || field === 'childrenIds') {
      const hasParent = field === 'parentId' ? value !== null : currentConfig.parentId !== null;
      const hasChildren = field === 'childrenIds' ? value.length > 0 : currentConfig.childrenIds.length > 0;
      
      if (hasParent && hasChildren) {
        newConfig.role = 'hybrid';
      } else if (hasParent) {
        newConfig.role = 'child';
      } else if (hasChildren) {
        newConfig.role = 'parent';
      } else {
        newConfig.role = 'standalone';
      }
    }

    // If setting as non-hierarchical, reset all related fields
    if (field === 'isHierarchical' && value === false) {
      newConfig.parentId = null;
      newConfig.childrenIds = [];
      newConfig.role = 'standalone';
      newConfig.routingStrategy = 'round-robin';
      newConfig.skillMapping = {};
    }

    onChange(newConfig);
  };

  // Handle toggling a child agent
  const handleToggleChild = (agentId) => {
    const childrenIds = [...currentConfig.childrenIds];
    const index = childrenIds.indexOf(agentId);
    
    if (index === -1) {
      // Add child
      childrenIds.push(agentId);
    } else {
      // Remove child
      childrenIds.splice(index, 1);
    }
    
    handleChange('childrenIds', childrenIds);
  };

  // Handle updating skill mapping for a child agent
  const handleSkillUpdate = (agentId, skills) => {
    const newSkillMapping = {
      ...currentConfig.skillMapping,
      [agentId]: skills
    };
    
    if (skills.length === 0) {
      delete newSkillMapping[agentId];
    }
    
    const newConfig = {
      ...currentConfig,
      skillMapping: newSkillMapping
    };
    
    onChange(newConfig);
  };

  // Reorder children (for priority-based routing)
  const handleReorderChild = (agentId, direction) => {
    const childrenIds = [...currentConfig.childrenIds];
    const index = childrenIds.indexOf(agentId);
    
    if (index === -1) return;
    
    if (direction === 'up' && index > 0) {
      // Move up (higher priority)
      [childrenIds[index], childrenIds[index - 1]] = [childrenIds[index - 1], childrenIds[index]];
    } else if (direction === 'down' && index < childrenIds.length - 1) {
      // Move down (lower priority)
      [childrenIds[index], childrenIds[index + 1]] = [childrenIds[index + 1], childrenIds[index]];
    }
    
    handleChange('childrenIds', childrenIds);
  };

  // Get available parents (excluding self and current children)
  const availableParents = availableAgents.filter(agent => 
    !currentConfig.childrenIds.includes(agent.id) && 
    agent.id !== currentConfig.id
  );

  // Get available children (excluding self and current parent)
  const availableChildren = availableAgents.filter(agent => 
    agent.id !== currentConfig.parentId && 
    agent.id !== currentConfig.id
  );

  return (
    <Box>
      <Typography variant="h6" gutterBottom>
        Hierarchical Configuration
        <Tooltip title="Configure this agent to work in a team with other agents. Parent agents can delegate tasks to children, and child agents can escalate to parents.">
          <IconButton size="small" sx={{ ml: 1 }}>
            <HelpOutlineIcon fontSize="small" />
          </IconButton>
        </Tooltip>
      </Typography>

      <FormControlLabel
        control={
          <Switch
            checked={currentConfig.isHierarchical}
            onChange={(e) => handleChange('isHierarchical', e.target.checked)}
          />
        }
        label="Enable Hierarchical Capabilities"
      />
      
      {!currentConfig.isHierarchical && (
        <Alert severity="info" sx={{ mt: 2 }}>
          Enable hierarchical capabilities to create teams of agents that can work together. 
          Parent agents can delegate tasks to specialized child agents, while child agents can escalate complex issues to parent agents.
        </Alert>
      )}

      {currentConfig.isHierarchical && (
        <>
          {/* Role Selection */}
          <FormControl fullWidth margin="normal">
            <InputLabel id="role-type-label">Agent Role</InputLabel>
            <Select
              labelId="role-type-label"
              value={currentConfig.role}
              onChange={(e) => handleChange('role', e.target.value)}
              label="Agent Role"
            >
              <MenuItem value="standalone">Standalone Agent (No Hierarchy)</MenuItem>
              <MenuItem value="parent">Parent Agent (Manager/Orchestrator)</MenuItem>
              <MenuItem value="child">Child Agent (Specialized Worker)</MenuItem>
              <MenuItem value="hybrid">Hybrid Agent (Both Parent and Child)</MenuItem>
            </Select>
            <FormHelperText>
              Define how this agent relates to others in a hierarchical structure
            </FormHelperText>
          </FormControl>

          {/* Parent Selection (for child or hybrid roles) */}
          {(currentConfig.role === 'child' || currentConfig.role === 'hybrid') && (
            <FormControl fullWidth margin="normal">
              <InputLabel id="parent-agent-label">Parent Agent</InputLabel>
              <Select
                labelId="parent-agent-label"
                value={currentConfig.parentId || ''}
                onChange={(e) => handleChange('parentId', e.target.value || null)}
                label="Parent Agent"
              >
                <MenuItem value="">
                  <em>None</em>
                </MenuItem>
                {availableParents.map(agent => (
                  <MenuItem key={agent.id} value={agent.id}>
                    {agent.name}
                  </MenuItem>
                ))}
              </Select>
              <FormHelperText>
                Select a parent agent that can delegate tasks to this agent
              </FormHelperText>
            </FormControl>
          )}

          {/* Children Configuration (for parent or hybrid roles) */}
          {(currentConfig.role === 'parent' || currentConfig.role === 'hybrid') && (
            <Box mt={3}>
              <Typography variant="subtitle1" gutterBottom>
                Child Agents
                <Tooltip title="Select agents that will work under this agent's direction. The parent can delegate tasks to these children based on the routing strategy.">
                  <IconButton size="small" sx={{ ml: 1 }}>
                    <HelpOutlineIcon fontSize="small" />
                  </IconButton>
                </Tooltip>
              </Typography>

              {/* Routing Strategy */}
              <FormControl fullWidth margin="normal">
                <InputLabel id="routing-strategy-label">Routing Strategy</InputLabel>
                <Select
                  labelId="routing-strategy-label"
                  value={currentConfig.routingStrategy}
                  onChange={(e) => handleChange('routingStrategy', e.target.value)}
                  label="Routing Strategy"
                >
                  <MenuItem value="round-robin">Round Robin (Balance workload evenly)</MenuItem>
                  <MenuItem value="skill-based">Skill-Based (Match tasks to agent capabilities)</MenuItem>
                  <MenuItem value="priority">Priority-Based (Try higher priority agents first)</MenuItem>
                </Select>
                <FormHelperText>
                  How this agent will decide which child to delegate tasks to
                </FormHelperText>
              </FormControl>

              {/* Children List */}
              <Paper variant="outlined" sx={{ mt: 2, p: 2, bgcolor: 'background.paper' }}>
                {currentConfig.childrenIds.length === 0 ? (
                  <Typography variant="body2" color="text.secondary" sx={{ py: 2, textAlign: 'center' }}>
                    No child agents selected. Add children below.
                  </Typography>
                ) : (
                  <List dense>
                    {currentConfig.childrenIds.map((childId, index) => {
                      const childAgent = availableAgents.find(a => a.id === childId) || { id: childId, name: `Agent ${childId}` };
                      return (
                        <ListItem key={childId} divider={index < currentConfig.childrenIds.length - 1}>
                          <ListItemIcon>
                            <SubdirectoryArrowRightIcon />
                          </ListItemIcon>
                          <ListItemText 
                            primary={childAgent.name}
                            secondary={
                              currentConfig.routingStrategy === 'skill-based' && (
                                <>
                                  {currentConfig.skillMapping[childId] && currentConfig.skillMapping[childId].length > 0 ? (
                                    <Stack direction="row" spacing={0.5} sx={{ mt: 0.5, flexWrap: 'wrap' }}>
                                      {currentConfig.skillMapping[childId].map(skill => (
                                        <Chip 
                                          key={skill} 
                                          label={skill} 
                                          size="small" 
                                          variant="outlined"
                                          onDelete={() => {
                                            const skills = currentConfig.skillMapping[childId].filter(s => s !== skill);
                                            handleSkillUpdate(childId, skills);
                                          }}
                                        />
                                      ))}
                                    </Stack>
                                  ) : (
                                    <Typography variant="caption" color="error">No skills defined</Typography>
                                  )}
                                </>
                              )
                            }
                          />
                          <ListItemSecondaryAction>
                            {currentConfig.routingStrategy === 'priority' && (
                              <>
                                <Tooltip title="Higher priority">
                                  <IconButton 
                                    edge="end" 
                                    disabled={index === 0}
                                    onClick={() => handleReorderChild(childId, 'up')}
                                  >
                                    <ArrowUpwardIcon />
                                  </IconButton>
                                </Tooltip>
                                <Tooltip title="Lower priority">
                                  <IconButton 
                                    edge="end" 
                                    disabled={index === currentConfig.childrenIds.length - 1}
                                    onClick={() => handleReorderChild(childId, 'down')}
                                  >
                                    <ArrowDownwardIcon />
                                  </IconButton>
                                </Tooltip>
                              </>
                            )}
                            <Tooltip title="Remove child">
                              <IconButton 
                                edge="end"
                                onClick={() => handleToggleChild(childId)}
                              >
                                <DeleteIcon />
                              </IconButton>
                            </Tooltip>
                          </ListItemSecondaryAction>
                        </ListItem>
                      );
                    })}
                  </List>
                )}

                {/* Add Child Dropdown */}
                <Box sx={{ mt: 2 }}>
                  <FormControl fullWidth size="small">
                    <InputLabel id="add-child-label">Add Child Agent</InputLabel>
                    <Select
                      labelId="add-child-label"
                      value=""
                      onChange={(e) => {
                        if (e.target.value) handleToggleChild(e.target.value);
                      }}
                      label="Add Child Agent"
                      displayEmpty
                    >
                      <MenuItem value="">
                        <em>Select an agent to add</em>
                      </MenuItem>
                      {availableChildren
                        .filter(agent => !currentConfig.childrenIds.includes(agent.id))
                        .map(agent => (
                          <MenuItem key={agent.id} value={agent.id}>
                            {agent.name}
                          </MenuItem>
                        ))
                      }
                    </Select>
                  </FormControl>
                </Box>

                {/* Skill Mapping for Skill-Based Routing */}
                {currentConfig.routingStrategy === 'skill-based' && currentConfig.childrenIds.length > 0 && (
                  <Box sx={{ mt: 3 }}>
                    <Typography variant="subtitle2" gutterBottom>
                      Skill Mapping
                      <Tooltip title="Define what skills each child agent has. When the parent receives a task, it will evaluate which child has the most relevant skills.">
                        <IconButton size="small" sx={{ ml: 1 }}>
                          <HelpOutlineIcon fontSize="small" />
                        </IconButton>
                      </Tooltip>
                    </Typography>
                    
                    {currentConfig.childrenIds.map((childId) => {
                      const childAgent = availableAgents.find(a => a.id === childId) || { id: childId, name: `Agent ${childId}` };
                      const skills = currentConfig.skillMapping[childId] || [];
                      
                      return (
                        <Box key={childId} sx={{ mb: 2 }}>
                          <Typography variant="body2">{childAgent.name}</Typography>
                          <Box sx={{ display: 'flex', mt: 0.5 }}>
                            <TextField
                              size="small"
                              placeholder="Add skill (e.g., 'customer service', 'technical')"
                              fullWidth
                              onKeyDown={(e) => {
                                if (e.key === 'Enter' && e.target.value) {
                                  handleSkillUpdate(childId, [...skills, e.target.value]);
                                  e.target.value = '';
                                }
                              }}
                            />
                            <Button
                              variant="outlined"
                              size="small"
                              startIcon={<AddIcon />}
                              onClick={(e) => {
                                const input = e.target.previousSibling.querySelector('input');
                                if (input && input.value) {
                                  handleSkillUpdate(childId, [...skills, input.value]);
                                  input.value = '';
                                }
                              }}
                            >
                              Add
                            </Button>
                          </Box>
                        </Box>
                      );
                    })}
                  </Box>
                )}
              </Paper>
            </Box>
          )}

          {/* Advanced Configuration Toggle */}
          <Box mt={3}>
            <FormControlLabel
              control={
                <Switch
                  checked={showAdvanced}
                  onChange={(e) => setShowAdvanced(e.target.checked)}
                />
              }
              label="Show Advanced Configuration"
            />
          </Box>

          {/* Advanced Configuration Options */}
          {showAdvanced && (
            <Paper variant="outlined" sx={{ mt: 2, p: 2 }}>
              <Typography variant="subtitle1" gutterBottom>
                Advanced Hierarchical Settings
              </Typography>
              
              <Alert severity="info" sx={{ mb: 2 }}>
                Advanced settings will be available in a future update, including custom routing logic, 
                feedback mechanisms, and sophisticated delegation strategies.
              </Alert>
            </Paper>
          )}
        </>
      )}
    </Box>
  );
};

export default HierarchicalConfig; 