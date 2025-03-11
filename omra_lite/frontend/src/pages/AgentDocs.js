/* eslint-disable no-unused-vars */
import React, { useState } from 'react';
import {
  Typography,
  Box,
  Paper,
  Grid,
  Tabs,
  Tab,
  List,
  ListItem,
  ListItemText,
  Divider,
  Button,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
} from '@mui/material';
import {
  ExpandMore as ExpandMoreIcon,
  Psychology as PsychologyIcon,
  Storage as StorageIcon,
  Help as HelpIcon,
  School as SchoolIcon,
  Architecture as ArchitectureIcon,
} from '@mui/icons-material';
/* eslint-enable no-unused-vars */

// TabPanel component for the tabbed interface
function TabPanel(props) {
  const { children, value, index, ...other } = props;

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`agent-docs-tabpanel-${index}`}
      aria-labelledby={`agent-docs-tab-${index}`}
      {...other}
    >
      {value === index && <Box p={3}>{children}</Box>}
    </div>
  );
}

const AgentDocs = () => {
  const [activeTab, setActiveTab] = useState(0);

  const handleTabChange = (event, newValue) => {
    setActiveTab(newValue);
  };

  return (
    <Box p={3}>
      <Box mb={4}>
        <Typography variant="h4" gutterBottom>
          Agent Creation Documentation
        </Typography>
        <Typography variant="body1" color="textSecondary">
          Comprehensive guide to creating effective AI agents, understanding agent types,
          configuring RAG for knowledge access, and implementing fine-tuning.
        </Typography>
      </Box>

      <Tabs value={activeTab} onChange={handleTabChange} centered sx={{ mb: 3 }}>
        <Tab icon={<SchoolIcon />} label="Getting Started" />
        <Tab icon={<ArchitectureIcon />} label="Agent Architecture" />
        <Tab icon={<StorageIcon />} label="RAG Configuration" />
        <Tab icon={<PsychologyIcon />} label="Fine-tuning" />
        <Tab icon={<HelpIcon />} label="Best Practices" />
      </Tabs>

      {/* Getting Started Tab */}
      <TabPanel value={activeTab} index={0}>
        <Typography variant="h5" gutterBottom>
          Getting Started with Agents
        </Typography>
        <Typography paragraph>
          An agent is an AI assistant configured for specific tasks and knowledge domains.
          This guide will help you create effective agents for your business needs.
        </Typography>

        <Box mb={4}>
          <Typography variant="h6" gutterBottom>
            Basic Agent Creation Process
          </Typography>
          <Paper elevation={1} sx={{ p: 3, bgcolor: '#f8f9fa' }}>
            <List>
              <ListItem>
                <ListItemText 
                  primary="1. Define the agent's purpose" 
                  secondary="Clearly identify what problems this agent will solve and what tasks it will perform." 
                />
              </ListItem>
              <Divider component="li" />
              <ListItem>
                <ListItemText 
                  primary="2. Choose an agent type" 
                  secondary="Select from types like Customer Service, Technical Support, Diagnosis, etc. based on your needs." 
                />
              </ListItem>
              <Divider component="li" />
              <ListItem>
                <ListItemText 
                  primary="3. Select an appropriate model" 
                  secondary="Choose a language model based on task complexity and performance requirements." 
                />
              </ListItem>
              <Divider component="li" />
              <ListItem>
                <ListItemText 
                  primary="4. Configure knowledge access" 
                  secondary="Set up RAG if the agent needs access to specific knowledge sources." 
                />
              </ListItem>
              <Divider component="li" />
              <ListItem>
                <ListItemText 
                  primary="5. Consider hierarchy" 
                  secondary="Decide if this agent should be part of a hierarchical structure with parent/child relationships." 
                />
              </ListItem>
              <Divider component="li" />
              <ListItem>
                <ListItemText 
                  primary="6. Test and refine" 
                  secondary="Test your agent with real-world scenarios and refine its configuration based on performance." 
                />
              </ListItem>
            </List>
          </Paper>
        </Box>

        <Box mb={4}>
          <Typography variant="h6" gutterBottom>
            When To Use Different Agent Types
          </Typography>
          <TableContainer component={Paper}>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell><strong>Agent Type</strong></TableCell>
                  <TableCell><strong>Best For</strong></TableCell>
                  <TableCell><strong>Example Use Case</strong></TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                <TableRow>
                  <TableCell>Customer Service</TableCell>
                  <TableCell>Handling customer inquiries, providing product information</TableCell>
                  <TableCell>First-line support for customer questions about products and services</TableCell>
                </TableRow>
                <TableRow>
                  <TableCell>Technical Support</TableCell>
                  <TableCell>Troubleshooting issues, providing technical solutions</TableCell>
                  <TableCell>Diagnosing and resolving technical problems with appliances</TableCell>
                </TableRow>
                <TableRow>
                  <TableCell>Diagnostic</TableCell>
                  <TableCell>Complex problem analysis, root cause identification</TableCell>
                  <TableCell>Analyzing symptoms to diagnose appliance malfunctions</TableCell>
                </TableRow>
                <TableRow>
                  <TableCell>Scheduling</TableCell>
                  <TableCell>Appointment setting, calendar management</TableCell>
                  <TableCell>Booking technician visits for service requests</TableCell>
                </TableRow>
                <TableRow>
                  <TableCell>Data Analysis</TableCell>
                  <TableCell>Analyzing trends, generating insights from data</TableCell>
                  <TableCell>Analyzing service request patterns to identify common issues</TableCell>
                </TableRow>
              </TableBody>
            </Table>
          </TableContainer>
        </Box>

        <Box mb={4}>
          <Typography variant="h6" gutterBottom>
            Choosing the Right Model
          </Typography>
          <TableContainer component={Paper}>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell><strong>Model</strong></TableCell>
                  <TableCell><strong>Best For</strong></TableCell>
                  <TableCell><strong>Considerations</strong></TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                <TableRow>
                  <TableCell>OpenAI GPT-4o</TableCell>
                  <TableCell>Versatile multimodal tasks, balanced performance</TableCell>
                  <TableCell>Handles text, image, and audio inputs with 128K context window</TableCell>
                </TableRow>
                <TableRow>
                  <TableCell>OpenAI GPT-4o mini</TableCell>
                  <TableCell>Cost-effective multimodal tasks, high throughput needs</TableCell>
                  <TableCell>Lower cost alternative to GPT-4o with excellent performance-to-cost ratio</TableCell>
                </TableRow>
                <TableRow>
                  <TableCell>OpenAI GPT-4.5 Preview</TableCell>
                  <TableCell>Highest-level reasoning, complex multi-step tasks</TableCell>
                  <TableCell>OpenAI's most capable model with superior reasoning abilities</TableCell>
                </TableRow>
                <TableRow>
                  <TableCell>Claude 3.7 Sonnet</TableCell>
                  <TableCell>Complex reasoning with extended thinking capabilities</TableCell>
                  <TableCell>Anthropic's most intelligent model with toggleable reasoning processes and 200K context window</TableCell>
                </TableRow>
                <TableRow>
                  <TableCell>Claude 3.5 Haiku</TableCell>
                  <TableCell>Fast, efficient tasks requiring low latency</TableCell>
                  <TableCell>Excellent for high-volume, time-sensitive applications with 200K context window</TableCell>
                </TableRow>
                <TableRow>
                  <TableCell>Gemini 2.0 Flash</TableCell>
                  <TableCell>Multimodal agent-based experiences, high performance</TableCell>
                  <TableCell>1M token context window, handles audio, images, video, and text</TableCell>
                </TableRow>
                <TableRow>
                  <TableCell>Gemini 2.0 Flash-Lite</TableCell>
                  <TableCell>Cost-efficient multimodal tasks</TableCell>
                  <TableCell>More affordable than Gemini 2.0 Flash while maintaining good performance</TableCell>
                </TableRow>
              </TableBody>
            </Table>
          </TableContainer>
        </Box>

        <Box mb={4}>
          <Typography variant="h6" gutterBottom>
            Advanced Model Capabilities
          </Typography>
          <Accordion>
            <AccordionSummary expandIcon={<ExpandMoreIcon />}>
              <Typography variant="subtitle1">Claude's Extended Thinking</Typography>
            </AccordionSummary>
            <AccordionDetails>
              <Typography paragraph>
                Claude 3.7 Sonnet introduces "extended thinking" capability, allowing the model to show its step-by-step reasoning process across complex tasks. This feature significantly improves performance on tasks requiring:
              </Typography>
              <List dense>
                <ListItem>
                  <ListItemText primary="Multi-step reasoning" secondary="Breaking down complex problems into logical steps" />
                </ListItem>
                <ListItem>
                  <ListItemText primary="Detailed explanations" secondary="Providing comprehensive rationales for decisions" />
                </ListItem>
                <ListItem>
                  <ListItemText primary="Longer outputs" secondary="Up to 64,000 tokens compared to standard 8,192 tokens" />
                </ListItem>
                <ListItem>
                  <ListItemText primary="Greater transparency" secondary="Making reasoning processes visible to users" />
                </ListItem>
              </List>
            </AccordionDetails>
          </Accordion>
          <Accordion>
            <AccordionSummary expandIcon={<ExpandMoreIcon />}>
              <Typography variant="subtitle1">Multimodal Capabilities</Typography>
            </AccordionSummary>
            <AccordionDetails>
              <Typography paragraph>
                Latest models from all three providers offer multimodal capabilities, processing various input types:
              </Typography>
              <List dense>
                <ListItem>
                  <ListItemText primary="Text" secondary="Standard text processing with improved comprehension" />
                </ListItem>
                <ListItem>
                  <ListItemText primary="Images" secondary="Vision capabilities for analyzing photos, diagrams, and screenshots" />
                </ListItem>
                <ListItem>
                  <ListItemText primary="Audio" secondary="Processing spoken language (available in GPT-4o and Gemini models)" />
                </ListItem>
                <ListItem>
                  <ListItemText primary="Video" secondary="Limited video understanding available in Gemini models" />
                </ListItem>
              </List>
            </AccordionDetails>
          </Accordion>
          <Accordion>
            <AccordionSummary expandIcon={<ExpandMoreIcon />}>
              <Typography variant="subtitle1">Context Window Advancements</Typography>
            </AccordionSummary>
            <AccordionDetails>
              <Typography paragraph>
                Larger context windows allow agents to process more information in a single request:
              </Typography>
              <List dense>
                <ListItem>
                  <ListItemText primary="Anthropic Claude: 200K tokens" secondary="Both Claude 3.7 Sonnet and 3.5 Haiku" />
                </ListItem>
                <ListItem>
                  <ListItemText primary="OpenAI GPT-4o: 128K tokens" secondary="Standard and mini variants" />
                </ListItem>
                <ListItem>
                  <ListItemText primary="Google Gemini 2.0: 1M tokens" secondary="The largest context window currently available" />
                </ListItem>
              </List>
              <Typography variant="body2" color="textSecondary">
                Larger context windows are particularly valuable for tasks requiring reference to extensive documentation, complex multi-step instructions, or analysis of lengthy conversations.
              </Typography>
            </AccordionDetails>
          </Accordion>
        </Box>
      </TabPanel>

      {/* Agent Architecture Tab */}
      <TabPanel value={activeTab} index={1}>
        <Typography variant="h5" gutterBottom>
          Agent Architecture & Implementation
        </Typography>
        <Typography paragraph>
          Understanding how to structure and implement AI agents is crucial for building effective systems.
          This section covers both architectural patterns and practical implementation approaches.
        </Typography>

        <Box mb={4}>
          <Typography variant="h6" gutterBottom>
            Agent Implementation Approaches
          </Typography>
          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <Paper elevation={1} sx={{ p: 3, height: '100%' }}>
                <Typography variant="subtitle1" gutterBottom>
                  Workflows
                </Typography>
                <Typography paragraph>
                  Systems where LLMs and tools are orchestrated through predefined code paths with specific steps.
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  <strong>Best for:</strong> Well-defined processes with predictable steps
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  <strong>Examples:</strong> Multi-step form filling, guided troubleshooting flows
                </Typography>
              </Paper>
            </Grid>
            <Grid item xs={12} md={6}>
              <Paper elevation={1} sx={{ p: 3, height: '100%' }}>
                <Typography variant="subtitle1" gutterBottom>
                  Autonomous Agents
                </Typography>
                <Typography paragraph>
                  Systems where LLMs dynamically direct their own processes and tool usage, maintaining control over task execution.
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  <strong>Best for:</strong> Open-ended problems with unpredictable steps
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  <strong>Examples:</strong> Complex customer support, coding tasks, research assistants
                </Typography>
              </Paper>
            </Grid>
          </Grid>
        </Box>

        <Box mb={4}>
          <Typography variant="h6" gutterBottom>
            Agent Implementation Core Principles
          </Typography>
          <Paper elevation={1} sx={{ p: 3, bgcolor: '#f8f9fa' }}>
            <List>
              <ListItem>
                <ListItemText 
                  primary="Simplicity" 
                  secondary="Maintain simple designs over complex frameworks. Start with basic components and add complexity only when necessary." 
                />
              </ListItem>
              <Divider component="li" />
              <ListItem>
                <ListItemText 
                  primary="Transparency" 
                  secondary="Make the agent's reasoning steps visible to users, especially for autonomous agents." 
                />
              </ListItem>
              <Divider component="li" />
              <ListItem>
                <ListItemText 
                  primary="Well-documented tools" 
                  secondary="Provide clear, detailed documentation for all tools your agent can use." 
                />
              </ListItem>
              <Divider component="li" />
              <ListItem>
                <ListItemText 
                  primary="Feedback loops" 
                  secondary="Implement mechanisms for agents to receive and incorporate feedback from their environment." 
                />
              </ListItem>
              <Divider component="li" />
              <ListItem>
                <ListItemText 
                  primary="Human oversight" 
                  secondary="Include appropriate checkpoints where humans can review and guide agent actions." 
                />
              </ListItem>
            </List>
          </Paper>
        </Box>

        <Box mb={4}>
          <Typography variant="h6" gutterBottom>
            Agent Hierarchy Patterns
          </Typography>
          <Typography paragraph>
            Hierarchical agent structures enable effective management of complex tasks by organizing agents into coordinated systems. These patterns have proven highly effective in production environments.
          </Typography>
          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <Paper elevation={1} sx={{ p: 3, height: '100%' }}>
                <Typography variant="subtitle1" gutterBottom>
                  Supervisor-Worker Pattern
                </Typography>
                <Typography paragraph>
                  A top-level supervisor agent coordinates tasks and delegates to specialized worker agents. The supervisor maintains oversight while workers focus on specific domains.
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  <strong>Configuration:</strong> Create a supervisor agent, then create worker agents with the supervisor's ID as their parent_id.
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  <strong>Best for:</strong> Complex workflows requiring different types of expertise
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  <strong>Real-world example:</strong> Customer service systems where a router agent delegates to specialized agents for billing, technical support, or scheduling
                </Typography>
              </Paper>
            </Grid>
            <Grid item xs={12} md={6}>
              <Paper elevation={1} sx={{ p: 3, height: '100%' }}>
                <Typography variant="subtitle1" gutterBottom>
                  Chain-of-Responsibility Pattern
                </Typography>
                <Typography paragraph>
                  Agents are arranged in a sequence, where each handles a specific part of a process and passes results to the next. This creates a clear workflow with defined handoffs.
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  <strong>Configuration:</strong> Create sequential agents linked through parent_id relationships.
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  <strong>Best for:</strong> Multi-stage processes with clear handoffs
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  <strong>Real-world example:</strong> Document processing workflows where one agent extracts data, another validates it, and a third generates reports
                </Typography>
              </Paper>
            </Grid>
            <Grid item xs={12} md={6}>
              <Paper elevation={1} sx={{ p: 3, height: '100%' }}>
                <Typography variant="subtitle1" gutterBottom>
                  Hub-and-Spoke Pattern
                </Typography>
                <Typography paragraph>
                  A central agent routes inquiries to specialized agents based on content, then aggregates responses. This pattern is similar to the supervisor-worker but focuses on routing and aggregation.
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  <strong>Configuration:</strong> Create hub agent, then spoke agents with hub's ID as parent_id.
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  <strong>Best for:</strong> Systems with diverse but clearly defined domains
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  <strong>Real-world example:</strong> Research assistant that routes queries to specialized knowledge agents (scientific, historical, mathematical) and combines their responses
                </Typography>
              </Paper>
            </Grid>
            <Grid item xs={12} md={6}>
              <Paper elevation={1} sx={{ p: 3, height: '100%' }}>
                <Typography variant="subtitle1" gutterBottom>
                  Recursive Hierarchy
                </Typography>
                <Typography paragraph>
                  Multiple levels of agents with each level supervising agents below while reporting to agents above. This creates a scalable management structure for complex systems.
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  <strong>Configuration:</strong> Create agents at each level with appropriate parent_id references.
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  <strong>Best for:</strong> Complex organizations with multiple management levels
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  <strong>Real-world example:</strong> Enterprise support systems with regional managers overseeing local support teams, all reporting to a global coordination agent
                </Typography>
              </Paper>
            </Grid>
          </Grid>
        </Box>

        <Box mb={4}>
          <Typography variant="h6" gutterBottom>
            Advanced Hierarchical Orchestration Models
          </Typography>
          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <Paper elevation={1} sx={{ p: 3, height: '100%' }}>
                <Typography variant="subtitle1" gutterBottom>
                  Centralized Orchestration
                </Typography>
                <Typography paragraph>
                  A single AI orchestrator agent acts as the "brain" of the system, directing all other agents, assigning tasks, and making final decisions.
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  <strong>Advantages:</strong> Clear control structure, consistent decision-making, predictable workflows
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  <strong>Challenges:</strong> Can become a bottleneck, single point of failure
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  <strong>Implementation:</strong> Tools like LangGraph support this model with a central supervisor for routing
                </Typography>
              </Paper>
            </Grid>
            <Grid item xs={12} md={6}>
              <Paper elevation={1} sx={{ p: 3, height: '100%' }}>
                <Typography variant="subtitle1" gutterBottom>
                  Decentralized Orchestration
                </Typography>
                <Typography paragraph>
                  Agents function through direct communication and collaboration without a central controller. Agents make independent decisions or reach consensus as a group.
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  <strong>Advantages:</strong> Highly resilient, scalable, no single point of failure
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  <strong>Challenges:</strong> More complex to design and debug, potential for conflicts
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  <strong>Implementation:</strong> Requires clear communication protocols and conflict resolution mechanisms
                </Typography>
              </Paper>
            </Grid>
            <Grid item xs={12} md={6}>
              <Paper elevation={1} sx={{ p: 3, height: '100%' }}>
                <Typography variant="subtitle1" gutterBottom>
                  Adaptive Orchestration
                </Typography>
                <Typography paragraph>
                  Agents adjust their roles, workflows, and priorities dynamically based on changing conditions and feedback from the environment.
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  <strong>Advantages:</strong> Highly responsive to changing conditions, self-improving
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  <strong>Challenges:</strong> Complex to implement, can be unpredictable
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  <strong>Implementation:</strong> Frameworks like AutoGen that allow agents to reconfigure workflows based on results
                </Typography>
              </Paper>
            </Grid>
            <Grid item xs={12} md={6}>
              <Paper elevation={1} sx={{ p: 3, height: '100%' }}>
                <Typography variant="subtitle1" gutterBottom>
                  Federated Orchestration
                </Typography>
                <Typography paragraph>
                  Enables collaboration between independent AI agents or separate organizations without fully sharing data or relinquishing control over individual systems.
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  <strong>Advantages:</strong> Preserves privacy and security, enables cross-organization collaboration
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  <strong>Challenges:</strong> Limited information sharing may reduce effectiveness
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  <strong>Implementation:</strong> Useful in healthcare, finance, or cross-company collaboration where data privacy is critical
                </Typography>
              </Paper>
            </Grid>
          </Grid>
        </Box>

        <Box mb={4}>
          <Typography variant="h6" gutterBottom>
            Best Practices for Hierarchical Agents
          </Typography>
          <Accordion>
            <AccordionSummary expandIcon={<ExpandMoreIcon />}>
              <Typography variant="subtitle1">Maintain Clear Responsibilities</Typography>
            </AccordionSummary>
            <AccordionDetails>
              <Typography>
                Each agent should have a clearly defined role with minimal overlap. Supervisor agents should know when and how to delegate, while worker agents should focus on their specific domains. Document the responsibilities of each agent in their descriptions and establish protocols for handling edge cases that might fall between domains.
              </Typography>
            </AccordionDetails>
          </Accordion>
          <Accordion>
            <AccordionSummary expandIcon={<ExpandMoreIcon />}>
              <Typography variant="subtitle1">Keep Hierarchies Shallow</Typography>
            </AccordionSummary>
            <AccordionDetails>
              <Typography>
                Limit to 2-3 levels when possible to reduce complexity and latency. Each level of hierarchy adds coordination overhead and potential points of failure. Only add levels when clearly beneficial. Research shows that deeper hierarchies often introduce diminishing returns in terms of effectiveness while increasing complexity exponentially.
              </Typography>
            </AccordionDetails>
          </Accordion>
          <Accordion>
            <AccordionSummary expandIcon={<ExpandMoreIcon />}>
              <Typography variant="subtitle1">Implement Effective Communication Protocols</Typography>
            </AccordionSummary>
            <AccordionDetails>
              <Typography>
                Define standard formats for messages between agents to ensure consistent interpretation. Supervisor agents should provide clear instructions to workers, and workers should return results in a structured format. Establish mechanisms for agents to request clarification when instructions are ambiguous, and design clear error reporting channels to quickly identify and resolve issues.
              </Typography>
            </AccordionDetails>
          </Accordion>
          <Accordion>
            <AccordionSummary expandIcon={<ExpandMoreIcon />}>
              <Typography variant="subtitle1">Create Robust Failure Handling</Typography>
            </AccordionSummary>
            <AccordionDetails>
              <Typography>
                Implement recovery mechanisms for when a child agent fails to complete a task. Supervisor agents should be able to detect failures and implement alternative strategies, such as retrying with different parameters, routing to a different agent, or escalating to human intervention. Design your system to be resilient against both individual agent failures and communication breakdowns between agents.
              </Typography>
            </AccordionDetails>
          </Accordion>
          <Accordion>
            <AccordionSummary expandIcon={<ExpandMoreIcon />}>
              <Typography variant="subtitle1">Define Clear Task Boundaries</Typography>
            </AccordionSummary>
            <AccordionDetails>
              <Typography>
                Clearly define when a task is complete and ready to be passed to the next agent in the hierarchy. Include validation steps to ensure that outputs from one agent meet the requirements for input to subsequent agents. This prevents cascade failures where errors from one agent propagate through the entire system. Design checkpoints where supervisor agents can validate intermediate results before continuing.
              </Typography>
            </AccordionDetails>
          </Accordion>
        </Box>
      </TabPanel>

      {/* RAG Configuration Tab */}
      <TabPanel value={activeTab} index={2}>
        <Typography variant="h5" gutterBottom>
          RAG Configuration
        </Typography>
        <Typography paragraph>
          Retrieval-Augmented Generation (RAG) enhances your agents with domain-specific knowledge,
          allowing them to access and apply information from your knowledge sources.
        </Typography>

        <Box mb={4}>
          <Typography variant="h6" gutterBottom>
            Key Components of RAG
          </Typography>
          <Grid container spacing={3}>
            <Grid item xs={12} md={4}>
              <Paper elevation={1} sx={{ p: 3, height: '100%' }}>
                <Typography variant="subtitle1" gutterBottom>
                  Embedding Models
                </Typography>
                <Typography paragraph>
                  Convert text into vector representations that capture semantic meaning.
                </Typography>
                <List dense>
                  <ListItem>
                    <ListItemText primary="OpenAI Ada 002" secondary="High quality, general purpose" />
                  </ListItem>
                  <ListItem>
                    <ListItemText primary="BGE Large/Base" secondary="Excellent performance/cost ratio" />
                  </ListItem>
                  <ListItem>
                    <ListItemText primary="Cohere Multilingual" secondary="Best for multiple languages" />
                  </ListItem>
                </List>
              </Paper>
            </Grid>
            <Grid item xs={12} md={4}>
              <Paper elevation={1} sx={{ p: 3, height: '100%' }}>
                <Typography variant="subtitle1" gutterBottom>
                  Chunking Strategies
                </Typography>
                <Typography paragraph>
                  Methods for dividing documents into smaller pieces for indexing.
                </Typography>
                <List dense>
                  <ListItem>
                    <ListItemText primary="Fixed Size (300-500 tokens)" secondary="Simple and effective for most content" />
                  </ListItem>
                  <ListItem>
                    <ListItemText primary="Semantic Chunking" secondary="Preserves meaning in complex documents" />
                  </ListItem>
                  <ListItem>
                    <ListItemText primary="Chunk Overlap (10-20%)" secondary="Prevents context fragmentation" />
                  </ListItem>
                </List>
              </Paper>
            </Grid>
            <Grid item xs={12} md={4}>
              <Paper elevation={1} sx={{ p: 3, height: '100%' }}>
                <Typography variant="subtitle1" gutterBottom>
                  Knowledge Sources
                </Typography>
                <Typography paragraph>
                  The documents and data your agent can access and reference.
                </Typography>
                <List dense>
                  <ListItem>
                    <ListItemText primary="Technical Documentation" secondary="Detailed product specifications" />
                  </ListItem>
                  <ListItem>
                    <ListItemText primary="Service Manuals" secondary="Repair and maintenance procedures" />
                  </ListItem>
                  <ListItem>
                    <ListItemText primary="FAQ Documents" secondary="Common questions and answers" />
                  </ListItem>
                </List>
              </Paper>
            </Grid>
          </Grid>
        </Box>

        <Box mb={4}>
          <Typography variant="h6" gutterBottom>
            RAG Configuration Guidelines
          </Typography>
          <TableContainer component={Paper}>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell><strong>Parameter</strong></TableCell>
                  <TableCell><strong>Recommended Setting</strong></TableCell>
                  <TableCell><strong>Notes</strong></TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                <TableRow>
                  <TableCell>Embedding Model</TableCell>
                  <TableCell>OpenAI Ada 002 or BGE Large</TableCell>
                  <TableCell>Balance quality and cost based on your needs</TableCell>
                </TableRow>
                <TableRow>
                  <TableCell>Chunk Size</TableCell>
                  <TableCell>300-500 tokens</TableCell>
                  <TableCell>Smaller for precise retrieval, larger for more context</TableCell>
                </TableRow>
                <TableRow>
                  <TableCell>Chunk Overlap</TableCell>
                  <TableCell>50 tokens (10-20%)</TableCell>
                  <TableCell>Prevents context loss between chunks</TableCell>
                </TableRow>
                <TableRow>
                  <TableCell>Knowledge Sources</TableCell>
                  <TableCell>Domain-specific resources</TableCell>
                  <TableCell>Select sources most relevant to the agent's purpose</TableCell>
                </TableRow>
              </TableBody>
            </Table>
          </TableContainer>
        </Box>

        <Box mb={4}>
          <Typography variant="h6" gutterBottom>
            RAG Best Practices
          </Typography>
          <Accordion>
            <AccordionSummary expandIcon={<ExpandMoreIcon />}>
              <Typography variant="subtitle1">Curate Knowledge Sources Carefully</Typography>
            </AccordionSummary>
            <AccordionDetails>
              <Typography>
                Quality matters more than quantity. Well-curated, accurate, and relevant knowledge sources will significantly improve RAG performance. Remove duplicate or outdated information, and organize content logically.
              </Typography>
            </AccordionDetails>
          </Accordion>
          <Accordion>
            <AccordionSummary expandIcon={<ExpandMoreIcon />}>
              <Typography variant="subtitle1">Optimize Retrieval Parameters</Typography>
            </AccordionSummary>
            <AccordionDetails>
              <Typography>
                Adjust chunk size, overlap, and retrieval settings based on your specific content. Technical documentation may benefit from smaller chunks (200-300 tokens), while narrative content might need larger chunks (500-800 tokens). Test retrieval with sample queries to find optimal settings.
              </Typography>
            </AccordionDetails>
          </Accordion>
          <Accordion>
            <AccordionSummary expandIcon={<ExpandMoreIcon />}>
              <Typography variant="subtitle1">Implement Hybrid Search</Typography>
            </AccordionSummary>
            <AccordionDetails>
              <Typography>
                Combine semantic search with keyword search for better results. This helps capture both semantic meaning and specific terms that might not be well-represented in embeddings. Hybrid search is especially valuable for technical content with domain-specific terminology.
              </Typography>
            </AccordionDetails>
          </Accordion>
          <Accordion>
            <AccordionSummary expandIcon={<ExpandMoreIcon />}>
              <Typography variant="subtitle1">Regularly Update Knowledge</Typography>
            </AccordionSummary>
            <AccordionDetails>
              <Typography>
                Implement processes to keep knowledge sources current. Outdated information can lead to incorrect responses. Schedule regular reviews and updates of knowledge sources, particularly for rapidly changing domains. 
              </Typography>
            </AccordionDetails>
          </Accordion>
        </Box>
      </TabPanel>

      {/* Fine-tuning Tab */}
      <TabPanel value={activeTab} index={3}>
        <Typography variant="h5" gutterBottom>
          Fine-tuning
        </Typography>
        <Typography paragraph>
          Fine-tuning adapts LLMs to specific tasks and domains, improving performance on your
          particular use cases by training on domain-specific examples.
        </Typography>

        <Box mb={4}>
          <Typography variant="h6" gutterBottom>
            Fine-tuning Methods
          </Typography>
          <Grid container spacing={3}>
            <Grid item xs={12} md={4}>
              <Paper elevation={1} sx={{ p: 3, height: '100%' }}>
                <Typography variant="subtitle1" gutterBottom>
                  LoRA (Low-Rank Adaptation)
                </Typography>
                <Typography paragraph>
                  Efficient parameter-efficient fine-tuning method that adapts specific parts of the model.
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  <strong>Pros:</strong> Resource efficient, works with fewer examples (100-300)
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  <strong>Cons:</strong> Slightly less performant than full fine-tuning
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  <strong>Best for:</strong> Most use cases with limited training data or compute resources
                </Typography>
              </Paper>
            </Grid>
            <Grid item xs={12} md={4}>
              <Paper elevation={1} sx={{ p: 3, height: '100%' }}>
                <Typography variant="subtitle1" gutterBottom>
                  QLoRA (Quantized LoRA)
                </Typography>
                <Typography paragraph>
                  Quantized version of LoRA that further reduces memory requirements.
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  <strong>Pros:</strong> Very resource efficient, works on consumer hardware
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  <strong>Cons:</strong> Slight quality degradation compared to LoRA
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  <strong>Best for:</strong> Resource-constrained environments with limited GPU memory
                </Typography>
              </Paper>
            </Grid>
            <Grid item xs={12} md={4}>
              <Paper elevation={1} sx={{ p: 3, height: '100%' }}>
                <Typography variant="subtitle1" gutterBottom>
                  Full Fine-tuning
                </Typography>
                <Typography paragraph>
                  Traditional approach that updates all parameters in the model.
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  <strong>Pros:</strong> Highest potential performance gains
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  <strong>Cons:</strong> Resource intensive, requires more data (500-1000+ examples)
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  <strong>Best for:</strong> Critical applications where maximum performance is needed
                </Typography>
              </Paper>
            </Grid>
          </Grid>
        </Box>

        <Box mb={4}>
          <Typography variant="h6" gutterBottom>
            Training Data Guidelines
          </Typography>
          <Paper elevation={1} sx={{ p: 3, bgcolor: '#f8f9fa' }}>
            <List>
              <ListItem>
                <ListItemText 
                  primary="Quality over quantity" 
                  secondary="Fewer high-quality examples are better than many poor-quality ones." 
                />
              </ListItem>
              <Divider component="li" />
              <ListItem>
                <ListItemText 
                  primary="Diverse examples" 
                  secondary="Cover the full range of scenarios and edge cases the agent will encounter." 
                />
              </ListItem>
              <Divider component="li" />
              <ListItem>
                <ListItemText 
                  primary="Balanced representation" 
                  secondary="Ensure different types of queries and responses are proportionally represented." 
                />
              </ListItem>
              <Divider component="li" />
              <ListItem>
                <ListItemText 
                  primary="Clear formatting" 
                  secondary="Maintain consistent input-output formatting across all examples." 
                />
              </ListItem>
              <Divider component="li" />
              <ListItem>
                <ListItemText 
                  primary="Include edge cases" 
                  secondary="Add examples for uncommon but important scenarios the agent should handle." 
                />
              </ListItem>
              <Divider component="li" />
              <ListItem>
                <ListItemText 
                  primary="Hold out test data" 
                  secondary="Reserve 10-20% of examples for evaluation after training." 
                />
              </ListItem>
            </List>
          </Paper>
        </Box>

        <Box mb={4}>
          <Typography variant="h6" gutterBottom>
            Fine-tuning Parameters
          </Typography>
          <TableContainer component={Paper}>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell><strong>Parameter</strong></TableCell>
                  <TableCell><strong>Recommended Setting</strong></TableCell>
                  <TableCell><strong>Notes</strong></TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                <TableRow>
                  <TableCell>Learning Rate</TableCell>
                  <TableCell>1e-5 to 3e-5</TableCell>
                  <TableCell>Start conservative, adjust based on results</TableCell>
                </TableRow>
                <TableRow>
                  <TableCell>Epochs</TableCell>
                  <TableCell>3-5</TableCell>
                  <TableCell>Monitor for overfitting after each epoch</TableCell>
                </TableRow>
                <TableRow>
                  <TableCell>Batch Size</TableCell>
                  <TableCell>4-8</TableCell>
                  <TableCell>Adjust based on available GPU memory</TableCell>
                </TableRow>
                <TableRow>
                  <TableCell>LoRA Rank (for LoRA)</TableCell>
                  <TableCell>8-16</TableCell>
                  <TableCell>Higher rank = more capacity but more parameters</TableCell>
                </TableRow>
              </TableBody>
            </Table>
          </TableContainer>
        </Box>
      </TabPanel>

      {/* Best Practices Tab */}
      <TabPanel value={activeTab} index={4}>
        <Typography variant="h5" gutterBottom>
          Agent Best Practices
        </Typography>
        <Typography paragraph>
          Follow these guidelines to create effective, reliable, and useful agents based on the latest research
          and industry experience.
        </Typography>

        <Box mb={4}>
          <Typography variant="h6" gutterBottom>
            Agent Design Principles
          </Typography>
          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <Paper elevation={1} sx={{ p: 3 }}>
                <Typography variant="subtitle1" gutterBottom>
                  Single Responsibility Principle
                </Typography>
                <Typography paragraph>
                  Each agent should have a clear, focused purpose rather than trying to handle too many different tasks.
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  <strong>Do:</strong> Create separate agents for customer service, technical diagnosis, and scheduling.
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  <strong>Don't:</strong> Create one agent that tries to handle all aspects of customer interaction.
                </Typography>
              </Paper>
            </Grid>
            <Grid item xs={12} md={6}>
              <Paper elevation={1} sx={{ p: 3 }}>
                <Typography variant="subtitle1" gutterBottom>
                  Progressive Enhancement
                </Typography>
                <Typography paragraph>
                  Start simple and add complexity only when needed and validated by testing.
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  <strong>Do:</strong> Begin with a basic agent, test it thoroughly, then add RAG or fine-tuning if needed.
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  <strong>Don't:</strong> Implement all advanced features at once without validating their necessity.
                </Typography>
              </Paper>
            </Grid>
            <Grid item xs={12} md={6}>
              <Paper elevation={1} sx={{ p: 3 }}>
                <Typography variant="subtitle1" gutterBottom>
                  Structured Tool Documentation
                </Typography>
                <Typography paragraph>
                  Tools available to agents need comprehensive documentation to ensure proper usage.
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  <strong>Do:</strong> Provide detailed descriptions of what each tool does, when to use it, and how parameters affect behavior.
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  <strong>Don't:</strong> Use vague tool descriptions that leave the agent guessing about functionality.
                </Typography>
              </Paper>
            </Grid>
            <Grid item xs={12} md={6}>
              <Paper elevation={1} sx={{ p: 3 }}>
                <Typography variant="subtitle1" gutterBottom>
                  Continuous Improvement
                </Typography>
                <Typography paragraph>
                  Regularly analyze agent performance and incorporate feedback into improvements.
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  <strong>Do:</strong> Monitor agent responses, collect feedback, and update configurations regularly.
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  <strong>Don't:</strong> Set up agents once and expect them to maintain performance without updates.
                </Typography>
              </Paper>
            </Grid>
          </Grid>
        </Box>

        <Box mb={4}>
          <Typography variant="h6" gutterBottom>
            Prompting Best Practices for Agents
          </Typography>
          <Accordion>
            <AccordionSummary expandIcon={<ExpandMoreIcon />}>
              <Typography variant="subtitle1">Use Clear System Instructions</Typography>
            </AccordionSummary>
            <AccordionDetails>
              <Typography>
                System instructions set the foundation for agent behavior. Clearly define the agent's role, goals, constraints, and tone. Be specific about what the agent should and should not do. For example, "You are a customer service agent for OMRA Appliance Repair. Your goal is to help customers diagnose issues with their appliances and schedule repair visits when necessary."
              </Typography>
            </AccordionDetails>
          </Accordion>
          <Accordion>
            <AccordionSummary expandIcon={<ExpandMoreIcon />}>
              <Typography variant="subtitle1">Structure Tool Definitions Carefully</Typography>
            </AccordionSummary>
            <AccordionDetails>
              <Typography>
                Describe each tool comprehensively with at least 3-4 sentences covering what the tool does, when to use it, what each parameter means, and any important caveats. Well-described tools significantly improve an agent's ability to select and use them appropriately. Include specific examples in tool descriptions where helpful.
              </Typography>
            </AccordionDetails>
          </Accordion>
          <Accordion>
            <AccordionSummary expandIcon={<ExpandMoreIcon />}>
              <Typography variant="subtitle1">Show Reasoning Through Chain-of-Thought</Typography>
            </AccordionSummary>
            <AccordionDetails>
              <Typography>
                Encourage agents to show their reasoning process, especially for complex tasks. This makes decision-making transparent and helps identify issues. For Claude models, use extended thinking when available. For other models, you can prompt for step-by-step reasoning: "Before answering, explain your reasoning step-by-step."
              </Typography>
            </AccordionDetails>
          </Accordion>
          <Accordion>
            <AccordionSummary expandIcon={<ExpandMoreIcon />}>
              <Typography variant="subtitle1">Create Structured Agent-Environment Interfaces</Typography>
            </AccordionSummary>
            <AccordionDetails>
              <Typography>
                Design a clean interface between the agent and its environment. For tools that interact with external systems, ensure inputs and outputs are well-defined and properly handled. Log interactions for debugging and include appropriate error handling for when tools fail.
              </Typography>
            </AccordionDetails>
          </Accordion>
        </Box>

        <Box mb={4}>
          <Typography variant="h6" gutterBottom>
            Common Implementation Pitfalls
          </Typography>
          <Accordion>
            <AccordionSummary expandIcon={<ExpandMoreIcon />}>
              <Typography variant="subtitle1">Over-engineering Agent Systems</Typography>
            </AccordionSummary>
            <AccordionDetails>
              <Typography>
                Success in building AI agents isn't about creating the most sophisticated system. Start with simple prompts and basic tools, then add complexity only when it demonstrably improves outcomes. Many complex frameworks add unnecessary layers of abstraction that make debugging and maintenance more difficult.
              </Typography>
            </AccordionDetails>
          </Accordion>
          <Accordion>
            <AccordionSummary expandIcon={<ExpandMoreIcon />}>
              <Typography variant="subtitle1">Neglecting Testing with Diverse Scenarios</Typography>
            </AccordionSummary>
            <AccordionDetails>
              <Typography>
                Test agents with a wide range of inputs and scenarios, including edge cases. Agents often perform well for common scenarios but fail on edge cases. Identify potential edge cases through systematic testing and user feedback, then update your agents to handle these situations appropriately.
              </Typography>
            </AccordionDetails>
          </Accordion>
          <Accordion>
            <AccordionSummary expandIcon={<ExpandMoreIcon />}>
              <Typography variant="subtitle1">Insufficient Tool Documentation</Typography>
            </AccordionSummary>
            <AccordionDetails>
              <Typography>
                Brief or vague tool descriptions lead to tool misuse. When the agent doesn't fully understand a tool's purpose or parameters, it may use it incorrectly or fail to use it when appropriate. Prioritize comprehensive tool descriptions over extensive examples, as clear explanations provide better guidance for the agent.
              </Typography>
            </AccordionDetails>
          </Accordion>
          <Accordion>
            <AccordionSummary expandIcon={<ExpandMoreIcon />}>
              <Typography variant="subtitle1">Lack of Human Oversight Mechanisms</Typography>
            </AccordionSummary>
            <AccordionDetails>
              <Typography>
                Include appropriate checkpoints for human review in agent workflows, especially for consequential actions. Agents should know when to seek human approval and how to present information clearly for human decision-makers. This is particularly important for financial transactions, data deletion, or communications with customers.
              </Typography>
            </AccordionDetails>
          </Accordion>
        </Box>

        <Box mb={4}>
          <Typography variant="h6" gutterBottom>
            Measuring Agent Success
          </Typography>
          <TableContainer component={Paper}>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell><strong>Metric</strong></TableCell>
                  <TableCell><strong>Description</strong></TableCell>
                  <TableCell><strong>Target</strong></TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                <TableRow>
                  <TableCell>Task Completion Rate</TableCell>
                  <TableCell>Percentage of tasks successfully completed without human intervention</TableCell>
                  <TableCell>{'>'}80%</TableCell>
                </TableRow>
                <TableRow>
                  <TableCell>Customer Satisfaction</TableCell>
                  <TableCell>User ratings of agent interactions</TableCell>
                  <TableCell>{'>'}4.5/5</TableCell>
                </TableRow>
                <TableRow>
                  <TableCell>Response Accuracy</TableCell>
                  <TableCell>Correctness of information provided</TableCell>
                  <TableCell>{'>'}90%</TableCell>
                </TableRow>
                <TableRow>
                  <TableCell>Average Resolution Time</TableCell>
                  <TableCell>Time to successfully complete a user request</TableCell>
                  <TableCell>Reduction vs. baseline</TableCell>
                </TableRow>
                <TableRow>
                  <TableCell>Escalation Rate</TableCell>
                  <TableCell>Percentage of interactions requiring human intervention</TableCell>
                  <TableCell>{'<'}20%</TableCell>
                </TableRow>
                <TableRow>
                  <TableCell>Tool Usage Accuracy</TableCell>
                  <TableCell>Percentage of tool calls made appropriately and successfully</TableCell>
                  <TableCell>{'>'}95%</TableCell>
                </TableRow>
              </TableBody>
            </Table>
          </TableContainer>
        </Box>
      </TabPanel>

      <Box mt={4} display="flex" justifyContent="flex-end">
        <Button
          variant="contained"
          color="primary"
          href="/agents"
          sx={{ mr: 2 }}
        >
          Create an Agent
        </Button>
        <Button
          variant="outlined"
          color="primary"
          href="https://docs.openai.com/tutorials/fine-tuning"
          target="_blank"
          rel="noopener noreferrer"
        >
          External Resources
        </Button>
      </Box>
    </Box>
  );
};

export default AgentDocs; 