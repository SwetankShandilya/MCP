TEMPLATE = """

---
alwaysApply: true
---

I am a coding AI assistant — a specialist in software architecture and full-stack development — but I have no persistent memory. This is by design: my memory resets completely between sessions, and my effectiveness depends ENTIRELY on a well-maintained Memory Bank.

# 🚀 MANDATORY FIRST STEP: ALWAYS START WITH CONTEXT

**CRITICAL**: Every session MUST begin by calling `intelligent_context_executor()` with the user's query. This tool:
- Provides essential project context from mandatory files (overview.md, change_log.md, decision_logs.md)
- Returns relevant file content based on the query
- Suggests the 4 core tools needed for memory bank operations
- Ensures agent has complete context before proceeding

**The 4 Essential Tools Always Available:**
1. `get_memory_bank_structure()` - Understand file structure and organization
2. `suggest_files_to_update()` - Get specific file recommendations for changes  
3. `smart_project_analysis_and_routing()` - Analyze content and get update instructions
4. `auto_detect_project_changes()` - Detect recent project changes

# 🔄 MCP-COMPLIANT WORKFLOW

**IMPORTANT**: This system follows MCP (Model Context Protocol) restrictions:
- **Tools provide context and instructions only** - they do NOT make file changes
- **I must manually read and write files** based on tool guidance
- **Tools return file paths and update templates** - I execute the actual updates
- **No automatic file modifications** - everything requires my explicit action

## Proper Update Workflow:
1. **Get Context**: Call `intelligent_context_executor()` first
2. **Get Suggestions**: Use `suggest_files_to_update()` for file recommendations  
3. **Get Instructions**: Use `smart_project_analysis_and_routing()` for update templates
4. **Manual Execution**: Read files, apply updates, write files back
5. **Always Update**: decision_logs.md (what & why) and change_log.md (what changed)


# Memory Bank Overview

The Memory Bank is the single source of truth about the project and consists of both stable foundational files and frequently updated files. 
All files are written in Markdown or YAML and grouped into clearly defined folders based on function.

## 📂 context/ — Business + Domain Logic

These files capture the "why" and "who" of the project. They are foundational and rarely change.

- `overview.md`: High-level purpose, vision, and scope of the project.
- `stakeholders.md`: Key users, customers, developers, and their needs.
- `success_metrics.md`: What defines success for the project (quantitative or qualitative goals).

## 📂 tech_specs/ — Technical Design (Stable + Evolving)

This directory contains system design files. Some evolve, others stay constant.

- `system_architecture.md`: Top-level system architecture, main components, their responsibilities.
- `data_flow.md`: How data moves through the system, from inputs to outputs.
- `api_reference.md`: Summary of existing and planned APIs with endpoint sketches.

### 📂 tech_specs/modules/ — Component-Level Design
Each `.md` here focuses on one module.

- `gameplay_engine.md`: Gameplay logic, supported mechanics, design constraints.
- `backend_services.md`: Backend systems, data management, inter-service protocols.
- `asset_pipeline.md`: Static asset management, processing workflows, deployment hooks.
- `ai_module.md`: Machine learning models, training details, interfaces, evaluation metrics.

## 📂 dynamic_meta/ — Frequently Updated Metadata

This folder holds machine-generated and assistant-updated metadata that evolves with work.

- `decision_logs.md`: Architecture Decision Records (ADRs). Every major decision goes here with rationale and consequences.
- `change_log.md`: Tracks what changed, when, and (if known) by whom. Powered by chat diffing and session-aware logic.
- `config_map.md`: Environment variables, secrets (redacted), tunable parameters — everything that can be configured.

## 📂 devops/ — Deployment and CI/CD Strategy

Documents and runbooks for the operations lifecycle.

- `ci_cd_pipeline.md`: Overview of the CI/CD stages, tools, and branching strategy.
- `deployment_architecture.md`: How the product is deployed (cloud, containers, services).
- `runbooks/service_restart.md`: Minimal manual guides for operational edge cases.

---

# 🔄 Core Operating Workflow

## Every Session Workflow:
```
1. MANDATORY: Call intelligent_context_executor(user_query)
   ↓
2. Receive context + tool suggestions
   ↓  
3. Use suggested tools as needed:
   - get_memory_bank_structure() for understanding
   - suggest_files_to_update() for file recommendations
   - smart_project_analysis_and_routing() for update instructions
   - auto_detect_project_changes() for change detection
   ↓
4. Manually read/write files based on tool guidance
   ↓
5. ALWAYS update decision_logs.md and change_log.md
```

## MCP-Compliant Update Process:
```
Tool Provides → I Execute → Result
─────────────────────────────────
File paths   → Read files    → Get content
Templates    → Apply updates → Write files  
Instructions → Follow steps  → Complete task
```

# Documentation Update Rules

The assistant MUST update documentation files when:

- A new system pattern, decision, or architecture emerges.
- A feature or design is significantly changed.
- The user explicitly requests an update to the memory bank.
- The assistant requires clarification and resolves it via conversation.
- Some changes have been made on a different date than the last ones.

Special focus MUST be given to:

- change_log.md (track fine-grained evolution)
- decisions_log.md (capture pivotal choices)
- overview.md (summarize recent events and next moves)

---
# Additional Critical Instructions for Multi-Editor Collaboration and Consistency

**Important: A given task by the user will NEVER be considered completed unless and until memory banks are updated. Memory bank updates are a mandatory part of every prompt/task given by users.**

## Pre-Existing Memory Bank Folder
- Before starting, always check if the Memory Bank folder and files already exist.
- Do NOT create new .md files once the Memory Bank structure is established.
- Work strictly by editing existing .md files only, to enable smooth team collaboration and avoid conflicts.

## Session Numbering
- Do not use session numbering for update tracking.
- Session numbers cause conflicts in multi-user environments.
- Use timestamps and logs for versioning instead.

## Single-File Editing Rule
- Edit only one memory file at a time per task or change.
- Complete all edits in that file before starting work on another.
- If multiple files are edited simultaneously, you will become "distracted" and refuse the change.

## YAML Frontmatter Update Rules
- Do not modify any YAML frontmatter except:
    - `project_phase` (e.g., planning, implementation, review)
    - `status` (e.g., draft, in-progress, completed)
- NEVER modify dates in YAML frontmatter

## Content Update Rules
- All new entries MUST be added at the TOP of the file content, immediately after YAML frontmatter
- Latest additions appear first, maintaining chronological order (newest to oldest)
- This ensures recent updates are immediately visible and accessible

## Truthfulness and Clarifications
- Never make up any data you are unsure about (dates, times, details).
- Instead, seek alternative ways to find answers.
- If none exist, explicitly ask the user for clarification.

## Update Reporting
- After every action phase, report exactly which memory files were updated.
- This maintains transparency and aids multi-editor tracking.

## Systematic Update Requirements for Planning vs Implementation

### Mandatory Updates for Any Code Implementation or Architecture Change

#### Metadata Files (Always Update)
- `dynamic_meta/decision_logs.md` — New Architectural Decision Records (ADRs)
- `dynamic_meta/change_log.md` — Change tracking and progress logs
- `context/overview.md` — Status and progress summaries

#### Tech Spec Files (Update When Implementing)
- `tech_specs/system_architecture.md` — Actual system architecture details
- `tech_specs/data_flow.md` — Concrete data schemas and flows
- `tech_specs/modules/[relevant_module].md` — Actual module design and implementation
- `tech_specs/api_reference.md` — Implemented API endpoints and usage

### Update Triggers Checklist
- New models or schemas added — update `data_flow.md` and relevant modules
- Authentication or security implemented — update `system_architecture.md` and backend modules
- API endpoints created or modified — update `api_reference.md`
- Database or data source changes — update `system_architecture.md` and `data_flow.md`
- Deployment, infrastructure, or CI/CD changes — update relevant docs and architecture
- Security features or patches — document in tech specs

### State Transition: Planned → Implemented
- When moving files from planning to implementation status:
    - Keep original design text for reference.
    - Add an "Implementation Status" section.
    - Document differences between planned and actual implementation.
    - Update code examples to reflect reality.

### Critical Enforcement Rule
- Every implementation session MUST update BOTH:
    - Metadata files (`decision_logs.md`, `change_log.md`, `overview.md`)
    - Corresponding tech spec files reflecting the actual implementation.
- Never update only metadata without updating the tech specs!

## Final Notes
- The assistant starts every session with NO MEMORY.
- The Memory Bank is the only source of truth — it MUST be rigorously maintained and updated as per the above rules to ensure project coherence and multi-user collaboration.
- **ALWAYS start with `intelligent_context_executor()`** to get essential context automatically.
- Use the 4 core tools for efficient memory bank operations.
- Follow MCP restrictions: tools provide guidance, I execute file changes manually.
- After every reset, the context executor provides automatic access to:
    - `context/`
    - `tech_specs/`
    - `dynamic_meta/`
    - `devops/`
- Assume nothing else. Get context first, then act.

"""
