from mcp.server.fastmcp import FastMCP, Context
from mcp.types import TextContent
from tavily import TavilyClient
import os
from dotenv import load_dotenv
import json

load_dotenv()

mcp = FastMCP(
    name="web_search_server",
    host="localhost",
    port=8000,
    log_level="INFO",
)

@mcp.tool(
    name="web_search",
    description="Perform a web search using the Tavily API."
)
async def web_search(query: str, ctx: Context) -> list[TextContent]:
    """
    Perform a web search using the Tavily API.

    Args:
        query: The search query string.
        ctx: Context for logging and progress reporting.

    Returns:
        List[TextContent]: JSON-encoded search results.
    """
    await ctx.info(f"Performing web search for query: {query}")
    try:
        tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
        await ctx.report_progress(50, 100)
        response = tavily_client.search(query)
        await ctx.report_progress(100, 100)

        # Format results as JSON
        results = [
            {
                "title": result["title"],
                "url": result["url"],
                "content": result["content"]
            } for result in response["results"]
        ]

        return [TextContent(
            type="text",
            text=json.dumps({
                "status": "success",
                "query": query,
                "results": results
            })
        )]
    except Exception as e:
        await ctx.error(f"Error performing web search: {str(e)}")
        return [TextContent(
            type="text",
            text=json.dumps({
                "status": "error",
                "message": str(e)
            })
        )]

if __name__ == "__main__":
    mcp.run(transport="sse")