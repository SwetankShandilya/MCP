"""
FastMCP 2.9 Middleware Classes for Memory Bank Management

This module contains middleware classes that work with FastMCP 2.9's middleware system
to provide enhanced memory bank functionality and agent behavior tracking.
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

from fastmcp.server.middleware import Middleware, MiddlewareContext


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


class ContextAwarePromptInjectionMiddleware(Middleware):
    """
    Middleware that injects context-aware prompts after technical tool usage.
    
    This middleware tracks technical tools and injects prompts instructing agents
    to analyze changes, use MCP tools, and update memory bank files.
    """
    
    def __init__(self):
        self.session_data = {
            'technical_tools_used': [],
            'start_time': datetime.now(timezone.utc),
            'last_activity': datetime.now(timezone.utc)
        }
        self.logger = self._setup_logging()
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging for this middleware"""
        memory_bank_path = Path("memory-bank")
        memory_bank_path.mkdir(exist_ok=True)
        
        log_file = memory_bank_path / "Logs.log"
        handler = logging.handlers.RotatingFileHandler(
            log_file, maxBytes=1024*1024, backupCount=1
        )
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - [ContextAware] - %(message)s'
        )
        handler.setFormatter(formatter)
        logger = logging.getLogger('context_aware_middleware')
        logger.setLevel(logging.INFO)
        if not logger.handlers:
            logger.addHandler(handler)
        return logger
    
    def _get_contributor_id(self) -> str:
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
    
    async def on_call_tool(self, context: MiddlewareContext, tool_name: str, arguments: Dict[str, Any]) -> None:
        """Handle tool calls and inject prompts for technical tools"""
        self.session_data['last_activity'] = datetime.now(timezone.utc)
        
        if tool_name in TECHNICAL_TOOLS:
            # Track technical tool usage
            self.session_data['technical_tools_used'].append({
                'tool': tool_name,
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'arguments': {k: str(v)[:100] for k, v in arguments.items()}  # Truncate for logging
            })
            
            contributor_id = self._get_contributor_id()
            
            # Log technical tool usage
            self.logger.info(f"Technical tool used by {contributor_id}: {tool_name}")
            
            # Generate context-aware prompt
            prompt = self._generate_context_prompt(tool_name, arguments, contributor_id)
            
            # Store the prompt in context for later injection
            if not hasattr(context, 'injected_prompts'):
                context.injected_prompts = []
            context.injected_prompts.append(prompt)
    
    def _generate_context_prompt(self, tool_name: str, arguments: Dict[str, Any], contributor_id: str) -> str:
        """Generate context-aware prompt based on tool usage"""
        timestamp = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')
        
        # Base prompt template
        base_prompt = f"""
🔧 TECHNICAL TOOL USED: {tool_name}
Timestamp: {timestamp}
Contributor: {contributor_id}

📋 REQUIRED ACTIONS:
1. Analyze the changes made by this tool
2. Use appropriate MCP tools to update memory bank
3. Update relevant memory bank files to reflect changes

🛠️ RECOMMENDED MCP TOOLS:
• intelligent_context_executor - Get context for affected areas
• suggest_files_to_update - Get file update suggestions
• auto_detect_project_changes - Detect all project changes
• generate_memory_bank_template - Create missing files if needed

⚠️ MEMORY BANK UPDATE REQUIREMENT:
This technical change MUST be documented in the memory bank.
Priority files to update: dynamic_meta/change_log.md

🎯 NEXT STEPS:
1. Run suggested MCP tools
2. Update memory bank files
3. Ensure traceability of changes
"""
        
        # Add tool-specific guidance
        if tool_name in ['edit_file', 'search_replace']:
            file_path = arguments.get('target_file') or arguments.get('file_path', 'unknown')
            base_prompt += f"""
📁 FILE MODIFIED: {file_path}
🔍 SPECIFIC ACTIONS:
• Use intelligent_context_executor to understand file purpose
• Check if system architecture needs updating
• Update API documentation if code changes affect interfaces
"""
        
        elif tool_name == 'run_terminal_cmd':
            command = arguments.get('command', 'unknown')
            base_prompt += f"""
💻 COMMAND EXECUTED: {command}
🔍 SPECIFIC ACTIONS:
• Document command purpose and results
• Update deployment/DevOps documentation if applicable
• Check if configuration changes need documentation
"""
        
        elif tool_name == 'delete_file':
            file_path = arguments.get('target_file', 'unknown')
            base_prompt += f"""
🗑️ FILE DELETED: {file_path}
🔍 SPECIFIC ACTIONS:
• Document file deletion rationale
• Update system architecture to reflect removal
• Check for broken dependencies or references
"""
        
        return base_prompt


class ToolLoggingMiddleware(Middleware):
    """
    Middleware that logs every tool call with timestamps and semantic summaries.
    
    This middleware logs all tool calls and generates semantic summaries for
    specific intelligent tools, appending to memory_bank/Logs.log.
    """
    
    def __init__(self):
        self.logger = self._setup_logging()
        self.session_start = datetime.now(timezone.utc)
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging for this middleware"""
        memory_bank_path = Path("memory-bank")
        memory_bank_path.mkdir(exist_ok=True)
        
        log_file = memory_bank_path / "Logs.log"
        handler = logging.handlers.RotatingFileHandler(
            log_file, maxBytes=1024*1024, backupCount=1
        )
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - [ToolLogging] - %(message)s'
        )
        handler.setFormatter(formatter)
        logger = logging.getLogger('tool_logging_middleware')
        logger.setLevel(logging.INFO)
        if not logger.handlers:
            logger.addHandler(handler)
        return logger
    
    def _get_contributor_id(self) -> str:
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
    
    def _sanitize_arguments(self, arguments: Dict[str, Any]) -> Dict[str, str]:
        """Sanitize arguments for logging"""
        sanitized = {}
        for key, value in arguments.items():
            if isinstance(value, str):
                # Truncate long strings
                sanitized[key] = value[:200] + "..." if len(value) > 200 else value
            elif isinstance(value, (list, dict)):
                sanitized[key] = f"<{type(value).__name__} with {len(value)} items>"
            else:
                sanitized[key] = str(value)
        return sanitized
    
    def _generate_semantic_summary(self, tool_name: str, arguments: Dict[str, Any], result: Any = None) -> str:
        """Generate semantic summary for specific tools"""
        if tool_name == 'intelligent_context_executor':
            query = arguments.get('query', 'unknown')
            return f"Context query executed: '{query[:100]}...'"
        
        elif tool_name == 'suggest_files_to_update':
            input_text = arguments.get('input_text', '')
            return f"File suggestions generated for: '{input_text[:50]}...'"
        
        elif tool_name == 'analyze_project_summary':
            summary = arguments.get('project_summary', '')
            return f"Project analysis completed for: '{summary[:50]}...'"
        
        elif tool_name == 'auto_detect_project_changes':
            return "Automatic project change detection executed"
        
        elif tool_name == 'generate_memory_bank_template':
            file_name = arguments.get('file_name', 'unknown')
            return f"Template generated for: '{file_name}'"
        
        elif tool_name == 'create_memory_bank_structure':
            return "Memory bank structure creation executed"
        
        elif tool_name == 'smart_content_analysis_and_routing':
            content = arguments.get('input_content', '')
            return f"Smart routing analysis for: '{content[:50]}...'"
        
        else:
            return f"Tool executed with {len(arguments)} arguments"
    
    async def on_call_tool(self, context: MiddlewareContext, tool_name: str, arguments: Dict[str, Any]) -> None:
        """Log every tool call"""
        contributor_id = self._get_contributor_id()
        timestamp = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')
        
        # Sanitize arguments for logging
        sanitized_args = self._sanitize_arguments(arguments)
        
        # Generate semantic summary for specific tools
        semantic_summary = ""
        if tool_name in MEMORY_BANK_TOOLS:
            semantic_summary = self._generate_semantic_summary(tool_name, arguments)
        
        # Create log entry
        log_entry = {
            'timestamp': timestamp,
            'contributor': contributor_id,
            'tool': tool_name,
            'arguments': sanitized_args,
            'semantic_summary': semantic_summary,
            'session_duration': str(datetime.now(timezone.utc) - self.session_start)
        }
        
        # Log the tool call
        if semantic_summary:
            self.logger.info(f"🔧 {tool_name} | {contributor_id} | {semantic_summary}")
        else:
            self.logger.info(f"🔧 {tool_name} | {contributor_id} | Args: {len(arguments)}")
        
        # Store detailed log in memory bank
        try:
            memory_bank_path = Path("memory-bank")
            detailed_log_file = memory_bank_path / "detailed_tool_log.json"
            
            # Load existing logs
            if detailed_log_file.exists():
                with open(detailed_log_file, 'r') as f:
                    logs = json.load(f)
            else:
                logs = []
            
            # Add new log entry
            logs.append(log_entry)
            
            # Keep only last 1000 entries
            if len(logs) > 1000:
                logs = logs[-1000:]
            
            # Save updated logs
            with open(detailed_log_file, 'w') as f:
                json.dump(logs, f, indent=2)
                
        except Exception as e:
            self.logger.error(f"Failed to write detailed log: {str(e)}")


class MemoryCompletenessEnforcementMiddleware(Middleware):
    """
    Middleware that enforces memory completeness by suggesting updates.
    
    This middleware simulates session end detection and calls auto_detect_project_changes
    and suggest_files_to_update, then injects prompts about needed memory file updates.
    """
    
    def __init__(self):
        self.logger = self._setup_logging()
        self.session_tools = set()
        self.last_check = datetime.now(timezone.utc)
        self.check_interval = 300  # 5 minutes
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging for this middleware"""
        memory_bank_path = Path("memory-bank")
        memory_bank_path.mkdir(exist_ok=True)
        
        log_file = memory_bank_path / "Logs.log"
        handler = logging.handlers.RotatingFileHandler(
            log_file, maxBytes=1024*1024, backupCount=1
        )
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - [MemoryCompleteness] - %(message)s'
        )
        handler.setFormatter(formatter)
        logger = logging.getLogger('memory_completeness_middleware')
        logger.setLevel(logging.INFO)
        if not logger.handlers:
            logger.addHandler(handler)
        return logger
    
    def _get_contributor_id(self) -> str:
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
    
    def _should_check_completeness(self) -> bool:
        """Determine if completeness check should be performed"""
        now = datetime.now(timezone.utc)
        
        # Check if enough time has passed
        if (now - self.last_check).total_seconds() < self.check_interval:
            return False
        
        # Check if significant tools have been used
        significant_tools = TECHNICAL_TOOLS.union(MEMORY_BANK_TOOLS)
        if not any(tool in self.session_tools for tool in significant_tools):
            return False
        
        return True
    
    async def on_call_tool(self, context: MiddlewareContext, tool_name: str, arguments: Dict[str, Any]) -> None:
        """Track tool usage and check completeness periodically"""
        self.session_tools.add(tool_name)
        
        # Check if we should perform completeness check
        if self._should_check_completeness():
            await self._perform_completeness_check(context)
            self.last_check = datetime.now(timezone.utc)
    
    async def _perform_completeness_check(self, context: MiddlewareContext) -> None:
        """Perform completeness check and inject prompts"""
        contributor_id = self._get_contributor_id()
        timestamp = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')
        
        self.logger.info(f"Performing completeness check for {contributor_id}")
        
        # Call auto_detect_project_changes through the context
        try:
            auto_detect_tool = context.fastmcp_context.fastmcp.get_tool('auto_detect_project_changes')
            if auto_detect_tool:
                detection_result = await auto_detect_tool.call({})
            else:
                detection_result = "Auto-detection tool not available"
        except Exception as e:
            detection_result = f"Auto-detection failed: {str(e)}"
        
        # Generate completeness prompt
        completeness_prompt = f"""
🔍 MEMORY COMPLETENESS CHECK
Timestamp: {timestamp}
Contributor: {contributor_id}

📊 SESSION SUMMARY:
Tools used in session: {len(self.session_tools)}
Technical tools: {len([t for t in self.session_tools if t in TECHNICAL_TOOLS])}
Memory bank tools: {len([t for t in self.session_tools if t in MEMORY_BANK_TOOLS])}

🎯 COMPLETENESS ENFORCEMENT:
The following memory bank files require attention:

📋 MANDATORY UPDATES:
• dynamic_meta/change_log.md - Document all changes made
• context/overview.md - Update project status if needed
• tech_specs/system_architecture.md - Update if architecture changed

🔍 AUTO-DETECTION RESULTS:
{detection_result}

⚠️ REQUIRED ACTIONS:
1. Review auto-detection results above
2. Use 'suggest_files_to_update' with relevant context
3. Update all suggested memory bank files
4. Ensure no changes are left undocumented

🛠️ RECOMMENDED WORKFLOW:
1. Run: suggest_files_to_update with session context
2. Update each suggested file
3. Use intelligent_context_executor for context
4. Verify all changes are documented

💡 MEMORY BANK INTEGRITY:
Every technical change must be reflected in the memory bank.
This ensures project continuity and knowledge preservation.
"""
        
        # Store the prompt in context for later injection
        if not hasattr(context, 'injected_prompts'):
            context.injected_prompts = []
        context.injected_prompts.append(completeness_prompt)


class CrossReferenceRedundancyMiddleware(Middleware):
    """
    Middleware that maintains content index and detects redundant content.
    
    This middleware tracks memory bank content, detects redundant information,
    and suggests cross-references instead of rewriting similar content.
    """
    
    def __init__(self):
        self.logger = self._setup_logging()
        self.content_index: Dict[str, Dict[str, Any]] = {}
        self.similarity_threshold = 0.3  # 30% similarity threshold
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging for this middleware"""
        memory_bank_path = Path("memory-bank")
        memory_bank_path.mkdir(exist_ok=True)
        
        log_file = memory_bank_path / "Logs.log"
        handler = logging.handlers.RotatingFileHandler(
            log_file, maxBytes=1024*1024, backupCount=1
        )
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - [CrossReference] - %(message)s'
        )
        handler.setFormatter(formatter)
        logger = logging.getLogger('cross_reference_middleware')
        logger.setLevel(logging.INFO)
        if not logger.handlers:
            logger.addHandler(handler)
        return logger
    
    def _get_contributor_id(self) -> str:
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
    
    def _calculate_content_hash(self, content: str) -> str:
        """Calculate MD5 hash of content"""
        return hashlib.md5(content.encode('utf-8')).hexdigest()
    
    def _calculate_similarity(self, content1: str, content2: str) -> float:
        """Calculate Jaccard similarity between two content strings"""
        # Simple word-based Jaccard similarity
        words1 = set(content1.lower().split())
        words2 = set(content2.lower().split())
        
        if not words1 and not words2:
            return 1.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union) if union else 0.0
    
    def _update_content_index(self, file_path: str, content: str) -> None:
        """Update content index with new content"""
        content_hash = self._calculate_content_hash(content)
        
        self.content_index[file_path] = {
            'hash': content_hash,
            'content': content,
            'last_updated': datetime.now(timezone.utc).isoformat(),
            'word_count': len(content.split())
        }
    
    def _find_similar_content(self, content: str, exclude_file: str = None) -> List[Dict[str, Any]]:
        """Find similar content in the index"""
        similar_files = []
        
        for file_path, file_data in self.content_index.items():
            if file_path == exclude_file:
                continue
            
            similarity = self._calculate_similarity(content, file_data['content'])
            
            if similarity >= self.similarity_threshold:
                similar_files.append({
                    'file': file_path,
                    'similarity': similarity,
                    'word_count': file_data['word_count'],
                    'last_updated': file_data['last_updated']
                })
        
        # Sort by similarity descending
        similar_files.sort(key=lambda x: x['similarity'], reverse=True)
        return similar_files
    
    def _generate_cross_reference_suggestion(self, file_path: str, similar_files: List[Dict[str, Any]]) -> str:
        """Generate cross-reference suggestion prompt"""
        contributor_id = self._get_contributor_id()
        timestamp = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')
        
        prompt = f"""
🔗 REDUNDANCY DETECTION & CROSS-REFERENCE SUGGESTION
Timestamp: {timestamp}
Contributor: {contributor_id}
Target File: {file_path}

⚠️ SIMILAR CONTENT DETECTED:
The content being added/updated has similarities with existing files.

📋 SIMILAR FILES FOUND:
"""
        
        for similar in similar_files[:3]:  # Show top 3
            prompt += f"""
• {similar['file']} (Similarity: {similar['similarity']:.1%})
  - Word count: {similar['word_count']}
  - Last updated: {similar['last_updated']}
"""
        
        prompt += f"""
💡 CROSS-REFERENCE RECOMMENDATIONS:
Instead of duplicating content, consider:

1. Use cross-references: [[see:{similar_files[0]['file']}]]
2. Create a shared section and reference it
3. Update the most comprehensive file and reference it

🔗 SUGGESTED CROSS-REFERENCE FORMAT:
For detailed information, see: [[see:{similar_files[0]['file']} - {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}]]

🛠️ RECOMMENDED ACTIONS:
1. Review similar files for overlap
2. Consolidate information in the most appropriate file
3. Use cross-references to avoid duplication
4. Update the content index after changes

📊 CONTENT OPTIMIZATION:
- Total indexed files: {len(self.content_index)}
- Similarity threshold: {self.similarity_threshold:.1%}
- Redundancy level: {'High' if similar_files[0]['similarity'] > 0.7 else 'Medium' if similar_files[0]['similarity'] > 0.5 else 'Low'}
"""
        
        return prompt
    
    async def on_call_tool(self, context: MiddlewareContext, tool_name: str, arguments: Dict[str, Any]) -> None:
        """Monitor file updates and detect redundancy"""
        # Only process tools that might update memory bank files
        if tool_name in ['edit_file', 'create_file', 'write_file', 'generate_memory_bank_template']:
            file_path = arguments.get('target_file') or arguments.get('file_name', '')
            
            # Only process memory bank files
            if 'memory-bank' in file_path or file_path.startswith('memory-bank/'):
                await self._check_for_redundancy(context, file_path, arguments)
    
    async def _check_for_redundancy(self, context: MiddlewareContext, file_path: str, arguments: Dict[str, Any]) -> None:
        """Check for content redundancy"""
        contributor_id = self._get_contributor_id()
        
        # Extract content from arguments
        content = ""
        if 'code_edit' in arguments:
            content = arguments['code_edit']
        elif 'content' in arguments:
            content = arguments['content']
        elif 'new_string' in arguments:
            content = arguments['new_string']
        
        if not content or len(content.split()) < 10:  # Skip very short content
            return
        
        # Find similar content
        similar_files = self._find_similar_content(content, file_path)
        
        if similar_files:
            self.logger.info(f"Redundancy detected for {file_path} by {contributor_id}: {len(similar_files)} similar files")
            
            # Generate cross-reference suggestion
            suggestion = self._generate_cross_reference_suggestion(file_path, similar_files)
            
            # Store the suggestion in context
            if not hasattr(context, 'injected_prompts'):
                context.injected_prompts = []
            context.injected_prompts.append(suggestion)
        
        # Update content index
        self._update_content_index(file_path, content)


class AgentBehaviorProfilerMiddleware(Middleware):
    """
    Middleware that tracks agent behavior and generates profiling reports.
    
    This middleware tracks tool usage frequency, calculates memory adherence ratio,
    and logs behavior reports in memory_bank/AgentBehaviorProfile.log.
    """
    
    def __init__(self):
        self.logger = self._setup_logging()
        self.behavior_logger = self._setup_behavior_logging()
        self.session_start = datetime.now(timezone.utc)
        self.tool_usage = Counter()
        self.tool_timing = defaultdict(list)
        self.memory_tool_calls = 0
        self.core_tool_calls = 0
        self.technical_tool_calls = 0
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging for this middleware"""
        memory_bank_path = Path("memory-bank")
        memory_bank_path.mkdir(exist_ok=True)
        
        log_file = memory_bank_path / "Logs.log"
        handler = logging.handlers.RotatingFileHandler(
            log_file, maxBytes=1024*1024, backupCount=1
        )
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - [BehaviorProfiler] - %(message)s'
        )
        handler.setFormatter(formatter)
        logger = logging.getLogger('behavior_profiler_middleware')
        logger.setLevel(logging.INFO)
        if not logger.handlers:
            logger.addHandler(handler)
        return logger
    
    def _setup_behavior_logging(self) -> logging.Logger:
        """Setup dedicated behavior logging"""
        memory_bank_path = Path("memory-bank")
        memory_bank_path.mkdir(exist_ok=True)
        
        log_file = memory_bank_path / "AgentBehaviorProfile.log"
        handler = logging.handlers.RotatingFileHandler(
            log_file, maxBytes=1024*1024, backupCount=1
        )
        formatter = logging.Formatter(
            '%(asctime)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger = logging.getLogger('agent_behavior_profile')
        logger.setLevel(logging.INFO)
        if not logger.handlers:
            logger.addHandler(handler)
        return logger
    
    def _get_contributor_id(self) -> str:
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
    
    def _calculate_memory_adherence_ratio(self) -> float:
        """Calculate memory adherence ratio"""
        total_calls = self.memory_tool_calls + self.core_tool_calls
        if total_calls == 0:
            return 0.0
        return self.memory_tool_calls / total_calls
    
    def _generate_behavior_report(self) -> Dict[str, Any]:
        """Generate comprehensive behavior report"""
        now = datetime.now(timezone.utc)
        session_duration = now - self.session_start
        contributor_id = self._get_contributor_id()
        
        # Calculate statistics
        total_tools = sum(self.tool_usage.values())
        memory_adherence = self._calculate_memory_adherence_ratio()
        
        # Top tools used
        top_tools = self.tool_usage.most_common(5)
        
        # Tool category distribution
        tool_categories = {
            'memory_bank_tools': sum(count for tool, count in self.tool_usage.items() if tool in MEMORY_BANK_TOOLS),
            'technical_tools': sum(count for tool, count in self.tool_usage.items() if tool in TECHNICAL_TOOLS),
            'core_tools': sum(count for tool, count in self.tool_usage.items() if tool in CORE_TOOLS),
            'other_tools': sum(count for tool, count in self.tool_usage.items() 
                             if tool not in MEMORY_BANK_TOOLS.union(TECHNICAL_TOOLS).union(CORE_TOOLS))
        }
        
        return {
            'timestamp': now.isoformat(),
            'contributor': contributor_id,
            'session_duration': str(session_duration),
            'total_tool_calls': total_tools,
            'memory_adherence_ratio': memory_adherence,
            'tool_categories': tool_categories,
            'top_tools': top_tools,
            'unique_tools_used': len(self.tool_usage),
            'session_start': self.session_start.isoformat(),
            'session_end': now.isoformat()
        }
    
    def _log_behavior_report(self, report: Dict[str, Any]) -> None:
        """Log behavior report to dedicated log file"""
        report_text = f"""
📊 AGENT BEHAVIOR PROFILE REPORT
Generated: {report['timestamp']}
Contributor: {report['contributor']}
Session Duration: {report['session_duration']}

🔧 TOOL USAGE STATISTICS:
Total Tool Calls: {report['total_tool_calls']}
Unique Tools Used: {report['unique_tools_used']}
Memory Adherence Ratio: {report['memory_adherence_ratio']:.2%}

📋 TOOL CATEGORIES:
• Memory Bank Tools: {report['tool_categories']['memory_bank_tools']} calls
• Technical Tools: {report['tool_categories']['technical_tools']} calls
• Core Tools: {report['tool_categories']['core_tools']} calls
• Other Tools: {report['tool_categories']['other_tools']} calls

🏆 TOP TOOLS USED:
{chr(10).join(f"• {tool}: {count} calls" for tool, count in report['top_tools'])}

📈 BEHAVIOR ANALYSIS:
Memory Adherence: {'High' if report['memory_adherence_ratio'] > 0.3 else 'Medium' if report['memory_adherence_ratio'] > 0.1 else 'Low'}
Tool Diversity: {'High' if report['unique_tools_used'] > 10 else 'Medium' if report['unique_tools_used'] > 5 else 'Low'}
Session Activity: {'High' if report['total_tool_calls'] > 20 else 'Medium' if report['total_tool_calls'] > 10 else 'Low'}

💡 RECOMMENDATIONS:
{self._generate_behavior_recommendations(report)}

{'='*80}
"""
        
        self.behavior_logger.info(report_text)
    
    def _generate_behavior_recommendations(self, report: Dict[str, Any]) -> str:
        """Generate behavior recommendations based on report"""
        recommendations = []
        
        # Memory adherence recommendations
        if report['memory_adherence_ratio'] < 0.1:
            recommendations.append("• Increase usage of memory bank tools for better documentation")
        elif report['memory_adherence_ratio'] > 0.5:
            recommendations.append("• Excellent memory bank tool usage - maintain this practice")
        
        # Tool diversity recommendations
        if report['unique_tools_used'] < 5:
            recommendations.append("• Consider using more diverse tools for comprehensive analysis")
        
        # Category balance recommendations
        categories = report['tool_categories']
        if categories['technical_tools'] > categories['memory_bank_tools'] * 3:
            recommendations.append("• Balance technical changes with memory bank updates")
        
        if not recommendations:
            recommendations.append("• Maintain current balanced tool usage patterns")
        
        return '\n'.join(recommendations)
    
    async def on_call_tool(self, context: MiddlewareContext, tool_name: str, arguments: Dict[str, Any]) -> None:
        """Track tool usage and update behavior statistics"""
        # Record tool usage
        self.tool_usage[tool_name] += 1
        
        # Record timing
        self.tool_timing[tool_name].append(datetime.now(timezone.utc))
        
        # Update category counters
        if tool_name in MEMORY_BANK_TOOLS:
            self.memory_tool_calls += 1
        elif tool_name in CORE_TOOLS:
            self.core_tool_calls += 1
        elif tool_name in TECHNICAL_TOOLS:
            self.technical_tool_calls += 1
        
        # Log behavior periodically (every 10 tool calls)
        total_calls = sum(self.tool_usage.values())
        if total_calls % 10 == 0:
            contributor_id = self._get_contributor_id()
            self.logger.info(f"Behavior checkpoint for {contributor_id}: {total_calls} total calls, {self._calculate_memory_adherence_ratio():.2%} memory adherence")
        
        # Generate full report every 25 tool calls
        if total_calls % 25 == 0:
            report = self._generate_behavior_report()
            self._log_behavior_report(report) 