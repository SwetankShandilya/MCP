"""
Memory Bank MCP Server Package

This package provides a comprehensive Memory Bank system for Model Context Protocol (MCP) servers.
It includes tools for intelligent context management, memory bank structure creation, and middleware
for enhanced agent behavior tracking.

The package is structured with:
- tools.py: Contains the FastMCP instance and all tool definitions
- middlewares.py: Contains middleware classes for enhanced functionality
- main.py: Main entry point that combines tools and middlewares

Usage:
    from mcp_memory_bank import mcp  # Import the configured FastMCP instance
    # or
    from mcp_memory_bank.main import main  # Import the main function
"""

# Import the configured FastMCP instance from main.py
from .main import mcp, main

# Import individual modules for direct access if needed
from . import tools
from . import middlewares
from . import main as main_module

# Import guide templates for external access
from .templates import memory_bank_instructions

# Version information
__version__ = "2.9.0"
__author__ = "Memory Bank MCP Team"
__description__ = "Comprehensive Memory Bank system for MCP servers with FastMCP 2.9+ support"

# Export the main components
__all__ = [
    'mcp',           # The configured FastMCP instance ready for use
    'main',          # Main initialization function
    'tools',         # Tools module
    'middlewares',   # Middlewares module  
    'main_module',   # Main module
    'memory_bank_instructions',  # Template instructions
    '__version__',
    '__author__',
    '__description__'
]
