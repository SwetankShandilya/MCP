"""
FastMCP 2.0 Middleware Classes for Memory Bank MCP Server

This module contains middleware classes that enhance the MCP server with:
- Context-aware prompt injection
- Tool logging with semantic summaries
- Memory completeness enforcement
- Cross-reference and redundancy minimization
- Agent behavior profiling
"""

import asyncio
import hashlib
import json
import logging
import os
import time
from collections import Counter, defaultdict
from datetime import datetime
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

from fastmcp.server.middleware import Middleware, MiddlewareContext

class ContextAwarePromptInjectionMiddleware(Middleware):
    """
    Middleware that injects context-aware prompts after technical tools are used.
    Triggers after tools like edit_file, run_terminal_cmd, etc.
    """
    
    def __init__(self):
        self.technical_tools = {
            'edit_file', 'run_terminal_cmd', 'search_replace', 'delete_file',
            'create_file', 'write_file', 'modify_file', 'update_file'
        }
        self.session_data = {}
        self.logger = self._setup_logger()
    
    def _setup_logger(self) -> logging.Logger:
        """Set up logging for the middleware"""
        logger = logging.getLogger('context_aware_prompt_injection')
        logger.setLevel(logging.INFO)
        
        # Create memory_bank directory if it doesn't exist
        memory_bank_dir = Path("memory_bank")
        memory_bank_dir.mkdir(exist_ok=True)
        
        handler = RotatingFileHandler(
            memory_bank_dir / "ContextAwarePrompts.log",
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5
        )
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
        return logger
    
    async def on_call_tool(self, context: MiddlewareContext, tool_name: str, arguments: Dict[str, Any]) -> None:
        """Called when a tool is invoked"""
        if tool_name in self.technical_tools:
            session_id = id(context)
            
            if session_id not in self.session_data:
                self.session_data[session_id] = {
                    'technical_tools_used': [],
                    'start_time': time.time()
                }
            
            self.session_data[session_id]['technical_tools_used'].append({
                'tool': tool_name,
                'timestamp': datetime.now().isoformat(),
                'arguments': arguments
            })
            
            # Generate context-aware prompt
            prompt = self._generate_context_prompt(tool_name, arguments)
            
            # Log the prompt injection
            self.logger.info(f"Injecting context prompt for tool: {tool_name}")
            self.logger.info(f"Prompt: {prompt}")
            
            # Store prompt for potential injection (in a real implementation,
            # this would be injected into the conversation context)
            self.session_data[session_id]['last_prompt'] = prompt
    
    def _generate_context_prompt(self, tool_name: str, arguments: Dict[str, Any]) -> str:
        """Generate context-aware prompt based on the tool used"""
        base_prompt = (
            f"After using {tool_name}, please analyze the changes made and:\n"
            "1. Use MCP tools to understand the project context\n"
            "2. Update relevant memory bank files with new knowledge\n"
            "3. Ensure all changes are properly documented\n"
            "4. Consider cross-references and dependencies\n"
        )
        
        if tool_name in ['edit_file', 'search_replace']:
            file_path = arguments.get('target_file') or arguments.get('file_path', 'unknown')
            return base_prompt + f"5. Specifically analyze changes to: {file_path}\n"
        elif tool_name == 'run_terminal_cmd':
            command = arguments.get('command', 'unknown')
            return base_prompt + f"5. Analyze the results of command: {command}\n"
        
        return base_prompt


class ToolLoggingMiddleware(Middleware):
    """
    Middleware that logs every tool call with timestamps and semantic summaries.
    Appends structured logs to memory_bank/Logs.log
    """
    
    def __init__(self):
        self.semantic_tools = {
            'intelligent_context_executor',
            'suggest_files_to_update',
            'analyze_project_summary'
        }
        self.logger = self._setup_logger()
    
    def _setup_logger(self) -> logging.Logger:
        """Set up logging for tool calls"""
        logger = logging.getLogger('tool_logging')
        logger.setLevel(logging.INFO)
        
        # Create memory_bank directory if it doesn't exist
        memory_bank_dir = Path("memory_bank")
        memory_bank_dir.mkdir(exist_ok=True)
        
        handler = RotatingFileHandler(
            memory_bank_dir / "Logs.log",
            maxBytes=50*1024*1024,  # 50MB
            backupCount=10
        )
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
        return logger
    
    async def on_call_tool(self, context: MiddlewareContext, tool_name: str, arguments: Dict[str, Any]) -> None:
        """Called when a tool is invoked"""
        # Sanitize arguments for logging
        sanitized_args = self._sanitize_arguments(arguments)
        
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'tool': tool_name,
            'arguments': sanitized_args,
            'session_id': str(id(context))
        }
        
        # Add semantic summary for specific tools
        if tool_name in self.semantic_tools:
            log_entry['semantic_summary'] = self._generate_semantic_summary(tool_name, arguments)
        
        # Log the tool call
        self.logger.info(f"TOOL_CALL: {json.dumps(log_entry, indent=2)}")
    
    def _sanitize_arguments(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize arguments to remove sensitive information"""
        sanitized = {}
        for key, value in arguments.items():
            if isinstance(value, str) and len(value) > 1000:
                sanitized[key] = f"<truncated:{len(value)}chars>"
            elif key.lower() in ['password', 'token', 'secret', 'key']:
                sanitized[key] = "<redacted>"
            else:
                sanitized[key] = value
        return sanitized
    
    def _generate_semantic_summary(self, tool_name: str, arguments: Dict[str, Any]) -> str:
        """Generate semantic summary for specific tools"""
        if tool_name == 'intelligent_context_executor':
            query = arguments.get('query', 'unknown')
            return f"Executed intelligent context query: {query[:100]}..."
        elif tool_name == 'suggest_files_to_update':
            context = arguments.get('context', 'unknown')
            return f"Suggested file updates based on: {context[:100]}..."
        elif tool_name == 'analyze_project_summary':
            return "Analyzed project summary and structure"
        
        return "No semantic summary available"


class MemoryCompletenessEnforcementMiddleware(Middleware):
    """
    Middleware that enforces memory completeness by checking for required updates.
    Triggers on session end and calls auto_detect_project_changes and suggest_files_to_update.
    """
    
    def __init__(self):
        self.session_activities = defaultdict(list)
        self.logger = self._setup_logger()
    
    def _setup_logger(self) -> logging.Logger:
        """Set up logging for memory completeness"""
        logger = logging.getLogger('memory_completeness')
        logger.setLevel(logging.INFO)
        
        # Create memory_bank directory if it doesn't exist
        memory_bank_dir = Path("memory_bank")
        memory_bank_dir.mkdir(exist_ok=True)
        
        handler = RotatingFileHandler(
            memory_bank_dir / "MemoryCompleteness.log",
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5
        )
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
        return logger
    
    async def on_call_tool(self, context: MiddlewareContext, tool_name: str, arguments: Dict[str, Any]) -> None:
        """Track tool usage for completeness analysis"""
        session_id = str(id(context))
        self.session_activities[session_id].append({
            'tool': tool_name,
            'timestamp': datetime.now().isoformat(),
            'arguments': arguments
        })
    
    async def on_session_end(self, context: MiddlewareContext) -> None:
        """Called when a session ends - enforce memory completeness"""
        session_id = str(id(context))
        activities = self.session_activities.get(session_id, [])
        
        if not activities:
            return
        
        # Analyze session activities
        completeness_report = self._analyze_completeness(activities)
        
        # Log completeness analysis
        self.logger.info(f"Session {session_id} completeness analysis:")
        self.logger.info(json.dumps(completeness_report, indent=2))
        
        # Generate completeness prompt
        prompt = self._generate_completeness_prompt(completeness_report)
        
        # In a real implementation, this would trigger the MCP tools
        # For now, we log the recommended actions
        self.logger.info(f"Recommended actions: {prompt}")
    
    def _analyze_completeness(self, activities: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze session activities for completeness"""
        tools_used = [activity['tool'] for activity in activities]
        tool_counts = Counter(tools_used)
        
        # Check for memory-related tools
        memory_tools = {
            'auto_detect_project_changes',
            'suggest_files_to_update',
            'update_memory_bank_file'
        }
        
        memory_tools_used = set(tools_used) & memory_tools
        
        return {
            'total_tools': len(activities),
            'unique_tools': len(set(tools_used)),
            'tool_counts': dict(tool_counts),
            'memory_tools_used': list(memory_tools_used),
            'memory_completeness_score': len(memory_tools_used) / len(memory_tools),
            'requires_memory_update': len(memory_tools_used) == 0 and len(activities) > 3
        }
    
    def _generate_completeness_prompt(self, report: Dict[str, Any]) -> str:
        """Generate prompt for memory completeness"""
        if report['requires_memory_update']:
            return (
                "Session analysis indicates memory bank updates are needed:\n"
                "1. Call auto_detect_project_changes to identify changes\n"
                "2. Call suggest_files_to_update to get update recommendations\n"
                "3. Update the following memory files:\n"
                "   - decision_logs.py (for decisions made)\n"
                "   - change_log.py (for changes implemented)\n"
                "   - system_architecture.py (for structural changes)\n"
                "   - config_map.py (for configuration changes)\n"
            )
        
        return "Memory bank appears to be up to date based on session activities."


class CrossReferenceRedundancyMiddleware(Middleware):
    """
    Middleware that minimizes redundancy by maintaining content index and suggesting cross-references.
    Triggers on memory bank file updates.
    """
    
    def __init__(self):
        self.content_index = {}  # MD5 hash -> file info
        self.similarity_threshold = 0.3  # 30% similarity threshold
        self.logger = self._setup_logger()
    
    def _setup_logger(self) -> logging.Logger:
        """Set up logging for cross-reference analysis"""
        logger = logging.getLogger('cross_reference')
        logger.setLevel(logging.INFO)
        
        # Create memory_bank directory if it doesn't exist
        memory_bank_dir = Path("memory_bank")
        memory_bank_dir.mkdir(exist_ok=True)
        
        handler = RotatingFileHandler(
            memory_bank_dir / "CrossReference.log",
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5
        )
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
        return logger
    
    async def on_call_tool(self, context: MiddlewareContext, tool_name: str, arguments: Dict[str, Any]) -> None:
        """Monitor file updates for redundancy analysis"""
        if tool_name in ['edit_file', 'create_file', 'update_memory_bank_file']:
            file_path = arguments.get('target_file') or arguments.get('file_path')
            
            if file_path and 'memory_bank' in file_path:
                await self._analyze_content_redundancy(file_path, arguments)
    
    async def _analyze_content_redundancy(self, file_path: str, arguments: Dict[str, Any]) -> None:
        """Analyze content for redundancy and suggest cross-references"""
        try:
            # Get content from arguments or read from file
            content = arguments.get('content') or arguments.get('code_edit', '')
            
            if not content:
                return
            
            # Calculate content hash
            content_hash = hashlib.md5(content.encode()).hexdigest()
            
            # Check for similar content
            similar_files = self._find_similar_content(content)
            
            if similar_files:
                # Log redundancy detection
                self.logger.info(f"Redundancy detected in {file_path}")
                self.logger.info(f"Similar content found in: {similar_files}")
                
                # Generate cross-reference suggestions
                suggestions = self._generate_cross_reference_suggestions(file_path, similar_files)
                self.logger.info(f"Cross-reference suggestions: {suggestions}")
            
            # Update content index
            self.content_index[content_hash] = {
                'file_path': file_path,
                'content_preview': content[:200],
                'timestamp': datetime.now().isoformat(),
                'word_count': len(content.split())
            }
            
        except Exception as e:
            self.logger.error(f"Error analyzing content redundancy: {e}")
    
    def _find_similar_content(self, content: str) -> List[str]:
        """Find files with similar content using simple text similarity"""
        similar_files = []
        content_words = set(content.lower().split())
        
        for content_hash, file_info in self.content_index.items():
            existing_words = set(file_info['content_preview'].lower().split())
            
            # Calculate Jaccard similarity
            intersection = len(content_words & existing_words)
            union = len(content_words | existing_words)
            
            if union > 0:
                similarity = intersection / union
                if similarity > self.similarity_threshold:
                    similar_files.append(file_info['file_path'])
        
        return similar_files
    
    def _generate_cross_reference_suggestions(self, current_file: str, similar_files: List[str]) -> List[str]:
        """Generate cross-reference suggestions"""
        suggestions = []
        
        for similar_file in similar_files:
            # Extract meaningful reference
            file_name = Path(similar_file).stem
            suggestions.append(f"[[see:{file_name} {datetime.now().strftime('%Y-%m-%d %H:%M')}]]")
        
        return suggestions


class AgentBehaviorProfilerMiddleware(Middleware):
    """
    Middleware that tracks agent behavior patterns and generates profiling reports.
    Monitors tool usage frequency and memory adherence.
    """
    
    def __init__(self):
        self.session_stats = defaultdict(lambda: {
            'tool_usage': Counter(),
            'start_time': time.time(),
            'memory_tools_used': 0,
            'core_tools_used': 0,
            'total_tools': 0
        })
        self.memory_tools = {
            'auto_detect_project_changes',
            'suggest_files_to_update',
            'update_memory_bank_file',
            'intelligent_context_executor'
        }
        self.logger = self._setup_logger()
    
    def _setup_logger(self) -> logging.Logger:
        """Set up logging for behavior profiling"""
        logger = logging.getLogger('agent_behavior_profiler')
        logger.setLevel(logging.INFO)
        
        # Create memory_bank directory if it doesn't exist
        memory_bank_dir = Path("memory_bank")
        memory_bank_dir.mkdir(exist_ok=True)
        
        handler = RotatingFileHandler(
            memory_bank_dir / "AgentBehaviorProfile.log",
            maxBytes=20*1024*1024,  # 20MB
            backupCount=10
        )
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
        return logger
    
    async def on_call_tool(self, context: MiddlewareContext, tool_name: str, arguments: Dict[str, Any]) -> None:
        """Track tool usage for behavior profiling"""
        session_id = str(id(context))
        stats = self.session_stats[session_id]
        
        # Update statistics
        stats['tool_usage'][tool_name] += 1
        stats['total_tools'] += 1
        
        if tool_name in self.memory_tools:
            stats['memory_tools_used'] += 1
        else:
            stats['core_tools_used'] += 1
    
    async def on_session_end(self, context: MiddlewareContext) -> None:
        """Generate behavior profile report at session end"""
        session_id = str(id(context))
        stats = self.session_stats[session_id]
        
        if stats['total_tools'] == 0:
            return
        
        # Calculate behavior metrics
        session_duration = time.time() - stats['start_time']
        memory_adherence_ratio = stats['memory_tools_used'] / stats['total_tools']
        
        # Generate comprehensive report
        report = {
            'session_id': session_id,
            'timestamp': datetime.now().isoformat(),
            'session_duration_seconds': round(session_duration, 2),
            'total_tools_used': stats['total_tools'],
            'memory_tools_used': stats['memory_tools_used'],
            'core_tools_used': stats['core_tools_used'],
            'memory_adherence_ratio': round(memory_adherence_ratio, 3),
            'tool_usage_frequency': dict(stats['tool_usage']),
            'most_used_tools': [
                {'tool': tool, 'count': count}
                for tool, count in stats['tool_usage'].most_common(5)
            ],
            'behavior_classification': self._classify_behavior(memory_adherence_ratio, stats),
            'recommendations': self._generate_recommendations(memory_adherence_ratio, stats)
        }
        
        # Log comprehensive report
        self.logger.info("=== AGENT BEHAVIOR PROFILE REPORT ===")
        self.logger.info(json.dumps(report, indent=2))
        
        # Clean up session data
        del self.session_stats[session_id]
    
    def _classify_behavior(self, memory_adherence_ratio: float, stats: Dict[str, Any]) -> str:
        """Classify agent behavior based on metrics"""
        if memory_adherence_ratio >= 0.7:
            return "Memory-Conscious Agent"
        elif memory_adherence_ratio >= 0.4:
            return "Balanced Agent"
        elif memory_adherence_ratio >= 0.2:
            return "Task-Focused Agent"
        else:
            return "Memory-Negligent Agent"
    
    def _generate_recommendations(self, memory_adherence_ratio: float, stats: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on behavior analysis"""
        recommendations = []
        
        if memory_adherence_ratio < 0.3:
            recommendations.append("Increase usage of memory bank tools for better context retention")
            recommendations.append("Consider calling auto_detect_project_changes more frequently")
        
        if stats['total_tools'] > 50:
            recommendations.append("High tool usage detected - consider optimizing workflow")
        
        # Check for tool diversity
        unique_tools = len(stats['tool_usage'])
        if unique_tools < 5:
            recommendations.append("Limited tool diversity - explore more available tools")
        
        if not recommendations:
            recommendations.append("Good balance of tool usage and memory adherence")
        
        return recommendations 