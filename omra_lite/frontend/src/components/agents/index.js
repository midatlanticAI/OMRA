/**
 * Agent Components - All components for creating and managing agents
 * 
 * This index file exports all components for creating and managing agents
 * allowing for clean imports of these components from other files.
 */

// Main form component
export { default as CreateAgentForm } from './CreateAgentForm';

// Sub-components
export { default as AgentTypeSelector } from './AgentTypeSelector';
export { default as ModelSelector } from './ModelSelector';
export { default as ChannelConfig } from './ChannelConfig';
export { ChatBotConfig, EmailBotConfig, VoiceBotConfig } from './ChannelConfig';
export { default as RagConfig } from './RagConfig';
export { default as FineTuningConfig } from './FineTuningConfig';
export { default as HierarchicalConfig } from './HierarchicalConfig';

// Export all components as a group
export const AgentComponents = {
  CreateAgentForm: require('./CreateAgentForm').default,
  AgentTypeSelector: require('./AgentTypeSelector').default,
  ModelSelector: require('./ModelSelector').default,
  ChannelConfig: require('./ChannelConfig').default,
  RagConfig: require('./RagConfig').default,
  FineTuningConfig: require('./FineTuningConfig').default,
  HierarchicalConfig: require('./HierarchicalConfig').default,
}; 