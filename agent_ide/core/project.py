"""Project management functionality."""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from datetime import datetime
import os
import yaml
import json
from pathlib import Path

from .agent import Agent


class ProjectConfig(BaseModel):
    """Configuration for a project."""
    
    name: str
    description: Optional[str] = None
    version: str = "0.1.0"
    author: Optional[str] = None
    python_version: str = ">=3.8"
    dependencies: List[str] = Field(default_factory=list)


class Project(BaseModel):
    """Represents an agent project."""
    
    config: ProjectConfig
    path: str
    agents: Dict[str, Agent] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    @classmethod
    def create(cls, path: str, config: ProjectConfig) -> "Project":
        """Create a new project."""
        project_path = Path(path)
        project_path.mkdir(parents=True, exist_ok=True)
        
        project = cls(config=config, path=str(project_path))
        project.save()
        return project
    
    @classmethod
    def load(cls, path: str) -> "Project":
        """Load a project from disk."""
        project_path = Path(path)
        config_file = project_path / "agent_project.yaml"
        
        if not config_file.exists():
            raise FileNotFoundError(f"Project config not found: {config_file}")
        
        with open(config_file, 'r') as f:
            data = yaml.safe_load(f)
        
        config = ProjectConfig(**data['config'])
        project = cls(config=config, path=str(project_path))
        
        # Load agents
        agents_dir = project_path / "agents"
        if agents_dir.exists():
            for agent_file in agents_dir.glob("*.json"):
                with open(agent_file, 'r') as f:
                    agent_data = json.load(f)
                agent = Agent(**agent_data)
                project.agents[agent.id] = agent
        
        return project
    
    def save(self) -> None:
        """Save project to disk."""
        project_path = Path(self.path)
        project_path.mkdir(parents=True, exist_ok=True)
        
        # Save project config
        config_file = project_path / "agent_project.yaml"
        project_data = {
            "config": self.config.model_dump(),
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
        
        with open(config_file, 'w') as f:
            yaml.dump(project_data, f, default_flow_style=False)
        
        # Save agents
        agents_dir = project_path / "agents"
        agents_dir.mkdir(exist_ok=True)
        
        for agent in self.agents.values():
            agent_file = agents_dir / f"{agent.id}.json"
            with open(agent_file, 'w') as f:
                json.dump(agent.model_dump(), f, indent=2, default=str)
        
        self.updated_at = datetime.now()
    
    def add_agent(self, agent: Agent) -> None:
        """Add an agent to the project."""
        self.agents[agent.id] = agent
        self.updated_at = datetime.now()
    
    def remove_agent(self, agent_id: str) -> None:
        """Remove an agent from the project."""
        if agent_id in self.agents:
            del self.agents[agent_id]
            # Remove agent file
            agent_file = Path(self.path) / "agents" / f"{agent_id}.json"
            if agent_file.exists():
                agent_file.unlink()
            self.updated_at = datetime.now()
    
    def get_agent(self, agent_id: str) -> Optional[Agent]:
        """Get an agent by ID."""
        return self.agents.get(agent_id)
    
    def list_agents(self) -> List[Agent]:
        """List all agents in the project."""
        return list(self.agents.values())
