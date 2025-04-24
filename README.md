# mcp-server-suite

**mcp-server-suite** is a customizable MCP (Model Context Protocol) server designed as a foundation for all your future automation, integration, and AI-powered workflows. Built for extensibility, it enables you to create, connect, and manage custom tools and services in a modular way.

## Features

- **Model Context Protocol** core for flexible context management
- Modular architecture for adding new tools and services
- Easy integration with APIs and external systems
- Environment variable support via `.env` files
- Designed for ongoing expansion and customization

## Getting Started

### Prerequisites

- Python 3.13 or higher
- [pip](https://pip.pypa.io/en/stable/)

### Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/Dadiya-Harsh/mcp-server-suite.git
    cd mcp-server-suite
    ```

2. Install dependencies:
    ```sh
    pip install -r requirements.txt
    ```
    Or, if using `pyproject.toml`:
    ```sh
    pip install .
    ```

3. Set up your environment variables (e.g., `TAVILY_API_KEY`) in a `.env` file.

### Running the Server

To start the main server:
```sh
python main.py
```

To run a specific tool server (e.g., web search):
```sh
python web_search_tavily.py
```

## Adding New Tools

Add new tools by creating Python modules and registering them with the MCP server. See [`web_search_tavily.py`](web_search_tavily.py) for an example. The platform is designed to support any future tool or integration you need.

---

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

---

## Roadmap

- Add more built-in tools (file management, scheduling, notifications, etc.)
- Expand documentation and usage examples
- Add authentication and security features
- Support more transports and deployment options
- Implement the full suite of planned MCP tools (see above)

## Contributing

Contributions are welcome! Please open issues or pull requests for suggestions, bug fixes, or new features.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.


---

