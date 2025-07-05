"""
Memory Bank MCP Tools Module

This module contains all the MCP tool implementations with the FastMCP instance.
Each tool is completely self-contained and independent.
"""
from mcp.server.fastmcp import FastMCP
from datetime import datetime, timezone
from typing import List
from pathlib import Path
import os
import subprocess
import socket
import logging
import logging.handlers
import json

# Import templates and guides as constants
from .templates.memory_bank_instructions import TEMPLATE as MEMORY_BANK_INSTRUCTIONS
from .templates.context.overview import TEMPLATE as OVERVIEW_TEMPLATE
from .templates.context.stakeholders import TEMPLATE as STAKEHOLDERS_TEMPLATE
from .templates.context.success_metrics import TEMPLATE as SUCCESS_METRICS_TEMPLATE
from .templates.tech_specs.system_architecture import TEMPLATE as SYSTEM_ARCHITECTURE_TEMPLATE
from .templates.tech_specs.data_flow import TEMPLATE as DATA_FLOW_TEMPLATE
from .templates.tech_specs.api_reference import TEMPLATE as API_REFERENCE_TEMPLATE
from .templates.devops.deployment_architecture import TEMPLATE as DEPLOYMENT_ARCHITECTURE_TEMPLATE
from .templates.devops.ci_cd_pipeline import TEMPLATE as CI_CD_PIPELINE_TEMPLATE
from .templates.dynamic_meta.change_log import TEMPLATE as CHANGE_LOG_TEMPLATE
from .templates.dynamic_meta.decision_logs import TEMPLATE as DECISION_LOGS_TEMPLATE
from .templates.dynamic_meta.config_map import TEMPLATE as CONFIG_MAP_TEMPLATE
from .guides.structure import GUIDE as STRUCTURE_GUIDE
from .guides.usage import GUIDE as USAGE_GUIDE
from .guides.benefits import GUIDE as BENEFITS_GUIDE
from .guides.setup import GUIDE as SETUP_GUIDE

# ============================================================================
# FASTMCP INSTANCE AND CONSTANTS
# ============================================================================

mcp = FastMCP("memory-bank-helper")

TEMPLATES = {
    "memory_bank_instructions.md": MEMORY_BANK_INSTRUCTIONS,
    "overview.md": OVERVIEW_TEMPLATE,
    "stakeholders.md": STAKEHOLDERS_TEMPLATE,
    "success_metrics.md": SUCCESS_METRICS_TEMPLATE,
    "system_architecture.md": SYSTEM_ARCHITECTURE_TEMPLATE,
    "data_flow.md": DATA_FLOW_TEMPLATE,
    "api_reference.md": API_REFERENCE_TEMPLATE,
    "deployment_architecture.md": DEPLOYMENT_ARCHITECTURE_TEMPLATE,
    "ci_cd_pipeline.md": CI_CD_PIPELINE_TEMPLATE,
    "change_log.md": CHANGE_LOG_TEMPLATE,
    "decision_logs.md": DECISION_LOGS_TEMPLATE,
    "config_map.md": CONFIG_MAP_TEMPLATE
}

GUIDES = {
    "setup": SETUP_GUIDE,
    "usage": USAGE_GUIDE,
    "benefits": BENEFITS_GUIDE,
    "structure": STRUCTURE_GUIDE
}

# ============================================================================
# TOOL DEFINITIONS
# ============================================================================

@mcp.tool()
def get_memory_bank_structure() -> str:
    """
    Get the current memory bank structure as a formatted string.
    
    Returns:
        str: A formatted string showing the memory bank directory structure
    """
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
        logger = logging.getLogger('memory_bank_structure')
        logger.setLevel(logging.INFO)
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
    
    def build_tree_structure(path, max_depth=4, current_depth=0):
        """Build tree structure recursively"""
        items = []
        if current_depth >= max_depth:
            return items
        
        try:
            for item in sorted(path.iterdir()):
                if item.name.startswith('.'):
                    continue
                
                indent = "  " * current_depth
                if item.is_dir():
                    items.append(f"{indent}📁 {item.name}/")
                    items.extend(build_tree_structure(item, max_depth, current_depth + 1))
                else:
                    items.append(f"{indent}📄 {item.name}")
        except PermissionError:
            indent = "  " * current_depth
            items.append(f"{indent}❌ Permission denied")
        
        return items
    
    # Setup
    logger = setup_logging()
    contributor_id = get_contributor_id()
    memory_bank_path = Path("memory-bank")
    timestamp = f"{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')} [{contributor_id}]"
    
    # Log the operation
    logger.info(f"🔍 Memory bank structure requested by {contributor_id}")
    
    # Build structure
    if not memory_bank_path.exists():
        return f"""
📂 Memory Bank Structure (Empty)
Generated: {timestamp}

The memory-bank directory doesn't exist yet.
Use 'create_memory_bank_structure' to initialize it.
"""
    
    structure_items = build_tree_structure(memory_bank_path)
    structure = "\n".join(structure_items)
    
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

@mcp.tool()
def create_memory_bank_structure() -> str:
    """
    Create the complete memory bank directory structure with all templates.
    
    Returns:
        str: Success message with created structure details
    """
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
        logger = logging.getLogger('memory_bank_create')
        logger.setLevel(logging.INFO)
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
    
    def create_template_with_metadata(template_content, timestamp, contributor_id):
        """Add metadata to template content"""
        return f"""---
created_by: {contributor_id}
created_at: {timestamp}
last_updated: {timestamp}
version: 1.0
---

{template_content}

---
## Change History
- **{timestamp}**: Initial creation by {contributor_id}
"""
    
    # Setup
    logger = setup_logging()
    contributor_id = get_contributor_id()
    memory_bank_path = Path("memory-bank")
    timestamp = f"{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')} [{contributor_id}]"
    
    # Log the operation
    logger.info(f"🏗️ Memory bank structure creation requested by {contributor_id}")
    
    # Create directory structure
    directories = [
        "context",
        "tech_specs",
        "tech_specs/modules",
        "devops",
        "dynamic_meta"
    ]
    
    created_dirs = []
    created_files = []
    
    try:
        # Create directories
        for dir_name in directories:
            dir_path = memory_bank_path / dir_name
            dir_path.mkdir(parents=True, exist_ok=True)
            created_dirs.append(dir_name)
        
        # Create files with templates
        file_mappings = {
            "memory_bank_instructions.md": TEMPLATES["memory_bank_instructions.md"],
            "context/overview.md": TEMPLATES["overview.md"],
            "context/stakeholders.md": TEMPLATES["stakeholders.md"],
            "context/success_metrics.md": TEMPLATES["success_metrics.md"],
            "tech_specs/system_architecture.md": TEMPLATES["system_architecture.md"],
            "tech_specs/data_flow.md": TEMPLATES["data_flow.md"],
            "tech_specs/api_reference.md": TEMPLATES["api_reference.md"],
            "devops/deployment_architecture.md": TEMPLATES["deployment_architecture.md"],
            "devops/ci_cd_pipeline.md": TEMPLATES["ci_cd_pipeline.md"],
            "dynamic_meta/change_log.md": TEMPLATES["change_log.md"],
            "dynamic_meta/decision_logs.md": TEMPLATES["decision_logs.md"],
            "dynamic_meta/config_map.md": TEMPLATES["config_map.md"]
        }
        
        for file_path, template_content in file_mappings.items():
            full_path = memory_bank_path / file_path
            
            # Only create if doesn't exist
            if not full_path.exists():
                content_with_metadata = create_template_with_metadata(
                    template_content, timestamp, contributor_id
                )
                full_path.write_text(content_with_metadata, encoding='utf-8')
                created_files.append(file_path)
        
        # Log successful creation
        logger.info(f"✅ Memory bank structure created successfully by {contributor_id}")
        
        return f"""
✅ Memory Bank Structure Created Successfully!

📁 Created Directories ({len(created_dirs)}):
{chr(10).join(f"  • {d}" for d in created_dirs)}

📄 Created Files ({len(created_files)}):
{chr(10).join(f"  • {f}" for f in created_files)}

👤 Created by: {contributor_id}
🕒 Timestamp: {timestamp}

🎯 Next Steps:
1. Review and customize the template files
2. Use 'intelligent_context_executor' to get context for specific files
3. Use 'generate_memory_bank_template' to create additional files
4. Update files regularly as your project evolves

The memory bank is ready for use! ✨
"""
    
    except Exception as e:
        logger.error(f"❌ Memory bank creation failed: {str(e)}")
        return f"""
❌ Memory Bank Creation Failed

An error occurred while creating the memory bank structure:
{str(e)}

Timestamp: {timestamp}

Please check permissions and try again.
"""

@mcp.tool()
def intelligent_context_executor(user_query: str = "") -> str:
    """
    Execute intelligent context analysis for memory bank files.
    
    Args:
        user_query: The user's query or context request
        
    Returns:
        str: Contextual information and suggestions
    """
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
        logger = logging.getLogger('memory_bank_context')
        logger.setLevel(logging.INFO)
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
    
    def extract_content_without_yaml(file_path, line_count=20):
        """Extract content from file without YAML frontmatter"""
        try:
            content = file_path.read_text(encoding='utf-8')
            lines = content.split('\n')
            
            # Skip YAML frontmatter
            start_idx = 0
            if lines and lines[0].strip() == '---':
                for i, line in enumerate(lines[1:], 1):
                    if line.strip() == '---':
                        start_idx = i + 1
                        break
            
            # Get content lines
            content_lines = lines[start_idx:start_idx + line_count]
            return '\n'.join(content_lines)
        except Exception:
            return ""
    
    def calculate_relevance_score(file_path, query_words):
        """Calculate relevance score for a file"""
        try:
            content = file_path.read_text(encoding='utf-8').lower()
            score = 0
            for word in query_words:
                score += content.count(word.lower())
            return score
        except Exception:
            return 0
    
    def get_relevant_files(memory_bank_path, user_query, mandatory_files, max_files=3):
        """Get relevant files based on query"""
        relevant_files = []
        query_words = user_query.lower().split()
        
        # Add mandatory files first
        for file_path in mandatory_files:
            if file_path.exists():
                content = extract_content_without_yaml(file_path)
                relevant_files.append({
                    'path': file_path,
                    'content': content,
                    'relevance': 'mandatory'
                })
        
        # Find other relevant files
        if query_words:
            file_scores = []
            for md_file in memory_bank_path.rglob("*.md"):
                if md_file.is_file() and md_file not in mandatory_files:
                    score = calculate_relevance_score(md_file, query_words)
                    if score > 0:
                        file_scores.append((md_file, score))
            
            # Sort by relevance and take top files
            file_scores.sort(key=lambda x: x[1], reverse=True)
            for file_path, score in file_scores[:max_files]:
                content = extract_content_without_yaml(file_path)
                relevant_files.append({
                    'path': file_path,
                    'content': content,
                    'relevance': score
                })
        
        return relevant_files
    
    def generate_tool_suggestions(user_query):
        """Generate tool suggestions based on query"""
        suggestions = []
        query_lower = user_query.lower()
        
        if any(word in query_lower for word in ['update', 'change', 'modify', 'edit']):
            suggestions.append("suggest_files_to_update")
        
        if any(word in query_lower for word in ['analyze', 'review', 'examine']):
            suggestions.append("smart_content_analysis_and_routing")
        
        if any(word in query_lower for word in ['create', 'generate', 'new']):
            suggestions.append("generate_memory_bank_template")
        
        if any(word in query_lower for word in ['structure', 'organization', 'layout']):
            suggestions.append("get_memory_bank_structure")
        
        if any(word in query_lower for word in ['project', 'summary', 'overview']):
            suggestions.append("analyze_project_summary")
        
        if any(word in query_lower for word in ['changes', 'detect', 'auto']):
            suggestions.append("auto_detect_project_changes")
        
        return suggestions
    
    # Setup
    logger = setup_logging()
    contributor_id = get_contributor_id()
    memory_bank_path = Path("memory-bank")
    timestamp = f"{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')} [{contributor_id}]"
    
    if not user_query:
        return f"""
❓ Context Query Required

Please provide a specific query or context request.

Examples:
- "What is the current project architecture?"
- "How do I update the deployment process?"
- "What are the current stakeholder requirements?"
- "Show me the latest project changes"

Timestamp: {timestamp}
"""
    
    # Log the operation
    logger.info(f"🧠 Context analysis requested by {contributor_id}: {user_query[:100]}...")
    
    # Check if memory bank exists
    if not memory_bank_path.exists():
        return f"""
❌ Memory Bank Not Found

The memory-bank directory doesn't exist yet.
Use 'create_memory_bank_structure' to initialize it first.

Query: {user_query}
Timestamp: {timestamp}
"""
    
    # Define mandatory files (always included if they exist)
    mandatory_files = [
        memory_bank_path / "memory_bank_instructions.md",
        memory_bank_path / "context" / "overview.md"
    ]
    
    # Get relevant files
    relevant_files = get_relevant_files(memory_bank_path, user_query, mandatory_files)
    
    if not relevant_files:
        return f"""
❌ No Relevant Content Found

No memory bank files found that match your query.

Query: {user_query}
Timestamp: {timestamp}

💡 Suggestions:
1. Use 'create_memory_bank_structure' to initialize the memory bank
2. Use 'generate_memory_bank_template' to create specific files
3. Try a broader query term
"""
    
    # Generate tool suggestions
    tool_suggestions = generate_tool_suggestions(user_query)
    
    # Build context response
    context_sections = []
    
    for file_info in relevant_files:
        relative_path = file_info['path'].relative_to(memory_bank_path)
        context_sections.append(f"""
📄 **{relative_path}** (Relevance: {file_info['relevance']})
```
{file_info['content'][:500]}{'...' if len(file_info['content']) > 500 else ''}
```
""")
    
    # Build response
    response = f"""
🧠 PROJECT CONTEXT ANALYSIS
Generated: {timestamp}
Query: "{user_query}"
Contributor: {contributor_id}

📊 RELEVANT CONTENT ({len(relevant_files)} files found):
{''.join(context_sections)}

🛠️ SUGGESTED TOOLS:
{chr(10).join(f"• {tool}" for tool in tool_suggestions) if tool_suggestions else "• No specific tool suggestions for this query"}

🎯 CONTEXTUAL INSIGHTS:
Based on your query "{user_query}", here are the key insights from your memory bank:

1. **Current State**: Review the content above from your memory bank files
2. **Relevant Files**: {len(relevant_files)} files contain information related to your query
3. **Next Actions**: Use the suggested tools to dive deeper or make updates

💡 RECOMMENDATIONS:
- Use 'suggest_files_to_update' if you need to update content
- Use 'smart_content_analysis_and_routing' for detailed analysis
- Use 'generate_memory_bank_template' to create new documentation

Query processed successfully! ✨
"""
    
    # Log successful execution
    logger.info(f"✅ Context analysis completed for {contributor_id}: {len(relevant_files)} files analyzed")
    
    return response 

@mcp.tool()
def generate_memory_bank_template(file_name: str = "") -> str:
    """
    Generate a memory bank template file with proper structure.
    
    Args:
        file_name: Name of the template file to create
        
    Returns:
        str: Success message with template details
    """
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
        logger = logging.getLogger('memory_bank_template')
        logger.setLevel(logging.INFO)
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
    
    # Setup
    logger = setup_logging()
    contributor_id = get_contributor_id()
    memory_bank_path = Path("memory-bank")
    timestamp = f"{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')} [{contributor_id}]"
    
    if not file_name:
        return f"""
❓ Template File Name Required

Please provide a file name for the template.

Examples:
- "features/authentication.md"
- "tech_specs/modules/user_management.md"
- "devops/monitoring.md"
- "context/user_personas.md"

Timestamp: {timestamp}
"""
    
    # Log the operation
    logger.info(f"📄 Template generation requested by {contributor_id}: {file_name}")
    
    # Ensure .md extension
    if not file_name.endswith('.md'):
        file_name += '.md'
    
    # Create full path
    full_path = memory_bank_path / file_name
    
    # Check if file already exists
    if full_path.exists():
        return f"""
❌ Template File Already Exists

The file '{file_name}' already exists in the memory bank.

Existing file: {full_path}
Timestamp: {timestamp}

💡 Suggestions:
1. Use a different file name
2. Use 'intelligent_context_executor' to view existing content
3. Edit the existing file directly
"""
    
    # Generate appropriate template based on file path
    title = file_name.replace('.md', '').replace('_', ' ').replace('/', ' - ').title()
    description = f"Documentation for {title}"
    
    # Determine template type based on path
    if 'tech_specs' in file_name:
        content_sections = [
            "## Technical Overview",
            "[Provide technical overview and architecture details]",
            "",
            "## Implementation Details",
            "[Detailed implementation specifications]",
            "",
            "## API Reference",
            "[API endpoints, methods, and parameters]",
            "",
            "## Data Models",
            "[Data structures and schemas]",
            "",
            "## Dependencies",
            "[Required dependencies and integrations]",
            "",
            "## Configuration",
            "[Configuration parameters and setup]",
            "",
            "## Testing",
            "[Testing approach and test cases]",
            "",
            "## Performance Considerations",
            "[Performance metrics and optimization notes]"
        ]
    elif 'devops' in file_name:
        content_sections = [
            "## Infrastructure Overview",
            "[Infrastructure components and architecture]",
            "",
            "## Deployment Process",
            "1. [Step 1]",
            "2. [Step 2]",
            "3. [Step 3]",
            "4. [Step 4]",
            "",
            "## Monitoring",
            "[Monitoring setup and metrics]",
            "",
            "## Troubleshooting",
            "[Common issues and solutions]",
            "",
            "## Maintenance",
            "[Maintenance procedures and schedules]"
        ]
    else:
        content_sections = [
            "## Overview",
            "[Provide an overview of this topic]",
            "",
            "## Details",
            "[Detailed information and specifications]",
            "",
            "## Usage",
            "[How to use or implement this]",
            "",
            "## Examples",
            "[Provide relevant examples]",
            "",
            "## Notes",
            "[Additional notes and considerations]"
        ]
    
    # Build complete template
    template_content = f"""---
title: {title}
description: {description}
last_updated: {timestamp}
version: 1.0
---

# {title}

{chr(10).join(content_sections)}

## Change History
- **{timestamp}**: Initial template created by {contributor_id}
"""
    
    # Generate and write template
    try:
        # Ensure parent directory exists
        full_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Write template to file
        full_path.write_text(template_content, encoding='utf-8')
        
        # Log successful creation
        logger.info(f"✅ Template created successfully: {file_name}")
        
        return f"""
✅ Template Created Successfully!

📄 File: {file_name}
📁 Full Path: {full_path}
👤 Created by: {contributor_id}
🕒 Timestamp: {timestamp}

📝 Template Structure:
- YAML frontmatter with metadata
- Structured content sections
- Placeholder content for customization
- Change history tracking

🎯 Next Steps:
1. Edit the template file with your specific content
2. Replace placeholder text with actual information
3. Use 'intelligent_context_executor' to get context for content
4. Update the file regularly as information changes

The template is ready for customization! ✨
"""
    
    except Exception as e:
        logger.error(f"❌ Template creation failed: {str(e)}")
        return f"""
❌ Template Creation Failed

An error occurred while creating the template:
{str(e)}

File: {file_name}
Timestamp: {timestamp}

Please check the file path and try again.
"""

@mcp.tool()
def analyze_project_summary(project_summary: str = "") -> str:
    """
    Analyze a project summary and provide structured insights.
    
    Args:
        project_summary: The project summary text to analyze
        
    Returns:
        str: Structured analysis with insights and recommendations
    """
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
        logger = logging.getLogger('memory_bank_analyze')
        logger.setLevel(logging.INFO)
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
    
    # Setup
    logger = setup_logging()
    contributor_id = get_contributor_id()
    timestamp = f"{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')} [{contributor_id}]"
    
    if not project_summary:
        return f"""
❌ Project Summary Required

Please provide a project summary to analyze.

Example usage:
- Paste your project description
- Include key features and technologies
- Mention goals and objectives

Timestamp: {timestamp}
"""
    
    # Log the operation
    logger.info(f"📊 Project analysis requested by {contributor_id}: {project_summary[:100]}...")
    
    # Analyze project summary - inline logic
    tech_keywords_list = [
        'api', 'database', 'frontend', 'backend', 'server', 'client',
        'authentication', 'authorization', 'security', 'deployment',
        'docker', 'kubernetes', 'aws', 'azure', 'gcp', 'cloud',
        'microservices', 'monolith', 'rest', 'graphql', 'websocket',
        'react', 'vue', 'angular', 'node', 'python', 'java', 'go',
        'mongodb', 'postgresql', 'mysql', 'redis', 'elasticsearch',
        'machine learning', 'ai', 'analytics', 'monitoring', 'logging'
    ]
    
    business_keywords_list = [
        'user', 'customer', 'business', 'revenue', 'profit', 'cost',
        'market', 'competition', 'strategy', 'growth', 'scalability',
        'performance', 'efficiency', 'productivity', 'automation',
        'integration', 'workflow', 'process', 'optimization'
    ]
    
    text_lower = project_summary.lower()
    tech_keywords = [kw for kw in tech_keywords_list if kw in text_lower]
    business_keywords = [kw for kw in business_keywords_list if kw in text_lower]
    
    # Identify project type
    if any(word in text_lower for word in ['web app', 'website', 'frontend', 'ui', 'ux']):
        project_type = "Web Application"
    elif any(word in text_lower for word in ['api', 'backend', 'server', 'microservice']):
        project_type = "Backend Service"
    elif any(word in text_lower for word in ['mobile', 'ios', 'android', 'app']):
        project_type = "Mobile Application"
    elif any(word in text_lower for word in ['data', 'analytics', 'ml', 'ai']):
        project_type = "Data/Analytics Platform"
    elif any(word in text_lower for word in ['devops', 'infrastructure', 'deployment']):
        project_type = "DevOps/Infrastructure"
    else:
        project_type = "General Software Project"
    
    # Determine complexity
    complexity_indicators = len(tech_keywords) + len(business_keywords)
    if complexity_indicators > 15:
        complexity = "High"
    elif complexity_indicators > 8:
        complexity = "Medium"
    else:
        complexity = "Low"
    
    # Generate recommendations
    recommendations = []
    
    if 'authentication' in text_lower or 'security' in text_lower:
        recommendations.append("Document security architecture and authentication flows")
    
    if any(word in text_lower for word in ['database', 'data', 'storage']):
        recommendations.append("Create data flow diagrams and database schemas")
    
    if any(word in text_lower for word in ['api', 'service', 'endpoint']):
        recommendations.append("Document API specifications and service interfaces")
    
    if any(word in text_lower for word in ['deployment', 'devops', 'infrastructure']):
        recommendations.append("Document deployment architecture and CI/CD processes")
    
    if any(word in text_lower for word in ['user', 'customer', 'stakeholder']):
        recommendations.append("Define user personas and stakeholder requirements")
    
    # Memory bank file suggestions
    suggested_files = []
    
    if project_type == "Web Application":
        suggested_files.extend([
            "tech_specs/system_architecture.md",
            "tech_specs/modules/frontend_architecture.md",
            "tech_specs/modules/backend_services.md",
            "devops/deployment_architecture.md"
        ])
    elif project_type == "Backend Service":
        suggested_files.extend([
            "tech_specs/api_reference.md",
            "tech_specs/system_architecture.md",
            "tech_specs/data_flow.md",
            "devops/deployment_architecture.md"
        ])
    elif project_type == "Mobile Application":
        suggested_files.extend([
            "tech_specs/modules/mobile_architecture.md",
            "tech_specs/system_architecture.md",
            "context/user_personas.md"
        ])
    
    # Always suggest these
    suggested_files.extend([
        "context/overview.md",
        "context/stakeholders.md",
        "dynamic_meta/change_log.md"
    ])
    
    # Remove duplicates
    suggested_files = list(set(suggested_files))
    
    # Log successful analysis
    logger.info(f"✅ Project analysis completed for {contributor_id}: {project_type}, {complexity} complexity")
    
    return f"""
📊 PROJECT ANALYSIS REPORT
Generated: {timestamp}
Analyzer: {contributor_id}

🎯 PROJECT TYPE: {project_type}
📈 COMPLEXITY: {complexity}

🔧 TECHNICAL KEYWORDS ({len(tech_keywords)}):
{', '.join(tech_keywords[:10])}{'...' if len(tech_keywords) > 10 else ''}

💼 BUSINESS KEYWORDS ({len(business_keywords)}):
{', '.join(business_keywords[:10])}{'...' if len(business_keywords) > 10 else ''}

📝 SUMMARY ANALYSIS:
- Word count: {len(project_summary.split())}
- Technical focus: {'High' if len(tech_keywords) > 8 else 'Medium' if len(tech_keywords) > 4 else 'Low'}
- Business focus: {'High' if len(business_keywords) > 6 else 'Medium' if len(business_keywords) > 3 else 'Low'}

🎯 RECOMMENDATIONS:
{chr(10).join(f"• {rec}" for rec in recommendations) if recommendations else "• No specific recommendations based on current analysis"}

📁 SUGGESTED MEMORY BANK FILES:
{chr(10).join(f"• {file}" for file in suggested_files[:8])}

🛠️ NEXT STEPS:
1. Use 'create_memory_bank_structure' to initialize your memory bank
2. Use 'generate_memory_bank_template' to create suggested files
3. Use 'intelligent_context_executor' to get context for specific areas
4. Start with high-priority files based on your project type

📊 ANALYSIS COMPLETE: Ready to structure your project documentation! ✨
"""

@mcp.tool()
def suggest_files_to_update(input_text: str = "") -> List[str]:
    """
    Suggest memory bank files to update based on input text analysis.
    
    Args:
        input_text: Text to analyze for file update suggestions
        
    Returns:
        List[str]: List of suggested file paths to update
    """
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
        logger = logging.getLogger('memory_bank_suggest')
        logger.setLevel(logging.INFO)
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
    
    # Setup
    logger = setup_logging()
    contributor_id = get_contributor_id()
    memory_bank_path = Path("memory-bank")
    timestamp = f"{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')} [{contributor_id}]"
    
    if not input_text:
        return [f"❌ Input text required for analysis. Timestamp: {timestamp}"]
    
    # Log the operation
    logger.info(f"📋 File suggestions requested by {contributor_id}: {input_text[:100]}...")
    
    # Analysis logic - inline implementation
    suggestions = []
    text_lower = input_text.lower()
    
    # Always suggest change log for any significant change
    suggestions.append("dynamic_meta/change_log.md")
    
    # Architecture and system changes
    if any(word in text_lower for word in ['architecture', 'system', 'design', 'structure', 'component']):
        suggestions.extend([
            "tech_specs/system_architecture.md",
            "tech_specs/data_flow.md"
        ])
    
    # API and service changes
    if any(word in text_lower for word in ['api', 'endpoint', 'service', 'interface', 'rest', 'graphql']):
        suggestions.extend([
            "tech_specs/api_reference.md",
            "tech_specs/system_architecture.md"
        ])
    
    # Database and data changes
    if any(word in text_lower for word in ['database', 'data', 'schema', 'model', 'storage', 'query']):
        suggestions.extend([
            "tech_specs/data_flow.md",
            "tech_specs/system_architecture.md"
        ])
    
    # Deployment and DevOps changes
    if any(word in text_lower for word in ['deploy', 'devops', 'ci/cd', 'pipeline', 'infrastructure', 'docker', 'kubernetes']):
        suggestions.extend([
            "devops/deployment_architecture.md",
            "devops/ci_cd_pipeline.md"
        ])
    
    # Configuration changes
    if any(word in text_lower for word in ['config', 'setting', 'environment', 'variable', 'parameter']):
        suggestions.append("dynamic_meta/config_map.md")
    
    # Decision and planning changes
    if any(word in text_lower for word in ['decision', 'choice', 'alternative', 'option', 'strategy']):
        suggestions.append("dynamic_meta/decision_logs.md")
    
    # User and stakeholder changes
    if any(word in text_lower for word in ['user', 'stakeholder', 'customer', 'requirement', 'persona']):
        suggestions.extend([
            "context/stakeholders.md",
            "context/overview.md"
        ])
    
    # Feature and functionality changes
    if any(word in text_lower for word in ['feature', 'functionality', 'capability', 'module', 'component']):
        suggestions.extend([
            "context/overview.md",
            "tech_specs/system_architecture.md"
        ])
    
    # Performance and monitoring changes
    if any(word in text_lower for word in ['performance', 'monitoring', 'metrics', 'logging', 'observability']):
        suggestions.extend([
            "devops/deployment_architecture.md",
            "tech_specs/system_architecture.md"
        ])
    
    # Security changes
    if any(word in text_lower for word in ['security', 'authentication', 'authorization', 'access', 'permission']):
        suggestions.extend([
            "tech_specs/system_architecture.md",
            "tech_specs/api_reference.md"
        ])
    
    # Testing changes
    if any(word in text_lower for word in ['test', 'testing', 'qa', 'quality', 'validation']):
        suggestions.extend([
            "tech_specs/system_architecture.md",
            "devops/ci_cd_pipeline.md"
        ])
    
    # Remove duplicates and sort
    suggestions = list(set(suggestions))
    suggestions.sort()
    
    # Filter to only existing files and add priority
    existing_files = []
    missing_files = []
    
    for suggestion in suggestions:
        file_path = memory_bank_path / suggestion
        if file_path.exists():
            existing_files.append(suggestion)
        else:
            missing_files.append(suggestion)
    
    # Prepare final suggestions with context
    final_suggestions = []
    
    if existing_files:
        final_suggestions.extend(existing_files)
    
    # Add missing files as creation suggestions
    if missing_files:
        final_suggestions.extend([f"CREATE: {file}" for file in missing_files[:3]])
    
    # Always include overview if it exists
    overview_path = "context/overview.md"
    if overview_path not in final_suggestions:
        overview_file = memory_bank_path / overview_path
        if overview_file.exists():
            final_suggestions.insert(0, overview_path)
    
    # Log successful analysis
    logger.info(f"✅ File suggestions completed for {contributor_id}: {len(final_suggestions)} files suggested")
    
    return final_suggestions[:10]  # Limit to top 10 suggestions

@mcp.tool()
def smart_content_analysis_and_routing(input_content: str = "") -> str:
    """
    Analyze input content and provide smart routing recommendations.
    
    Args:
        input_content: Content to analyze for routing decisions
        
    Returns:
        str: Analysis results with routing recommendations
    """
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
        logger = logging.getLogger('memory_bank_routing')
        logger.setLevel(logging.INFO)
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
    
    # Setup
    logger = setup_logging()
    contributor_id = get_contributor_id()
    memory_bank_path = Path("memory-bank")
    timestamp = f"{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')} [{contributor_id}]"
    
    if not input_content:
        return f"""
❓ Content Analysis Required

Please provide content to analyze for smart routing.

Examples:
- Code changes or implementations
- Architecture decisions
- Feature requirements
- Bug reports or issues
- Deployment procedures

Timestamp: {timestamp}
"""
    
    # Log the operation
    logger.info(f"🧭 Smart routing analysis requested by {contributor_id}: {input_content[:100]}...")
    
    # Content analysis - inline logic
    content_lower = input_content.lower()
    content_length = len(input_content)
    word_count = len(input_content.split())
    
    # Categorize content type
    content_categories = []
    
    if any(word in content_lower for word in ['class', 'function', 'method', 'import', 'def', 'const', 'var']):
        content_categories.append("Code Implementation")
    
    if any(word in content_lower for word in ['architecture', 'design', 'pattern', 'structure']):
        content_categories.append("Architecture/Design")
    
    if any(word in content_lower for word in ['api', 'endpoint', 'rest', 'graphql', 'service']):
        content_categories.append("API/Service")
    
    if any(word in content_lower for word in ['database', 'schema', 'query', 'model', 'table']):
        content_categories.append("Data/Database")
    
    if any(word in content_lower for word in ['deploy', 'devops', 'ci/cd', 'pipeline', 'infrastructure']):
        content_categories.append("DevOps/Deployment")
    
    if any(word in content_lower for word in ['user', 'requirement', 'feature', 'story', 'acceptance']):
        content_categories.append("Requirements/Features")
    
    if any(word in content_lower for word in ['bug', 'issue', 'error', 'fix', 'problem']):
        content_categories.append("Bug/Issue")
    
    if any(word in content_lower for word in ['test', 'testing', 'spec', 'validation']):
        content_categories.append("Testing/QA")
    
    if any(word in content_lower for word in ['config', 'setting', 'environment', 'variable']):
        content_categories.append("Configuration")
    
    if any(word in content_lower for word in ['decision', 'choice', 'alternative', 'option']):
        content_categories.append("Decision/Planning")
    
    # Determine primary category
    primary_category = content_categories[0] if content_categories else "General"
    
    # Generate routing recommendations
    routing_recommendations = []
    
    if "Code Implementation" in content_categories:
        routing_recommendations.extend([
            "tech_specs/system_architecture.md - Document code structure",
            "dynamic_meta/change_log.md - Record implementation changes",
            "tech_specs/api_reference.md - Update API documentation if applicable"
        ])
    
    if "Architecture/Design" in content_categories:
        routing_recommendations.extend([
            "tech_specs/system_architecture.md - Update architecture documentation",
            "tech_specs/data_flow.md - Document data flow changes",
            "dynamic_meta/decision_logs.md - Record architectural decisions"
        ])
    
    if "API/Service" in content_categories:
        routing_recommendations.extend([
            "tech_specs/api_reference.md - Update API specifications",
            "tech_specs/system_architecture.md - Document service architecture",
            "dynamic_meta/change_log.md - Record API changes"
        ])
    
    if "Data/Database" in content_categories:
        routing_recommendations.extend([
            "tech_specs/data_flow.md - Document data flow and schemas",
            "tech_specs/system_architecture.md - Update data architecture",
            "dynamic_meta/config_map.md - Document database configurations"
        ])
    
    if "DevOps/Deployment" in content_categories:
        routing_recommendations.extend([
            "devops/deployment_architecture.md - Update deployment procedures",
            "devops/ci_cd_pipeline.md - Document pipeline changes",
            "dynamic_meta/change_log.md - Record deployment changes"
        ])
    
    if "Requirements/Features" in content_categories:
        routing_recommendations.extend([
            "context/overview.md - Update project overview",
            "context/stakeholders.md - Document stakeholder requirements",
            "context/success_metrics.md - Define success criteria"
        ])
    
    if "Bug/Issue" in content_categories:
        routing_recommendations.extend([
            "dynamic_meta/change_log.md - Record bug fixes",
            "tech_specs/system_architecture.md - Update if architectural fix",
            "devops/deployment_architecture.md - Update if deployment related"
        ])
    
    if "Testing/QA" in content_categories:
        routing_recommendations.extend([
            "tech_specs/system_architecture.md - Document testing approach",
            "devops/ci_cd_pipeline.md - Update testing pipeline",
            "dynamic_meta/change_log.md - Record testing changes"
        ])
    
    if "Configuration" in content_categories:
        routing_recommendations.extend([
            "dynamic_meta/config_map.md - Document configuration changes",
            "devops/deployment_architecture.md - Update deployment configs",
            "dynamic_meta/change_log.md - Record configuration changes"
        ])
    
    if "Decision/Planning" in content_categories:
        routing_recommendations.extend([
            "dynamic_meta/decision_logs.md - Record decisions and rationale",
            "context/overview.md - Update project direction",
            "context/stakeholders.md - Update stakeholder impacts"
        ])
    
    # Remove duplicates and limit
    routing_recommendations = list(set(routing_recommendations))[:8]
    
    # Determine urgency level
    urgency_indicators = [
        'urgent', 'critical', 'immediate', 'asap', 'emergency',
        'breaking', 'production', 'live', 'hotfix'
    ]
    
    urgency_level = "High" if any(word in content_lower for word in urgency_indicators) else "Medium"
    
    # Generate action items
    action_items = []
    
    if urgency_level == "High":
        action_items.append("Prioritize immediate documentation updates")
        action_items.append("Notify relevant stakeholders of changes")
    
    action_items.extend([
        "Review and update suggested memory bank files",
        "Cross-reference with existing documentation",
        "Validate changes with team members"
    ])
    
    # Check which files exist
    existing_files = []
    missing_files = []
    
    for rec in routing_recommendations:
        file_path = rec.split(' - ')[0]
        full_path = memory_bank_path / file_path
        if full_path.exists():
            existing_files.append(rec)
        else:
            missing_files.append(rec)
    
    # Log successful analysis
    logger.info(f"✅ Smart routing completed for {contributor_id}: {primary_category}, {urgency_level} urgency")
    
    return f"""
🧭 SMART CONTENT ANALYSIS & ROUTING
Generated: {timestamp}
Analyzer: {contributor_id}

📊 CONTENT ANALYSIS:
- Word Count: {word_count}
- Character Count: {content_length}
- Primary Category: {primary_category}
- All Categories: {', '.join(content_categories) if content_categories else 'General'}
- Urgency Level: {urgency_level}

🎯 ROUTING RECOMMENDATIONS:

✅ EXISTING FILES TO UPDATE:
{chr(10).join(f"• {rec}" for rec in existing_files) if existing_files else "• No existing files match this content"}

❌ MISSING FILES TO CREATE:
{chr(10).join(f"• {rec}" for rec in missing_files) if missing_files else "• All suggested files already exist"}

🚀 ACTION ITEMS:
{chr(10).join(f"• {item}" for item in action_items)}

🛠️ RECOMMENDED TOOLS:
• suggest_files_to_update - Get additional file suggestions
• generate_memory_bank_template - Create missing files
• intelligent_context_executor - Get context for specific files

📈 PRIORITY MATRIX:
- High Priority: {len([r for r in routing_recommendations if 'change_log' in r or 'decision_logs' in r])} files
- Medium Priority: {len([r for r in routing_recommendations if 'system_architecture' in r or 'overview' in r])} files
- Low Priority: {len(routing_recommendations) - len([r for r in routing_recommendations if any(x in r for x in ['change_log', 'decision_logs', 'system_architecture', 'overview'])])} files

🎯 ROUTING COMPLETE: Content analyzed and recommendations generated! ✨
"""

@mcp.tool()
def auto_detect_project_changes() -> str:
    """
    Automatically detect project changes and suggest memory bank updates.
    
    Returns:
        str: Detected changes and update suggestions
    """
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
        logger = logging.getLogger('memory_bank_auto_detect')
        logger.setLevel(logging.INFO)
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
    
    # Setup
    logger = setup_logging()
    contributor_id = get_contributor_id()
    memory_bank_path = Path("memory-bank")
    timestamp = f"{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')} [{contributor_id}]"
    
    # Log the operation
    logger.info(f"🔍 Auto-detection requested by {contributor_id}")
    
    # Detect git changes - inline logic
    git_changes = {
        'git_available': False,
        'recent_commits': [],
        'modified_files': [],
        'new_files': [],
        'deleted_files': []
    }
    
    try:
        # Check if git is available
        git_result = subprocess.run(['git', 'status'], capture_output=True, text=True, timeout=5)
        if git_result.returncode == 0:
            git_changes['git_available'] = True
            
            # Get recent commits
            commits_result = subprocess.run(
                ['git', 'log', '--oneline', '-5'], 
                capture_output=True, text=True, timeout=10
            )
            if commits_result.returncode == 0:
                git_changes['recent_commits'] = commits_result.stdout.strip().split('\n')
            
            # Get modified files
            status_result = subprocess.run(
                ['git', 'status', '--porcelain'], 
                capture_output=True, text=True, timeout=10
            )
            if status_result.returncode == 0:
                for line in status_result.stdout.strip().split('\n'):
                    if line:
                        status_code = line[:2]
                        file_path = line[3:]
                        if status_code.strip() == 'M':
                            git_changes['modified_files'].append(file_path)
                        elif status_code.strip() in ['A', '??']:
                            git_changes['new_files'].append(file_path)
                        elif status_code.strip() == 'D':
                            git_changes['deleted_files'].append(file_path)
    
    except Exception as e:
        logger.warning(f"Git detection failed: {str(e)}")
    
    # Detect file system changes - inline logic
    file_changes = {
        'recent_files': [],
        'large_files': [],
        'config_files': []
    }
    
    try:
        # Get recent files (modified in last 24 hours)
        current_time = datetime.now().timestamp()
        for file_path in Path('.').rglob('*'):
            if file_path.is_file() and not file_path.name.startswith('.'):
                try:
                    mod_time = file_path.stat().st_mtime
                    if current_time - mod_time < 28800:  # 8 hours
                        file_changes['recent_files'].append(str(file_path))
                except:
                    continue
        
        # Limit to 10 most recent
        file_changes['recent_files'] = file_changes['recent_files'][:10]
        
        # Detect config files
        config_patterns = ['*.json', '*.yaml', '*.yml', '*.toml', '*.ini', '*.conf']
        for pattern in config_patterns:
            for file_path in Path('.').rglob(pattern):
                if file_path.is_file():
                    file_changes['config_files'].append(str(file_path))
        
        # Limit config files
        file_changes['config_files'] = file_changes['config_files'][:10]
    
    except Exception as e:
        logger.warning(f"File detection failed: {str(e)}")
    
    # Analyze the impact of detected changes - inline logic
    impact_analysis = {
        'suggested_updates': [],
        'priority_level': 'low',
        'change_categories': []
    }
    
    # Analyze git changes
    if git_changes['git_available']:
        if git_changes['recent_commits']:
            impact_analysis['change_categories'].append('code_changes')
            impact_analysis['suggested_updates'].append({
                'file': 'dynamic_meta/change_log.md',
                'reason': f"Document {len(git_changes['recent_commits'])} recent commits",
                'priority': 'high'
            })
        
        if git_changes['new_files']:
            impact_analysis['change_categories'].append('new_files')
            impact_analysis['suggested_updates'].append({
                'file': 'tech_specs/system_architecture.md',
                'reason': f"Update architecture for {len(git_changes['new_files'])} new files",
                'priority': 'medium'
            })
        
        if git_changes['deleted_files']:
            impact_analysis['change_categories'].append('deleted_files')
            impact_analysis['suggested_updates'].append({
                'file': 'dynamic_meta/change_log.md',
                'reason': f"Document {len(git_changes['deleted_files'])} deleted files",
                'priority': 'medium'
            })
    
    # Analyze file changes
    if file_changes['recent_files']:
        impact_analysis['change_categories'].append('recent_activity')
        if len(file_changes['recent_files']) > 5:
            impact_analysis['priority_level'] = 'high'
            impact_analysis['suggested_updates'].append({
                'file': 'context/overview.md',
                'reason': f"High activity detected: {len(file_changes['recent_files'])} recent files",
                'priority': 'high'
            })
    
    if file_changes['config_files']:
        impact_analysis['change_categories'].append('configuration')
        impact_analysis['suggested_updates'].append({
            'file': 'dynamic_meta/config_map.md',
            'reason': f"Update configuration documentation for {len(file_changes['config_files'])} config files",
            'priority': 'medium'
        })
    
    # Determine overall priority
    if len(impact_analysis['change_categories']) >= 3:
        impact_analysis['priority_level'] = 'high'
    elif len(impact_analysis['change_categories']) >= 2:
        impact_analysis['priority_level'] = 'medium'
    
    # Check which suggested files exist
    existing_updates = []
    missing_updates = []
    
    for update in impact_analysis['suggested_updates']:
        file_path = memory_bank_path / update['file']
        if file_path.exists():
            existing_updates.append(update)
        else:
            missing_updates.append(update)
    
    # Log successful detection
    logger.info(f"✅ Auto-detection completed for {contributor_id}: {len(impact_analysis['suggested_updates'])} suggestions")
    
    return f"""
🔍 Auto-Detect Project Changes
Generated: {timestamp}
Detector: {contributor_id}

📊 CHANGE DETECTION SUMMARY:
Priority Level: {impact_analysis['priority_level'].upper()}
Change Categories: {', '.join(impact_analysis['change_categories']) if impact_analysis['change_categories'] else 'None detected'}

🔄 GIT CHANGES:
Git Available: {'Yes' if git_changes['git_available'] else 'No'}
Recent Commits: {len(git_changes['recent_commits'])}
Modified Files: {len(git_changes['modified_files'])}
New Files: {len(git_changes['new_files'])}
Deleted Files: {len(git_changes['deleted_files'])}

📁 FILE SYSTEM CHANGES:
Recent Files (24h): {len(file_changes['recent_files'])}
Config Files: {len(file_changes['config_files'])}

🎯 SUGGESTED UPDATES:

✅ EXISTING FILES TO UPDATE:
{chr(10).join(f"• {u['file']} ({u['priority']} priority) - {u['reason']}" for u in existing_updates) if existing_updates else 'None identified'}

❌ MISSING FILES TO CREATE:
{chr(10).join(f"• {u['file']} ({u['priority']} priority) - {u['reason']}" for u in missing_updates) if missing_updates else 'None identified'}

📋 RECENT ACTIVITY:
{chr(10).join(f"• {commit}" for commit in git_changes['recent_commits'][:3]) if git_changes['recent_commits'] else 'No recent commits'}

🛠️ RECOMMENDED ACTIONS:
1. Review and update suggested files
2. Create missing files using 'generate_memory_bank_template'
3. Use 'intelligent_context_executor' for additional context
4. Update change log to record this content addition

💡 DETECTION INSIGHTS:
- Change detection frequency: {'High' if impact_analysis['priority_level'] == 'high' else 'Normal'}
- Update priority: {impact_analysis['priority_level'].title()}
- Categories affected: {len(impact_analysis['change_categories'])}
"""

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