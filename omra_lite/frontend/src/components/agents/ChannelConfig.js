import React from 'react';
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
  Divider,
} from '@mui/material';

/**
 * ChatBotConfig - Configuration options for chat-based agents
 * 
 * @param {Object} props - Component props
 * @param {Object} props.config - Current chat configuration
 * @param {Function} props.onChange - Function to update the configuration
 * @param {Array} props.availableEmbeddings - List of available embedding models
 */
export const ChatBotConfig = ({ config, onChange, availableEmbeddings = [] }) => {
  // Default config structure with sensible defaults
  const defaultConfig = {
    platform: 'web',
    webSettings: {
      widgetTitle: 'AI Assistant',
      primaryColor: '#3f51b5',
      welcomeMessage: 'Hello! How can I help you today?',
      inputPlaceholder: 'Type your message...',
    },
    useLocalEmbedding: false,
    embeddingModel: 'text-embedding-ada-002',
  };

  // Use provided config or default
  const currentConfig = config || defaultConfig;

  const handleChange = (field, value) => {
    const newConfig = {
      ...currentConfig,
      [field]: value,
    };
    onChange(newConfig);
  };

  const handleWebSettingChange = (field, value) => {
    const newWebSettings = {
      ...currentConfig.webSettings,
      [field]: value,
    };
    const newConfig = {
      ...currentConfig,
      webSettings: newWebSettings,
    };
    onChange(newConfig);
  };

  return (
    <Box>
      <Typography variant="h6" gutterBottom>
        Chat Configuration
      </Typography>
      
      <FormControl fullWidth margin="normal">
        <InputLabel id="chat-platform-label">Chat Platform</InputLabel>
        <Select
          labelId="chat-platform-label"
          value={currentConfig.platform}
          onChange={(e) => handleChange('platform', e.target.value)}
          label="Chat Platform"
        >
          <MenuItem value="web">Website Widget</MenuItem>
          <MenuItem value="discord">Discord Bot</MenuItem>
          <MenuItem value="telegram">Telegram Bot</MenuItem>
          <MenuItem value="slack">Slack App</MenuItem>
        </Select>
        <FormHelperText>
          Where will this agent be deployed?
        </FormHelperText>
      </FormControl>

      {currentConfig.platform === 'web' && (
        <Box mt={2} p={2} border={1} borderColor="divider" borderRadius={1}>
          <Typography variant="subtitle1" gutterBottom>
            Website Widget Settings
          </Typography>
          
          <Grid container spacing={2}>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Widget Title"
                value={currentConfig.webSettings.widgetTitle}
                onChange={(e) => handleWebSettingChange('widgetTitle', e.target.value)}
                margin="normal"
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Primary Color"
                type="color"
                value={currentConfig.webSettings.primaryColor}
                onChange={(e) => handleWebSettingChange('primaryColor', e.target.value)}
                margin="normal"
                InputProps={{ sx: { height: 56 } }}
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Welcome Message"
                value={currentConfig.webSettings.welcomeMessage}
                onChange={(e) => handleWebSettingChange('welcomeMessage', e.target.value)}
                margin="normal"
                multiline
                rows={2}
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Input Placeholder"
                value={currentConfig.webSettings.inputPlaceholder}
                onChange={(e) => handleWebSettingChange('inputPlaceholder', e.target.value)}
                margin="normal"
              />
            </Grid>
          </Grid>
        </Box>
      )}

      <Box mt={3}>
        <Typography variant="subtitle1" gutterBottom>
          Knowledge Management
        </Typography>
        
        <FormControlLabel
          control={
            <Switch
              checked={currentConfig.useLocalEmbedding}
              onChange={(e) => handleChange('useLocalEmbedding', e.target.checked)}
            />
          }
          label="Use Local Embedding Model (Free)"
        />
        
        {!currentConfig.useLocalEmbedding && (
          <FormControl fullWidth margin="normal">
            <InputLabel id="embedding-model-label">Embedding Model</InputLabel>
            <Select
              labelId="embedding-model-label"
              value={currentConfig.embeddingModel}
              onChange={(e) => handleChange('embeddingModel', e.target.value)}
              label="Embedding Model"
            >
              <MenuItem value="text-embedding-ada-002">OpenAI Ada 002</MenuItem>
              <MenuItem value="text-embedding-3-small">OpenAI Text Embedding 3 Small</MenuItem>
              <MenuItem value="text-embedding-3-large">OpenAI Text Embedding 3 Large</MenuItem>
              <MenuItem value="cohere-embed-english">Cohere Embed English</MenuItem>
              <MenuItem value="cohere-embed-multilingual">Cohere Embed Multilingual</MenuItem>
              {availableEmbeddings.map(model => (
                <MenuItem key={model.id} value={model.id}>{model.name}</MenuItem>
              ))}
            </Select>
            <FormHelperText>
              Model used to convert text into vector representations
            </FormHelperText>
          </FormControl>
        )}
      </Box>
    </Box>
  );
};

/**
 * EmailBotConfig - Configuration options for email-based agents
 * 
 * @param {Object} props - Component props
 * @param {Object} props.config - Current email configuration
 * @param {Function} props.onChange - Function to update the configuration
 */
export const EmailBotConfig = ({ config, onChange }) => {
  // Default config structure with sensible defaults
  const defaultConfig = {
    emailProvider: 'smtp',
    smtpSettings: {
      host: '',
      port: 587,
      secure: true,
      username: '',
      password: '',
    },
    emailTemplates: {
      signature: '\n\nBest regards,\nAI Assistant',
      footer: '\n\nThis is an automated response.',
    },
    monitoredFolder: 'INBOX',
    responseDelay: 0, // in minutes, 0 for immediate
  };

  // Use provided config or default
  const currentConfig = config || defaultConfig;

  const handleChange = (field, value) => {
    const newConfig = {
      ...currentConfig,
      [field]: value,
    };
    onChange(newConfig);
  };

  const handleSmtpSettingChange = (field, value) => {
    const newSmtpSettings = {
      ...currentConfig.smtpSettings,
      [field]: value,
    };
    const newConfig = {
      ...currentConfig,
      smtpSettings: newSmtpSettings,
    };
    onChange(newConfig);
  };

  const handleTemplateChange = (field, value) => {
    const newTemplates = {
      ...currentConfig.emailTemplates,
      [field]: value,
    };
    const newConfig = {
      ...currentConfig,
      emailTemplates: newTemplates,
    };
    onChange(newConfig);
  };

  return (
    <Box>
      <Typography variant="h6" gutterBottom>
        Email Configuration
      </Typography>
      
      <FormControl fullWidth margin="normal">
        <InputLabel id="email-provider-label">Email Provider</InputLabel>
        <Select
          labelId="email-provider-label"
          value={currentConfig.emailProvider}
          onChange={(e) => handleChange('emailProvider', e.target.value)}
          label="Email Provider"
        >
          <MenuItem value="smtp">SMTP (Custom)</MenuItem>
          <MenuItem value="gmail">Gmail</MenuItem>
          <MenuItem value="outlook">Outlook</MenuItem>
        </Select>
        <FormHelperText>
          Which email service will handle sending and receiving emails?
        </FormHelperText>
      </FormControl>

      {currentConfig.emailProvider === 'smtp' && (
        <Box mt={2} p={2} border={1} borderColor="divider" borderRadius={1}>
          <Typography variant="subtitle1" gutterBottom>
            SMTP Settings
          </Typography>
          
          <Grid container spacing={2}>
            <Grid item xs={12} md={8}>
              <TextField
                fullWidth
                label="SMTP Host"
                value={currentConfig.smtpSettings.host}
                onChange={(e) => handleSmtpSettingChange('host', e.target.value)}
                margin="normal"
                placeholder="smtp.example.com"
              />
            </Grid>
            <Grid item xs={12} md={4}>
              <TextField
                fullWidth
                label="Port"
                type="number"
                value={currentConfig.smtpSettings.port}
                onChange={(e) => handleSmtpSettingChange('port', parseInt(e.target.value, 10))}
                margin="normal"
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Username"
                value={currentConfig.smtpSettings.username}
                onChange={(e) => handleSmtpSettingChange('username', e.target.value)}
                margin="normal"
                placeholder="user@example.com"
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Password"
                type="password"
                value={currentConfig.smtpSettings.password}
                onChange={(e) => handleSmtpSettingChange('password', e.target.value)}
                margin="normal"
              />
            </Grid>
            <Grid item xs={12}>
              <FormControlLabel
                control={
                  <Switch
                    checked={currentConfig.smtpSettings.secure}
                    onChange={(e) => handleSmtpSettingChange('secure', e.target.checked)}
                  />
                }
                label="Use SSL/TLS"
              />
            </Grid>
          </Grid>
        </Box>
      )}

      <Box mt={3}>
        <Typography variant="subtitle1" gutterBottom>
          Email Templates
        </Typography>
        
        <Grid container spacing={2}>
          <Grid item xs={12}>
            <TextField
              fullWidth
              label="Email Signature"
              value={currentConfig.emailTemplates.signature}
              onChange={(e) => handleTemplateChange('signature', e.target.value)}
              margin="normal"
              multiline
              rows={3}
              placeholder="Best regards,\nAI Assistant"
            />
          </Grid>
          <Grid item xs={12}>
            <TextField
              fullWidth
              label="Email Footer"
              value={currentConfig.emailTemplates.footer}
              onChange={(e) => handleTemplateChange('footer', e.target.value)}
              margin="normal"
              multiline
              rows={2}
              placeholder="This is an automated response."
            />
          </Grid>
        </Grid>
      </Box>

      <Box mt={3}>
        <Typography variant="subtitle1" gutterBottom>
          Email Processing
        </Typography>
        
        <Grid container spacing={2}>
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              label="Monitored Folder"
              value={currentConfig.monitoredFolder}
              onChange={(e) => handleChange('monitoredFolder', e.target.value)}
              margin="normal"
              placeholder="INBOX"
            />
            <FormHelperText>
              Which email folder to monitor for incoming messages
            </FormHelperText>
          </Grid>
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              label="Response Delay (minutes)"
              type="number"
              value={currentConfig.responseDelay}
              onChange={(e) => handleChange('responseDelay', parseInt(e.target.value, 10))}
              margin="normal"
              InputProps={{ inputProps: { min: 0 } }}
            />
            <FormHelperText>
              Optional delay before sending responses (0 for immediate)
            </FormHelperText>
          </Grid>
        </Grid>
      </Box>
    </Box>
  );
};

/**
 * VoiceBotConfig - Configuration options for voice-based agents
 * 
 * @param {Object} props - Component props
 * @param {Object} props.config - Current voice configuration
 * @param {Function} props.onChange - Function to update the configuration
 * @param {Array} props.availableVoices - List of available voice options
 */
export const VoiceBotConfig = ({ config, onChange, availableVoices = [] }) => {
  // Default config structure with sensible defaults
  const defaultConfig = {
    voiceProvider: 'openai',
    useLocalVoice: false,
    voice: 'alloy', // OpenAI default voice
    speed: 1.0,
    phoneProvider: 'twilio',
    twilioSettings: {
      accountSid: '',
      authToken: '',
      phoneNumber: '',
    },
    callHandling: {
      maxDuration: 10, // in minutes
      transcribeCall: true,
      recordCall: false,
    },
  };

  // Use provided config or default
  const currentConfig = config || defaultConfig;

  const handleChange = (field, value) => {
    const newConfig = {
      ...currentConfig,
      [field]: value,
    };
    onChange(newConfig);
  };

  const handleTwilioSettingChange = (field, value) => {
    const newTwilioSettings = {
      ...currentConfig.twilioSettings,
      [field]: value,
    };
    const newConfig = {
      ...currentConfig,
      twilioSettings: newTwilioSettings,
    };
    onChange(newConfig);
  };

  const handleCallHandlingChange = (field, value) => {
    const newCallHandling = {
      ...currentConfig.callHandling,
      [field]: value,
    };
    const newConfig = {
      ...currentConfig,
      callHandling: newCallHandling,
    };
    onChange(newConfig);
  };

  return (
    <Box>
      <Typography variant="h6" gutterBottom>
        Voice Configuration
      </Typography>
      
      <Divider sx={{ my: 2 }} />
      
      <Typography variant="subtitle1" gutterBottom>
        Text-to-Speech Settings
      </Typography>
      
      <FormControlLabel
        control={
          <Switch
            checked={currentConfig.useLocalVoice}
            onChange={(e) => handleChange('useLocalVoice', e.target.checked)}
          />
        }
        label="Use Local Voice Model (Free)"
      />
      
      {!currentConfig.useLocalVoice && (
        <>
          <FormControl fullWidth margin="normal">
            <InputLabel id="voice-provider-label">Voice Provider</InputLabel>
            <Select
              labelId="voice-provider-label"
              value={currentConfig.voiceProvider}
              onChange={(e) => handleChange('voiceProvider', e.target.value)}
              label="Voice Provider"
            >
              <MenuItem value="openai">OpenAI TTS</MenuItem>
              <MenuItem value="elevenlabs">ElevenLabs</MenuItem>
              <MenuItem value="google">Google Cloud TTS</MenuItem>
            </Select>
            <FormHelperText>
              Service that will generate the voice responses
            </FormHelperText>
          </FormControl>

          <FormControl fullWidth margin="normal">
            <InputLabel id="voice-label">Voice</InputLabel>
            <Select
              labelId="voice-label"
              value={currentConfig.voice}
              onChange={(e) => handleChange('voice', e.target.value)}
              label="Voice"
            >
              {currentConfig.voiceProvider === 'openai' && (
                <>
                  <MenuItem value="alloy">Alloy (Neutral)</MenuItem>
                  <MenuItem value="echo">Echo (Male)</MenuItem>
                  <MenuItem value="fable">Fable (Male)</MenuItem>
                  <MenuItem value="onyx">Onyx (Male)</MenuItem>
                  <MenuItem value="nova">Nova (Female)</MenuItem>
                  <MenuItem value="shimmer">Shimmer (Female)</MenuItem>
                </>
              )}
              {availableVoices.map(voice => (
                <MenuItem key={voice.id} value={voice.id}>{voice.name}</MenuItem>
              ))}
            </Select>
            <FormHelperText>
              Select the voice that will speak for your agent
            </FormHelperText>
          </FormControl>
        </>
      )}

      <TextField
        fullWidth
        label="Speech Speed"
        type="number"
        value={currentConfig.speed}
        onChange={(e) => handleChange('speed', parseFloat(e.target.value))}
        margin="normal"
        InputProps={{ 
          inputProps: { min: 0.5, max: 2.0, step: 0.1 },
          endAdornment: 'x'
        }}
      />
      <FormHelperText>
        Adjust speech speed (0.5 = slow, 1.0 = normal, 2.0 = fast)
      </FormHelperText>
      
      <Divider sx={{ my: 2 }} />
      
      <Typography variant="subtitle1" gutterBottom>
        Phone Integration
      </Typography>
      
      <FormControl fullWidth margin="normal">
        <InputLabel id="phone-provider-label">Phone Provider</InputLabel>
        <Select
          labelId="phone-provider-label"
          value={currentConfig.phoneProvider}
          onChange={(e) => handleChange('phoneProvider', e.target.value)}
          label="Phone Provider"
        >
          <MenuItem value="twilio">Twilio</MenuItem>
          <MenuItem value="jambonz">Jambonz (Self-hosted)</MenuItem>
          <MenuItem value="none">None (Web-only)</MenuItem>
        </Select>
        <FormHelperText>
          Service that will handle phone calls
        </FormHelperText>
      </FormControl>

      {currentConfig.phoneProvider === 'twilio' && (
        <Box mt={2} p={2} border={1} borderColor="divider" borderRadius={1}>
          <Typography variant="subtitle2" gutterBottom>
            Twilio Settings
          </Typography>
          
          <Grid container spacing={2}>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Account SID"
                value={currentConfig.twilioSettings.accountSid}
                onChange={(e) => handleTwilioSettingChange('accountSid', e.target.value)}
                margin="normal"
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Auth Token"
                type="password"
                value={currentConfig.twilioSettings.authToken}
                onChange={(e) => handleTwilioSettingChange('authToken', e.target.value)}
                margin="normal"
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Phone Number"
                value={currentConfig.twilioSettings.phoneNumber}
                onChange={(e) => handleTwilioSettingChange('phoneNumber', e.target.value)}
                margin="normal"
                placeholder="+15551234567"
              />
              <FormHelperText>
                Twilio phone number in E.164 format (e.g., +15551234567)
              </FormHelperText>
            </Grid>
          </Grid>
        </Box>
      )}

      <Box mt={3}>
        <Typography variant="subtitle2" gutterBottom>
          Call Handling Options
        </Typography>
        
        <Grid container spacing={2}>
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              label="Max Call Duration"
              type="number"
              value={currentConfig.callHandling.maxDuration}
              onChange={(e) => handleCallHandlingChange('maxDuration', parseInt(e.target.value, 10))}
              margin="normal"
              InputProps={{ 
                inputProps: { min: 1, max: 60 },
                endAdornment: 'minutes'
              }}
            />
          </Grid>
          <Grid item xs={12} md={6}>
            <FormControlLabel
              control={
                <Switch
                  checked={currentConfig.callHandling.transcribeCall}
                  onChange={(e) => handleCallHandlingChange('transcribeCall', e.target.checked)}
                />
              }
              label="Transcribe Calls"
            />
          </Grid>
          <Grid item xs={12} md={6}>
            <FormControlLabel
              control={
                <Switch
                  checked={currentConfig.callHandling.recordCall}
                  onChange={(e) => handleCallHandlingChange('recordCall', e.target.checked)}
                />
              }
              label="Record Calls"
            />
          </Grid>
        </Grid>
      </Box>
    </Box>
  );
};

/**
 * ChannelConfig - Container component that renders the appropriate configuration
 * panel based on the selected channel type
 * 
 * @param {Object} props - Component props
 * @param {string} props.channelType - Type of channel (chat, email, voice)
 * @param {Object} props.config - Current configuration
 * @param {Function} props.onChange - Function to update the configuration
 * @param {Object} props.resources - Available resources like embedding models and voices
 */
const ChannelConfig = ({ channelType, config, onChange, resources = {} }) => {
  return (
    <Box>
      {channelType === 'chat' && (
        <ChatBotConfig 
          config={config} 
          onChange={onChange}
          availableEmbeddings={resources.embeddings || []}
        />
      )}
      
      {channelType === 'email' && (
        <EmailBotConfig 
          config={config} 
          onChange={onChange}
        />
      )}
      
      {channelType === 'voice' && (
        <VoiceBotConfig 
          config={config} 
          onChange={onChange}
          availableVoices={resources.voices || []}
        />
      )}
    </Box>
  );
};

export default ChannelConfig; 