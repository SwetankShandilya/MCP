"""
Memory Bank Tools Server

A modular FastMCP server containing all memory bank tools.
This server is designed to be mounted or imported into a main server.
"""

import asyncio
import json
import logging
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastmcp import FastMCP
from fastmcp.server.context import Context

# Import template and guide modules
from .templates.memory_bank_instructions import TEMPLATE as MEMORY_BANK_INSTRUCTIONS
from .guides import setup, structure, usage, benefits

# Create tools server instance
tools_server = FastMCP(name="MemoryBankTools")

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@tools_server.resource("memory-bank://guide")
async def memory_bank_guide() -> str:
    """Comprehensive guide for the Memory Bank MCP Server"""
    return MEMORY_BANK_INSTRUCTIONS


@tools_server.tool
async def get_memory_bank_structure(context: Context) -> Dict[str, Any]:
    """
    Get the current structure of the memory bank directory.
    Returns a hierarchical view of all memory bank files and their purposes.
    """
    memory_bank_path = Path("memory_bank")
    
    if not memory_bank_path.exists():
        return {
            "exists": False,
            "message": "Memory bank directory does not exist. Use create_memory_bank_structure to initialize it."
        }
    
    def scan_directory(path: Path) -> Dict[str, Any]:
        """Recursively scan directory structure"""
        structure = {
            "type": "directory" if path.is_dir() else "file",
            "name": path.name,
            "path": str(path),
        }
        
        if path.is_file():
            try:
                structure["size"] = path.stat().st_size
                structure["modified"] = datetime.fromtimestamp(path.stat().st_mtime).isoformat()
                
                # Add content preview for small files
                if path.suffix == '.py' and structure["size"] < 5000:
                    with open(path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        # Extract docstring if present
                        if '"""' in content:
                            start = content.find('"""') + 3
                            end = content.find('"""', start)
                            if end != -1:
                                structure["description"] = content[start:end].strip()
            except Exception as e:
                structure["error"] = str(e)
        
        elif path.is_dir():
            structure["children"] = []
            try:
                for child in sorted(path.iterdir()):
                    structure["children"].append(scan_directory(child))
            except PermissionError:
                structure["error"] = "Permission denied"
        
        return structure
    
    return {
        "exists": True,
        "structure": scan_directory(memory_bank_path),
        "scan_time": datetime.now().isoformat()
    }


@tools_server.tool
async def create_memory_bank_structure(context: Context) -> Dict[str, Any]:
    """
    Create the complete memory bank directory structure with all template files.
    This initializes the memory bank with proper organization and template content.
    """
    try:
        # Import and use the setup guide
        result = setup.create_memory_bank_structure()
        return {
            "success": True,
            "message": "Memory bank structure created successfully",
            "details": result
        }
    except Exception as e:
        logger.error(f"Error creating memory bank structure: {e}")
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to create memory bank structure"
        }


@tools_server.tool
async def intelligent_context_executor(
    context: Context,
    query: str,
    target_directories: Optional[List[str]] = None,
    max_results: int = 10
) -> Dict[str, Any]:
    """
    Execute intelligent context analysis using semantic search and file inspection.
    
    Args:
        query: Natural language query about the project
        target_directories: Optional list of directories to focus search on
        max_results: Maximum number of results to return
    """
    try:
        # Use the usage guide functionality
        result = usage.execute_intelligent_query(query, target_directories, max_results)
        return {
            "success": True,
            "query": query,
            "results": result,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error in intelligent context executor: {e}")
        return {
            "success": False,
            "error": str(e),
            "query": query
        }


@tools_server.tool
async def auto_detect_project_changes(context: Context) -> Dict[str, Any]:
    """
    Automatically detect recent changes in the project using git and file system analysis.
    Returns structured information about modifications, additions, and deletions.
    """
    try:
        changes = {
            "git_changes": [],
            "file_system_changes": [],
            "timestamp": datetime.now().isoformat()
        }
        
        # Check if we're in a git repository
        try:
            # Get recent git changes
            git_log_cmd = ["git", "log", "--oneline", "--since=24 hours ago"]
            git_result = subprocess.run(git_log_cmd, capture_output=True, text=True, cwd=".")
            
            if git_result.returncode == 0 and git_result.stdout.strip():
                changes["git_changes"] = [
                    line.strip() for line in git_result.stdout.strip().split('\n')
                ]
            
            # Get git status
            git_status_cmd = ["git", "status", "--porcelain"]
            status_result = subprocess.run(git_status_cmd, capture_output=True, text=True, cwd=".")
            
            if status_result.returncode == 0:
                changes["git_status"] = [
                    line.strip() for line in status_result.stdout.strip().split('\n')
                    if line.strip()
                ]
        
        except Exception as git_error:
            changes["git_error"] = str(git_error)
        
        # Analyze recent file modifications
        project_root = Path(".")
        recent_files = []
        
        for file_path in project_root.rglob("*"):
            if file_path.is_file() and not any(part.startswith('.') for part in file_path.parts):
                try:
                    stat = file_path.stat()
                    modified_time = datetime.fromtimestamp(stat.st_mtime)
                    
                    # Check if modified in last 24 hours
                    if (datetime.now() - modified_time).total_seconds() < 86400:
                        recent_files.append({
                            "path": str(file_path),
                            "modified": modified_time.isoformat(),
                            "size": stat.st_size
                        })
                except Exception:
                    continue
        
        changes["recent_files"] = sorted(recent_files, key=lambda x: x["modified"], reverse=True)[:20]
        
        return {
            "success": True,
            "changes": changes
        }
    
    except Exception as e:
        logger.error(f"Error detecting project changes: {e}")
        return {
            "success": False,
            "error": str(e)
        }


@tools_server.tool
async def suggest_files_to_update(
    context: Context,
    context_description: str,
    change_type: str = "general"
) -> Dict[str, Any]:
    """
    Suggest which memory bank files should be updated based on the given context.
    
    Args:
        context_description: Description of changes or new information
        change_type: Type of change (feature, bugfix, refactor, documentation, etc.)
    """
    try:
        suggestions = usage.suggest_memory_updates(context_description, change_type)
        return {
            "success": True,
            "context": context_description,
            "change_type": change_type,
            "suggestions": suggestions,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error suggesting file updates: {e}")
        return {
            "success": False,
            "error": str(e),
            "context": context_description
        }


@tools_server.tool
async def analyze_project_summary(context: Context) -> Dict[str, Any]:
    """
    Analyze the current project state and generate a comprehensive summary.
    This includes codebase analysis, recent changes, and memory bank status.
    """
    try:
        # Get project structure
        project_files = []
        for file_path in Path(".").rglob("*"):
            if file_path.is_file() and not any(part.startswith('.') for part in file_path.parts):
                project_files.append(str(file_path))
        
        # Analyze memory bank status
        memory_bank_status = await get_memory_bank_structure(context)
        
        # Get recent changes
        recent_changes = await auto_detect_project_changes(context)
        
        summary = {
            "project_overview": {
                "total_files": len(project_files),
                "file_types": {},
                "directory_structure": []
            },
            "memory_bank_status": memory_bank_status,
            "recent_changes": recent_changes,
            "analysis_timestamp": datetime.now().isoformat()
        }
        
        # Analyze file types
        for file_path in project_files:
            ext = Path(file_path).suffix.lower()
            summary["project_overview"]["file_types"][ext] = summary["project_overview"]["file_types"].get(ext, 0) + 1
        
        return {
            "success": True,
            "summary": summary
        }
    
    except Exception as e:
        logger.error(f"Error analyzing project summary: {e}")
        return {
            "success": False,
            "error": str(e)
        }


@tools_server.tool
async def update_memory_bank_file(
    context: Context,
    file_path: str,
    content: str,
    update_type: str = "append"
) -> Dict[str, Any]:
    """
    Update a specific memory bank file with new content.
    
    Args:
        file_path: Path to the memory bank file (relative to memory_bank/)
        content: Content to add or replace
        update_type: How to update ("append", "replace", "prepend")
    """
    try:
        memory_bank_path = Path("memory_bank")
        target_file = memory_bank_path / file_path
        
        # Ensure the directory exists
        target_file.parent.mkdir(parents=True, exist_ok=True)
        
        if update_type == "replace":
            with open(target_file, 'w', encoding='utf-8') as f:
                f.write(content)
        elif update_type == "append":
            with open(target_file, 'a', encoding='utf-8') as f:
                f.write(f"\n{content}")
        elif update_type == "prepend":
            existing_content = ""
            if target_file.exists():
                with open(target_file, 'r', encoding='utf-8') as f:
                    existing_content = f.read()
            
            with open(target_file, 'w', encoding='utf-8') as f:
                f.write(f"{content}\n{existing_content}")
        
        return {
            "success": True,
            "file_path": str(target_file),
            "update_type": update_type,
            "timestamp": datetime.now().isoformat()
        }
    
    except Exception as e:
        logger.error(f"Error updating memory bank file: {e}")
        return {
            "success": False,
            "error": str(e),
            "file_path": file_path
        }


@tools_server.tool
async def get_contributor_id(context: Context) -> Dict[str, str]:
    """Get the contributor ID for tracking changes in the memory bank."""
    try:
        # Try to get git user info
        name_result = subprocess.run(
            ["git", "config", "user.name"], 
            capture_output=True, text=True
        )
        email_result = subprocess.run(
            ["git", "config", "user.email"], 
            capture_output=True, text=True
        )
        
        if name_result.returncode == 0 and email_result.returncode == 0:
            name = name_result.stdout.strip()
            email = email_result.stdout.strip()
            return {
                "contributor_id": f"{name} <{email}>",
                "name": name,
                "email": email,
                "source": "git"
            }
    except Exception:
        pass
    
    # Fallback to environment variables or system user
    import getpass
    username = os.getenv("USER") or os.getenv("USERNAME") or getpass.getuser()
    
    return {
        "contributor_id": username,
        "name": username,
        "email": f"{username}@local",
        "source": "system"
    } 