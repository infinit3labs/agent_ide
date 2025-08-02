"""Basic tests for Agent IDE."""

import pytest
from agent_ide.core.agent import Agent, AgentConfig
from agent_ide.core.project import Project, ProjectConfig
import tempfile
import shutil
from pathlib import Path


def test_agent_creation():
    """Test basic agent creation."""
    config = AgentConfig(name="TestAgent", agent_type="general")
    agent = Agent(config=config)
    
    assert agent.config.name == "TestAgent"
    assert agent.config.agent_type == "general"
    assert agent.state.status == "idle"
    assert not agent.is_running()


def test_project_creation():
    """Test project creation and management."""
    with tempfile.TemporaryDirectory() as temp_dir:
        config = ProjectConfig(name="TestProject", description="Test project")
        project = Project.create(temp_dir, config)
        
        assert project.config.name == "TestProject"
        assert project.path == temp_dir
        assert len(project.agents) == 0
        
        # Test adding agent
        agent_config = AgentConfig(name="TestAgent")
        agent = Agent(config=agent_config)
        project.add_agent(agent)
        
        assert len(project.agents) == 1
        assert agent.id in project.agents
        
        # Test saving and loading
        project.save()
        loaded_project = Project.load(temp_dir)
        
        assert loaded_project.config.name == "TestProject"
        assert len(loaded_project.agents) == 1


def test_agent_state_updates():
    """Test agent state management."""
    config = AgentConfig(name="TestAgent")
    agent = Agent(config=config)
    
    agent.update_state(status="running", iteration_count=5)
    
    assert agent.state.status == "running"
    assert agent.state.iteration_count == 5
    assert agent.is_running()
    
    agent.reset()
    assert agent.state.status == "idle"
    assert agent.state.iteration_count == 0
    assert not agent.is_running()


if __name__ == "__main__":
    pytest.main([__file__])
