"""Agent execution environment."""

from typing import Dict, Any, List, Optional, Callable
from pydantic import BaseModel
import asyncio
import logging
from datetime import datetime
import threading
import queue
import traceback

from .agent import Agent, AgentState


class ExecutionResult(BaseModel):
    """Result of agent execution."""
    
    agent_id: str
    success: bool
    output: Optional[str] = None
    error: Optional[str] = None
    duration: float = 0.0
    iterations: int = 0


class ExecutionEnvironment:
    """Environment for executing agents safely."""
    
    def __init__(self):
        self.running_agents: Dict[str, threading.Thread] = {}
        self.results: Dict[str, ExecutionResult] = {}
        self.logger = logging.getLogger(__name__)
        self.stop_events: Dict[str, threading.Event] = {}
    
    def execute_agent(self, agent: Agent, callback: Optional[Callable] = None) -> str:
        """Execute an agent asynchronously."""
        if agent.is_running():
            raise RuntimeError(f"Agent {agent.id} is already running")
        
        # Create stop event for this agent
        stop_event = threading.Event()
        self.stop_events[agent.id] = stop_event
        
        # Create and start execution thread
        thread = threading.Thread(
            target=self._run_agent,
            args=(agent, callback, stop_event),
            name=f"agent-{agent.id}"
        )
        
        self.running_agents[agent.id] = thread
        agent.update_state(
            status="running",
            start_time=datetime.now(),
            iteration_count=0
        )
        
        thread.start()
        return agent.id
    
    def stop_agent(self, agent_id: str) -> bool:
        """Stop a running agent."""
        if agent_id not in self.running_agents:
            return False
        
        # Signal the agent to stop
        if agent_id in self.stop_events:
            self.stop_events[agent_id].set()
        
        # Wait for thread to finish
        thread = self.running_agents[agent_id]
        thread.join(timeout=5.0)
        
        if thread.is_alive():
            self.logger.warning(f"Agent {agent_id} did not stop gracefully")
            return False
        
        # Clean up
        del self.running_agents[agent_id]
        if agent_id in self.stop_events:
            del self.stop_events[agent_id]
        
        return True
    
    def get_result(self, agent_id: str) -> Optional[ExecutionResult]:
        """Get execution result for an agent."""
        return self.results.get(agent_id)
    
    def is_running(self, agent_id: str) -> bool:
        """Check if an agent is currently running."""
        return agent_id in self.running_agents
    
    def list_running_agents(self) -> List[str]:
        """List all currently running agents."""
        return list(self.running_agents.keys())
    
    def _run_agent(self, agent: Agent, callback: Optional[Callable], stop_event: threading.Event) -> None:
        """Internal method to run an agent."""
        start_time = datetime.now()
        result = ExecutionResult(agent_id=agent.id, success=False)
        
        try:
            # This is a simplified execution - in a real implementation,
            # you would compile and execute the agent's code safely
            output = self._execute_agent_code(agent, stop_event)
            
            result.success = True
            result.output = output
            result.iterations = agent.state.iteration_count
            
            agent.update_state(
                status="completed",
                end_time=datetime.now()
            )
            
        except Exception as e:
            error_msg = str(e)
            self.logger.error(f"Agent {agent.id} failed: {error_msg}")
            
            result.error = error_msg
            agent.update_state(
                status="error",
                error_message=error_msg,
                end_time=datetime.now()
            )
        
        finally:
            end_time = datetime.now()
            result.duration = (end_time - start_time).total_seconds()
            self.results[agent.id] = result
            
            # Clean up
            if agent.id in self.running_agents:
                del self.running_agents[agent.id]
            if agent.id in self.stop_events:
                del self.stop_events[agent.id]
            
            # Call callback if provided
            if callback:
                try:
                    callback(agent, result)
                except Exception as e:
                    self.logger.error(f"Callback failed for agent {agent.id}: {e}")
    
    def _execute_agent_code(self, agent: Agent, stop_event: threading.Event) -> str:
        """Execute the agent's code safely."""
        # This is a simplified implementation
        # In a real system, you'd want to:
        # 1. Parse and validate the code
        # 2. Execute in a sandboxed environment
        # 3. Handle timeouts and resource limits
        # 4. Provide proper agent APIs
        
        if not agent.code.strip():
            return "No code to execute"
        
        # Simulate execution with progress updates
        max_iterations = agent.config.max_iterations
        for i in range(max_iterations):
            if stop_event.is_set():
                return f"Execution stopped at iteration {i}"
            
            agent.update_state(iteration_count=i + 1)
            
            # Simulate some work
            import time
            time.sleep(0.1)
        
        return f"Agent executed successfully for {max_iterations} iterations"
