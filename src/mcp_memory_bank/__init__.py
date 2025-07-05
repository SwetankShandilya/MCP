"""
Memory Bank MCP Server Package

This package provides a comprehensive Memory Bank system for Model Context Protocol (MCP) servers.
Following the FastMCP examples pattern from https://github.com/jlowin/fastmcp/tree/main/examples

The package is structured with:
- server.py: Contains the FastMCP instance and all tool definitions (main file)
- tools.py: Legacy tools module (kept for compatibility)
- middlewares.py: Legacy middlewares module (kept for compatibility)
- main.py: Legacy main module (kept for compatibility)

Usage:
    from mcp_memory_bank import mcp  # Import the configured FastMCP instance
    # or
    python src/mcp_memory_bank/server.py  # Run directly
"""

# Import the configured FastMCP instance from server.py (main file)
from .server import mcp

# Import guide templates for external access
from .templates import memory_bank_instructions

# Version information
__version__ = "2.9.0"
__author__ = "Memory Bank MCP Team"
__description__ = "Comprehensive Memory Bank system for MCP servers with FastMCP 2.9+ support"

# Export the main components
__all__ = [
    'mcp',           # The configured FastMCP instance ready for use
    'memory_bank_instructions',  # Template instructions
    '__version__',
    '__author__',
    '__description__'
]
