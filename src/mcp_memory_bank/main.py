"""
Memory Bank MCP Server - Main Composition

A comprehensive Model Context Protocol (MCP) server for intelligent project memory management.
This server follows FastMCP 2.0 composition patterns by mounting modular subservers.

FastMCP 2.0 Composition Structure:
- Main server mounts tools and middleware subservers
- Uses live linking for dynamic updates
- Follows modular architecture patterns from FastMCP documentation
"""

import asyncio
import logging
from fastmcp import FastMCP

# Import modular subservers
from .tools import tools_server
from .middleware_server import middleware_server

# Create main server instance
mcp = FastMCP(name="Memory Bank MCP Server")

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def setup_composition():
    """
    Setup server composition using FastMCP mounting patterns.
    This follows the documentation at: https://gofastmcp.com/servers/composition#mounting-live-linking
    """
    logger.info("Setting up FastMCP server composition...")
    
    # Mount the tools server using live linking (no prefix - components keep original names)
    # This creates a live link where changes to tools_server are immediately reflected
    mcp.mount(tools_server)
    logger.info("Mounted tools server with live linking")
    
    # Mount the middleware server using live linking
    # Middleware will be applied to all requests through the main server
    mcp.mount(middleware_server)
    logger.info("Mounted middleware server with live linking")
    
    logger.info("FastMCP server composition setup complete")


async def main():
    """Main entry point for the composed server"""
    await setup_composition()
    return mcp


if __name__ == "__main__":
    # Setup composition and run the server
    asyncio.run(setup_composition())
    mcp.run()
