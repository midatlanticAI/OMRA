import React from 'react';
import {
  Box,
  Typography,
  Grid,
  Card,
  CardContent,
  CardActionArea,
  Chip,
  Tooltip,
  IconButton,
} from '@mui/material';
import HelpOutlineIcon from '@mui/icons-material/HelpOutline';
import ChatIcon from '@mui/icons-material/Chat';
import AlternateEmailIcon from '@mui/icons-material/AlternateEmail';
import PhoneIcon from '@mui/icons-material/Phone';
import SmartToyIcon from '@mui/icons-material/SmartToy';
import ForumIcon from '@mui/icons-material/Forum';
import CodeIcon from '@mui/icons-material/Code';
import StorageIcon from '@mui/icons-material/Storage';

/**
 * Agent types with their descriptions and capabilities
 */
const AGENT_TYPES = [
  {
    id: 'chat',
    name: 'Chat Bot',
    description: 'Interactive chatbot for websites, apps and messaging platforms',
    capabilities: ['text-based', 'real-time', 'webpage'],
    icon: <ChatIcon sx={{ fontSize: 60 }} />,
    color: '#4dabf5',
    channels: ['web', 'discord', 'slack', 'telegram'],
    beginner: true,
  },
  {
    id: 'email',
    name: 'Email Assistant',
    description: 'Automated email responder that can manage inbox communication',
    capabilities: ['scheduled', 'attachments', 'templates'],
    icon: <AlternateEmailIcon sx={{ fontSize: 60 }} />,
    color: '#49bb7b',
    channels: ['smtp', 'gmail', 'outlook'],
    beginner: true,
  },
  {
    id: 'voice',
    name: 'Voice Agent',
    description: 'Voice-enabled assistant for phone calls or voice interfaces',
    capabilities: ['speech', 'phone', 'audio'],
    icon: <PhoneIcon sx={{ fontSize: 60 }} />,
    color: '#f57c00',
    channels: ['twilio', 'jambonz', 'web audio'],
    beginner: false,
  },
  {
    id: 'general',
    name: 'General Assistant',
    description: 'Versatile assistant without predefined channel, flexible for any use case',
    capabilities: ['customizable', 'multi-purpose', 'adaptable'],
    icon: <SmartToyIcon sx={{ fontSize: 60 }} />,
    color: '#9c27b0',
    channels: [],
    beginner: true,
  },
  {
    id: 'knowledge',
    name: 'Knowledge Base',
    description: 'Specialized in retrieving and providing information from a knowledge base',
    capabilities: ['documents', 'search', 'data retrieval'],
    icon: <StorageIcon sx={{ fontSize: 60 }} />,
    color: '#2196f3',
    channels: ['web', 'internal'],
    beginner: false,
  },
  {
    id: 'conversations',
    name: 'Forum Moderator',
    description: 'Monitors and moderates conversations in forums, comment sections or communities',
    capabilities: ['moderation', 'summarization', 'community'],
    icon: <ForumIcon sx={{ fontSize: 60 }} />,
    color: '#ff5722',
    channels: ['reddit', 'discord', 'web forums'],
    beginner: false,
  },
  {
    id: 'code',
    name: 'Code Assistant',
    description: 'Specialized in helping with code, providing solutions and reviewing code',
    capabilities: ['code generation', 'code review', 'explanations'],
    icon: <CodeIcon sx={{ fontSize: 60 }} />,
    color: '#37474f',
    channels: ['ide', 'github', 'cli'],
    beginner: false,
  },
];

/**
 * AgentTypeSelector - Component for selecting agent type with visual cards
 * 
 * @param {Object} props - Component props
 * @param {string} props.selectedType - Currently selected agent type ID
 * @param {Function} props.onTypeChange - Function to call when type selection changes
 * @param {boolean} props.showBeginnerOnly - Whether to only show beginner-friendly types
 */
const AgentTypeSelector = ({
  selectedType,
  onTypeChange,
  showBeginnerOnly = false,
}) => {
  // Filter agent types by beginner-friendly if needed
  const filteredTypes = showBeginnerOnly
    ? AGENT_TYPES.filter(type => type.beginner)
    : AGENT_TYPES;
  
  const handleTypeSelect = (typeId) => {
    onTypeChange(typeId);
  };
  
  return (
    <Box>
      <Typography variant="h6" gutterBottom>
        Agent Type
        <Tooltip title="Choose the type of agent you want to create. This determines the capabilities and channels your agent will support.">
          <IconButton size="small" sx={{ ml: 1 }}>
            <HelpOutlineIcon fontSize="small" />
          </IconButton>
        </Tooltip>
      </Typography>
      
      <Grid container spacing={2} sx={{ mt: 1 }}>
        {filteredTypes.map((type) => (
          <Grid item xs={12} sm={6} md={4} key={type.id}>
            <Card 
              variant={selectedType === type.id ? "elevation" : "outlined"}
              elevation={selectedType === type.id ? 6 : 1}
              sx={{ 
                height: '100%',
                borderColor: selectedType === type.id ? type.color : 'divider',
                transition: 'all 0.3s ease-in-out',
                '&:hover': {
                  transform: 'translateY(-4px)',
                  boxShadow: 3,
                },
              }}
            >
              <CardActionArea 
                onClick={() => handleTypeSelect(type.id)}
                sx={{ height: '100%', display: 'flex', flexDirection: 'column', alignItems: 'stretch' }}
              >
                <Box 
                  sx={{ 
                    py: 3,
                    display: 'flex', 
                    justifyContent: 'center', 
                    bgcolor: type.color + '22', // Light version of the color
                  }}
                >
                  <Box sx={{ color: type.color }}>
                    {type.icon}
                  </Box>
                </Box>
                <CardContent sx={{ flexGrow: 1, display: 'flex', flexDirection: 'column' }}>
                  <Typography variant="h6" component="div" gutterBottom>
                    {type.name}
                    {type.beginner && (
                      <Chip
                        label="Beginner Friendly"
                        size="small"
                        color="success"
                        sx={{ ml: 1 }}
                      />
                    )}
                  </Typography>
                  
                  <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                    {type.description}
                  </Typography>
                  
                  <Box sx={{ mt: 'auto' }}>
                    {type.capabilities.length > 0 && (
                      <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5, mb: 1 }}>
                        {type.capabilities.map(capability => (
                          <Chip
                            key={capability}
                            label={capability}
                            size="small"
                            variant="outlined"
                          />
                        ))}
                      </Box>
                    )}
                    
                    {type.channels.length > 0 && (
                      <Typography variant="caption" color="text.secondary" component="div">
                        Channels: {type.channels.join(', ')}
                      </Typography>
                    )}
                  </Box>
                </CardContent>
              </CardActionArea>
            </Card>
          </Grid>
        ))}
      </Grid>
    </Box>
  );
};

export default AgentTypeSelector; 