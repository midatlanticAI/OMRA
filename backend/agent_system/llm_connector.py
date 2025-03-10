"""
LLM Connector module for interfacing with different LLM APIs
Supports Claude, GPT-4o, and GPT-4o-mini
"""
import asyncio
from typing import Dict, Any, Optional

class LLMConnector:
    """
    Handles connections to different LLM APIs
    Supports Claude, GPT-4o, and GPT-4o-mini
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the LLM connector with configuration
        
        Args:
            config: Configuration dictionary with API keys and settings
        """
        self.config = config
        self.claude_client = None
        self.openai_client = None
        self._initialize_clients()
        
    def _initialize_clients(self):
        """Initialize API clients"""
        # Initialize Claude client
        if self.config.get("api_keys", {}).get("claude"):
            try:
                import anthropic
                self.claude_client = anthropic.Anthropic(
                    api_key=self.config["api_keys"]["claude"]
                )
            except ImportError:
                raise ImportError("anthropic package is required for Claude integration")
            
        # Initialize OpenAI client
        if self.config.get("api_keys", {}).get("openai"):
            try:
                import openai
                self.openai_client = openai.OpenAI(
                    api_key=self.config["api_keys"]["openai"]
                )
            except ImportError:
                raise ImportError("openai package is required for OpenAI integration")
    
    async def generate(self, model: str, prompt: str, system_prompt: str = None,
                      max_tokens: int = 1000, temperature: float = 0.7) -> str:
        """
        Generate text from LLM
        
        Args:
            model: Model name (claude-3-sonnet, gpt-4o, gpt-4o-mini)
            prompt: The prompt to send
            system_prompt: Optional system prompt
            max_tokens: Maximum tokens to generate
            temperature: Temperature for generation
            
        Returns:
            Generated text
        """
        if model.startswith("claude"):
            return await self._generate_claude(
                model, prompt, system_prompt, max_tokens, temperature
            )
        elif model.startswith("gpt"):
            return await self._generate_openai(
                model, prompt, system_prompt, max_tokens, temperature
            )
        else:
            raise ValueError(f"Unsupported model: {model}")
    
    async def _generate_claude(self, model: str, prompt: str, system_prompt: str = None,
                              max_tokens: int = 1000, temperature: float = 0.7) -> str:
        """Generate text using Claude API"""
        if not self.claude_client:
            raise ValueError("Claude API client not initialized")
            
        # Create messages
        messages = [{"role": "user", "content": prompt}]
        
        # Call Claude API
        try:
            response = await asyncio.to_thread(
                self.claude_client.messages.create,
                model=model,
                max_tokens=max_tokens,
                temperature=temperature,
                system=system_prompt,
                messages=messages
            )
            
            return response.content[0].text
        except Exception as e:
            raise Exception(f"Error calling Claude API: {str(e)}")
    
    async def _generate_openai(self, model: str, prompt: str, system_prompt: str = None,
                              max_tokens: int = 1000, temperature: float = 0.7) -> str:
        """Generate text using OpenAI API"""
        if not self.openai_client:
            raise ValueError("OpenAI API client not initialized")
            
        # Create messages
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        # Call OpenAI API
        try:
            response = await asyncio.to_thread(
                self.openai_client.chat.completions.create,
                model=model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature
            )
            
            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"Error calling OpenAI API: {str(e)}") 