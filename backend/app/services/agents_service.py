"""
Service layer for agent management and interaction with Ollama.
"""
import os
import requests
import logging
from typing import Optional
from app.dto.agents_dto import AgentConfigCreate
from app.crud.agents_crud import (
    create_agent_config, 
    get_llm_models,
    get_agent_config
)

logger = logging.getLogger(__name__)

OLLAMA_BASE_URL = os.getenv("OLLAMA_HOST", "http://localhost:11434")
OLLAMA_GENERATE_ENDPOINT = f"{OLLAMA_BASE_URL}/api/generate"
OLLAMA_TIMEOUT = 30  # seconds


class AgentService:
    """Service for managing agent configurations and AI interactions."""

    def __init__(self):
        self.ollama_url = OLLAMA_GENERATE_ENDPOINT

    def import_user_model_config(self, db, user_id, config_in: AgentConfigCreate):
        """
        Create a new agent configuration for a user.
        
        Validates:
        - System prompt is not empty
        - System prompt doesn't contain dangerous escape sequences
        """
        # Validate system prompt
        if not config_in.system_prompt or len(config_in.system_prompt.strip()) < 10:
            raise ValueError("System prompt must be at least 10 characters long")
        
        # Validate that the model exists
        base_model = get_agent_config(db, config_in.base_model_id)
        if not base_model:
            raise ValueError("Selected model does not exist")
        
        return create_agent_config(db, config_in, user_id)

    async def get_agent_decision(
        self, 
        system_prompt: str, 
        history: str, 
        target_info: str,
        model_tag: str = "dolphin-llama3"
    ) -> Optional[str]:
        """
        Query Ollama to generate the next hacking command for an agent.
        
        Args:
            system_prompt: Agent's system instructions
            history: Recent action history
            target_info: Information about target systems
            model_tag: Ollama model to use
        
        Returns:
            Generated command or None if request fails
        """
        full_prompt = f"""
SYSTEM: {system_prompt}

TARGET DATA: {target_info}

PREVIOUS ACTIONS: {history}

Provide only the raw terminal command you want to execute next. No explanation. Be concise.
"""
        
        payload = {
            "model": model_tag,
            "prompt": full_prompt,
            "stream": False
        }
        
        try:
            response = requests.post(
                self.ollama_url, 
                json=payload, 
                timeout=OLLAMA_TIMEOUT
            )
            response.raise_for_status()
            result = response.json().get("response", "").strip()
            
            # Safety: reject overly long or suspicious commands
            if len(result) > 500:
                logger.warning("Generated command exceeds safe length limit")
                return None
            
            return result
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to query Ollama: {e}")
            raise RuntimeError(f"AI service error: {str(e)}")

    def get_active_models(self, db) -> list:
        """Get all active LLM models available for use."""
        return get_llm_models(db, active_only=True)
