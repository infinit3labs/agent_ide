"""FastAPI web server for Agent IDE."""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import uvicorn
import os
from pathlib import Path

from ..core.project import Project
from ..core.agent import Agent, AgentConfig
from ..core.execution import ExecutionEnvironment

# Global variables
current_project: Optional[Project] = None
execution_env = ExecutionEnvironment()

app = FastAPI(
    title="Agent IDE",
    description="An intelligent development environment for AI agents",
    version="0.1.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request/Response models
class CreateAgentRequest(BaseModel):
    name: str
    description: Optional[str] = None
    agent_type: str = "general"
    model: Optional[str] = None


class UpdateAgentRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    code: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None


class ExecuteAgentRequest(BaseModel):
    agent_id: str


@app.on_event("startup")
async def startup_event():
    """Initialize the application."""
    global current_project
    try:
        current_project = Project.load('.')
    except FileNotFoundError:
        current_project = None


@app.get("/", response_class=HTMLResponse)
async def get_index():
    """Serve the main IDE interface."""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Agent IDE</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body { 
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                margin: 0; 
                padding: 20px; 
                background: #f5f5f5;
            }
            .container { 
                max-width: 1200px; 
                margin: 0 auto; 
                background: white; 
                padding: 20px; 
                border-radius: 8px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }
            .header { 
                border-bottom: 1px solid #eee; 
                padding-bottom: 20px; 
                margin-bottom: 20px;
            }
            .agent-list { 
                display: grid; 
                gap: 20px; 
                grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            }
            .agent-card { 
                border: 1px solid #ddd; 
                padding: 15px; 
                border-radius: 8px;
                background: #fafafa;
            }
            .agent-card h3 { 
                margin: 0 0 10px 0; 
                color: #333;
            }
            .status { 
                padding: 4px 8px; 
                border-radius: 4px; 
                font-size: 12px; 
                font-weight: bold;
            }
            .status.idle { background: #e3f2fd; color: #1976d2; }
            .status.running { background: #fff3e0; color: #f57c00; }
            .status.completed { background: #e8f5e8; color: #2e7d32; }
            .status.error { background: #ffebee; color: #c62828; }
            .btn { 
                padding: 8px 16px; 
                border: none; 
                border-radius: 4px; 
                cursor: pointer; 
                margin: 5px;
                font-size: 14px;
            }
            .btn-primary { background: #1976d2; color: white; }
            .btn-success { background: #2e7d32; color: white; }
            .btn-danger { background: #c62828; color: white; }
            .form-group { margin: 15px 0; }
            .form-group label { display: block; margin-bottom: 5px; font-weight: bold; }
            .form-group input, .form-group textarea, .form-group select { 
                width: 100%; 
                padding: 8px; 
                border: 1px solid #ddd; 
                border-radius: 4px;
                font-size: 14px;
            }
            .form-group textarea { height: 200px; resize: vertical; }
            .modal { 
                display: none; 
                position: fixed; 
                top: 0; 
                left: 0; 
                width: 100%; 
                height: 100%; 
                background: rgba(0,0,0,0.5);
                z-index: 1000;
            }
            .modal-content { 
                background: white; 
                margin: 5% auto; 
                padding: 20px; 
                width: 80%; 
                max-width: 600px;
                border-radius: 8px;
            }
            .close { 
                float: right; 
                font-size: 28px; 
                font-weight: bold; 
                cursor: pointer;
            }
            .loading { 
                display: inline-block; 
                animation: spin 1s linear infinite;
            }
            @keyframes spin { 
                0% { transform: rotate(0deg); } 
                100% { transform: rotate(360deg); } 
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🤖 Agent IDE</h1>
                <p>Intelligent Development Environment for AI Agents</p>
                <button class="btn btn-primary" onclick="showCreateModal()">+ Create Agent</button>
                <button class="btn btn-success" onclick="refreshAgents()">🔄 Refresh</button>
            </div>
            
            <div id="project-info"></div>
            <div id="agents-container">
                <div class="agent-list" id="agent-list">
                    <p>Loading agents...</p>
                </div>
            </div>
        </div>

        <!-- Create Agent Modal -->
        <div id="createModal" class="modal">
            <div class="modal-content">
                <span class="close" onclick="hideCreateModal()">&times;</span>
                <h2>Create New Agent</h2>
                <form id="createAgentForm">
                    <div class="form-group">
                        <label>Name:</label>
                        <input type="text" id="agentName" required>
                    </div>
                    <div class="form-group">
                        <label>Description:</label>
                        <input type="text" id="agentDescription">
                    </div>
                    <div class="form-group">
                        <label>Type:</label>
                        <select id="agentType">
                            <option value="general">General</option>
                            <option value="chat">Chat</option>
                            <option value="task">Task</option>
                            <option value="analysis">Analysis</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>Model:</label>
                        <input type="text" id="agentModel" placeholder="e.g., gpt-4, claude-3">
                    </div>
                    <button type="submit" class="btn btn-primary">Create Agent</button>
                </form>
            </div>
        </div>

        <!-- Edit Agent Modal -->
        <div id="editModal" class="modal">
            <div class="modal-content">
                <span class="close" onclick="hideEditModal()">&times;</span>
                <h2>Edit Agent</h2>
                <form id="editAgentForm">
                    <input type="hidden" id="editAgentId">
                    <div class="form-group">
                        <label>Name:</label>
                        <input type="text" id="editAgentName" required>
                    </div>
                    <div class="form-group">
                        <label>Description:</label>
                        <input type="text" id="editAgentDescription">
                    </div>
                    <div class="form-group">
                        <label>Code:</label>
                        <textarea id="editAgentCode" placeholder="Enter Python code for your agent..."></textarea>
                    </div>
                    <button type="submit" class="btn btn-primary">Save Changes</button>
                </form>
            </div>
        </div>

        <script>
            let agents = [];
            let projectInfo = null;

            // Load initial data
            document.addEventListener('DOMContentLoaded', function() {
                loadProjectInfo();
                refreshAgents();
            });

            async function loadProjectInfo() {
                try {
                    const response = await fetch('/api/project');
                    if (response.ok) {
                        projectInfo = await response.json();
                        document.getElementById('project-info').innerHTML = 
                            `<h3>📁 Project: ${projectInfo.config.name}</h3>
                             <p>${projectInfo.config.description}</p>`;
                    }
                } catch (error) {
                    console.error('Error loading project info:', error);
                }
            }

            async function refreshAgents() {
                try {
                    const response = await fetch('/api/agents');
                    agents = await response.json();
                    renderAgents();
                } catch (error) {
                    console.error('Error fetching agents:', error);
                    document.getElementById('agent-list').innerHTML = '<p>Error loading agents</p>';
                }
            }

            function renderAgents() {
                const container = document.getElementById('agent-list');
                if (agents.length === 0) {
                    container.innerHTML = '<p>No agents found. Create your first agent!</p>';
                    return;
                }

                container.innerHTML = agents.map(agent => `
                    <div class="agent-card">
                        <h3>${agent.config.name}</h3>
                        <p><strong>Type:</strong> ${agent.config.agent_type}</p>
                        <p><strong>ID:</strong> ${agent.id.substring(0, 8)}...</p>
                        <p><strong>Status:</strong> <span class="status ${agent.state.status}">${agent.state.status}</span></p>
                        <p><strong>Created:</strong> ${new Date(agent.created_at).toLocaleString()}</p>
                        <div>
                            <button class="btn btn-primary" onclick="editAgent('${agent.id}')">✏️ Edit</button>
                            <button class="btn btn-success" onclick="runAgent('${agent.id}')" 
                                    ${agent.state.status === 'running' ? 'disabled' : ''}>
                                ${agent.state.status === 'running' ? '⏳ Running...' : '▶️ Run'}
                            </button>
                            <button class="btn btn-danger" onclick="deleteAgent('${agent.id}')">🗑️ Delete</button>
                        </div>
                    </div>
                `).join('');
            }

            function showCreateModal() {
                document.getElementById('createModal').style.display = 'block';
            }

            function hideCreateModal() {
                document.getElementById('createModal').style.display = 'none';
                document.getElementById('createAgentForm').reset();
            }

            function showEditModal() {
                document.getElementById('editModal').style.display = 'block';
            }

            function hideEditModal() {
                document.getElementById('editModal').style.display = 'none';
                document.getElementById('editAgentForm').reset();
            }

            async function editAgent(agentId) {
                const agent = agents.find(a => a.id === agentId);
                if (!agent) return;

                document.getElementById('editAgentId').value = agent.id;
                document.getElementById('editAgentName').value = agent.config.name;
                document.getElementById('editAgentDescription').value = agent.config.description || '';
                document.getElementById('editAgentCode').value = agent.code || '';
                showEditModal();
            }

            async function runAgent(agentId) {
                try {
                    const response = await fetch('/api/agents/execute', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ agent_id: agentId })
                    });
                    
                    if (response.ok) {
                        alert('Agent execution started!');
                        refreshAgents();
                    } else {
                        const error = await response.json();
                        alert(`Error: ${error.detail}`);
                    }
                } catch (error) {
                    alert(`Error: ${error.message}`);
                }
            }

            async function deleteAgent(agentId) {
                if (!confirm('Are you sure you want to delete this agent?')) return;
                
                try {
                    const response = await fetch(`/api/agents/${agentId}`, {
                        method: 'DELETE'
                    });
                    
                    if (response.ok) {
                        refreshAgents();
                    } else {
                        const error = await response.json();
                        alert(`Error: ${error.detail}`);
                    }
                } catch (error) {
                    alert(`Error: ${error.message}`);
                }
            }

            // Form submission handlers
            document.getElementById('createAgentForm').addEventListener('submit', async function(e) {
                e.preventDefault();
                
                const data = {
                    name: document.getElementById('agentName').value,
                    description: document.getElementById('agentDescription').value,
                    agent_type: document.getElementById('agentType').value,
                    model: document.getElementById('agentModel').value || null
                };

                try {
                    const response = await fetch('/api/agents', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(data)
                    });

                    if (response.ok) {
                        hideCreateModal();
                        refreshAgents();
                    } else {
                        const error = await response.json();
                        alert(`Error: ${error.detail}`);
                    }
                } catch (error) {
                    alert(`Error: ${error.message}`);
                }
            });

            document.getElementById('editAgentForm').addEventListener('submit', async function(e) {
                e.preventDefault();
                
                const agentId = document.getElementById('editAgentId').value;
                const data = {
                    name: document.getElementById('editAgentName').value,
                    description: document.getElementById('editAgentDescription').value,
                    code: document.getElementById('editAgentCode').value
                };

                try {
                    const response = await fetch(`/api/agents/${agentId}`, {
                        method: 'PUT',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(data)
                    });

                    if (response.ok) {
                        hideEditModal();
                        refreshAgents();
                    } else {
                        const error = await response.json();
                        alert(`Error: ${error.detail}`);
                    }
                } catch (error) {
                    alert(`Error: ${error.message}`);
                }
            });

            // Auto-refresh agents every 5 seconds
            setInterval(refreshAgents, 5000);
        </script>
    </body>
    </html>
    """
    return html_content


@app.get("/api/project")
async def get_project():
    """Get current project information."""
    if not current_project:
        raise HTTPException(status_code=404, detail="No project loaded")
    
    return {
        "config": current_project.config.model_dump(),
        "path": current_project.path,
        "created_at": current_project.created_at.isoformat(),
        "updated_at": current_project.updated_at.isoformat(),
    }


@app.get("/api/agents")
async def list_agents():
    """List all agents in the current project."""
    if not current_project:
        raise HTTPException(status_code=404, detail="No project loaded")
    
    return [agent.model_dump() for agent in current_project.list_agents()]


@app.post("/api/agents")
async def create_agent(request: CreateAgentRequest):
    """Create a new agent."""
    if not current_project:
        raise HTTPException(status_code=404, detail="No project loaded")
    
    config = AgentConfig(
        name=request.name,
        description=request.description,
        agent_type=request.agent_type,
        model=request.model
    )
    
    agent = Agent(config=config)
    current_project.add_agent(agent)
    current_project.save()
    
    return agent.model_dump()


@app.get("/api/agents/{agent_id}")
async def get_agent(agent_id: str):
    """Get a specific agent."""
    if not current_project:
        raise HTTPException(status_code=404, detail="No project loaded")
    
    agent = current_project.get_agent(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    return agent.model_dump()


@app.put("/api/agents/{agent_id}")
async def update_agent(agent_id: str, request: UpdateAgentRequest):
    """Update an agent."""
    if not current_project:
        raise HTTPException(status_code=404, detail="No project loaded")
    
    agent = current_project.get_agent(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    # Update agent properties
    if request.name is not None:
        agent.config.name = request.name
    if request.description is not None:
        agent.config.description = request.description
    if request.code is not None:
        agent.code = request.code
    if request.parameters is not None:
        agent.config.parameters.update(request.parameters)
    
    agent.updated_at = agent.updated_at.__class__.now()
    current_project.save()
    
    return agent.model_dump()


@app.delete("/api/agents/{agent_id}")
async def delete_agent(agent_id: str):
    """Delete an agent."""
    if not current_project:
        raise HTTPException(status_code=404, detail="No project loaded")
    
    agent = current_project.get_agent(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    current_project.remove_agent(agent_id)
    current_project.save()
    
    return {"message": "Agent deleted successfully"}


@app.post("/api/agents/execute")
async def execute_agent(request: ExecuteAgentRequest, background_tasks: BackgroundTasks):
    """Execute an agent."""
    if not current_project:
        raise HTTPException(status_code=404, detail="No project loaded")
    
    agent = current_project.get_agent(request.agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    if agent.is_running():
        raise HTTPException(status_code=400, detail="Agent is already running")
    
    if not agent.code.strip():
        raise HTTPException(status_code=400, detail="Agent has no code to execute")
    
    try:
        execution_id = execution_env.execute_agent(agent)
        return {
            "message": "Agent execution started",
            "execution_id": execution_id,
            "agent_id": agent.id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/agents/{agent_id}/result")
async def get_execution_result(agent_id: str):
    """Get execution result for an agent."""
    result = execution_env.get_result(agent_id)
    if not result:
        raise HTTPException(status_code=404, detail="No execution result found")
    
    return result.model_dump()


@app.get("/api/status")
async def get_status():
    """Get system status."""
    running_agents = execution_env.list_running_agents()
    
    return {
        "status": "healthy",
        "project_loaded": current_project is not None,
        "running_agents": len(running_agents),
        "agent_ids": running_agents
    }


def start_server(host: str = "127.0.0.1", port: int = 8000, reload: bool = False):
    """Start the FastAPI server."""
    uvicorn.run(
        "agent_ide.web.server:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info"
    )


if __name__ == "__main__":
    start_server()
