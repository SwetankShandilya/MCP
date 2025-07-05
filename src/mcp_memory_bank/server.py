#!/usr/bin/env python3
"""
Memory Bank MCP Server

A comprehensive FastMCP server providing memory bank management tools and middleware.
Based on FastMCP examples pattern from https://github.com/jlowin/fastmcp/tree/main/examples
"""

import json
import logging
import logging.handlers
import os
import hashlib
import socket
import subprocess
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Set, Any, Optional

from fastmcp import FastMCP, Context
from fastmcp.server.middleware import Middleware, MiddlewareContext

# Create FastMCP server instance
mcp = FastMCP("Memory Bank Server")

# Global constants for middleware
TECHNICAL_TOOLS = {
    'edit_file', 'run_terminal_cmd', 'search_replace', 'delete_file',
    'create_file', 'write_file', 'append_file', 'move_file', 'copy_file'
}

MEMORY_BANK_TOOLS = {
    'intelligent_context_executor', 'create_memory_bank_structure',
    'generate_memory_bank_template', 'analyze_project_summary',
    'suggest_files_to_update', 'smart_content_analysis_and_routing',
    'auto_detect_project_changes'
}

CORE_TOOLS = {
    'read_file', 'list_dir', 'grep_search', 'file_search', 'codebase_search'
}

# Guide content
GUIDES = {
    "setup": """
# Memory Bank Setup Guide

## Quick Start
1. Run `create_memory_bank_structure` to initialize your memory bank
2. Use `generate_memory_bank_template` to create specific files
3. Use `intelligent_context_executor` to get context for any area

## Directory Structure
- `context/` - Project overview, stakeholders, success metrics
- `tech_specs/` - Technical documentation and API references
- `devops/` - Deployment and CI/CD documentation
- `dynamic_meta/` - Change logs, decisions, configurations

## Best Practices
- Update `change_log.md` for every significant change
- Use cross-references to avoid duplication
- Keep files focused and well-organized
""",
    "usage": """
# Memory Bank Usage Guide

## Core Tools
- `intelligent_context_executor` - Get intelligent context for any query
- `create_memory_bank_structure` - Initialize the complete directory structure
- `generate_memory_bank_template` - Create new files with proper templates

## Workflow
1. Start with project analysis using `analyze_project_summary`
2. Create structure with `create_memory_bank_structure`
3. Generate specific files with `generate_memory_bank_template`
4. Use `intelligent_context_executor` for ongoing context needs

## File Organization
- Use descriptive file names
- Follow the established directory structure
- Cross-reference related information
""",
    "benefits": """
# Memory Bank Benefits

## For Development Teams
- Centralized project knowledge
- Consistent documentation structure
- Easy onboarding for new team members
- Historical decision tracking

## For AI Agents
- Structured context for better responses
- Consistent information format
- Reduced hallucination through grounded data
- Efficient knowledge retrieval

## For Project Management
- Clear project status visibility
- Decision audit trail
- Stakeholder requirement tracking
- Success metrics monitoring
"""
}

# Utility functions
def setup_logging():
    """Setup logging for this tool"""
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
    logger = logging.getLogger('memory_bank')
    logger.setLevel(logging.INFO)
    if not logger.handlers:
        logger.addHandler(handler)
    return logger

def get_contributor_id():
    """Get contributor ID from environment or git"""
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
    
    return contributor_id

# Tools
@mcp.tool()
def get_memory_bank_structure() -> str:
    """
    Get the current memory bank structure as a formatted string.
    
    Returns:
        str: Formatted directory structure of the memory bank
    """
    logger = setup_logging()
    contributor_id = get_contributor_id()
    timestamp = f"{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')} [{contributor_id}]"
    
    logger.info(f"📁 Structure request by {contributor_id}")
    
    memory_bank_path = Path("memory-bank")
    
    if not memory_bank_path.exists():
        return f"""
❌ Memory Bank Not Found

The memory-bank directory does not exist yet.

🚀 Quick Start:
Use 'create_memory_bank_structure' to initialize your memory bank.

Timestamp: {timestamp}
"""
    
    def build_tree(path, prefix="", max_depth=3, current_depth=0):
        if current_depth >= max_depth:
            return ""
        
        items = []
        try:
            for item in sorted(path.iterdir()):
                if item.name.startswith('.'):
                    continue
                    
                if item.is_dir():
                    items.append(f"{prefix}📁 {item.name}/")
                    if current_depth < max_depth - 1:
                        sub_items = build_tree(item, prefix + "  ", max_depth, current_depth + 1)
                        if sub_items:
                            items.append(sub_items)
                else:
                    size = item.stat().st_size
                    size_str = f"({size} bytes)" if size < 1024 else f"({size//1024}KB)"
                    items.append(f"{prefix}📄 {item.name} {size_str}")
        except PermissionError:
            items.append(f"{prefix}❌ Permission denied")
        
        return "\n".join(items)
    
    tree_structure = build_tree(memory_bank_path)
    
    # Count files and directories
    total_files = sum(1 for _ in memory_bank_path.rglob('*') if _.is_file())
    total_dirs = sum(1 for _ in memory_bank_path.rglob('*') if _.is_dir())
    
    return f"""
📁 MEMORY BANK STRUCTURE
Generated: {timestamp}

{tree_structure}

📊 SUMMARY:
• Total Directories: {total_dirs}
• Total Files: {total_files}
• Root Path: {memory_bank_path.absolute()}

💡 USAGE:
• Use 'intelligent_context_executor' to get context from any file
• Use 'generate_memory_bank_template' to create new files
• Use 'create_memory_bank_structure' to add missing directories

✨ Structure retrieved successfully!
"""


@mcp.tool()
def create_memory_bank_structure() -> str:
    """
    Create the complete memory bank directory structure with all templates.
    
    Returns:
        str: Success message with details of created structure
    """
    logger = setup_logging()
    contributor_id = get_contributor_id()
    timestamp = f"{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')} [{contributor_id}]"
    
    logger.info(f"🏗️ Structure creation requested by {contributor_id}")
    
    # Define the complete directory structure
    structure = {
        "memory-bank": {
            "context": {
                "overview.md": f"""---
title: Project Overview
description: High-level project overview and current status
last_updated: {timestamp}
version: 1.0
---

# Project Overview

## Current Status
[Describe the current state of the project]

## Key Objectives
1. [Primary objective]
2. [Secondary objective]
3. [Additional objectives]

## Recent Updates
- **{timestamp}**: Memory bank structure initialized by {contributor_id}

## Next Steps
1. Update this overview with project-specific information
2. Define stakeholders and success metrics
3. Document technical architecture
""",
                "stakeholders.md": f"""---
title: Stakeholders
description: Project stakeholders and their roles
last_updated: {timestamp}
version: 1.0
---

# Stakeholders

## Primary Stakeholders
- **Project Owner**: [Name and role]
- **Technical Lead**: [Name and role]
- **Product Manager**: [Name and role]

## Secondary Stakeholders
- **End Users**: [Description]
- **Support Team**: [Description]
- **Operations Team**: [Description]

## Communication Plan
- **Weekly Updates**: [Schedule and participants]
- **Monthly Reviews**: [Schedule and participants]
- **Quarterly Planning**: [Schedule and participants]

## Change History
- **{timestamp}**: Initial stakeholder documentation created by {contributor_id}
""",
                "success_metrics.md": f"""---
title: Success Metrics
description: Key performance indicators and success criteria
last_updated: {timestamp}
version: 1.0
---

# Success Metrics

## Key Performance Indicators (KPIs)
1. **[Metric Name]**: [Description and target]
2. **[Metric Name]**: [Description and target]
3. **[Metric Name]**: [Description and target]

## Success Criteria
- [ ] [Specific, measurable goal]
- [ ] [Specific, measurable goal]
- [ ] [Specific, measurable goal]

## Measurement Plan
- **Data Collection**: [How metrics will be collected]
- **Reporting Frequency**: [How often metrics will be reported]
- **Review Process**: [How metrics will be reviewed and acted upon]

## Change History
- **{timestamp}**: Initial success metrics defined by {contributor_id}
"""
            },
            "tech_specs": {
                "system_architecture.md": f"""---
title: System Architecture
description: High-level system architecture and design decisions
last_updated: {timestamp}
version: 1.0
---

# System Architecture

## Overview
[High-level description of the system architecture]

## Core Components
1. **[Component Name]**: [Description and responsibilities]
2. **[Component Name]**: [Description and responsibilities]
3. **[Component Name]**: [Description and responsibilities]

## Technology Stack
- **Frontend**: [Technologies used]
- **Backend**: [Technologies used]
- **Database**: [Technologies used]
- **Infrastructure**: [Technologies used]

## Architecture Decisions
1. **[Decision]**: [Rationale and implications]
2. **[Decision]**: [Rationale and implications]

## Change History
- **{timestamp}**: Initial architecture documentation created by {contributor_id}
""",
                "api_reference.md": f"""---
title: API Reference
description: API endpoints, methods, and specifications
last_updated: {timestamp}
version: 1.0
---

# API Reference

## Base URL
`[API Base URL]`

## Authentication
[Authentication method and requirements]

## Endpoints

### [Endpoint Category]

#### GET /endpoint
- **Description**: [What this endpoint does]
- **Parameters**: [Query parameters]
- **Response**: [Response format]
- **Example**: [Usage example]

## Error Handling
- **400 Bad Request**: [When this occurs]
- **401 Unauthorized**: [When this occurs]
- **404 Not Found**: [When this occurs]
- **500 Internal Server Error**: [When this occurs]

## Change History
- **{timestamp}**: Initial API documentation created by {contributor_id}
""",
                "data_flow.md": f"""---
title: Data Flow
description: Data flow diagrams and data processing workflows
last_updated: {timestamp}
version: 1.0
---

# Data Flow

## Overview
[Description of how data flows through the system]

## Data Sources
1. **[Source Name]**: [Description and format]
2. **[Source Name]**: [Description and format]

## Processing Pipeline
1. **[Step]**: [Description]
2. **[Step]**: [Description]
3. **[Step]**: [Description]

## Data Storage
- **[Storage Type]**: [What data is stored and how]
- **[Storage Type]**: [What data is stored and how]

## Data Security
- **Encryption**: [Encryption methods used]
- **Access Control**: [Who can access what data]
- **Compliance**: [Regulatory compliance requirements]

## Change History
- **{timestamp}**: Initial data flow documentation created by {contributor_id}
""",
                "modules": {}
            },
            "devops": {
                "deployment_architecture.md": f"""---
title: Deployment Architecture
description: Infrastructure and deployment configuration
last_updated: {timestamp}
version: 1.0
---

# Deployment Architecture

## Infrastructure Overview
[Description of the deployment infrastructure]

## Environments
- **Development**: [Configuration and purpose]
- **Staging**: [Configuration and purpose]
- **Production**: [Configuration and purpose]

## Deployment Process
1. **[Step]**: [Description]
2. **[Step]**: [Description]
3. **[Step]**: [Description]

## Monitoring and Logging
- **Application Monitoring**: [Tools and configuration]
- **Infrastructure Monitoring**: [Tools and configuration]
- **Log Management**: [Tools and configuration]

## Disaster Recovery
- **Backup Strategy**: [How backups are performed]
- **Recovery Procedures**: [How to recover from failures]

## Change History
- **{timestamp}**: Initial deployment documentation created by {contributor_id}
""",
                "ci_cd_pipeline.md": f"""---
title: CI/CD Pipeline
description: Continuous integration and deployment processes
last_updated: {timestamp}
version: 1.0
---

# CI/CD Pipeline

## Overview
[Description of the CI/CD process]

## Build Pipeline
1. **[Stage]**: [Description and tools]
2. **[Stage]**: [Description and tools]
3. **[Stage]**: [Description and tools]

## Testing Strategy
- **Unit Tests**: [Coverage and tools]
- **Integration Tests**: [Coverage and tools]
- **End-to-End Tests**: [Coverage and tools]

## Deployment Pipeline
1. **[Stage]**: [Description]
2. **[Stage]**: [Description]
3. **[Stage]**: [Description]

## Quality Gates
- **[Gate]**: [Criteria for passing]
- **[Gate]**: [Criteria for passing]

## Change History
- **{timestamp}**: Initial CI/CD documentation created by {contributor_id}
"""
            },
            "dynamic_meta": {
                "change_log.md": f"""---
title: Change Log
description: Record of all significant changes to the project
last_updated: {timestamp}
version: 1.0
---

# Change Log

## Format
All notable changes to this project will be documented in this file.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [{timestamp}] - Memory Bank Initialization

### Added
- Complete memory bank directory structure
- Initial documentation templates
- Context, technical specifications, and DevOps directories
- Dynamic metadata tracking system

### Created by
{contributor_id}

### Notes
This is the initial setup of the memory bank system. All files contain template content that should be customized for the specific project.

---

## Template for Future Entries

## [YYYY-MM-DD HH:MM:SS UTC] - [Change Title]

### Added
- [New features or files]

### Changed
- [Modified features or files]

### Deprecated
- [Features marked for removal]

### Removed
- [Deleted features or files]

### Fixed
- [Bug fixes]

### Security
- [Security improvements]

### Created/Modified by
[Contributor name]

### Notes
[Additional context or important information]
""",
                "decision_logs.md": f"""---
title: Decision Logs
description: Record of important project decisions and their rationale
last_updated: {timestamp}
version: 1.0
---

# Decision Logs

## Decision Log Format
Each decision should include:
- **Date**: When the decision was made
- **Decision**: What was decided
- **Context**: Why the decision was needed
- **Options Considered**: Alternative approaches
- **Rationale**: Why this option was chosen
- **Consequences**: Expected impact
- **Status**: Current status (Proposed, Accepted, Superseded)

---

## [{timestamp}] - Memory Bank Structure Implementation

**Decision**: Implement comprehensive memory bank structure with predefined templates

**Context**: Need for organized project documentation and knowledge management system

**Options Considered**:
1. Simple flat file structure
2. Wiki-based documentation
3. Structured memory bank with templates
4. External documentation tools

**Rationale**: Structured approach provides consistency, is version-controllable, and integrates well with development workflow

**Consequences**: 
- Positive: Consistent documentation, easy maintenance, good for AI context
- Negative: Initial setup overhead, requires discipline to maintain

**Status**: Accepted

**Decision Maker**: {contributor_id}

---

## Template for Future Decisions

## [YYYY-MM-DD HH:MM:SS UTC] - [Decision Title]

**Decision**: [What was decided]

**Context**: [Why the decision was needed]

**Options Considered**:
1. [Option 1]
2. [Option 2]
3. [Option 3]

**Rationale**: [Why this option was chosen]

**Consequences**: 
- Positive: [Expected benefits]
- Negative: [Expected drawbacks or costs]

**Status**: [Proposed/Accepted/Superseded]

**Decision Maker**: [Name]
""",
                "config_map.md": f"""---
title: Configuration Map
description: Configuration settings and environment variables
last_updated: {timestamp}
version: 1.0
---

# Configuration Map

## Environment Variables

### Application Configuration
- **APP_NAME**: [Application name]
- **APP_VERSION**: [Current version]
- **APP_ENV**: [Environment: development/staging/production]

### Database Configuration
- **DB_HOST**: [Database host]
- **DB_PORT**: [Database port]
- **DB_NAME**: [Database name]
- **DB_USER**: [Database username]
- **DB_PASSWORD**: [Database password - reference to secret]

### External Services
- **API_KEY_SERVICE1**: [Description and usage]
- **API_URL_SERVICE2**: [Description and usage]

## Configuration Files
- **config.json**: [Purpose and location]
- **settings.yaml**: [Purpose and location]

## Secrets Management
- **Development**: [How secrets are managed in dev]
- **Production**: [How secrets are managed in prod]

## Change History
- **{timestamp}**: Initial configuration documentation created by {contributor_id}
"""
            }
        }
    }
    
    # Create the directory structure and files
    def create_structure(base_path, structure_dict):
        created_items = []
        
        for name, content in structure_dict.items():
            current_path = base_path / name
            
            if isinstance(content, dict):
                # It's a directory
                current_path.mkdir(parents=True, exist_ok=True)
                created_items.append(f"📁 {current_path}")
                
                # Recursively create subdirectories and files
                sub_items = create_structure(current_path, content)
                created_items.extend(sub_items)
            else:
                # It's a file
                current_path.parent.mkdir(parents=True, exist_ok=True)
                current_path.write_text(content, encoding='utf-8')
                created_items.append(f"📄 {current_path}")
        
        return created_items
    
    try:
        # Create the structure
        created_items = create_structure(Path("."), structure)
        
        # Log the creation
        logger.info(f"✅ Memory bank structure created by {contributor_id}: {len(created_items)} items")
        
        return f"""
🏗️ MEMORY BANK STRUCTURE CREATED!
Generated: {timestamp}
Creator: {contributor_id}

📊 SUMMARY:
• Total items created: {len(created_items)}
• Base directory: memory-bank/
• Template files: Ready for customization

📁 CREATED STRUCTURE:
{chr(10).join(created_items[:15])}
{'...' if len(created_items) > 15 else ''}

🎯 NEXT STEPS:
1. Customize template content for your project
2. Use 'intelligent_context_executor' to get context
3. Use 'generate_memory_bank_template' for additional files
4. Keep 'change_log.md' updated with all changes

✨ Your memory bank is ready! Start documenting your project knowledge.
"""
    
    except Exception as e:
        logger.error(f"❌ Structure creation failed: {str(e)}")
        return f"""
❌ STRUCTURE CREATION FAILED

An error occurred while creating the memory bank structure:
{str(e)}

Timestamp: {timestamp}
Creator: {contributor_id}

Please check permissions and try again.
"""


@mcp.tool()
def intelligent_context_executor(user_query: str = "") -> str:
    """
    Execute intelligent context analysis for memory bank files.
    
    Args:
        user_query: The query or context request from the user
        
    Returns:
        str: Intelligent context response with relevant information
    """
    logger = setup_logging()
    contributor_id = get_contributor_id()
    memory_bank_path = Path("memory-bank")
    timestamp = f"{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')} [{contributor_id}]"
    
    if not user_query:
        return f"""
❓ Context Query Required

Please provide a query to get intelligent context.

Examples:
- "What is the current project status?"
- "How is the system architected?"
- "What are the deployment procedures?"
- "Who are the key stakeholders?"

Timestamp: {timestamp}
"""
    
    logger.info(f"🧠 Context request by {contributor_id}: {user_query[:100]}...")
    
    if not memory_bank_path.exists():
        return f"""
❌ Memory Bank Not Found

The memory-bank directory doesn't exist yet.

🚀 Quick Fix:
Use 'create_memory_bank_structure' to initialize your memory bank first.

Query: {user_query}
Timestamp: {timestamp}
"""
    
    # Simple context matching logic
    query_lower = user_query.lower()
    relevant_files = []
    
    # Define context mapping
    context_mapping = {
        'overview': ['context/overview.md'],
        'status': ['context/overview.md', 'dynamic_meta/change_log.md'],
        'architecture': ['tech_specs/system_architecture.md', 'tech_specs/data_flow.md'],
        'api': ['tech_specs/api_reference.md'],
        'deployment': ['devops/deployment_architecture.md', 'devops/ci_cd_pipeline.md'],
        'stakeholder': ['context/stakeholders.md'],
        'decision': ['dynamic_meta/decision_logs.md'],
        'config': ['dynamic_meta/config_map.md'],
        'change': ['dynamic_meta/change_log.md'],
        'metric': ['context/success_metrics.md']
    }
    
    # Find relevant files based on query
    for keyword, files in context_mapping.items():
        if keyword in query_lower:
            relevant_files.extend(files)
    
    # If no specific matches, provide general guidance
    if not relevant_files:
        relevant_files = ['context/overview.md']
    
    # Remove duplicates and check file existence
    relevant_files = list(set(relevant_files))
    found_files = []
    missing_files = []
    
    for file_path in relevant_files:
        full_path = memory_bank_path / file_path
        if full_path.exists():
            found_files.append(file_path)
        else:
            missing_files.append(file_path)
    
    # Read content from found files
    context_content = []
    for file_path in found_files[:3]:  # Limit to 3 files
        try:
            full_path = memory_bank_path / file_path
            content = full_path.read_text(encoding='utf-8')
            context_content.append(f"📄 {file_path}:\n{content[:500]}...")
        except Exception as e:
            context_content.append(f"📄 {file_path}: Error reading file - {str(e)}")
    
    response = f"""
🧠 INTELLIGENT CONTEXT RESPONSE
Query: {user_query}
Generated: {timestamp}
Contributor: {contributor_id}

📋 RELEVANT CONTEXT:
{chr(10).join(context_content) if context_content else "No relevant content found."}

📁 ANALYZED FILES:
✅ Found: {', '.join(found_files) if found_files else 'None'}
❌ Missing: {', '.join(missing_files) if missing_files else 'None'}

💡 SUGGESTIONS:
"""
    
    if missing_files:
        response += f"• Create missing files: {', '.join(missing_files)}\n"
    if not found_files:
        response += "• Initialize memory bank with 'create_memory_bank_structure'\n"
    response += "• Use 'generate_memory_bank_template' for specific documentation\n"
    response += "• Keep files updated as project evolves\n"
    
    response += f"\n🎯 Context analysis complete! Use this information to understand your project better."
    
    logger.info(f"✅ Context provided for {contributor_id}: {len(found_files)} files analyzed")
    
    return response


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


if __name__ == "__main__":
    mcp.run(transport="stdio") 