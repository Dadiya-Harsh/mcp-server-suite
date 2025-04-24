# my-mcp-servers

**my-mcp-servers** is a customizable MCP (Modular Command Platform) server designed to serve as a foundation for a wide range of automation, integration, and AI-powered tasks. This project aims to provide a flexible, extensible platform for building and running custom tools and services.

## Features

- Modular architecture for adding new tools and services
- Easy integration with APIs (e.g., Tavily web search)
- Environment variable support via `.env` files
- Designed for future expansion and customization

## Getting Started

### Prerequisites

- Python 3.13 or higher
- [pip](https://pip.pypa.io/en/stable/)

### Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/yourusername/my-mcp-servers.git
    cd my-mcp-servers
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

You can add new tools by creating Python modules and registering them with the MCP server. See [`web_search_tavily.py`](web_search_tavily.py) for an example.

## Roadmap

- Add more built-in tools (e.g., file management, scheduling, notifications)
- Improve documentation and usage examples
- Add authentication and security features
- Support for more transports and deployment options

## Contributing

Contributions are welcome! Please open issues or pull requests for suggestions, bug fixes, or new features.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.