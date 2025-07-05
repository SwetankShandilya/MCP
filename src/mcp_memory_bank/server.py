"""
Memory Bank MCP Server - Self-Contained Tools

This module contains all the MCP tool implementations with embedded logic.
Each tool is completely self-contained and independent, with all required
logic written directly within the tool function.
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


# from .middlewares import (
#     ContextAwarePromptInjectionMiddleware,
#     ToolLoggingMiddleware,
#     MemoryCompletenessEnforcementMiddleware,
#     CrossReferenceRedundancyMiddleware,
#     AgentBehaviorProfilerMiddleware
# )

mcp = FastMCP("memory-bank-helper")

# mcp.add_middleware(ContextAwarePromptInjectionMiddleware())
# mcp.add_middleware(ToolLoggingMiddleware())
# mcp.add_middleware(MemoryCompletenessEnforcementMiddleware())
# mcp.add_middleware(CrossReferenceRedundancyMiddleware())
# mcp.add_middleware(AgentBehaviorProfilerMiddleware())




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
        # Extract title from template if it exists
        if "title:" in template_content:
            return template_content.replace(
                "last_updated: [timestamp]", 
                f"last_updated: {timestamp}"
            ).replace(
                "created_by: [contributor]",
                f"created_by: {contributor_id}"
            )
        else:
            # Add basic metadata header
            return f"""---
title: Generated Template
description: Auto-generated template file
last_updated: {timestamp}
created_by: {contributor_id}
version: 1.0
---

{template_content}"""
    
    # Setup
    logger = setup_logging()
    contributor_id = get_contributor_id()
    memory_bank_path = Path("memory-bank")
    timestamp = f"{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')} [{contributor_id}]"
    
    # Log the operation
    logger.info(f"🏗️ Memory bank structure creation initiated by {contributor_id}")
    
    # Define directory structure
    directories = [
        "context",
        "tech_specs",
        "tech_specs/modules",
        "devops",
        "dynamic_meta"
    ]
    
    # Define template files using imported templates
    templates = {
        "memory_bank_instructions.md": create_template_with_metadata(MEMORY_BANK_INSTRUCTIONS, timestamp, contributor_id),
        "context/overview.md": create_template_with_metadata(OVERVIEW_TEMPLATE, timestamp, contributor_id),
        "context/stakeholders.md": create_template_with_metadata(STAKEHOLDERS_TEMPLATE, timestamp, contributor_id),
        "context/success_metrics.md": create_template_with_metadata(SUCCESS_METRICS_TEMPLATE, timestamp, contributor_id),
        "tech_specs/system_architecture.md": create_template_with_metadata(SYSTEM_ARCHITECTURE_TEMPLATE, timestamp, contributor_id),
        "tech_specs/data_flow.md": create_template_with_metadata(DATA_FLOW_TEMPLATE, timestamp, contributor_id),
        "tech_specs/api_reference.md": create_template_with_metadata(API_REFERENCE_TEMPLATE, timestamp, contributor_id),
        "devops/deployment_architecture.md": create_template_with_metadata(DEPLOYMENT_ARCHITECTURE_TEMPLATE, timestamp, contributor_id),
        "devops/ci_cd_pipeline.md": create_template_with_metadata(CI_CD_PIPELINE_TEMPLATE, timestamp, contributor_id),
        "dynamic_meta/change_log.md": create_template_with_metadata(CHANGE_LOG_TEMPLATE, timestamp, contributor_id),
        "dynamic_meta/decision_logs.md": create_template_with_metadata(DECISION_LOGS_TEMPLATE, timestamp, contributor_id),
        "dynamic_meta/config_map.md": create_template_with_metadata(CONFIG_MAP_TEMPLATE, timestamp, contributor_id),
    }
    
    # Create directories
    created_dirs = []
    for directory in directories:
        dir_path = memory_bank_path / directory
        dir_path.mkdir(parents=True, exist_ok=True)
        created_dirs.append(directory)
    
    # Create template files
    created_files = []
    for file_path, content in templates.items():
        full_path = memory_bank_path / file_path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_text(content, encoding='utf-8')
        created_files.append(file_path)
    
    # Log successful creation
    logger.info(f"✅ Memory bank structure created successfully by {contributor_id}")
    logger.info(f"📁 Created {len(created_dirs)} directories: {', '.join(created_dirs)}")
    logger.info(f"📄 Created {len(created_files)} template files")
    
    return f"""
✅ Memory Bank Structure Created Successfully!

📊 Summary:
- Directories created: {len(created_dirs)}
- Template files created: {len(created_files)}
- Created by: {contributor_id}
- Timestamp: {timestamp}

📁 Directory Structure:
{chr(10).join(f"  📁 {d}/" for d in created_dirs)}

📄 Template Files:
{chr(10).join(f"  📄 {f}" for f in created_files)}

🎯 Next Steps:
1. Review and customize the template files
2. Use 'intelligent_context_executor' to get project context
3. Update files with project-specific information
4. Use other MCP tools for ongoing maintenance

The memory bank is now ready for use! 🚀
"""

@mcp.tool() 
def intelligent_context_executor(user_query: str = "") -> str:
    """
    Intelligent context executor that provides comprehensive project context.
    
    Args:
        user_query: The user's query or request for context
        
    Returns:
        str: Comprehensive context response with relevant files and tool suggestions
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
        """Extract content from file, skipping YAML frontmatter"""
        try:
            content = file_path.read_text(encoding='utf-8')
            lines = content.split('\n')
            
            # Find YAML frontmatter end marker
            yaml_end = 0
            if lines and lines[0].strip().startswith('---'):
                for i, line in enumerate(lines[1:], 1):
                    if line.strip() == '---':
                        yaml_end = i + 1
                        break
            
            # Extract only content, skip YAML frontmatter
            content_lines = lines[yaml_end:yaml_end+line_count]
            return '\n'.join(content_lines)
        except Exception as e:
            return f"Error reading file: {str(e)}"
    
    def calculate_relevance_score(file_path, query_words):
        """Calculate relevance score for a file based on query"""
        try:
            content = file_path.read_text(encoding='utf-8')
            
            score = 0.0
            
            # Score based on path relevance
            path_words = set(str(file_path).lower().replace('/', ' ').replace('_', ' ').split())
            score += len(query_words.intersection(path_words)) * 2
            
            # Score based on content relevance (first 300 chars)
            content_words = set(content.lower()[:300].split())
            score += len(query_words.intersection(content_words))
            
            return score
        except Exception:
            return 0.0
    
    def get_relevant_files(memory_bank_path, user_query, mandatory_files, max_files=3):
        """Get relevant files based on query"""
        if not user_query:
            return []
        
        mandatory_file_set = set(mandatory_files)
        scored_files = []
        query_words = set(user_query.lower().split())
        
        for md_file in memory_bank_path.rglob("*.md"):
            if md_file.is_file():
                relative_path = str(md_file.relative_to(memory_bank_path))
                if relative_path not in mandatory_file_set:
                    score = calculate_relevance_score(md_file, query_words)
                    if score > 0:
                        content = extract_content_without_yaml(md_file, 15)
                        scored_files.append((relative_path, content, score))
        
        # Sort by score and get top files
        scored_files.sort(key=lambda x: x[2], reverse=True)
        return scored_files[:max_files]
    
    def generate_tool_suggestions(user_query):
        """Generate tool suggestions based on query"""
        tool_suggestions = []
        query_lower = user_query.lower()
        
        if any(word in query_lower for word in ['create', 'generate', 'template', 'new']):
            tool_suggestions.append("🛠️ generate_memory_bank_template - Create new template files")
        
        if any(word in query_lower for word in ['analyze', 'summary', 'overview']):
            tool_suggestions.append("🛠️ analyze_project_summary - Analyze project information")
        
        if any(word in query_lower for word in ['update', 'modify', 'change', 'edit']):
            tool_suggestions.append("🛠️ suggest_files_to_update - Get file update suggestions")
        
        if any(word in query_lower for word in ['route', 'organize', 'structure']):
            tool_suggestions.append("🛠️ smart_project_analysis_and_routing - Analyze and route content")
        
        if any(word in query_lower for word in ['detect', 'changes', 'diff']):
            tool_suggestions.append("🛠️ auto_detect_project_changes - Detect project changes")
        
        # Default suggestions if no specific matches
        if not tool_suggestions:
            tool_suggestions = [
                "🛠️ generate_memory_bank_template - Create new template files",
                "🛠️ analyze_project_summary - Analyze project information",
                "🛠️ suggest_files_to_update - Get file update suggestions",
                "🛠️ smart_project_analysis_and_routing - Analyze and route content"
            ]
        
        return tool_suggestions
    
    # Setup
    logger = setup_logging()
    contributor_id = get_contributor_id()
    memory_bank_path = Path("memory-bank")
    timestamp = f"{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')} [{contributor_id}]"
    
    # Log the operation
    logger.info(f"🧠 Context execution requested by {contributor_id}: {user_query[:100]}...")
    
    # Check if memory bank exists
    if not memory_bank_path.exists():
        return f"""
❌ Memory Bank Not Found

The memory-bank directory doesn't exist yet. Please run 'create_memory_bank_structure' first to initialize the memory bank.

Query: {user_query}
Timestamp: {timestamp}
"""
    
    # Extract context from mandatory files
    mandatory_files = ["context/overview.md", "dynamic_meta/change_log.md", "dynamic_meta/decision_logs.md"]
    mandatory_context = []
    
    for file_path in mandatory_files:
        full_path = memory_bank_path / file_path
        if full_path.exists():
            content = extract_content_without_yaml(full_path, 20)
            mandatory_context.append({"path": file_path, "content": content})
        else:
            mandatory_context.append({"path": file_path, "error": "File not found"})
    
    # Get additional relevant files based on query
    relevant_files = get_relevant_files(memory_bank_path, user_query, mandatory_files)
    
    # Build context response
    context_sections = []
    
    # Add mandatory context
    for ctx in mandatory_context:
        if "error" not in ctx:
            context_sections.append(f"""
📄 {ctx['path']}:
{ctx['content']}
""")
        else:
            context_sections.append(f"""
❌ {ctx['path']}: {ctx['error']}
""")
    
    # Add relevant context
    if relevant_files:
        context_sections.append("\n🎯 Additional Relevant Context:")
        for file_path, content, _ in relevant_files:
            context_sections.append(f"""
📄 {file_path}:
{content}
""")
    
    # Generate tool suggestions
    tool_suggestions = generate_tool_suggestions(user_query)
    
    # Log successful context execution
    logger.info(f"✅ Context executed successfully for query: {user_query[:50]}...")
    
    return f"""
🧠 Intelligent Context Executor
Query: {user_query}
Generated: {timestamp}

📚 PROJECT CONTEXT:
{''.join(context_sections)}

🎯 RECOMMENDED TOOLS:
{chr(10).join(tool_suggestions)}

💡 USAGE NOTES:
- This context is based on your memory bank files
- Use the suggested tools for specific operations
- Update memory bank files regularly for better context
- Query-specific files are prioritized based on relevance

🔄 NEXT STEPS:
1. Review the provided context
2. Use recommended tools for specific tasks
3. Update memory bank files as needed
4. Re-run this tool for updated context
"""

@mcp.tool()
def generate_memory_bank_template(file_name: str = "") -> str:
    """
    Generate a new memory bank template file with proper structure.
    
    Args:
        file_name: Name of the template file to create
        
    Returns:
        str: Success message with template details
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
    logger = logging.getLogger('memory_bank_template')
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
    
    if not file_name:
        return f"""
❌ File Name Required

Please provide a file name for the template.

Examples:
- "tech_specs/database_schema.md"
- "devops/monitoring_setup.md"
- "context/user_personas.md"

Timestamp: {timestamp}
"""
    
    # Log the operation
    logger.info(f"📝 Template generation requested by {contributor_id}: {file_name}")
    
    # Ensure .md extension
    if not file_name.endswith('.md'):
        file_name += '.md'
    
    # Create full path
    full_path = memory_bank_path / file_name
    
    # Check if file already exists
    if full_path.exists():
        return f"""
⚠️ File Already Exists

The file '{file_name}' already exists in the memory bank.
Use a different name or delete the existing file first.

Existing file path: {full_path}
Timestamp: {timestamp}
"""
    
    # Generate template content based on file path - inline logic
    # Extract title from file name
    title = Path(file_name).stem.replace('_', ' ').title()
    
    # Generate description based on path
    path_parts = Path(file_name).parts
    if 'context' in path_parts:
        description = f"Context information for {title.lower()}"
    elif 'tech_specs' in path_parts:
        description = f"Technical specifications for {title.lower()}"
    elif 'devops' in path_parts:
        description = f"DevOps and operational information for {title.lower()}"
    elif 'dynamic_meta' in path_parts:
        description = f"Dynamic metadata for {title.lower()}"
    else:
        description = f"Documentation for {title.lower()}"
    
    # Generate content sections based on category
    content_sections = []
    
    if 'context' in path_parts:
        content_sections = [
            "## Overview",
            "[Provide a high-level overview of this context area]",
            "",
            "## Key Information",
            "- [Key point 1]",
            "- [Key point 2]",
            "- [Key point 3]",
            "",
            "## Stakeholders",
            "- [Stakeholder 1]: [Role/Responsibility]",
            "- [Stakeholder 2]: [Role/Responsibility]",
            "",
            "## Impact",
            "[Describe the impact and importance of this context]"
        ]
    elif 'tech_specs' in path_parts:
        content_sections = [
            "## Technical Overview",
            "[Provide technical overview and purpose]",
            "",
            "## Architecture",
            "[Describe the architecture and design]",
            "",
            "## Implementation Details",
            "### Components",
            "- [Component 1]: [Description]",
            "- [Component 2]: [Description]",
            "",
            "### Dependencies",
            "- [Dependency 1]: [Version/Purpose]",
            "- [Dependency 2]: [Version/Purpose]",
            "",
            "## Configuration",
            "[Configuration details and settings]",
            "",
            "## API/Interface",
            "[API endpoints, interfaces, or usage patterns]"
        ]
    elif 'devops' in path_parts:
        content_sections = [
            "## Purpose",
            "[Describe the DevOps purpose and goals]",
            "",
            "## Infrastructure",
            "[Infrastructure components and setup]",
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
    logger = logging.getLogger('memory_bank_analyze')
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
    # Extract keywords
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
    elif any(word in text_lower for word in ['data', 'analytics', 'machine learning', 'ai']):
        project_type = "Data/Analytics Platform"
    elif any(word in text_lower for word in ['devops', 'infrastructure', 'deployment']):
        project_type = "DevOps/Infrastructure"
    elif any(word in text_lower for word in ['game', 'gaming', 'entertainment']):
        project_type = "Gaming/Entertainment"
    else:
        project_type = "General Software Project"
    
    # Suggest architecture patterns
    architecture_patterns = []
    
    if any(word in text_lower for word in ['microservice', 'distributed', 'scalable']):
        architecture_patterns.append("Microservices Architecture")
    
    if any(word in text_lower for word in ['event', 'message', 'queue', 'async']):
        architecture_patterns.append("Event-Driven Architecture")
    
    if any(word in text_lower for word in ['api', 'rest', 'graphql']):
        architecture_patterns.append("API-First Architecture")
    
    if any(word in text_lower for word in ['layer', 'tier', 'separation']):
        architecture_patterns.append("Layered Architecture")
    
    if any(word in text_lower for word in ['serverless', 'lambda', 'function']):
        architecture_patterns.append("Serverless Architecture")
    
    if not architecture_patterns:
        architecture_patterns.append("Monolithic Architecture")
    
    # Identify technology stack
    tech_stack = {
        'frontend': [],
        'backend': [],
        'database': [],
        'infrastructure': [],
        'tools': []
    }
    
    # Frontend technologies
    frontend_techs = ['react', 'vue', 'angular', 'svelte', 'html', 'css', 'javascript', 'typescript']
    tech_stack['frontend'] = [tech for tech in frontend_techs if tech in text_lower]
    
    # Backend technologies
    backend_techs = ['node', 'python', 'java', 'go', 'php', 'ruby', 'c#', 'scala']
    tech_stack['backend'] = [tech for tech in backend_techs if tech in text_lower]
    
    # Database technologies
    db_techs = ['postgresql', 'mysql', 'mongodb', 'redis', 'elasticsearch', 'sqlite']
    tech_stack['database'] = [tech for tech in db_techs if tech in text_lower]
    
    # Infrastructure
    infra_techs = ['docker', 'kubernetes', 'aws', 'azure', 'gcp', 'heroku', 'netlify']
    tech_stack['infrastructure'] = [tech for tech in infra_techs if tech in text_lower]
    
    # Tools
    tool_techs = ['git', 'jenkins', 'github', 'gitlab', 'jira', 'slack']
    tech_stack['tools'] = [tech for tech in tool_techs if tech in text_lower]
    
    # Generate recommendations
    recommendations = []
    
    if 'security' in tech_keywords:
        recommendations.append("🔒 Implement comprehensive security measures including authentication, authorization, and data encryption")
    
    if 'scalability' in business_keywords:
        recommendations.append("📈 Design for horizontal scaling with load balancing and distributed architecture")
    
    if 'performance' in business_keywords:
        recommendations.append("⚡ Implement caching strategies and performance monitoring")
    
    if 'api' in tech_keywords:
        recommendations.append("🔌 Design RESTful APIs with proper versioning and documentation")
    
    if not recommendations:
        recommendations.append("📋 Consider implementing proper logging, monitoring, and testing strategies")
    
    # Log successful analysis
    logger.info(f"✅ Project analysis completed for {contributor_id}")
    
    return f"""
📊 Project Analysis Report
Generated: {timestamp}
Analyst: {contributor_id}

📝 PROJECT SUMMARY:
{project_summary[:500]}{'...' if len(project_summary) > 500 else ''}

🎯 PROJECT TYPE: {project_type}

🔧 TECHNICAL KEYWORDS:
{', '.join(tech_keywords) if tech_keywords else 'None identified'}

💼 BUSINESS KEYWORDS:
{', '.join(business_keywords) if business_keywords else 'None identified'}

🏗️ SUGGESTED ARCHITECTURE PATTERNS:
{chr(10).join(f"• {pattern}" for pattern in architecture_patterns)}

💻 IDENTIFIED TECHNOLOGY STACK:
• Frontend: {', '.join(tech_stack['frontend']) if tech_stack['frontend'] else 'Not specified'}
• Backend: {', '.join(tech_stack['backend']) if tech_stack['backend'] else 'Not specified'}
• Database: {', '.join(tech_stack['database']) if tech_stack['database'] else 'Not specified'}
• Infrastructure: {', '.join(tech_stack['infrastructure']) if tech_stack['infrastructure'] else 'Not specified'}
• Tools: {', '.join(tech_stack['tools']) if tech_stack['tools'] else 'Not specified'}

💡 RECOMMENDATIONS:
{chr(10).join(recommendations)}

📋 SUGGESTED MEMORY BANK FILES TO CREATE:
• context/project_overview.md - Detailed project description
• tech_specs/system_architecture.md - Architecture documentation
• tech_specs/api_reference.md - API documentation
• devops/deployment_architecture.md - Deployment strategy
• context/stakeholders.md - Project stakeholders

🔄 NEXT STEPS:
1. Use 'generate_memory_bank_template' to create suggested files
2. Update templates with project-specific information
3. Use 'suggest_files_to_update' for ongoing maintenance
4. Regular analysis updates as project evolves
"""


@mcp.tool()     
def suggest_files_to_update(input_text: str = "") -> List[str]:
    """
    Suggest memory bank files to update based on input text analysis.
    
    Args:
        input_text: Text to analyze for file update suggestions
        
    Returns:
        List[str]: List of suggested files to update with reasons
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
    logger = logging.getLogger('memory_bank_suggest')
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
    
    if not input_text:
        return [f"""
❌ Input Text Required

Please provide text to analyze for file update suggestions.

Examples:
- Code changes or new features
- Architecture decisions
- Bug fixes or improvements
- New requirements or specifications

Timestamp: {timestamp}
"""]
    
    # Log the operation
    logger.info(f"🎯 File update suggestions requested by {contributor_id}: {input_text[:100]}...")
    
    # Analyze input text for file suggestions - inline logic
    file_suggestions = {}
    text_lower = input_text.lower()
    
    # Context files
    if any(word in text_lower for word in ['overview', 'description', 'purpose', 'goal', 'objective']):
        file_suggestions['context/overview.md'] = "Project overview and description updates"
    
    if any(word in text_lower for word in ['stakeholder', 'team', 'role', 'responsibility', 'owner']):
        file_suggestions['context/stakeholders.md'] = "Stakeholder information and roles"
    
    if any(word in text_lower for word in ['metric', 'kpi', 'success', 'performance', 'measure']):
        file_suggestions['context/success_metrics.md'] = "Success metrics and KPIs"
    
    # Technical specifications
    if any(word in text_lower for word in ['architecture', 'design', 'pattern', 'structure', 'component']):
        file_suggestions['tech_specs/system_architecture.md'] = "System architecture and design patterns"
    
    if any(word in text_lower for word in ['api', 'endpoint', 'rest', 'graphql', 'interface']):
        file_suggestions['tech_specs/api_reference.md'] = "API documentation and endpoints"
    
    if any(word in text_lower for word in ['data', 'flow', 'pipeline', 'process', 'transformation']):
        file_suggestions['tech_specs/data_flow.md'] = "Data flow and processing pipelines"
    
    if any(word in text_lower for word in ['module', 'service', 'microservice', 'component']):
        file_suggestions['tech_specs/modules/'] = "Module-specific technical specifications"
    
    # DevOps files
    if any(word in text_lower for word in ['deploy', 'deployment', 'infrastructure', 'server', 'cloud']):
        file_suggestions['devops/deployment_architecture.md'] = "Deployment and infrastructure setup"
    
    if any(word in text_lower for word in ['ci/cd', 'pipeline', 'build', 'test', 'automation']):
        file_suggestions['devops/ci_cd_pipeline.md'] = "CI/CD pipeline and automation"
    
    # Dynamic metadata
    if any(word in text_lower for word in ['change', 'update', 'modify', 'fix', 'feature']):
        file_suggestions['dynamic_meta/change_log.md'] = "Change log and modification history"
    
    if any(word in text_lower for word in ['decision', 'choice', 'option', 'alternative', 'rationale']):
        file_suggestions['dynamic_meta/decision_logs.md'] = "Decision logs and rationale"
    
    if any(word in text_lower for word in ['config', 'configuration', 'setting', 'environment', 'variable']):
        file_suggestions['dynamic_meta/config_map.md'] = "Configuration and environment settings"
    
    # Check which files exist
    existing_files = []
    missing_files = []
    
    for file_path, reason in file_suggestions.items():
        full_path = memory_bank_path / file_path
        if file_path.endswith('/'):  # Directory suggestion
            if full_path.exists():
                existing_files.append(f"📁 {file_path} - {reason}")
            else:
                missing_files.append(f"📁 {file_path} - {reason} (Directory needs creation)")
        else:  # File suggestion
            if full_path.exists():
                existing_files.append(f"📄 {file_path} - {reason}")
            else:
                missing_files.append(f"📄 {file_path} - {reason} (File needs creation)")
    
    # Generate priority suggestions
    priority_suggestions = []
    
    # Always suggest change log for any input
    if 'dynamic_meta/change_log.md' not in file_suggestions:
        priority_suggestions.append("📄 dynamic_meta/change_log.md - Record this change/update")
    
    # Suggest overview for significant changes
    if len(input_text) > 200 and 'context/overview.md' not in file_suggestions:
        priority_suggestions.append("📄 context/overview.md - Update project overview if needed")
    
    # Log successful suggestion generation
    logger.info(f"✅ File suggestions generated for {contributor_id}: {len(file_suggestions)} files")
    
    result = [f"""
🎯 File Update Suggestions
Generated: {timestamp}
Analyst: {contributor_id}

📝 INPUT ANALYSIS:
{input_text[:300]}{'...' if len(input_text) > 300 else ''}

📋 SUGGESTED FILES TO UPDATE:

✅ EXISTING FILES:
{chr(10).join(existing_files) if existing_files else 'None identified'}

❌ MISSING FILES (Create First):
{chr(10).join(missing_files) if missing_files else 'None identified'}

⭐ PRIORITY SUGGESTIONS:
{chr(10).join(priority_suggestions) if priority_suggestions else 'None identified'}

🛠️ RECOMMENDED ACTIONS:
1. Create missing files using 'generate_memory_bank_template'
2. Update existing files with relevant information
3. Use 'intelligent_context_executor' for context before updating
4. Update change log with this modification

📊 ANALYSIS SUMMARY:
- Total suggestions: {len(file_suggestions)}
- Existing files: {len(existing_files)}
- Missing files: {len(missing_files)}
- Priority items: {len(priority_suggestions)}
"""]
    
    return result



@mcp.tool()                 
def smart_project_analysis_and_routing(input_content: str = "") -> str:
    """
    Smart project analysis and routing for content organization.
    
    Args:
        input_content: Content to analyze and route to appropriate memory bank sections
        
    Returns:
        str: Analysis results with routing recommendations
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
    logger = logging.getLogger('memory_bank_routing')
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
    
    if not input_content:
        return f"""
❌ Input Content Required

Please provide content to analyze and route.

Examples:
- Technical documentation
- Architecture decisions
- Code changes or features
- Project requirements
- Meeting notes or discussions

Timestamp: {timestamp}
"""
    
    # Log the operation
    logger.info(f"🧠 Smart routing requested by {contributor_id}: {input_content[:100]}...")
    
    # Content analysis and routing logic - all inline
    content_lower = input_content.lower()
    routing_analysis = {
        'primary_category': 'general',
        'confidence': 0.0,
        'suggested_files': [],
        'content_type': 'unknown',
        'key_topics': []
    }
    
    # Category scoring
    category_scores = {
        'context': 0,
        'tech_specs': 0,
        'devops': 0,
        'dynamic_meta': 0
    }
    
    # Context indicators
    context_indicators = ['overview', 'stakeholder', 'business', 'goal', 'objective', 'requirement', 'user', 'customer']
    category_scores['context'] = sum(1 for indicator in context_indicators if indicator in content_lower)
    
    # Technical specifications indicators
    tech_indicators = ['architecture', 'design', 'pattern', 'structure', 'component']
    category_scores['tech_specs'] = sum(1 for indicator in tech_indicators if indicator in content_lower)
    
    # DevOps indicators
    devops_indicators = ['deploy', 'infrastructure', 'server', 'cloud', 'pipeline', 'ci/cd', 'monitoring', 'build']
    category_scores['devops'] = sum(1 for indicator in devops_indicators if indicator in content_lower)
    
    # Dynamic metadata indicators
    meta_indicators = ['change', 'decision', 'config', 'update', 'modify', 'log', 'history', 'version']
    category_scores['dynamic_meta'] = sum(1 for indicator in meta_indicators if indicator in content_lower)
    
    # Determine primary category
    max_score = max(category_scores.values())
    if max_score > 0:
        routing_analysis['primary_category'] = max(category_scores, key=category_scores.get)
        routing_analysis['confidence'] = max_score / len(input_content.split()) * 100
    
    # Determine content type
    if any(word in content_lower for word in ['class', 'function', 'method', 'import', 'def', 'var', 'const']):
        routing_analysis['content_type'] = 'code'
    elif any(word in content_lower for word in ['# ', '## ', '### ', 'markdown', 'documentation']):
        routing_analysis['content_type'] = 'documentation'
    elif any(word in content_lower for word in ['meeting', 'discussion', 'notes', 'agenda']):
        routing_analysis['content_type'] = 'meeting_notes'
    elif any(word in content_lower for word in ['decision', 'choice', 'option', 'alternative']):
        routing_analysis['content_type'] = 'decision_record'
    elif any(word in content_lower for word in ['bug', 'issue', 'fix', 'error', 'problem']):
        routing_analysis['content_type'] = 'issue_report'
    else:
        routing_analysis['content_type'] = 'general_content'
    
    # Generate specific file routing suggestions based on analysis - inline
    routing_suggestions = []
    primary_category = routing_analysis['primary_category']
    content_type = routing_analysis['content_type']
    
    # Category-based routing
    if primary_category == 'context':
        if 'overview' in input_content.lower():
            routing_suggestions.append({
                'file': 'context/overview.md',
                'reason': 'Contains project overview information',
                'priority': 'high'
            })
        if any(word in input_content.lower() for word in ['stakeholder', 'team', 'role']):
            routing_suggestions.append({
                'file': 'context/stakeholders.md',
                'reason': 'Contains stakeholder information',
                'priority': 'high'
            })
        if any(word in input_content.lower() for word in ['metric', 'kpi', 'success', 'performance']):
            routing_suggestions.append({
                'file': 'context/success_metrics.md',
                'reason': 'Contains success metrics and KPIs',
                'priority': 'medium'
            })
    
    elif primary_category == 'tech_specs':
        if any(word in input_content.lower() for word in ['architecture', 'design', 'pattern']):
            routing_suggestions.append({
                'file': 'tech_specs/system_architecture.md',
                'reason': 'Contains system architecture information',
                'priority': 'high'
            })
        if any(word in input_content.lower() for word in ['api', 'endpoint', 'rest', 'graphql']):
            routing_suggestions.append({
                'file': 'tech_specs/api_reference.md',
                'reason': 'Contains API documentation',
                'priority': 'high'
            })
        if any(word in input_content.lower() for word in ['data', 'flow', 'pipeline']):
            routing_suggestions.append({
                'file': 'tech_specs/data_flow.md',
                'reason': 'Contains data flow information',
                'priority': 'medium'
            })
    
    elif primary_category == 'devops':
        if any(word in input_content.lower() for word in ['deploy', 'deployment', 'infrastructure']):
            routing_suggestions.append({
                'file': 'devops/deployment_architecture.md',
                'reason': 'Contains deployment information',
                'priority': 'high'
            })
        if any(word in input_content.lower() for word in ['ci/cd', 'pipeline', 'build']):
            routing_suggestions.append({
                'file': 'devops/ci_cd_pipeline.md',
                'reason': 'Contains CI/CD pipeline information',
                'priority': 'high'
            })
    
    elif primary_category == 'dynamic_meta':
        if content_type == 'decision_record':
            routing_suggestions.append({
                'file': 'dynamic_meta/decision_logs.md',
                'reason': 'Contains decision information',
                'priority': 'high'
            })
        if any(word in input_content.lower() for word in ['change', 'update', 'modify']):
            routing_suggestions.append({
                'file': 'dynamic_meta/change_log.md',
                'reason': 'Contains change information',
                'priority': 'high'
            })
        if any(word in input_content.lower() for word in ['config', 'configuration', 'setting']):
            routing_suggestions.append({
                'file': 'dynamic_meta/config_map.md',
                'reason': 'Contains configuration information',
                'priority': 'medium'
            })
    
    # Content type specific routing
    if content_type == 'meeting_notes':
        routing_suggestions.append({
            'file': 'dynamic_meta/change_log.md',
            'reason': 'Meeting notes should be logged as changes',
            'priority': 'medium'
        })
    
    if content_type == 'issue_report':
        routing_suggestions.append({
            'file': 'dynamic_meta/change_log.md',
            'reason': 'Issue reports should be tracked in change log',
            'priority': 'high'
        })
    
    # Remove duplicates and sort by priority
    unique_suggestions = []
    seen_files = set()
    for suggestion in routing_suggestions:
        if suggestion['file'] not in seen_files:
            unique_suggestions.append(suggestion)
            seen_files.add(suggestion['file'])
    
    # Sort by priority (high first)
    priority_order = {'high': 0, 'medium': 1, 'low': 2}
    unique_suggestions.sort(key=lambda x: priority_order.get(x['priority'], 3))
    
    routing_suggestions = unique_suggestions
    
    # Extract key topics
    words = input_content.lower().split()
    key_topics = []
    topic_keywords = ['api', 'database', 'frontend', 'backend', 'authentication', 'security', 'deployment', 'testing']
    for keyword in topic_keywords:
        if keyword in words:
            key_topics.append(keyword)
    
    routing_analysis['key_topics'] = key_topics[:5]  # Limit to top 5
    
    # Check file existence
    existing_files = []
    missing_files = []
    
    for suggestion in routing_suggestions:
        file_path = memory_bank_path / suggestion['file']
        if file_path.exists():
            existing_files.append(suggestion)
        else:
            missing_files.append(suggestion)
    
    # Log successful routing
    logger.info(f"✅ Smart routing completed for {contributor_id}: {len(routing_suggestions)} suggestions")
    
    return f"""
🧠 Smart Project Analysis & Routing
Generated: {timestamp}
Analyst: {contributor_id}

📝 CONTENT ANALYSIS:
Content Type: {routing_analysis['content_type'].replace('_', ' ').title()}
Primary Category: {routing_analysis['primary_category'].replace('_', ' ').title()}
Confidence: {routing_analysis['confidence']:.1f}%
Key Topics: {', '.join(routing_analysis['key_topics']) if routing_analysis['key_topics'] else 'None identified'}

📄 CONTENT PREVIEW:
{input_content[:400]}{'...' if len(input_content) > 400 else ''}

🎯 ROUTING RECOMMENDATIONS:

✅ EXISTING FILES TO UPDATE:
{chr(10).join(f"• {s['file']} ({s['priority']} priority) - {s['reason']}" for s in existing_files) if existing_files else 'None identified'}

❌ MISSING FILES TO CREATE:
{chr(10).join(f"• {s['file']} ({s['priority']} priority) - {s['reason']}" for s in missing_files) if missing_files else 'None identified'}

📊 ROUTING ANALYSIS:
- Total suggestions: {len(routing_suggestions)}
- Existing files: {len(existing_files)}
- Missing files: {len(missing_files)}
- High priority: {len([s for s in routing_suggestions if s['priority'] == 'high'])}
- Medium priority: {len([s for s in routing_suggestions if s['priority'] == 'medium'])}

🛠️ RECOMMENDED ACTIONS:
1. Create missing files using 'generate_memory_bank_template'
2. Update existing files with the provided content
3. Use 'intelligent_context_executor' for additional context
4. Update change log to record this content addition

💡 ROUTING STRATEGY:
- Primary focus: {routing_analysis['primary_category'].replace('_', ' ').title()} files
- Content type: {routing_analysis['content_type'].replace('_', ' ').title()}
- Confidence level: {routing_analysis['confidence']:.1f}%
"""


@mcp.tool()                                 
def auto_detect_project_changes() -> str:
    """
    Auto-detect project changes and suggest memory bank updates.
    
    Returns:
        str: Detected changes and update suggestions
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
    logger = logging.getLogger('memory_bank_detect')
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
    logger.info(f"🔍 Auto-detection requested by {contributor_id}")
    
    # Detect git changes - inline logic
    git_changes = {
        'recent_commits': [],
        'modified_files': [],
        'new_files': [],
        'deleted_files': [],
        'git_available': False
    }
    
    try:
        # Check if git is available
        result = subprocess.run(['git', 'status'], capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            git_changes['git_available'] = True
            
            # Get recent commits (last 5)
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
                    if current_time - mod_time < 86400:  # 24 hours
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
    

def main():
    """Main entry point for the MCP server."""
    mcp.run()

if __name__ == "__main__":
    main()
