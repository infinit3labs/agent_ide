"""Core agent model and functionality."""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from datetime import datetime
import uuid


class AgentConfig(BaseModel):
    """Configuration for an agent."""
    
    name: str
    description: Optional[str] = None
    agent_type: str = "general"
    parameters: Dict[str, Any] = Field(default_factory=dict)
    capabilities: List[str] = Field(default_factory=list)
    model: Optional[str] = None
    max_iterations: int = 100
    timeout: int = 300  # seconds


class AgentState(BaseModel):
    """Current state of an agent."""
    
    status: str = "idle"  # idle, running, paused, completed, error
    current_task: Optional[str] = None
    iteration_count: int = 0
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    error_message: Optional[str] = None


class Agent(BaseModel):
    """Represents an AI agent in the IDE."""
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    config: AgentConfig
    state: AgentState = Field(default_factory=AgentState)
    code: str = ""
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    def update_state(self, **kwargs) -> None:
        """Update the agent's state."""
        for key, value in kwargs.items():
            if hasattr(self.state, key):
                setattr(self.state, key, value)
        self.updated_at = datetime.now()
    
    def is_running(self) -> bool:
        """Check if the agent is currently running."""
        return self.state.status == "running"
    
    def reset(self) -> None:
        """Reset the agent to initial state."""
        self.state = AgentState()
        self.updated_at = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert agent to dictionary."""
        return {
            "id": self.id,
            "config": self.config.model_dump(),
            "state": self.state.model_dump(),
            "code": self.code,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
