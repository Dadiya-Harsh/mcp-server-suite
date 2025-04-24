from mcp.server.fastmcp import FastMCP
from tavily import TavilyClient
import os
from dotenv import load_dotenv

load_dotenv()

mcp = FastMCP(name = "Web Search", host = "localhost", port = 8000)


@mcp.tool()
async def web_search(query: str) -> dict:
    """Perform a web search using the Tavily API.

    Args:
        query: The search query string.

    Returns:
        A list of URLs from the search results.
    """
    # Simulate a web search using Tavily API
    tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

    response = tavily_client.search(query)
    for result in response['results']:
        print(result['title'])
        print(result['content'])

    return response

if __name__ == "__main__":
    mcp.run(transport="stdio")
