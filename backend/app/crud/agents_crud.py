"""
CRUD operations for agent and LLM model management.
"""
from sqlalchemy.orm import Session
from app.models.agents import LLMModel, AgentConfig
from app.dto.agents_dto import AgentConfigCreate
from uuid import UUID


def get_llm_models(db: Session, active_only: bool = True):
    """Get all available LLM models, optionally filtered to active only."""
    query = db.query(LLMModel)
    if active_only:
        query = query.filter(LLMModel.is_active == True)
    return query.all()


def get_llm_model(db: Session, model_id: UUID):
    """Get a specific LLM model by ID."""
    return db.query(LLMModel).filter(LLMModel.id == model_id).first()


def create_llm_model(db: Session, ollama_tag: str, description: str = None, size_bytes: int = None):
    """Create a new LLM model record."""
    db_model = LLMModel(
        ollama_tag=ollama_tag,
        description=description,
        size_bytes=size_bytes
    )
    db.add(db_model)
    db.commit()
    db.refresh(db_model)
    return db_model


def create_agent_config(db: Session, config_in: AgentConfigCreate, user_id: UUID):
    """Create a new agent configuration for a user."""
    db_config = AgentConfig(
        **config_in.model_dump(),
        user_id=user_id
    )
    db.add(db_config)
    db.commit()
    db.refresh(db_config)
    return db_config


def get_user_agents(db: Session, user_id: UUID):
    """Get all agent configurations for a user."""
    return db.query(AgentConfig).filter(AgentConfig.user_id == user_id).all()


def get_agent_config(db: Session, config_id: UUID):
    """Get a specific agent configuration by ID."""
    return db.query(AgentConfig).filter(AgentConfig.id == config_id).first()


def update_agent_config(db: Session, config_id: UUID, config_data: dict):
    """Update an agent configuration."""
    db_config = get_agent_config(db, config_id)
    if not db_config:
        return None
    
    for key, value in config_data.items():
        if value is not None:
            setattr(db_config, key, value)
    
    db.commit()
    db.refresh(db_config)
    return db_config


def delete_agent_config(db: Session, config_id: UUID):
    """Delete an agent configuration."""
    db_config = get_agent_config(db, config_id)
    if db_config:
        db.delete(db_config)
        db.commit()
        return True
    return False
