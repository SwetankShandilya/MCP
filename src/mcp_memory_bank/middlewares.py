"""
FastMCP 2.9 Middleware Classes for Memory Bank MCP Server

This module contains 5 production-ready middleware classes that integrate
with the FastMCP 2.9 middleware system using proper semantic awareness.
"""

from fastmcp.server.middleware import Middleware, MiddlewareContext
from fastmcp.exceptions import ToolError
from datetime import datetime, timezone
from pathlib import Path
import logging
import logging.handlers
import json
import asyncio
from collections import defaultdict, Counter
import hashlib
from typing import Any, Dict, List, Optional

# ============================================================================
# 1. CONTEXT-AWARE PROMPT INJECTION MIDDLEWARE
# ============================================================================

class ContextAwarePromptInjectionMiddleware(Middleware):
    """
    Middleware that injects prompts after technical tool usage to encourage
    memory bank updates and analysis.
    
    Triggers after any technical tool is used (e.g., edit_file, run_terminal_cmd).
    Injects a prompt instructing the agent to:
    - Analyze the change
    - Use relevant MCP tools (suggest_files_to_update, smart_content_analysis_and_routing, update_memory_bank)
    - Update the memory bank
    - Dynamically include the edited file name and action
    """
    
    def __init__(self):
        self.session_data = {}
        self.setup_logging()
        
        # Technical tools that should trigger context-aware middleware
        self.technical_tools = {
            'edit_file', 'run_terminal_cmd', 'search_replace', 'delete_file', 
            'edit_notebook', 'create_diagram', 'grep_search', 'codebase_search'
        }
    
    def setup_logging(self):
        """Setup logging for this middleware"""
        memory_bank_path = Path("memory-bank")
        memory_bank_path.mkdir(exist_ok=True)
        
        log_file = memory_bank_path / "Logs.log"
        handler = logging.handlers.RotatingFileHandler(
            log_file, maxBytes=1024*1024, backupCount=1
        )
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - ContextAwareMiddleware - %(message)s'
        )
        handler.setFormatter(formatter)
        self.logger = logging.getLogger('context_aware_middleware')
        self.logger.setLevel(logging.INFO)
        if not self.logger.handlers:
            self.logger.addHandler(handler)
    
    async def on_call_tool(self, context: MiddlewareContext, call_next):
        """Called after a tool is called"""
        tool_name = context.message.name
        
        # Execute the tool first
        result = await call_next(context)
        
        # Check if this is a technical tool that requires context injection
        if tool_name in self.technical_tools:
            try:
                self.logger.info(f"Technical tool '{tool_name}' used, preparing context prompt injection")
                
                # Extract arguments from the context
                arguments = getattr(context.message, 'arguments', {}) or {}
                
                # Generate context-aware prompt
                prompt = await self._generate_context_prompt(tool_name, arguments, result)
                
                # Store prompt for potential injection
                session_id = getattr(context, 'session_id', 'default')
                if session_id not in self.session_data:
                    self.session_data[session_id] = []
                
                self.session_data[session_id].append({
                    'timestamp': datetime.now(timezone.utc).isoformat(),
                    'tool_used': tool_name,
                    'prompt': prompt,
                    'arguments': arguments
                })
                
                # Log the generated prompt - the agent will use this for guidance
                self.logger.info(f"Context prompt generated for {tool_name}: {prompt[:100]}...")
                
            except Exception as e:
                self.logger.error(f"Error in context-aware middleware: {str(e)}")
        
        return result
    
    async def _generate_context_prompt(self, tool_name: str, arguments: dict, result: Any) -> str:
        """Generate a context-aware prompt based on the tool used"""
        file_name = ""
        action_description = ""
        
        # Extract file information and action
        if tool_name == 'edit_file':
            file_name = arguments.get('target_file', 'unknown file')
            action_description = f"edited file {file_name}"
        elif tool_name == 'run_terminal_cmd':
            command = arguments.get('command', 'unknown command')
            action_description = f"executed command: {command}"
        elif tool_name == 'search_replace':
            file_name = arguments.get('file_path', 'unknown file')
            action_description = f"performed search/replace in {file_name}"
        elif tool_name == 'delete_file':
            file_name = arguments.get('target_file', 'unknown file')
            action_description = f"deleted file {file_name}"
        else:
            action_description = f"used {tool_name}"
        
        prompt = f"""
🎯 CONTEXT-AWARE ANALYSIS REQUIRED

You just {action_description}. As per memory bank protocol, you must now:

1. **ANALYZE THE CHANGE**:
   - What was modified/created/deleted?
   - How does this impact the project architecture?
   - What are the implications for stakeholders?

2. **USE MEMORY BANK TOOLS**:
   - Call `suggest_files_to_update("{action_description}")` to get file recommendations
   - Call `smart_project_analysis_and_routing("{action_description}")` for routing guidance
   - Call `intelligent_context_executor("analyze impact of {action_description}")` for context

3. **UPDATE MEMORY BANK**:
   - Update relevant memory bank files based on tool suggestions
   - Always update `dynamic_meta/change_log.md` with this change
   - Update `dynamic_meta/decision_logs.md` if architectural or coding logic decisions were made

4. **VERIFY COMPLETENESS**:
   - Ensure all related documentation is updated
   - Cross-reference with existing memory bank content

File affected: {file_name}
Action: {action_description}
Timestamp: {datetime.now(timezone.utc).isoformat()}

Remember: Every technical change MUST be reflected in the memory bank for project continuity.
"""
        
        return prompt


# ============================================================================
# 2. TOOL LOGGING MIDDLEWARE WITH SEMANTIC SUMMARY
# ============================================================================

class ToolLoggingMiddleware(Middleware):
    """
    Middleware that logs every tool name, arguments, and timestamp.
    For tools like intelligent_context_executor, suggest_files_to_update, and analyze_project_summary,
    also logs a one-line summary of what the tool returned.
    Appends log entries to a Logs.log file inside the memory_bank/ directory.
    """
    
    def __init__(self):
        self.setup_logging()
        
        # Tools that need semantic summaries
        self.semantic_summary_tools = {
            'intelligent_context_executor', 'suggest_files_to_update', 'analyze_project_summary',
            'smart_project_analysis_and_routing', 'auto_detect_project_changes'
        }
    
    def setup_logging(self):
        """Setup logging for this middleware"""
        memory_bank_path = Path("memory-bank")
        memory_bank_path.mkdir(exist_ok=True)
        
        self.log_file = memory_bank_path / "Logs.log"
        handler = logging.handlers.RotatingFileHandler(
            self.log_file, maxBytes=1024*1024, backupCount=1
        )
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - ToolLogging - %(message)s'
        )
        handler.setFormatter(formatter)
        self.logger = logging.getLogger('tool_logging_middleware')
        self.logger.setLevel(logging.INFO)
        if not self.logger.handlers:
            self.logger.addHandler(handler)
    
    async def on_call_tool(self, context: MiddlewareContext, call_next):
        """Called when a tool is called"""
        tool_name = context.message.name
        arguments = getattr(context.message, 'arguments', {}) or {}
        
        # Execute the tool
        result = await call_next(context)
        
        try:
            timestamp = datetime.now(timezone.utc).isoformat()
            session_id = getattr(context, 'session_id', 'unknown')
            
            # Basic logging for all tools
            log_entry = {
                'timestamp': timestamp,
                'tool_name': tool_name,
                'arguments': self._sanitize_arguments(arguments),
                'session_id': session_id
            }
            
            # Add semantic summary for specific tools
            if tool_name in self.semantic_summary_tools:
                summary = self._generate_semantic_summary(tool_name, arguments, result)
                log_entry['semantic_summary'] = summary
            
            # Log to file
            self._append_to_log_file(log_entry)
            
            # Log to logger
            summary_text = log_entry.get('semantic_summary', 'N/A')
            self.logger.info(f"Tool executed: {tool_name} | Summary: {summary_text}")
            
        except Exception as e:
            self.logger.error(f"Error in tool logging middleware: {str(e)}")
        
        return result
    
    def _sanitize_arguments(self, arguments: dict) -> dict:
        """Sanitize arguments to remove sensitive data and limit size"""
        sanitized = {}
        for key, value in arguments.items():
            if isinstance(value, str) and len(value) > 200:
                sanitized[key] = value[:200] + "...[truncated]"
            elif key.lower() in ['password', 'token', 'secret', 'key']:
                sanitized[key] = "[REDACTED]"
            else:
                sanitized[key] = value
        return sanitized
    
    def _generate_semantic_summary(self, tool_name: str, arguments: dict, result: Any) -> str:
        """Generate a one-line semantic summary of what the tool returned"""
        try:
            if tool_name == 'intelligent_context_executor':
                query = arguments.get('user_query', 'unknown query')
                if isinstance(result, str) and 'PROJECT CONTEXT' in result:
                    return f"Provided context for: {query[:50]}..."
                return f"Context request for: {query[:50]}..."
            
            elif tool_name == 'suggest_files_to_update':
                input_text = arguments.get('input_text', 'unknown input')
                if isinstance(result, list) and result:
                    return f"Suggested {len(result)} file updates for: {input_text[:30]}..."
                return f"File update analysis for: {input_text[:30]}..."
            
            elif tool_name == 'analyze_project_summary':
                summary = arguments.get('project_summary', 'unknown summary')
                if isinstance(result, str) and 'PROJECT TYPE' in result:
                    # Try to extract project type from result
                    lines = result.split('\n')
                    project_type = "unknown type"
                    for line in lines:
                        if 'PROJECT TYPE:' in line:
                            project_type = line.split(':')[1].strip()
                            break
                    return f"Analyzed {project_type} project: {summary[:30]}..."
                return f"Project analysis for: {summary[:30]}..."
            
            elif tool_name == 'smart_project_analysis_and_routing':
                content = arguments.get('input_content', 'unknown content')
                return f"Smart routing analysis for: {content[:30]}..."
                
            elif tool_name == 'auto_detect_project_changes':
                return "Auto-detected project changes and generated suggestions"
            
            return "Tool executed successfully"
            
        except Exception as e:
            return f"Summary generation failed: {str(e)}"
    
    def _append_to_log_file(self, log_entry: dict):
        """Append log entry to the log file"""
        try:
            log_line = f"TOOL_LOG: {json.dumps(log_entry)}\n"
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(log_line)
        except Exception as e:
            self.logger.error(f"Failed to write to log file: {str(e)}")


# ============================================================================
# 3. MEMORY COMPLETENESS ENFORCEMENT MIDDLEWARE
# ============================================================================

class MemoryCompletenessEnforcementMiddleware(Middleware):
    """
    Middleware that enforces memory completeness at the end of a session.
    Triggers at the end of a session (on_session_end).
    Calls auto_detect_project_changes and suggest_files_to_update.
    Injects a prompt to the agent listing memory files that still need updates.
    """
    
    def __init__(self):
        self.setup_logging()
        self.session_activity = defaultdict(list)
    
    def setup_logging(self):
        """Setup logging for this middleware"""
        memory_bank_path = Path("memory-bank")
        memory_bank_path.mkdir(exist_ok=True)
        
        log_file = memory_bank_path / "Logs.log"
        handler = logging.handlers.RotatingFileHandler(
            log_file, maxBytes=1024*1024, backupCount=1
        )
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - MemoryCompleteness - %(message)s'
        )
        handler.setFormatter(formatter)
        self.logger = logging.getLogger('memory_completeness_middleware')
        self.logger.setLevel(logging.INFO)
        if not self.logger.handlers:
            self.logger.addHandler(handler)
    
    async def on_call_tool(self, context: MiddlewareContext, call_next):
        """Track tool usage during session"""
        tool_name = context.message.name
        session_id = getattr(context, 'session_id', 'default')
        
        # Execute the tool
        result = await call_next(context)
        
        # Track session activity
        self.session_activity[session_id].append({
            'tool': tool_name,
            'timestamp': datetime.now(timezone.utc).isoformat()
        })
        
        return result
    
    async def on_session_end(self, context: MiddlewareContext):
        """Called at the end of a session"""
        session_id = getattr(context, 'session_id', 'default')
        
        try:
            self.logger.info(f"Session ending: {session_id}, checking memory completeness")
            
            # Get session activity
            activity = self.session_activity.get(session_id, [])
            
            # Call actual tools through the FastMCP context
            changes_result = await self._call_auto_detect_changes(context)
            suggestions_result = await self._call_suggest_files_update(context, changes_result)
            
            # Generate completeness prompt
            prompt = await self._generate_completeness_prompt(session_id, changes_result, suggestions_result, activity)
            
            # Clean up session data
            if session_id in self.session_activity:
                del self.session_activity[session_id]
            
            self.logger.info("Memory completeness check completed")
            self.logger.info(f"Completeness prompt generated: {prompt[:100]}...")
            
        except Exception as e:
            self.logger.error(f"Error in memory completeness middleware: {str(e)}")
    
    async def _call_auto_detect_changes(self, context: MiddlewareContext) -> str:
        """Call the actual auto_detect_project_changes tool"""
        try:
            # Access the FastMCP server through context
            fastmcp_server = context.fastmcp_context.fastmcp
            
            # Get the tool and call it
            tool = await fastmcp_server.get_tool('auto_detect_project_changes')
            if tool:
                result = await tool.call()
                return str(result) if result else "No changes detected"
            else:
                self.logger.warning("auto_detect_project_changes tool not found")
                return "Tool not available"
        except Exception as e:
            self.logger.error(f"Failed to call auto_detect_project_changes: {str(e)}")
            return "Failed to detect changes"
    
    async def _call_suggest_files_update(self, context: MiddlewareContext, changes_info: str) -> str:
        """Call the actual suggest_files_to_update tool"""
        try:
            # Access the FastMCP server through context
            fastmcp_server = context.fastmcp_context.fastmcp
            
            # Get the tool and call it
            tool = await fastmcp_server.get_tool('suggest_files_to_update')
            if tool:
                result = await tool.call(input_text=changes_info)
                return str(result) if result else "No suggestions available"
            else:
                self.logger.warning("suggest_files_to_update tool not found")
                return "Tool not available"
        except Exception as e:
            self.logger.error(f"Failed to call suggest_files_to_update: {str(e)}")
            return "Failed to get suggestions"
    
    async def _generate_completeness_prompt(self, session_id: str, changes_result: str, suggestions_result: str, activity: List[Dict]) -> str:
        """Generate prompt for memory completeness"""
        timestamp = datetime.now(timezone.utc).isoformat()
        
        prompt = f"""
🔍 SESSION END - MEMORY COMPLETENESS CHECK

Session ID: {session_id}
Session ended at: {timestamp}
Tools used in session: {len(activity)}

**DETECTED CHANGES:**
{changes_result}

**SUGGESTED UPDATES:**
{suggestions_result}

**ACTION REQUIRED:**
Before this session is considered complete, please ensure:

1. **Review Change Detection Results**:
   - Examine all detected project changes
   - Verify that significant changes are documented

2. **Update Memory Bank Files**:
   - Follow the file update suggestions provided
   - Prioritize high-priority files first
   - Ensure consistency across related files

3. **Missing Updates Check**:
   The following files may need updates based on session activity:
   - dynamic_meta/change_log.md (session changes)
   - dynamic_meta/decision_logs.md (any decisions made)
   - context/overview.md (project status updates)
   - tech_specs/ files (if architecture changed)

4. **Verify Cross-References**:
   - Check that all references between files are valid
   - Update any broken or outdated cross-references

**MEMORY BANK INTEGRITY STATUS**: ⚠️ PENDING UPDATES

This session cannot be considered complete until memory bank files are updated according to the suggestions above.
"""
        
        return prompt


# ============================================================================
# 4. CROSS-REFERENCE AND REDUNDANCY MINIMIZATION MIDDLEWARE
# ============================================================================

class CrossReferenceRedundancyMiddleware(Middleware):
    """
    Middleware that minimizes redundancy by tracking content and suggesting cross-references.
    Triggers on calls to update_memory_bank.
    Maintains a temporary in-memory index of memory bank content summaries.
    If redundant or overlapping content is detected, injects a prompt asking the agent
    to consider referencing an existing file using cross-links instead of rewriting.
    """
    
    def __init__(self):
        self.content_index = {}  # Hash -> file_path mapping
        self.setup_logging()
        # Initialize content index
        asyncio.create_task(self._initialize_content_index())
    
    def setup_logging(self):
        """Setup logging for this middleware"""
        memory_bank_path = Path("memory-bank")
        memory_bank_path.mkdir(exist_ok=True)
        
        log_file = memory_bank_path / "Logs.log"
        handler = logging.handlers.RotatingFileHandler(
            log_file, maxBytes=1024*1024, backupCount=1
        )
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - CrossReference - %(message)s'
        )
        handler.setFormatter(formatter)
        self.logger = logging.getLogger('cross_reference_middleware')
        self.logger.setLevel(logging.INFO)
        if not self.logger.handlers:
            self.logger.addHandler(handler)
    
    async def on_call_tool(self, context: MiddlewareContext, call_next):
        """Called when a tool is called"""
        tool_name = context.message.name
        
        # Check if this is a memory bank update operation
        if tool_name in ['generate_memory_bank_template', 'edit_file']:
            arguments = getattr(context.message, 'arguments', {}) or {}
            
            # Pre-execution check for redundancy
            if tool_name == 'edit_file':
                file_path = arguments.get('target_file', '')
                content = arguments.get('code_edit', '')
                
                # Check if this is a memory bank file
                if 'memory-bank' in file_path and content:
                    await self._check_for_redundancy(file_path, content, context)
        
        # Execute the tool
        result = await call_next(context)
        
        # Post-execution update of content index
        if tool_name in ['generate_memory_bank_template', 'edit_file']:
            # Only update if it's a memory bank file
            arguments = getattr(context.message, 'arguments', {}) or {}
            file_path = arguments.get('target_file', '')
            if 'memory-bank' in file_path:
                await self._update_content_index()
        
        return result
    
    async def _initialize_content_index(self):
        """Initialize the content index from existing memory bank files"""
        try:
            memory_bank_path = Path("memory-bank")
            if not memory_bank_path.exists():
                return
            
            for md_file in memory_bank_path.rglob("*.md"):
                if md_file.is_file():
                    try:
                        content = md_file.read_text(encoding='utf-8')
                        content_hash = self._generate_content_hash(content)
                        relative_path = str(md_file.relative_to(memory_bank_path))
                        self.content_index[content_hash] = relative_path
                    except Exception as e:
                        self.logger.warning(f"Failed to index {md_file}: {str(e)}")
            
            self.logger.info(f"Initialized content index with {len(self.content_index)} files")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize content index: {str(e)}")
    
    async def _check_for_redundancy(self, file_path: str, content: str, context: MiddlewareContext):
        """Check for redundant content and suggest cross-references"""
        try:
            self.logger.info(f"Checking for redundancy in: {file_path}")
            
            # Find similar content
            similar_files = self._find_similar_content(content, file_path)
            
            if similar_files:
                # Generate cross-reference suggestion prompt
                prompt = await self._generate_cross_reference_prompt(file_path, content, similar_files)
                
                self.logger.info(f"Found similar content, suggesting cross-references for {file_path}")
                self.logger.info(f"Cross-reference prompt generated: {prompt[:100]}...")
                
        except Exception as e:
            self.logger.error(f"Error in cross-reference check: {str(e)}")
    
    async def _update_content_index(self):
        """Update the content index after memory bank changes"""
        await self._initialize_content_index()
    
    def _generate_content_hash(self, content: str) -> str:
        """Generate a hash for content similarity comparison"""
        # Normalize content by removing whitespace and converting to lowercase
        normalized = ' '.join(content.lower().split())
        return hashlib.md5(normalized.encode()).hexdigest()
    
    def _find_similar_content(self, content: str, current_file: str) -> List[str]:
        """Find files with similar content"""
        similar_files = []
        content_words = set(content.lower().split())
        
        memory_bank_path = Path("memory-bank")
        if not memory_bank_path.exists():
            return similar_files
        
        for md_file in memory_bank_path.rglob("*.md"):
            if md_file.is_file():
                try:
                    relative_path = str(md_file.relative_to(memory_bank_path))
                    if relative_path == current_file or current_file.endswith(relative_path):
                        continue
                    
                    existing_content = md_file.read_text(encoding='utf-8')
                    existing_words = set(existing_content.lower().split())
                    
                    # Calculate similarity (Jaccard similarity)
                    intersection = len(content_words.intersection(existing_words))
                    union = len(content_words.union(existing_words))
                    
                    if union > 0:
                        similarity = intersection / union
                        if similarity > 0.3:  # 30% similarity threshold
                            similar_files.append(relative_path)
                
                except Exception as e:
                    self.logger.warning(f"Failed to compare with {md_file}: {str(e)}")
        
        return similar_files
    
    async def _generate_cross_reference_prompt(self, file_path: str, content: str, similar_files: List[str]) -> str:
        """Generate prompt suggesting cross-references instead of duplication"""
        timestamp = datetime.now(timezone.utc).isoformat()
        
        prompt = f"""
🔗 REDUNDANCY DETECTED - CROSS-REFERENCE SUGGESTION

File being updated: {file_path}
Timestamp: {timestamp}

**SIMILAR CONTENT FOUND IN:**
{chr(10).join(f"  • {file}" for file in similar_files)}

**RECOMMENDATION:**
Instead of duplicating content, consider using cross-references to existing information:

1. **Review Existing Content**:
   - Check the similar files listed above
   - Identify what information already exists
   - Determine if new content adds unique value

2. **Use Cross-Reference Format**:
   Instead of rewriting, use references like:
   - `[[see:decision_logs {datetime.now().strftime('%Y-%m-%d')} Architecture Decision]]`
   - `[[see:change_log Latest deployment changes]]`
   - `[[see:overview Project status as of {datetime.now().strftime('%Y-%m-%d')}]]`

3. **Add Only New Information**:
   - Focus on what's genuinely new or different
   - Link to existing content for background/context
   - Maintain single source of truth for shared concepts

4. **Update Cross-References**:
   - Ensure existing files reference this new content if relevant
   - Create bidirectional links where appropriate

**DETECTED SIMILARITY**: {len(similar_files)} files with overlapping content

Would you like to proceed with cross-references instead of full content duplication?
"""
        
        return prompt


# ============================================================================
# 5. AGENT BEHAVIOR PROFILER MIDDLEWARE
# ============================================================================

class AgentBehaviorProfilerMiddleware(Middleware):
    """
    Middleware that tracks agent behavior patterns and tool usage.
    Tracks usage frequency of each tool by the agent per session.
    Tracks how often memory bank updates are called after core dev tools.
    At the end of each session, logs a report in memory_bank/AgentBehaviorProfile.log.
    """
    
    def __init__(self):
        self.session_stats = defaultdict(lambda: {
            'tool_usage': Counter(),
            'memory_tools_used': 0,
            'core_tools_used': 0,
            'session_start': datetime.now(timezone.utc),
            'last_activity': datetime.now(timezone.utc),
            'tool_sequence': []
        })
        self.setup_logging()
        
        # Define tool categories
        self.memory_bank_tools = {
            'suggest_files_to_update', 'smart_content_analysis_and_routing', 
            'intelligent_context_executor', 'analyze_project_summary',
            'auto_detect_project_changes', 'generate_memory_bank_template',
            'get_memory_bank_structure', 'create_memory_bank_structure'
        }
        
        self.core_dev_tools = {
            'edit_file', 'run_terminal_cmd', 'search_replace', 'delete_file', 
            'edit_notebook', 'create_diagram', 'grep_search', 'codebase_search'
        }
    
    def setup_logging(self):
        """Setup logging for this middleware"""
        memory_bank_path = Path("memory-bank")
        memory_bank_path.mkdir(exist_ok=True)
        
        self.profile_log_file = memory_bank_path / "AgentBehaviorProfile.log"
        
        log_file = memory_bank_path / "Logs.log"
        handler = logging.handlers.RotatingFileHandler(
            log_file, maxBytes=1024*1024, backupCount=1
        )
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - BehaviorProfiler - %(message)s'
        )
        handler.setFormatter(formatter)
        self.logger = logging.getLogger('behavior_profiler_middleware')
        self.logger.setLevel(logging.INFO)
        if not self.logger.handlers:
            self.logger.addHandler(handler)
    
    async def on_call_tool(self, context: MiddlewareContext, call_next):
        """Called when a tool is called"""
        tool_name = context.message.name
        session_id = getattr(context, 'session_id', 'default_session')
        
        # Execute the tool
        result = await call_next(context)
        
        try:
            stats = self.session_stats[session_id]
            
            # Update tool usage count
            stats['tool_usage'][tool_name] += 1
            stats['last_activity'] = datetime.now(timezone.utc)
            stats['tool_sequence'].append({
                'tool': tool_name,
                'timestamp': datetime.now(timezone.utc).isoformat()
            })
            
            # Categorize tool usage
            if tool_name in self.memory_bank_tools:
                stats['memory_tools_used'] += 1
            elif tool_name in self.core_dev_tools:
                stats['core_tools_used'] += 1
            
            self.logger.info(f"Tool usage tracked: {tool_name} (session: {session_id})")
            
        except Exception as e:
            self.logger.error(f"Error in behavior profiler middleware: {str(e)}")
        
        return result
    
    async def on_session_end(self, context: MiddlewareContext):
        """Called at the end of a session"""
        session_id = getattr(context, 'session_id', 'default_session')
        
        try:
            if session_id not in self.session_stats:
                return
            
            stats = self.session_stats[session_id]
            report = await self._generate_behavior_report(session_id, stats)
            
            # Write report to behavior profile log
            await self._write_behavior_report(report)
            
            # Clean up session data
            del self.session_stats[session_id]
            
            self.logger.info(f"Behavior profile report generated for session: {session_id}")
            
        except Exception as e:
            self.logger.error(f"Error generating behavior report: {str(e)}")
    
    async def _generate_behavior_report(self, session_id: str, stats: dict) -> dict:
        """Generate comprehensive behavior report"""
        session_duration = (stats['last_activity'] - stats['session_start']).total_seconds()
        
        # Calculate memory adherence ratio
        total_tools = stats['memory_tools_used'] + stats['core_tools_used']
        memory_adherence_ratio = (
            stats['memory_tools_used'] / total_tools if total_tools > 0 else 0
        )
        
        # Get top tools used
        top_tools = stats['tool_usage'].most_common(10)
        
        # Analyze tool patterns
        sequence = stats['tool_sequence']
        pattern_analysis = self._analyze_tool_patterns(sequence)
        
        report = {
            'session_id': session_id,
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'session_duration_seconds': session_duration,
            'session_duration_formatted': f"{session_duration/60:.1f} minutes",
            'total_tool_calls': sum(stats['tool_usage'].values()),
            'unique_tools_used': len(stats['tool_usage']),
            'memory_tools_used': stats['memory_tools_used'],
            'core_tools_used': stats['core_tools_used'],
            'memory_adherence_ratio': memory_adherence_ratio,
            'memory_adherence_percentage': f"{memory_adherence_ratio * 100:.1f}%",
            'top_tools': [{'tool': tool, 'count': count} for tool, count in top_tools],
            'tool_usage_breakdown': dict(stats['tool_usage']),
            'pattern_analysis': pattern_analysis,
            'session_start': stats['session_start'].isoformat(),
            'session_end': stats['last_activity'].isoformat()
        }
        
        return report
    
    def _analyze_tool_patterns(self, sequence: List[Dict]) -> Dict:
        """Analyze patterns in tool usage"""
        if len(sequence) < 2:
            return {'patterns': [], 'memory_follow_up_rate': 0}
        
        patterns = []
        memory_follow_ups = 0
        core_tool_uses = 0
        
        for i in range(len(sequence) - 1):
            current_tool = sequence[i]['tool']
            next_tool = sequence[i + 1]['tool']
            
            # Check if core tool is followed by memory tool
            if current_tool in self.core_dev_tools:
                core_tool_uses += 1
                if next_tool in self.memory_bank_tools:
                    memory_follow_ups += 1
                    patterns.append(f"{current_tool} → {next_tool}")
        
        memory_follow_up_rate = (memory_follow_ups / core_tool_uses * 100) if core_tool_uses > 0 else 0
        
        return {
            'patterns': patterns[:5],  # Top 5 patterns
            'memory_follow_up_rate': f"{memory_follow_up_rate:.1f}%",
            'core_tool_uses': core_tool_uses,
            'memory_follow_ups': memory_follow_ups
        }
    
    async def _write_behavior_report(self, report: dict):
        """Write behavior report to log file"""
        try:
            # Format report for readability
            formatted_report = f"""
================================================================================
AGENT BEHAVIOR PROFILE REPORT
================================================================================
Session ID: {report['session_id']}
Generated: {report['timestamp']}
Duration: {report['session_duration_formatted']}

TOOL USAGE SUMMARY:
- Total Tool Calls: {report['total_tool_calls']}
- Unique Tools Used: {report['unique_tools_used']}
- Memory Bank Tools: {report['memory_tools_used']}
- Core/Technical Tools: {report['core_tools_used']}

MEMORY ADHERENCE:
- Ratio: {report['memory_adherence_percentage']}
- Assessment: {"EXCELLENT" if report['memory_adherence_ratio'] > 0.8 else "GOOD" if report['memory_adherence_ratio'] > 0.5 else "NEEDS IMPROVEMENT"}
- Memory Follow-up Rate: {report['pattern_analysis']['memory_follow_up_rate']}

TOP TOOLS USED:
{chr(10).join(f"  {i+1}. {tool['tool']}: {tool['count']} times" for i, tool in enumerate(report['top_tools'][:5]))}

TOOL PATTERNS:
{chr(10).join(f"  • {pattern}" for pattern in report['pattern_analysis']['patterns'])}

DETAILED BREAKDOWN:
{json.dumps(report['tool_usage_breakdown'], indent=2)}

SESSION TIMELINE:
- Started: {report['session_start']}
- Ended: {report['session_end']}

================================================================================
"""
            
            # Append to behavior profile log
            with open(self.profile_log_file, 'a', encoding='utf-8') as f:
                f.write(formatted_report)
                f.write('\n')
            
            # Also log structured data
            with open(self.profile_log_file, 'a', encoding='utf-8') as f:
                f.write(f"STRUCTURED_DATA: {json.dumps(report)}\n")
        
        except Exception as e:
            self.logger.error(f"Failed to write behavior report: {str(e)}") 