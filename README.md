# Agent IDE

An intelligent development environment for creating, managing, and executing AI agents.

## Overview

Agent IDE provides a comprehensive platform for developing AI agents with features including:

- **Agent Creation**: Visual and code-based agent development tools
- **Agent Management**: Organize and version your agents
- **Execution Environment**: Safe and monitored agent execution
- **Debugging Tools**: Debug and trace agent behavior
- **Integration**: Connect with various AI services and APIs

## Installation

```bash
pip install -e .
```

## Quick Start

1. Initialize a new agent project:
```bash
agent-ide init my-agent-project
```

2. Create a new agent:
```bash
agent-ide create-agent --name "MyAgent" --type "chat"
```

3. Run the IDE:
```bash
agent-ide serve
```

4. Open your browser to `http://localhost:8000` to access the web interface.

## Features

- **Web-based IDE**: Modern web interface for agent development
- **CLI Tools**: Command-line tools for automation and scripting
- **Agent Templates**: Pre-built templates for common agent types
- **Live Monitoring**: Real-time agent execution monitoring
- **Plugin System**: Extensible architecture for custom functionality

## Documentation

For detailed documentation, visit the [docs](./docs) directory or run:

```bash
agent-ide docs
```

## Development

To set up for development:

```bash
pip install -e .[dev]
pytest
```

## License

MIT License - see LICENSE file for details.