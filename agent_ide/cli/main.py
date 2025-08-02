"""Main CLI interface for Agent IDE."""

import click
import os
import sys
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich import print as rprint

from ..core.project import Project, ProjectConfig
from ..core.agent import Agent, AgentConfig
from ..core.execution import ExecutionEnvironment
from ..web.server import start_server

console = Console()


@click.group()
@click.version_option(version="0.1.0")
def main():
    """Agent IDE - An intelligent development environment for AI agents."""
    pass


@main.command()
@click.argument('path', type=click.Path())
@click.option('--name', '-n', help='Project name')
@click.option('--description', '-d', help='Project description')
@click.option('--author', '-a', help='Project author')
def init(path: str, name: str, description: str, author: str):
    """Initialize a new agent project."""
    project_path = Path(path).resolve()
    
    if not name:
        name = project_path.name
    
    config = ProjectConfig(
        name=name,
        description=description or f"Agent project: {name}",
        author=author
    )
    
    try:
        project = Project.create(str(project_path), config)
        console.print(f"✅ Created new project: {name}", style="green")
        console.print(f"📁 Location: {project_path}")
        
        # Create basic directory structure
        (project_path / "agents").mkdir(exist_ok=True)
        (project_path / "templates").mkdir(exist_ok=True)
        (project_path / "docs").mkdir(exist_ok=True)
        
        console.print("\n📋 Next steps:")
        console.print("1. cd into your project directory")
        console.print("2. Run 'agent-ide create-agent' to create your first agent")
        console.print("3. Run 'agent-ide serve' to start the web interface")
        
    except Exception as e:
        console.print(f"❌ Error creating project: {e}", style="red")
        sys.exit(1)


@main.command()
@click.option('--name', '-n', required=True, help='Agent name')
@click.option('--type', '-t', default='general', help='Agent type')
@click.option('--description', '-d', help='Agent description')
@click.option('--model', '-m', help='AI model to use')
def create_agent(name: str, type: str, description: str, model: str):
    """Create a new agent."""
    try:
        # Find project
        project = Project.load('.')
        
        # Create agent
        config = AgentConfig(
            name=name,
            agent_type=type,
            description=description or f"Agent: {name}",
            model=model
        )
        
        agent = Agent(config=config)
        project.add_agent(agent)
        project.save()
        
        console.print(f"✅ Created agent: {name}", style="green")
        console.print(f"🆔 Agent ID: {agent.id}")
        console.print(f"📝 Type: {type}")
        
    except FileNotFoundError:
        console.print("❌ No project found. Run 'agent-ide init' first.", style="red")
        sys.exit(1)
    except Exception as e:
        console.print(f"❌ Error creating agent: {e}", style="red")
        sys.exit(1)


@main.command()
def list_agents():
    """List all agents in the current project."""
    try:
        project = Project.load('.')
        agents = project.list_agents()
        
        if not agents:
            console.print("No agents found in this project.")
            return
        
        table = Table(title="Project Agents")
        table.add_column("Name", style="cyan")
        table.add_column("ID", style="magenta")
        table.add_column("Type", style="green")
        table.add_column("Status", style="yellow")
        table.add_column("Created", style="blue")
        
        for agent in agents:
            table.add_row(
                agent.config.name,
                agent.id[:8] + "...",
                agent.config.agent_type,
                agent.state.status,
                agent.created_at.strftime("%Y-%m-%d %H:%M")
            )
        
        console.print(table)
        
    except FileNotFoundError:
        console.print("❌ No project found. Run 'agent-ide init' first.", style="red")
        sys.exit(1)
    except Exception as e:
        console.print(f"❌ Error listing agents: {e}", style="red")
        sys.exit(1)


@main.command()
@click.argument('agent_id')
def run_agent(agent_id: str):
    """Run an agent."""
    try:
        project = Project.load('.')
        agent = project.get_agent(agent_id)
        
        if not agent:
            console.print(f"❌ Agent not found: {agent_id}", style="red")
            sys.exit(1)
        
        if not agent.code.strip():
            console.print(f"❌ Agent has no code to execute", style="red")
            sys.exit(1)
        
        console.print(f"🚀 Running agent: {agent.config.name}")
        
        # Create execution environment
        env = ExecutionEnvironment()
        
        def on_complete(agent, result):
            if result.success:
                console.print(f"✅ Agent completed successfully", style="green")
                console.print(f"📊 Duration: {result.duration:.2f}s")
                console.print(f"🔄 Iterations: {result.iterations}")
                if result.output:
                    console.print(f"📤 Output:\n{result.output}")
            else:
                console.print(f"❌ Agent failed: {result.error}", style="red")
        
        # Start execution
        env.execute_agent(agent, callback=on_complete)
        
        # Wait for completion
        import time
        while env.is_running(agent.id):
            time.sleep(0.5)
            console.print(".", end="")
        
        console.print()  # New line
        
    except FileNotFoundError:
        console.print("❌ No project found. Run 'agent-ide init' first.", style="red")
        sys.exit(1)
    except Exception as e:
        console.print(f"❌ Error running agent: {e}", style="red")
        sys.exit(1)


@main.command()
@click.option('--host', default='127.0.0.1', help='Host to bind to')
@click.option('--port', default=8000, help='Port to bind to')
@click.option('--reload', is_flag=True, help='Enable auto-reload')
def serve(host: str, port: int, reload: bool):
    """Start the web server."""
    try:
        # Check if we're in a project directory
        project = Project.load('.')
        console.print(f"🌐 Starting Agent IDE server...")
        console.print(f"📁 Project: {project.config.name}")
        console.print(f"🔗 URL: http://{host}:{port}")
        
        start_server(host=host, port=port, reload=reload)
        
    except FileNotFoundError:
        console.print("❌ No project found. Run 'agent-ide init' first.", style="red")
        sys.exit(1)
    except Exception as e:
        console.print(f"❌ Error starting server: {e}", style="red")
        sys.exit(1)


@main.command()
def docs():
    """Open documentation."""
    import webbrowser
    docs_url = "https://github.com/infinit3labs/agent_ide/blob/main/README.md"
    webbrowser.open(docs_url)
    console.print(f"📖 Opening documentation: {docs_url}")


if __name__ == '__main__':
    main()
