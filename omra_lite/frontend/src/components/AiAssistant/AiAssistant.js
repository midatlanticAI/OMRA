import React, { useState, useRef, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  TextField,
  Button,
  IconButton,
  Fab,
  Drawer,
  List,
  ListItem,
  ListItemText,
  Divider,
  CircularProgress,
  Card,
  CardContent,
  Collapse,
  Alert,
  Tab,
  Tabs,
  Avatar,
  Badge
} from '@mui/material';
import {
  Close as CloseIcon,
  Send as SendIcon,
  SmartToy as SmartToyIcon,
  History as HistoryIcon,
  Person as PersonIcon,
  Refresh as RefreshIcon,
  ExpandMore as ExpandMoreIcon,
  ExpandLess as ExpandLessIcon,
  Tools as ToolsIcon
} from '@mui/icons-material';
import { useAiAssistant } from '../../contexts/AiAssistantContext';
import { format } from 'date-fns';
import ReactMarkdown from 'react-markdown';
import { styled } from '@mui/material/styles';

// Styled components
const AssistantFab = styled(Fab)(({ theme }) => ({
  position: 'fixed',
  bottom: 24,
  right: 24,
  zIndex: 1000,
}));

const MessageContainer = styled(Box)(({ theme, role }) => ({
  display: 'flex',
  flexDirection: 'column',
  alignItems: role === 'user' ? 'flex-end' : 'flex-start',
  marginBottom: theme.spacing(2),
}));

const MessageBubble = styled(Paper)(({ theme, role }) => ({
  padding: theme.spacing(2),
  maxWidth: '80%',
  borderRadius: role === 'user' ? '18px 18px 0 18px' : '18px 18px 18px 0',
  backgroundColor: role === 'user' ? theme.palette.primary.main : theme.palette.background.paper,
  color: role === 'user' ? theme.palette.primary.contrastText : theme.palette.text.primary,
  position: 'relative',
}));

const MarkdownContent = styled(ReactMarkdown)(({ theme }) => ({
  '& p': {
    margin: '0.5em 0',
  },
  '& code': {
    backgroundColor: theme.palette.action.hover,
    padding: '2px 4px',
    borderRadius: 4,
    fontFamily: 'monospace',
  },
  '& pre': {
    backgroundColor: theme.palette.action.hover,
    padding: theme.spacing(1),
    borderRadius: 4,
    overflow: 'auto',
    '& code': {
      backgroundColor: 'transparent',
      padding: 0,
    },
  },
  '& a': {
    color: theme.palette.primary.main,
  },
  '& ul, & ol': {
    paddingLeft: theme.spacing(2),
  },
}));

const ToolOutputContainer = styled(Card)(({ theme }) => ({
  marginTop: theme.spacing(1),
  backgroundColor: theme.palette.action.hover,
}));

const MessageHeader = styled(Box)(({ theme }) => ({
  display: 'flex',
  alignItems: 'center',
  marginBottom: theme.spacing(0.5),
  gap: theme.spacing(1),
}));

const TypingIndicator = styled(Box)(({ theme }) => ({
  display: 'flex',
  padding: theme.spacing(1),
  '& span': {
    width: 8,
    height: 8,
    backgroundColor: theme.palette.primary.main,
    borderRadius: '50%',
    margin: '0 2px',
    animation: 'typing-animation 1.4s infinite both',
    '&:nth-of-type(2)': {
      animationDelay: '0.2s',
    },
    '&:nth-of-type(3)': {
      animationDelay: '0.4s',
    },
  },
  '@keyframes typing-animation': {
    '0%': {
      opacity: 0.2,
      transform: 'translateY(0)',
    },
    '50%': {
      opacity: 1,
      transform: 'translateY(-5px)',
    },
    '100%': {
      opacity: 0.2,
      transform: 'translateY(0)',
    },
  },
}));

const AiAssistant = () => {
  const {
    isOpen,
    toggleAssistant,
    loading,
    error,
    messages,
    conversationId,
    conversationHistory,
    sendMessage,
    loadConversation,
    clearConversation
  } = useAiAssistant();
  
  const [messageText, setMessageText] = useState('');
  const [tabValue, setTabValue] = useState(0);
  const [expandedTools, setExpandedTools] = useState({});
  const messagesEndRef = useRef(null);
  
  // Scroll to bottom when messages change
  useEffect(() => {
    scrollToBottom();
  }, [messages]);
  
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };
  
  const handleSendMessage = (e) => {
    e.preventDefault();
    if (messageText.trim()) {
      sendMessage(messageText);
      setMessageText('');
    }
  };
  
  const handleTabChange = (event, newValue) => {
    setTabValue(newValue);
  };
  
  const handleExpandTool = (id) => {
    setExpandedTools(prev => ({
      ...prev,
      [id]: !prev[id]
    }));
  };
  
  const renderToolOutputs = (toolOutputs) => {
    if (!toolOutputs || toolOutputs.length === 0) return null;
    
    return toolOutputs.map((tool, index) => {
      const id = `tool-${index}`;
      return (
        <ToolOutputContainer key={id}>
          <CardContent sx={{ p: 1.5, '&:last-child': { pb: 1.5 } }}>
            <Box
              sx={{ 
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                cursor: 'pointer'
              }}
              onClick={() => handleExpandTool(id)}
            >
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <ToolsIcon fontSize="small" color="action" />
                <Typography variant="body2" color="text.secondary">
                  Tool: {tool.tool_call_id.split(':')[0]}
                </Typography>
              </Box>
              {expandedTools[id] ? <ExpandLessIcon /> : <ExpandMoreIcon />}
            </Box>
            
            <Collapse in={expandedTools[id]} timeout="auto" unmountOnExit>
              <Box sx={{ mt: 1.5 }}>
                <pre style={{ 
                  overflowX: 'auto', 
                  margin: 0, 
                  fontSize: 12,
                  padding: 8,
                  backgroundColor: 'rgba(0,0,0,0.04)',
                  borderRadius: 4
                }}>
                  {JSON.stringify(tool.output, null, 2)}
                </pre>
              </Box>
            </Collapse>
          </CardContent>
        </ToolOutputContainer>
      );
    });
  };
  
  const renderMessages = () => {
    return messages.map((message, index) => {
      const isUser = message.role === 'user';
      const avatar = isUser ? <PersonIcon /> : <SmartToyIcon />;
      const toolOutputs = message.metadata?.tool_outputs || [];
      
      return (
        <MessageContainer key={message._id || index} role={message.role}>
          <MessageHeader>
            <Avatar sx={{ width: 24, height: 24, bgcolor: isUser ? 'primary.main' : 'secondary.main' }}>
              {avatar}
            </Avatar>
            <Typography variant="caption" color="text.secondary">
              {message.timestamp 
                ? format(new Date(message.timestamp), 'MMM d, h:mm a')
                : 'Just now'}
            </Typography>
          </MessageHeader>
          
          <MessageBubble role={message.role} elevation={1}>
            <MarkdownContent>
              {message.content}
            </MarkdownContent>
          </MessageBubble>
          
          {!isUser && renderToolOutputs(toolOutputs)}
        </MessageContainer>
      );
    });
  };
  
  const renderConversationHistory = () => {
    if (conversationHistory.length === 0) {
      return (
        <Box sx={{ p: 2, textAlign: 'center' }}>
          <Typography variant="body2" color="text.secondary">
            No previous conversations
          </Typography>
        </Box>
      );
    }
    
    return (
      <List>
        {conversationHistory.map((conversation) => (
          <React.Fragment key={conversation._id}>
            <ListItem
              button
              onClick={() => {
                loadConversation(conversation._id);
                setTabValue(0);  // Switch to chat tab
              }}
              selected={conversation._id === conversationId}
            >
              <ListItemText
                primary={conversation.title}
                secondary={format(new Date(conversation.updated_at), 'MMM d, yyyy, h:mm a')}
                primaryTypographyProps={{
                  noWrap: true,
                  style: { maxWidth: '250px' }
                }}
              />
            </ListItem>
            <Divider />
          </React.Fragment>
        ))}
      </List>
    );
  };
  
  return (
    <>
      {/* Floating action button to toggle the assistant */}
      <AssistantFab
        color="primary"
        aria-label="ai assistant"
        onClick={toggleAssistant}
      >
        <Badge color="error" variant="dot" invisible={!isOpen}>
          <SmartToyIcon />
        </Badge>
      </AssistantFab>
      
      {/* Assistant drawer */}
      <Drawer
        anchor="right"
        open={isOpen}
        onClose={toggleAssistant}
        PaperProps={{
          sx: { width: { xs: '100%', sm: 400 }, maxWidth: '100%' }
        }}
      >
        {/* Header */}
        <Box sx={{ p: 2, borderBottom: 1, borderColor: 'divider', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <SmartToyIcon color="primary" />
            <Typography variant="h6">OMRA AI Assistant</Typography>
          </Box>
          <IconButton onClick={toggleAssistant} edge="end">
            <CloseIcon />
          </IconButton>
        </Box>
        
        {/* Tabs for chat and history */}
        <Tabs
          value={tabValue}
          onChange={handleTabChange}
          variant="fullWidth"
          indicatorColor="primary"
          textColor="primary"
          sx={{ borderBottom: 1, borderColor: 'divider' }}
        >
          <Tab icon={<SmartToyIcon />} label="Chat" id="tab-0" />
          <Tab icon={<HistoryIcon />} label="History" id="tab-1" />
        </Tabs>
        
        {/* Chat tab */}
        <Box
          role="tabpanel"
          hidden={tabValue !== 0}
          id="tabpanel-0"
          sx={{ 
            display: 'flex', 
            flexDirection: 'column', 
            height: tabValue === 0 ? 'calc(100% - 104px)' : 0,
            overflow: 'hidden'
          }}
        >
          {/* Error message */}
          {error && (
            <Alert severity="error" sx={{ m: 2 }}>
              {error}
            </Alert>
          )}
          
          {/* Messages area */}
          <Box
            sx={{
              p: 2,
              flexGrow: 1,
              overflowY: 'auto',
              display: 'flex',
              flexDirection: 'column'
            }}
          >
            {messages.length === 0 ? (
              <Box
                sx={{
                  display: 'flex',
                  flexDirection: 'column',
                  alignItems: 'center',
                  justifyContent: 'center',
                  height: '100%',
                  textAlign: 'center',
                  color: 'text.secondary',
                  p: 3,
                }}
              >
                <SmartToyIcon sx={{ fontSize: 60, mb: 2, color: 'primary.main' }} />
                <Typography variant="h6" gutterBottom>
                  How can I assist you today?
                </Typography>
                <Typography variant="body2">
                  I can help with managing customers, service requests, and AI agents.
                  I have access to all documentation and program data.
                </Typography>
              </Box>
            ) : (
              renderMessages()
            )}
            
            {/* Typing indicator */}
            {loading && (
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mt: 2 }}>
                <Avatar sx={{ width: 24, height: 24, bgcolor: 'secondary.main' }}>
                  <SmartToyIcon sx={{ fontSize: 16 }} />
                </Avatar>
                <TypingIndicator>
                  <span></span>
                  <span></span>
                  <span></span>
                </TypingIndicator>
              </Box>
            )}
            
            <div ref={messagesEndRef} />
          </Box>
          
          {/* Input area */}
          <Box
            component="form"
            onSubmit={handleSendMessage}
            sx={{
              p: 2,
              borderTop: 1,
              borderColor: 'divider',
              backgroundColor: 'background.paper',
              display: 'flex',
              alignItems: 'center',
              gap: 1
            }}
          >
            {messages.length > 0 && (
              <IconButton
                color="default"
                onClick={clearConversation}
                disabled={loading}
                title="New conversation"
              >
                <RefreshIcon />
              </IconButton>
            )}
            
            <TextField
              fullWidth
              variant="outlined"
              placeholder="Ask something..."
              value={messageText}
              onChange={(e) => setMessageText(e.target.value)}
              disabled={loading}
              size="small"
              autoComplete="off"
              InputProps={{
                sx: { borderRadius: 3 }
              }}
            />
            
            <IconButton
              color="primary"
              type="submit"
              disabled={loading || !messageText.trim()}
            >
              {loading ? <CircularProgress size={24} /> : <SendIcon />}
            </IconButton>
          </Box>
        </Box>
        
        {/* History tab */}
        <Box
          role="tabpanel"
          hidden={tabValue !== 1}
          id="tabpanel-1"
          sx={{ 
            height: tabValue === 1 ? 'calc(100% - 104px)' : 0,
            overflow: 'auto'
          }}
        >
          {renderConversationHistory()}
        </Box>
      </Drawer>
    </>
  );
};

export default AiAssistant; 