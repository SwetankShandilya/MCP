"""
Memory Bank Middleware Server

A modular FastMCP server containing all middleware functionality.
This server is designed to be mounted or imported into a main server.
"""

from fastmcp import FastMCP

# Import middleware classes
from .middlewares import (
    ContextAwarePromptInjectionMiddleware,
    ToolLoggingMiddleware,
    MemoryCompletenessEnforcementMiddleware,
    CrossReferenceRedundancyMiddleware,
    AgentBehaviorProfilerMiddleware
)

# Create middleware server instance
middleware_server = FastMCP(name="MemoryBankMiddleware")

# Add all middleware to this server
middleware_server.add_middleware(ContextAwarePromptInjectionMiddleware())
middleware_server.add_middleware(ToolLoggingMiddleware())
middleware_server.add_middleware(MemoryCompletenessEnforcementMiddleware())
middleware_server.add_middleware(CrossReferenceRedundancyMiddleware())
middleware_server.add_middleware(AgentBehaviorProfilerMiddleware()) 