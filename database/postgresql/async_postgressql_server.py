import os
import json
from typing import List, Optional
import asyncio
import asyncpg
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP, Context
from mcp.types import TextContent
from pydantic import BaseModel, Field

# Load environment variables
load_dotenv()

# Create FastMCP instance
mcp = FastMCP(
    name="postgres_server",
    port=8002,
    host="localhost",
    log_level="INFO",
    description="Access PostgreSQL databases by name and perform SQL operations"
)

# Global connection pool and event loop
db_pool: Optional[asyncpg.Pool] = None
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

# Database connection configuration
DB_CONFIG = {
    "user": os.getenv("POSTGRES_USER", "postgres"),
    "password": os.getenv("POSTGRES_PASSWORD", ""),
    "host": os.getenv("POSTGRES_HOST", "localhost"),
    "port": int(os.getenv("POSTGRES_PORT", 5432))
}

class SQLQuery(BaseModel):
    query: str = Field(..., description="The SQL query to execute")
    params: Optional[List] = Field(None, description="Parameters for the query")

class TableDescription(BaseModel):
    table_name: str = Field(..., description="The name of the table to describe")

async def init_db_pool(db_name: str = None):
    """Initialize the asyncpg connection pool for the specified database."""
    global db_pool

    # Close existing pool if it exists
    if db_pool is not None:
        await db_pool.close()
        db_pool = None

    # Create configuration with database name if provided
    config = DB_CONFIG.copy()
    if db_name:
        config["database"] = db_name
    else:
        config["database"] = os.getenv("POSTGRES_DB", "postgres")

    # Create new connection pool
    try:
        db_pool = await asyncpg.create_pool(**config)
        return True
    except Exception as e:
        print(f"Error initializing pool: {str(e)}")
        return False

@mcp.resource(
    name="postgres_server",
    description="Provides access to PostgreSQL database in localhost.",
    uri=os.getenv("DATABASE_URI", "resource://postgres-server"),
    mime_type="application/json"
)
async def postgres_server() -> str:
    """
    Provides metadata about the PostgreSQL server resource.

    Returns:
        str: JSON-encoded connection status information
    """
    return json.dumps({"status": "ready", "message": "PostgreSQL connection resource is ready"})

@mcp.prompt(
    name="postgres_query_prompt",
    description="Prompt for executing SQL queries on the PostgreSQL database."
)
def postgres_query_prompt() -> List[dict]:
    """
    Provides guidance for executing SQL queries.

    Returns:
        List[dict]: A list of chat messages for the AI to consider
    """
    return [
        {
            "role": "system",
            "content": """You are a PostgreSQL database assistant. Use the following tools to interact with the database:
- connect_database: Connect to a specific database by name
- execute_query: Execute an SQL query with optional parameters
- list_tables: List all tables in the database
- describe_table: Describe the structure of a specific table
- close_connection: Close the database connection

For any query:
1. Connect to the specified database if not already connected
2. Execute the query or list tables if no query is provided
3. Use parameterized queries for user inputs to prevent SQL injection
4. Format results clearly in JSON
5. Suggest follow-up queries based on results
"""
        },
        {
            "role": "user",
            "content": "I need to perform SQL operations on a PostgreSQL database. Please help with queries or database exploration."
        }
    ]

@mcp.prompt(
    name="analyze_table_prompt",
    description="Prompt for analyzing the structure and content of a database table."
)
def analyze_table_prompt() -> List[dict]:
    """
    Provides a prompt for analyzing a database table.

    Returns:
        List[dict]: A list of chat messages for the AI to consider
    """
    return [
        {
            "role": "system",
            "content": """You are a PostgreSQL database assistant. Use the following tools to analyze a table:
- connect_database: Connect to the database
- describe_table: Get the table's structure
- execute_query: Sample data or run analysis queries
- list_tables: List available tables if needed

For table analysis:
1. Connect to the specified database
2. Describe the table structure
3. Sample 5-10 rows of data
4. Analyze primary keys, data types, constraints, and indexing opportunities
5. Summarize the table's purpose
6. Suggest useful queries
"""
        },
        {
            "role": "user",
            "content": "I need to analyze a specific table in a PostgreSQL database. Please describe its structure and provide insights."
        }
    ]

@mcp.tool(
    name="connect_database",
    description="Connect to a specific PostgreSQL database."
)
async def connect_database(db_name: str, ctx: Context) -> List[TextContent]:
    """
    Connects to a specific PostgreSQL database using the global pool.

    Args:
        db_name: Name of the database to connect to
        ctx: Context for logging and progress reporting

    Returns:
        List[TextContent]: JSON-encoded connection status
    """
    await ctx.info(f"Connecting to database: {db_name}")
    if not db_name:
        await ctx.error("Database name is required")
        return [TextContent(type="text", text=json.dumps({"status": "error", "message": "Database name is required"}))]

    try:
        # Create a new pool with the specified database
        success = await init_db_pool(db_name)
        if success:
            await ctx.report_progress(100, 100)
            return [TextContent(type="text", text=json.dumps({"status": "success", "message": f"Connected to database '{db_name}'"}))]
        else:
            await ctx.error(f"Failed to connect to database '{db_name}'")
            return [TextContent(type="text", text=json.dumps({"status": "error", "message": f"Failed to connect to database '{db_name}'"}))
                    ]
    except Exception as e:
        await ctx.error(f"Error connecting to database: {str(e)}")
        return [TextContent(type="text", text=json.dumps({"status": "error", "message": str(e)}))]

@mcp.tool(
    name="execute_query",
    description="Execute SQL queries on the connected PostgreSQL database."
)
async def execute_query(query: SQLQuery, ctx: Context) -> List[TextContent]:
    """
    Executes SQL queries on the specified database.

    Args:
        query: SQLQuery model with query string and optional parameters
        ctx: Context for logging and progress reporting

    Returns:
        List[TextContent]: JSON-encoded query results or error
    """
    await ctx.info(f"Executing query: {query.query}")
    global db_pool

    if db_pool is None:
        await ctx.error("No database connection established")
        return [TextContent(type="text", text=json.dumps({"status": "error", "message": "No database connection established. Please connect to a database first."}))]

    try:
        async with db_pool.acquire() as connection:
            await ctx.report_progress(50, 100)
            if query.query.strip().upper().startswith("SELECT"):
                results = await connection.fetch(query.query, *(query.params or []))
                await ctx.report_progress(100, 100)
                return [TextContent(
                    type="text",
                    text=json.dumps({
                        "status": "success",
                        "results": [dict(record) for record in results]
                    }, default=str)  # Added default=str to handle non-serializable types
                )]
            else:
                result = await connection.execute(query.query, *(query.params or []))
                await ctx.report_progress(100, 100)
                rows_affected = int(result.split()[-1]) if result and (result.startswith("INSERT") or result.startswith("UPDATE") or result.startswith("DELETE")) else 0
                return [TextContent(
                    type="text",
                    text=json.dumps({
                        "status": "success",
                        "command": result,
                        "rows_affected": rows_affected
                    })
                )]
    except Exception as e:
        await ctx.error(f"Error executing query: {str(e)}")
        return [TextContent(type="text", text=json.dumps({"status": "error", "message": str(e)}))]

@mcp.tool(
    name="list_tables",
    description="List all tables in the specified database."
)
async def list_tables(ctx: Context) -> List[TextContent]:
    """
    Lists all tables in the current database.

    Args:
        ctx: Context for logging and progress reporting

    Returns:
        List[TextContent]: JSON-encoded list of tables or error
    """
    await ctx.info("Listing tables in current database")
    global db_pool

    if db_pool is None:
        await ctx.error("No database connection established")
        return [TextContent(type="text", text=json.dumps({"status": "error", "message": "No database connection established. Please connect to a database first."}))]

    query = """
    SELECT table_name 
    FROM information_schema.tables 
    WHERE table_schema = 'public'
    ORDER BY table_name;
    """
    return await execute_query(SQLQuery(query=query, params=None), ctx)

@mcp.tool(
    name="describe_table",
    description="Describe the structure of a specific table."
)
async def describe_table(table: TableDescription, ctx: Context) -> List[TextContent]:
    """
    Describes the structure of a specific table.

    Args:
        table: TableDescription model with table name
        ctx: Context for logging and progress reporting

    Returns:
        List[TextContent]: JSON-encoded table structure or error
    """
    await ctx.info(f"Describing table {table.table_name}")
    global db_pool

    if db_pool is None:
        await ctx.error("No database connection established")
        return [TextContent(type="text", text=json.dumps({"status": "error", "message": "No database connection established. Please connect to a database first."}))]

    query = """
    SELECT 
        column_name, 
        data_type, 
        is_nullable,
        column_default
    FROM 
        information_schema.columns
    WHERE 
        table_schema = 'public' AND 
        table_name = $1
    ORDER BY 
        ordinal_position;
    """
    return await execute_query(SQLQuery(query=query, params=[table.table_name]), ctx)

@mcp.tool(
    name="close_connection",
    description="Close the connection to the database."
)
async def close_connection(ctx: Context) -> List[TextContent]:
    """
    Closes the connection to the database.

    Args:
        ctx: Context for logging and progress reporting

    Returns:
        List[TextContent]: JSON-encoded operation status
    """
    await ctx.info("Closing database connection")
    global db_pool

    if db_pool is None:
        await ctx.warning("No active database connection to close")
        return [TextContent(type="text", text=json.dumps({"status": "warning", "message": "No active database connection to close"}))]

    try:
        # Use the current event loop to close the connection
        loop = asyncio.get_running_loop()
        await loop.create_task(db_pool.close())
        db_pool = None
        await ctx.report_progress(100, 100)
        return [TextContent(type="text", text=json.dumps({"status": "success", "message": "Database connection closed successfully"}))]
    except Exception as e:
        await ctx.error(f"Error closing connection: {str(e)}")
        return [TextContent(type="text", text=json.dumps({"status": "error", "message": str(e)}))]

async def cleanup():
    """Cleanup function to properly close the database pool when the application exits."""
    global db_pool
    if db_pool is not None:
        await db_pool.close()
        print("Database connection pool closed during cleanup")

if __name__ == "__main__":
    # Register cleanup function
    loop.run_until_complete(init_db_pool())

    # Add shutdown event handlers
    try:
        import atexit
        atexit.register(lambda: loop.run_until_complete(cleanup()))
    except Exception as e:
        print(f"Warning: Could not register cleanup handler: {e}")

    print(f"Starting MCP PostgreSQL server on http://localhost:8001/sse")
    mcp.run(transport="sse")