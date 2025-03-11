import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { useApi } from './ApiContext';
import { useAuth } from './AuthContext';

const AiAssistantContext = createContext();

export const useAiAssistant = () => useContext(AiAssistantContext);

export const AiAssistantProvider = ({ children }) => {
  const { apiCall } = useApi();
  const { isAuthenticated } = useAuth();
  const [isOpen, setIsOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [messages, setMessages] = useState([]);
  const [conversationId, setConversationId] = useState(null);
  const [conversationHistory, setConversationHistory] = useState([]);

  // Load conversation history when authenticated
  useEffect(() => {
    if (isAuthenticated) {
      fetchConversationHistory();
    }
  }, [isAuthenticated]);

  // Fetch conversation history
  const fetchConversationHistory = async () => {
    try {
      const result = await apiCall('/api/conversations?metadata.source=ai_assistant', 'GET');
      if (result && result.conversations) {
        setConversationHistory(result.conversations);
      }
    } catch (err) {
      console.error('Error fetching conversation history:', err);
    }
  };

  // Load a specific conversation
  const loadConversation = async (id) => {
    try {
      setLoading(true);
      const result = await apiCall(`/api/conversations/${id}/messages`, 'GET');
      if (result && result.messages) {
        setMessages(result.messages);
        setConversationId(id);
      }
    } catch (err) {
      setError('Error loading conversation');
      console.error('Error loading conversation:', err);
    } finally {
      setLoading(false);
    }
  };

  // Send a message to the AI assistant
  const sendMessage = async (messageText) => {
    if (!messageText.trim()) return;

    try {
      // Add user message to UI immediately
      const newMessage = {
        role: 'user',
        content: messageText,
        timestamp: new Date().toISOString(),
        // Use temporary ID until we get the actual one from the server
        _id: `temp-${Date.now()}`
      };

      setMessages((prevMessages) => [...prevMessages, newMessage]);
      setLoading(true);
      setError(null);

      // Send message to API
      const payload = {
        message: messageText,
        conversation_id: conversationId
      };

      const result = await apiCall('/api/ai-assistant/chat', 'POST', payload);
      
      // Handle API response
      if (result) {
        // Add assistant's response to UI
        const assistantMessage = {
          role: 'agent',
          content: result.response,
          timestamp: new Date().toISOString(),
          _id: `response-${Date.now()}`,
          metadata: { tool_outputs: result.tool_outputs || [] }
        };

        setMessages((prevMessages) => [...prevMessages, assistantMessage]);
        
        // Update conversation ID if this is a new conversation
        if (!conversationId && result.conversation_id) {
          setConversationId(result.conversation_id);
          // Refresh conversation history
          fetchConversationHistory();
        }
      }
    } catch (err) {
      setError('Error sending message to assistant');
      console.error('Error in sendMessage:', err);
    } finally {
      setLoading(false);
    }
  };

  const clearConversation = () => {
    setMessages([]);
    setConversationId(null);
  };

  const toggleAssistant = () => {
    setIsOpen((prev) => !prev);
  };

  const value = {
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
  };

  return (
    <AiAssistantContext.Provider value={value}>
      {children}
    </AiAssistantContext.Provider>
  );
};

export default AiAssistantContext; 