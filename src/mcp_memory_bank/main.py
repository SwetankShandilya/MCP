from mcp.server.fastmcp import FastMCP
from datetime import datetime, timezone, timedelta
from typing import List
from pathlib import Path
import os
import subprocess
import socket
import logging
import logging.handlers

mcp = FastMCP("memory-bank-helper")


from mcp_memory_bank.templates.memory_bank_instructions import TEMPLATE as MEMORY_BANK_INSTRUCTIONS_TEMPLATE
from mcp_memory_bank.templates.projectbrief import TEMPLATE as PROJECTBRIEF_TEMPLATE
from mcp_memory_bank.templates.product_context import TEMPLATE as PRODUCT_CONTEXT_TEMPLATE
from mcp_memory_bank.templates.active_context import TEMPLATE as ACTIVE_CONTEXT_TEMPLATE
from mcp_memory_bank.templates.system_patterns import TEMPLATE as SYSTEM_PATTERNS_TEMPLATE
from mcp_memory_bank.templates.tech_context import TEMPLATE as TECH_CONTEXT_TEMPLATE
from mcp_memory_bank.templates.progress import TEMPLATE as PROGRESS_TEMPLATE

from mcp_memory_bank.guides.setup import GUIDE as SETUP_GUIDE
from mcp_memory_bank.guides.usage import GUIDE as USAGE_GUIDE
from mcp_memory_bank.guides.benefits import GUIDE as BENEFITS_GUIDE
from mcp_memory_bank.guides.structure import GUIDE as STRUCTURE_GUIDE



TEMPLATES = {
    "memory_bank_instructions.md": MEMORY_BANK_INSTRUCTIONS_TEMPLATE,
    "projectbrief.md": PROJECTBRIEF_TEMPLATE,
    "productContext.md": PRODUCT_CONTEXT_TEMPLATE,
    "activeContext.md": ACTIVE_CONTEXT_TEMPLATE,
    "systemPatterns.md": SYSTEM_PATTERNS_TEMPLATE,
    "techContext.md": TECH_CONTEXT_TEMPLATE,
    "progress.md": PROGRESS_TEMPLATE
}

GUIDES = {
    "setup": SETUP_GUIDE,
    "usage": USAGE_GUIDE,
    "benefits": BENEFITS_GUIDE,
    "structure": STRUCTURE_GUIDE
}

# Define a tool to get Memory Bank structure
@mcp.tool()
def get_memory_bank_structure() -> str:
    """
    Get the current memory bank structure as a formatted string.
    
    Returns:
        str: A formatted string showing the memory bank directory structure
    """
    # Embedded logging setup
    memory_bank_path = Path("memory-bank")
    memory_bank_path.mkdir(exist_ok=True)
    
    log_file = memory_bank_path / "Logs.log"
    handler = logging.handlers.RotatingFileHandler(
        log_file, maxBytes=1024*1024, backupCount=1
    )
    formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(funcName)s - %(message)s'
    )
    handler.setFormatter(formatter)
    logger = logging.getLogger('memory_bank_structure')
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)
    
    # Get contributor ID
    contributor_id = None
    for env_var in ["GIT_AUTHOR_NAME", "USER", "USERNAME"]:
        value = os.environ.get(env_var)
        if value:
            contributor_id = value.strip()
            break
    
    if not contributor_id:
        try:
            result = subprocess.run(
                ["git", "config", "user.name"], 
                capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0 and result.stdout.strip():
                contributor_id = result.stdout.strip()
        except:
            pass
    
    if not contributor_id:
        try:
            contributor_id = f"user-{socket.gethostname()}"
        except:
            contributor_id = "unknown-user"
    
    # Generate timestamp
    timestamp = f"{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')} [{contributor_id}]"
    
    # Log the operation
    logger.info(f"🔍 Memory bank structure requested by {contributor_id}")
    
    # Build structure representation
    def build_tree_structure(path: Path, prefix: str = "", max_depth: int = 3, current_depth: int = 0) -> str:
        if current_depth > max_depth:
            return ""
        
        items = []
        if path.exists():
            try:
                for item in sorted(path.iterdir()):
                    if item.name.startswith('.'):
                        continue
                    
                    if item.is_dir():
                        items.append(f"{prefix}📁 {item.name}/")
                        if current_depth < max_depth:
                            sub_items = build_tree_structure(
                                item, prefix + "  ", max_depth, current_depth + 1
                            )
                            if sub_items:
                                items.append(sub_items)
                    else:
                        items.append(f"{prefix}📄 {item.name}")
            except PermissionError:
                items.append(f"{prefix}❌ Permission denied")
        
        return "\n".join(items)
    
    structure = build_tree_structure(memory_bank_path)
    
    if not structure:
        return f"""
📂 Memory Bank Structure (Empty)
Generated: {timestamp}

The memory-bank directory exists but is empty.
Use 'create_memory_bank_structure' to initialize it.
"""
    
    return f"""
📂 Memory Bank Structure
Generated: {timestamp}

{structure}

Total files: {len(list(memory_bank_path.rglob('*'))) if memory_bank_path.exists() else 0}
"""

# Define a tool to generate Memory Bank template
@mcp.tool()
async def generate_memory_bank_template(file_name: str) -> str:
    """Generate a template for a specific Memory Bank file.
    
    Args:
        file_name: The name of the file to generate a template for (e.g., "projectbrief.md")
    """
    if file_name in TEMPLATES:
        return TEMPLATES[file_name]
    else:
        available_templates = ", ".join(TEMPLATES.keys())
        return f"Template for {file_name} not found. Available templates: {available_templates}"

# Define a tool to analyze project summary
@mcp.tool()
async def analyze_project_summary(project_summary: str) -> str:
    """Analyze a project summary and provide suggestions for Memory Bank content.
    
    Args:
        project_summary: A summary of the project
    """    # Extract potential project name (first few words)
    
    return f"""Based on your project summary, here are suggestions for your Memory Bank:

### Core Files (Required)
1. `memory_bank_instructions.md`
    - Instructions for the Memory Bank
    - Describes how to use the Memory Bank
    
2. `projectbrief.md`
   - Foundation document that shapes all other files
   - Created at project start if it doesn't exist
   - Defines core requirements and goals
   - Source of truth for project scope

3. `productContext.md`
   - Why this project exists
   - Problems it solves
   - How it should work
   - User experience goals

4. `activeContext.md`
   - Current work focus
   - Recent changes
   - Next steps
   - Active decisions and considerations
   - Important patterns and preferences
   - Learnings and project insights

5. `systemPatterns.md`
   - System architecture
   - Key technical decisions
   - Design patterns in use
   - Component relationships
   - Critical implementation paths

6. `techContext.md`
   - Technologies used
   - Development setup
   - Technical constraints
   - Dependencies
   - Tool usage patterns

7. `progress.md`
   - What works
   - What's left to build
   - Current status
   - Known issues
   - Evolution of project decisions

## Files Location:
All files must be located in the 'memory-bank/' directory

## Next Steps:
1. Create 'memory-bank/' directory
2. Fetch and create 'memory_bank_instructions.md' file as is without any edits 
3. Create the core files using our templates
4. Fill in the details based on these suggestions
5. Update regularly as your project evolves
6. Ensure details accurately reflect your project context and current state"""

# Add a resource for Memory Bank guide
@mcp.resource("memory_bank_guide://{section}")
async def memory_bank_guide(section: str) -> tuple[str, str]:
    """Provide guidance on Memory Bank setup and usage.
    
    Args:
        section: The section of the guide to retrieve
    """
    if section in GUIDES:
        content = f"# Memory Bank Guide: {section}\n\n{GUIDES[section]}"
        return content, "text/markdown"
    else:
        available_guides = ", ".join(GUIDES.keys())
        return f"Guide for {section} not found. Available guides: {available_guides}", "text/plain"

def main():
    """Entry point for the application when run with uvx."""
    mcp.run(transport='stdio')


if __name__ == "__main__":
    main()
