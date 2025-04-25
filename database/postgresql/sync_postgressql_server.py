import os

import psycopg2
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from psycopg2.extras import RealDictCursor

# Load environment variables from .env file
load_dotenv()

# Initialize FastMCP server
mcp = FastMCP(
    name="postgres_server",
    port=8001,
    host="localhost",
    description="Access PostgresSQL databases by name and perform SQL operations"
)

# Database connection pool
db_connections = {}

@mcp.resource(name="postgres_server", description="Provides access to PostgresSQL database in localhost.", uri=os.getenv("DATABASE_URI"))
def postgres_server():
    """
    This resource establishes a connection to the specified PostgresSQL database.

    Returns:
        dict: Connection status information
    """
    return {"status": "ready", "message": "PostgresSQL connection resource is ready"}

@mcp.prompt(
    name="postgres_query_prompt",
    description="Prompt for executing a SQL query on the PostgresSQL database."
)
def postgres_query_prompt(db_name, query=None):
    """
    Provides guidance and context for executing SQL queries.

    Args:
        db_name: The name of the database to query        : Optional query to execute

    Returns:
        list: A list of chat messages for the AI to consider
        :param db_name:
        :param query:
    """
    # If query is provided, include it in the prompt
    query_context = f"\nQuery to execute: {query}" if query else ""

    return [
        {
            "role": "user",
            "content": f"""I need to work with the PostgresSQL database named '{db_name}'.{query_context}

Please help me with the following:

1. Connect to the database '{db_name}' using the connect_database tool
2. If I provided a query, execute it using the execute_query tool
3. If I didn't provide a query, help me explore the database by listing tables
4. Format the results in a clear, readable way
5. Provide brief explanations of what the data represents (if applicable)
6. Suggest possible follow-up queries based on the schema or results

Remember to use parameterized queries for any values that come from user input to prevent SQL injection.
"""
        }
    ]

@mcp.prompt(
    name="analyze_table_prompt",
    description="Prompt for analyzing the structure and content of a database table."
)
def analyze_table_prompt(db_name, table_name):
    """
    Provides a prompt for analyzing a specific database table.

    Args:
        db_name: The name of the database
        table_name: The name of the table to analyze

    Returns:
        list: A list of chat messages for the AI to consider
    """
    return [
        {
            "role": "user",
            "content": f"""I need to analyze the table '{table_name}' in the PostgresSQL database '{db_name}'.

Please help me with the following:

1. Connect to the database '{db_name}' using the connect_database tool
2. Describe the structure of the '{table_name}' table using the describe_table tool
3. Get a sample of the data (first 5-10 rows) using execute_query
4. Analyze the table structure and provide insights on:
   - Primary keys and relationships
   - Data types and constraints
   - Potential indexing opportunities
   - Any anomalies in the schema design
5. Summarize what this table appears to represent in the database
6. Suggest some useful queries I might want to run on this table

Format the results in a clear, readable way with appropriate markdown formatting.
"""
        }
    ]

@mcp.tool(name="connect_database", description="Connect to a specific PostgresSQL database.")
def connect_database(db_name):
    """
    Connects to a specific PostgresSQL database.

    Args:
        db_name (str): Name of the database to connect to

    Returns:
        dict: Connection status information
    """
    if not db_name:
        return {"error": "Database name is required"}

    try:
        # Get connection string from environment variables
        base_uri = os.getenv("DATABASE_URI")
        if not base_uri:
            return {"error": "DATABASE_URI environment variable not set"}

        # Create a connection to the specified database
        connection = psycopg2.connect(f"{base_uri}/{db_name}")

        # Store the connection in our pool
        db_connections[db_name] = connection

        return {"status": "success", "message": f"Connected to database '{db_name}'"}

    except Exception as e:
        return {"error": str(e)}

@mcp.tool(name="execute_query", description="Executes SQL queries on the connected PostgresSQL database.")
def execute_query(db_name, query, params=None):
    """
    Executes SQL queries on the specified database.

    Args:
        db_name (str): Name of the database to query         (str): SQL query to execute
        params (list, optional): Parameters for the query

    Returns:
        dict: Query results or error information
        :param db_name:
        :param params:
        :param query:
    """
    if not db_name:
        return {"error": "Database name is required"}

    if not query:
        return {"error": "Query is required"}

    if db_name not in db_connections:
        # Try to connect if not already connected
        connection_result = connect_database(db_name)
        if "error" in connection_result:
            return connection_result

    connection = db_connections[db_name]

    try:
        with connection.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(query, params or [])

            # For SELECT queries, return the results
            if query.strip().upper().startswith("SELECT"):
                results = cursor.fetchall()
                # Convert results to a list of dictionaries
                return {"results": [dict(row) for row in results]}

            # For other queries (INSERT, UPDATE, DELETE), commit and return row count
            else:
                connection.commit()
                return {"status": "success", "rows_affected": cursor.rowcount}

    except Exception as e:
        connection.rollback()  # Rollback in case of error
        return {"error": str(e)}

@mcp.tool(name="list_tables", description="Lists all tables in the specified database.")
def list_tables(db_name):
    """
    Lists all tables in the specified database.

    Args:
        db_name (str): Name of the database

    Returns:
        dict: List of tables or error information
    """
    if not db_name:
        return {"error": "Database name is required"}

    query = """
    SELECT table_name 
    FROM information_schema.tables 
    WHERE table_schema = 'public'
    ORDER BY table_name;
    """

    return execute_query(db_name, query)

@mcp.tool(name="describe_table", description="Describes the structure of a specific table.")
def describe_table(db_name, table_name):
    """
    Describes the structure of a specific table.

    Args:
        db_name (str): Name of the database
        table_name (str): Name of the table to describe

    Returns:
        dict: Table structure information or error
    """
    if not db_name or not table_name:
        return {"error": "Database name and table name are required"}

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
        table_name = %s
    ORDER BY 
        ordinal_position;
    """

    return execute_query(db_name, query, [table_name])

@mcp.tool(name="close_connection", description="Closes the connection to the specified database.")
def close_connection(db_name):
    """
    Closes the connection to the specified database.

    Args:
        db_name (str): Name of the database connection to close

    Returns:
        dict: Operation status
    """
    if not db_name:
        return {"error": "Database name is required"}

    if db_name not in db_connections:
        return {"error": f"No active connection to database '{db_name}'"}

    try:
        db_connections[db_name].close()
        del db_connections[db_name]
        return {"status": "success", "message": f"Connection to '{db_name}' closed"}

    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    print(f"Starting MCP PostgresSQL server on http://localhost:5000")
    mcp.run(transport="sse")