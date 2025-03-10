"""
Tests for the base agent functionality.
"""
import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from backend.agents.base import AgentBase

# Create a concrete implementation of the abstract base class for testing
class TestAgent(AgentBase):
    """Test agent implementation of the abstract base class."""
    
    def __init__(self, name="TestAgent", agent_type="test"):
        super().__init__(name=name, agent_type=agent_type)
    
    async def process(self, input_data):
        """Process the input data and return the result."""
        # Pre-process input
        processed_input = await self._pre_process(input_data)
        
        # Process input (simulated)
        output_data = {
            "success": True,
            "response": f"Processed: {processed_input.get('query', '')}",
            "model": "test_model"
        }
        
        # Post-process output
        processed_output = await self._post_process(output_data)
        
        return processed_output

@patch("backend.core.logging.log_agent_activity")
def test_agent_initialization(mock_log_activity):
    """Test agent initialization."""
    agent = TestAgent(name="CustomTestAgent", agent_type="custom")
    
    assert agent.name == "CustomTestAgent"
    assert agent.agent_type == "custom"
    assert agent.agent_id is not None
    
    # Verify logging was called
    mock_log_activity.assert_called_once_with(
        agent_type="custom",
        agent_name="CustomTestAgent",
        action="initialized",
        details={"agent_id": agent.agent_id}
    )

@pytest.mark.asyncio
@patch("backend.core.logging.log_agent_activity")
async def test_agent_pre_process(mock_log_activity):
    """Test agent pre-processing functionality."""
    agent = TestAgent()
    input_data = {"query": "test query", "parameters": {"key": "value"}}
    
    result = await agent._pre_process(input_data)
    
    assert result == input_data
    mock_log_activity.assert_called_with(
        agent_type="test",
        agent_name="TestAgent",
        action="pre_processing",
        details={"input_keys": ["query", "parameters"]}
    )

@pytest.mark.asyncio
@patch("backend.core.logging.log_agent_activity")
async def test_agent_post_process(mock_log_activity):
    """Test agent post-processing functionality."""
    agent = TestAgent()
    output_data = {
        "success": True,
        "response": "test response",
        "model": "test_model"
    }
    
    result = await agent._post_process(output_data)
    
    assert result == output_data
    mock_log_activity.assert_called_with(
        agent_type="test",
        agent_name="TestAgent",
        action="post_processing",
        details={"output_keys": ["success", "response", "model"]}
    )

@pytest.mark.asyncio
@patch("backend.core.logging.log_agent_activity")
async def test_agent_process(mock_log_activity):
    """Test agent processing functionality."""
    agent = TestAgent()
    input_data = {"query": "test query"}
    
    result = await agent.process(input_data)
    
    assert result["success"] is True
    assert result["response"] == "Processed: test query"
    assert result["model"] == "test_model"
    
    # Verify logging was called multiple times (init, pre-process, post-process)
    assert mock_log_activity.call_count >= 3

@pytest.mark.asyncio
@patch("backend.core.logging.log_agent_activity")
async def test_agent_error_handling(mock_log_activity):
    """Test agent error handling functionality."""
    agent = TestAgent()
    
    # Create an agent that raises an exception during processing
    error_agent = TestAgent()
    error_agent._pre_process = AsyncMock(side_effect=ValueError("Test error"))
    
    # Test error handling
    input_data = {"query": "test query"}
    result = await error_agent.handle_error(ValueError("Test error"), input_data)
    
    assert result["success"] is False
    assert "Test error" in result["error"]
    assert result["error_type"] == "ValueError"
    
    # Verify error was logged
    mock_log_activity.assert_called_with(
        agent_type="test",
        agent_name="TestAgent",
        action="error",
        details={
            "error_type": "ValueError",
            "error_message": "Test error",
            "input_keys": ["query"]
        }
    ) 