"""Stakeholders and Product Context Template"""

TEMPLATE = """# Stakeholders and Product Context

---
title: Stakeholders and Roles
tags: [context, stakeholders, roles, communication]
description: Key internal and external stakeholders and their responsibilities
memory_type: long_term
category: business_context
priority: medium
---


## Product Creators
Describe the team creating this product — their roles, background, and priorities.

Examples:
- Cross-functional team of backend engineers, AI researchers, and a product owner.
- Small founding team building MVPs rapidly, with an iterative mindset.
- Prefers open-source tools and low-overhead solutions over enterprise-grade complexity.

## Technical Preferences of Engineers
Capture the technical leanings and engineering preferences of the team to influence architecture, tool selection, and workflow.

- Preferred languages or frameworks (e.g., Python, TypeScript, FastAPI)
- DevOps preferences (e.g., GitHub Actions, Docker, local-first dev)
- Avoided tech or anti-patterns (e.g., monoliths, complex CI/CD in MVP)
- Standards or conventions the team follows (e.g., PEP8, DDD, clean architecture)

Example:
- Strong preference for Python over JS.
- Lightweight frameworks like FastAPI and Starlette.
- Minimal external dependencies in v1.
- Favor simple modular code over deeply layered abstractions.

## Product Consumers
Describe the intended users of this product — their goals, pain points, and expectations.

Examples:
- Internal analysts with limited coding skills.
- Gamers seeking story-based fantasy experiences with high immersion.
- Enterprise clients that prioritize stability and compliance.

## Alignment Considerations
Outline the key tensions or values that should guide decision-making during design/development.

Examples:
- Prioritize developer velocity over feature completeness in early stages.
- Minimize cognitive load in UI decisions.
- Favor extensibility even at the cost of initial setup complexity.

## Decision-Making Compass
When a trade-off must be made, the assistant should bias toward:
- [ ] Stability over Speed
- [ ] Clarity over Flexibility
- [ ] User Control over Automation
- [ ] Completeness over Simplicity
(Add checkboxes or comments based on team philosophy.)
"""
