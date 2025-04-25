# mcp-server-suite

**mcp-server-suite** is a comprehensive collection of MCP (Model Context Protocol) servers designed to be the "HuggingFace for automation". Our vision is to create a community-driven platform where developers can both use pre-built servers and contribute their own, making automation and AI-powered workflows accessible to everyone.

## Features

- **Model Context Protocol** core for flexible context management
- Modular architecture for adding new tools and services
- Growing collection of ready-to-use MCP servers
- Easy integration with APIs and external systems
- Environment variable support via `.env` files
- Community-driven expansion and customization

## Available Servers

### Core Servers
- **Web Search Server**: Integrate web search capabilities using Tavily API
- **File Explorer Server**: Safe file system operations with progress reporting
- **PostgreSQL Server**: Both sync and async database operations
- More coming soon!

## Getting Started

### Prerequisites

- Python 3.13 or higher
- [UV](https://github.com/astral-sh/uv) - Fast Python package installer and resolver

### Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/Dadiya-Harsh/mcp-server-suite.git
    cd mcp-server-suite
    ```

2. Install UV if you haven't already:
    ```sh
    pip install uv
    ```

3. Create and activate a virtual environment:
    ```sh
    uv venv
    # On Windows:
    .venv\Scripts\activate
    # On Unix/macOS:
    source .venv/bin/activate
    ```

4. Install dependencies using UV:
    ```sh
    uv pip install -e .
    ```

5. Set up your environment variables in a `.env` file:
    ```sh
    # Required for web search server
    TAVILY_API_KEY=your_api_key_here
    
    # Required for PostgreSQL server
    DATABASE_URI=postgresql://user:password@localhost:5432
    
    # Required for file explorer server
    ALLOWED_BASE_PATH=E:\Your\Safe\Path
    ```

### Running the Servers

Each server can be run independently:

```sh
# Web Search Server
python web_search/web_search_sse.py

# File Explorer Server
python file_explore/basic_file_server.py

# PostgreSQL Server (async)
python database/postgresql/async_postgresql_server.py
```

## Using the Platform

### As a User

1. Install the package:
    ```sh
    uv pip install mcp-server-suite
    ```

2. Import and use any server:
    ```python
    from mcp_server_suite.web_search import web_search_server
    from mcp_server_suite.database import async_postgresql_server
    ```

## 📌 Planned MCP Servers

### For AI/ML Engineers
- **Dataset Explorer MCP**: Browse/filter datasets from HuggingFace, Kaggle, etc.
- **Model Evaluation MCP**: Compare model performance across tasks or datasets.
- **Experiment Tracker MCP**: Visualize experiment logs and metrics from MLflow/W&B.
- **Training Job Manager MCP**: Start, monitor, and manage training jobs locally or on the cloud.
- **Paper Summary MCP**: Summarize and interact with AI papers via arXiv or Semantic Scholar.

### For Software Engineers
- **Codebase Q&A MCP**: Ask natural language questions about source code.
- **Issue Debugger MCP**: Summarize GitHub/GitLab issues and provide solutions.
- **CI/CD Monitor MCP**: Check pipeline status and deployment history.
- **API Inspector MCP**: Query and understand OpenAPI/Swagger docs via natural prompts.

### For Non-Technical Users
- **Health Assistant MCP**: Get simple, symptom-based answers and medication guidance.
- **Finance Tracker MCP**: Analyze and summarize personal spending from CSV/PDF exports.
- **Smart Task Planner MCP**: Convert vague goals into structured, scheduled learning/task plans.
- **FAQ Assistant MCP**: Answer questions based on uploaded files or organization docs.

## Vision & Roadmap

We're building the "HuggingFace for automation" with these goals:

### Immediate Goals
- Expand server collection with most-requested functionalities
- Build a central registry for discovering and sharing servers
- Create comprehensive documentation and examples
- Implement authentication and security features

### Community Features (Coming Soon)
- Server discovery and search
- Easy server deployment and sharing
- Version control and dependency management
- Usage analytics and monitoring
- Community ratings and reviews

### Server Categories

#### Data & Analytics
- Database connectors (MySQL, MongoDB, etc.)
- Analytics engines
- Data transformation tools

#### AI/ML Tools
- Model deployment servers
- Training job managers
- Dataset handlers
- Experiment trackers

#### DevOps & Infrastructure
- CI/CD integrators
- Cloud service managers
- Monitoring tools
- Log analyzers

#### Application Integration
- Email/SMS servers
- Payment processors
- Authentication services
- File storage connectors

## Contributing

Join us in building the future of automation! Contributions are welcome:

1. Fork the repository
2. Create your feature branch
3. Add your server or improvements
4. Submit a pull request

See our [Contributing Guidelines](CONTRIBUTING.md) for more details.

## Support

- [Documentation](docs/)
- [Discord Community](https://discord.gg/your-server)
- [GitHub Issues](https://github.com/Dadiya-Harsh/mcp-server-suite/issues)

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---