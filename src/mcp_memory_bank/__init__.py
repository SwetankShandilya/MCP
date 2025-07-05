"""
Memory Bank MCP Server Package

A comprehensive Model Context Protocol (MCP) server for intelligent project memory management.
This package provides tools for maintaining project context, detecting changes, and managing
a structured memory bank of project knowledge.

FastMCP 2.0 compatible package structure.
"""

from .main import mcp

# Export the main server instance for FastMCP CLI discovery
__all__ = ["mcp"]

# Package metadata
__version__ = "1.0.0"
__author__ = "Memory Bank MCP Team"
__description__ = "Intelligent project memory management for MCP"
