"""
Memory Bank MCP Server

This module provides the main entry point for the Memory Bank MCP server,
importing tools and middlewares from their respective modules.
"""

import asyncio
import logging
import sys
from pathlib import Path

# Import the FastMCP instance and all tools from tools.py
from .tools import mcp

# Import middleware classes from middlewares.py
from .middlewares import (
    ContextAwarePromptInjectionMiddleware,
    ToolLoggingMiddleware,
    MemoryCompletenessEnforcementMiddleware,
    CrossReferenceRedundancyMiddleware,
    AgentBehaviorProfilerMiddleware
)


def setup_logging():
    """Setup logging for the main server"""
    memory_bank_path = Path("memory-bank")
    memory_bank_path.mkdir(exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(memory_bank_path / "server.log")
        ]
    )


def register_middlewares():
    """Register all middleware classes with the FastMCP instance"""
    logger = logging.getLogger(__name__)
    
    try:
        # Register middleware classes
        middlewares = [
            ContextAwarePromptInjectionMiddleware(),
            ToolLoggingMiddleware(),
            MemoryCompletenessEnforcementMiddleware(),
            CrossReferenceRedundancyMiddleware(),
            AgentBehaviorProfilerMiddleware()
        ]
        
        for middleware in middlewares:
            mcp.add_middleware(middleware)
            logger.info(f"Registered middleware: {middleware.__class__.__name__}")
        
        logger.info(f"Successfully registered {len(middlewares)} middleware classes")
        
    except Exception as e:
        logger.error(f"Failed to register middlewares: {str(e)}")
        raise


def main():
    """Main entry point for the Memory Bank MCP server"""
    setup_logging()
    logger = logging.getLogger(__name__)
    
    logger.info("Starting Memory Bank MCP Server")
    
    try:
        # Register middlewares
        register_middlewares()
        
        # The FastMCP instance (mcp) is already configured with all tools in tools.py
        # All tools are automatically registered when the tools.py module is imported
        
        logger.info("Memory Bank MCP Server initialized successfully")
        logger.info("All tools and middlewares are registered and ready")
        
        # Return the configured FastMCP instance
        return mcp
        
    except Exception as e:
        logger.error(f"Failed to initialize Memory Bank MCP Server: {str(e)}")
        raise


# For direct execution
if __name__ == "__main__":
    try:
        server = main()
        # Run the server
        asyncio.run(server.run())
    except KeyboardInterrupt:
        print("\nServer stopped by user")
    except Exception as e:
        print(f"Server error: {e}")
        sys.exit(1)


# Export the configured FastMCP instance for use by MCP clients
__all__ = ['mcp', 'main']
