import json
import os
from pathlib import Path
from typing import Dict, List, Optional

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP, Context
from mcp.server.fastmcp.exceptions import ResourceError
from mcp.types import TextContent
from pydantic import BaseModel, Field

# Load environment variables from .env file
load_dotenv()

# Configuration
ALLOWED_BASE_PATH = os.getenv("ALLOWED_BASE_PATH", "E:\\Test")  # Default to E:\Test if not set
# Normalize path for cross-platform compatibility
ALLOWED_BASE_PATH = str(Path(ALLOWED_BASE_PATH).resolve())
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB limit for file operations

mcp = FastMCP(
    name="folder_server",
    host="localhost",
    port=8002,
    log_level="INFO",
)

# Input models for validation
class FileOperation(BaseModel):
    path: str = Field(..., description="Relative path to the file")
    content: Optional[str] = Field(None, description="Content to write to the file")

class FolderAnalysis(BaseModel):
    path: str = Field(..., description="Relative path to the folder")

# Security check for file paths
def sanitize_path(path: str) -> str:
    """Ensure path is safe and within allowed directory."""
    # Normalize input path and remove leading slashes
    full_path = os.path.abspath(os.path.join(ALLOWED_BASE_PATH, path.lstrip("/").lstrip("\\")))
    if not full_path.startswith(ALLOWED_BASE_PATH):
        raise ValueError("Access outside allowed directory")
    return full_path

@mcp.resource(
    name="folder_server",
    description="Provides access to a folder on the server.",
    uri="resource://folder-server",
    mime_type="application/json"
)
def folder_server() -> str:
    """
    Provides metadata about the folder server resource.

    Returns:
        str: JSON-encoded information about the folder server resource
    """
    return json.dumps({
        "status": "ready",
        "message": "Folder server resource is ready",
        "base_path": ALLOWED_BASE_PATH
    })

@mcp.tool(
    name="file_read",
    description="Read content from a specified file in the allowed folder."
)
async def file_read(op: FileOperation, ctx: Context) -> List[TextContent]:
    """
    Read content from a specified file.

    Args:
        op: FileOperation model containing the file path
        ctx: Context for logging and progress reporting

    Returns:
        List[TextContent]: File content and status
    """
    await ctx.info(f"Attempting to read file: {op.path}")
    try:
        safe_path = sanitize_path(op.path)
        if not os.path.exists(safe_path):
            await ctx.error(f"File not found: {op.path}")
            return [TextContent(type="text", text=json.dumps({"status": "error", "message": "File not found"}))]
        if not os.path.isfile(safe_path):
            await ctx.error(f"Path is not a file: {op.path}")
            return [TextContent(type="text", text=json.dumps({"status": "error", "message": "Path is not a file"}))]

        file_size = os.path.getsize(safe_path)
        if file_size > MAX_FILE_SIZE:
            await ctx.error(f"File too large: {file_size} bytes")
            return [TextContent(type="text", text=json.dumps({"status": "error", "message": "File too large"}))]

        await ctx.report_progress(50, 100)
        with open(safe_path, 'r', encoding='utf-8') as f:
            content = f.read()
        await ctx.report_progress(100, 100)

        return [TextContent(type="text", text=json.dumps({
            "status": "success",
            "path": op.path,
            "content": content
        }))]
    except Exception as e:
        await ctx.error(f"Error reading file {op.path}: {str(e)}")
        return [TextContent(type="text", text=json.dumps({"status": "error", "message": str(e)}))]

@mcp.tool(
    name="file_write",
    description="Write content to a specified file in the allowed folder."
)
async def file_write(op: FileOperation, ctx: Context) -> List[TextContent]:
    """
    Write content to a specified file.

    Args:
        op: FileOperation model containing path and content
        ctx: Context for logging and progress reporting

    Returns:
        List[TextContent]: Operation status
    """
    await ctx.info(f"Attempting to write file: {op.path}")
    try:
        if not op.content:
            await ctx.error("Content is required for file write")
            return [TextContent(type="text", text=json.dumps({"status": "error", "message": "Content is required"}))]

        safe_path = sanitize_path(op.path)
        os.makedirs(os.path.dirname(safe_path), exist_ok=True)

        await ctx.report_progress(50, 100)
        with open(safe_path, 'w', encoding='utf-8') as f:
            f.write(op.content)
        await ctx.report_progress(100, 100)

        return [TextContent(type="text", text=json.dumps({
            "status": "success",
            "path": op.path,
            "message": "File written successfully"
        }))]
    except Exception as e:
        await ctx.error(f"Error writing file {op.path}: {str(e)}")
        return [TextContent(type="text", text=json.dumps({"status": "error", "message": str(e)}))]

@mcp.tool(
    name="file_delete",
    description="Delete a specified file in the allowed folder."
)
async def file_delete(op: FileOperation, ctx: Context) -> List[TextContent]:
    """
    Delete a specified file.

    Args:
        op: FileOperation model containing the file path
        ctx: Context for logging and progress reporting

    Returns:
        List[TextContent]: Operation status
    """
    await ctx.info(f"Attempting to delete file: {op.path}")
    try:
        safe_path = sanitize_path(op.path)
        if not os.path.exists(safe_path):
            await ctx.error(f"File not found: {op.path}")
            return [TextContent(type="text", text=json.dumps({"status": "error", "message": "File not found"}))]
        if not os.path.isfile(safe_path):
            await ctx.error(f"Path is not a file: {op.path}")
            return [TextContent(type="text", text=json.dumps({"status": "error", "message": "Path is not a file"}))]

        await ctx.report_progress(50, 100)
        os.remove(safe_path)
        await ctx.report_progress(100, 100)

        return [TextContent(type="text", text=json.dumps({
            "status": "success",
            "path": op.path,
            "message": "File deleted successfully"
        }))]
    except Exception as e:
        await ctx.error(f"Error deleting file {op.path}: {str(e)}")
        return [TextContent(type="text", text=json.dumps({"status": "error", "message": str(e)}))]

@mcp.tool(
    name="folder_analysis",
    description="Analyze a folder to provide context about its contents."
)
async def folder_analysis(folder: FolderAnalysis, ctx: Context) -> List[TextContent]:
    """
    Analyze a folder's contents.

    Args:
        folder: FolderAnalysis model containing the folder path
        ctx: Context for logging and progress reporting

    Returns:
        List[TextContent]: Folder analysis results
    """
    await ctx.info(f"Analyzing folder: {folder.path}")
    try:
        safe_path = sanitize_path(folder.path)
        if not os.path.exists(safe_path):
            await ctx.error(f"Folder not found: {folder.path}")
            return [TextContent(type="text", text=json.dumps({"status": "error", "message": "Folder not found"}))]
        if not os.path.isdir(safe_path):
            await ctx.error(f"Path is not a directory: {folder.path}")
            return [TextContent(type="text", text=json.dumps({"status": "error", "message": "Path is not a directory"}))]

        files = []
        total_size = 0
        file_count = 0
        await ctx.report_progress(0, 100)

        for root, _, filenames in os.walk(safe_path):
            for i, filename in enumerate(filenames):
                file_path = os.path.join(root, filename)
                file_size = os.path.getsize(file_path)
                total_size += file_size
                file_count += 1
                files.append({
                    "name": filename,
                    "path": os.path.relpath(file_path, ALLOWED_BASE_PATH),
                    "size": file_size,
                    "modified": os.path.getmtime(file_path)
                })
                # Report progress every 10 files
                if (i + 1) % 10 == 0:
                    await ctx.report_progress(min(90, (i + 1) * 90 // len(filenames)), 100)

        await ctx.report_progress(100, 100)

        return [TextContent(type="text", text=json.dumps({
            "status": "success",
            "path": folder.path,
            "file_count": file_count,
            "total_size": total_size,
            "files": files[:50],  # Limit to 50 files for brevity
            "message": "Folder analysis completed"
        }))]
    except Exception as e:
        await ctx.error(f"Error analyzing folder {folder.path}: {str(e)}")
        return [TextContent(type="text", text=json.dumps({"status": "error", "message": str(e)}))]

@mcp.prompt(
    name="folder_server_prompt",
    description="Prompt for performing operations in the folder server."
)
def folder_server_prompt() -> List[Dict]:
    """
    Provides guidance and context for performing operations in the folder server.

    Returns:
        List[Dict]: A list of chat messages for the AI to consider
    """
    return [
        {
            "role": "system",
            "content": f"You are a folder server assistant. All operations must be performed within {ALLOWED_BASE_PATH}. "
                       f"Available tools: file_read, file_write, file_delete, folder_analysis. "
                       f"Use these tools to perform file and folder operations safely."
        },
        {
            "role": "user",
            "content": "I need to perform operations in the folder server. Please help me with file operations or folder analysis."
        }
    ]

@mcp.resource(
    name="folder_content",
    description="Read content of a specific file as a resource.",
    uri="resource://folder-content/{path}",
    mime_type="text/plain"
)
async def folder_content(path: str) -> str:
    """
    Read content of a specific file as a resource.

    Args:
        path: Relative path to the file

    Returns:
        str: File content
    """
    ctx = Context(fastmcp=mcp)  # Create context manually for logging
    await ctx.info(f"Reading file content as resource: {path}")
    try:
        safe_path = sanitize_path(path)
        if not os.path.exists(safe_path):
            await ctx.error(f"File not found: {path}")
            raise ResourceError(f"File not found: {path}")
        if not os.path.isfile(safe_path):
            await ctx.error(f"Path is not a file: {path}")
            raise ResourceError(f"Path is not a file: {path}")

        file_size = os.path.getsize(safe_path)
        if file_size > MAX_FILE_SIZE:
            await ctx.error(f"File too large: {file_size} bytes")
            raise ResourceError(f"File too large: {file_size} bytes")

        with open(safe_path, 'r', encoding='utf-8') as f:
            content = f.read()

        return content
    except Exception as e:
        await ctx.error(f"Error reading file resource {path}: {str(e)}")
        raise ResourceError(str(e))

if __name__ == "__main__":
    # Ensure the base path exists
    os.makedirs(ALLOWED_BASE_PATH, exist_ok=True)
    mcp.run(transport="sse")  # Use SSE transport for HTTP compatibility