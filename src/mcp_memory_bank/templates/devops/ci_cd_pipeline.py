"""CI/CD Pipeline Template"""

TEMPLATE = """# CI/CD Pipeline

---
title: CI/CD Pipeline
tags: [ci, cd, pipeline, devops, automation]
description: CI/CD automation setup and best practices
memory_type: long_term
category: devops
priority: medium
---

## Overview
[Describe the goal and structure of the CI/CD pipeline for the project.]

## CI (Continuous Integration)
- [Describe the testing/build steps triggered on code commits.]
- [Mention tools used, e.g., GitHub Actions, CircleCI, Jenkins.]

## CD (Continuous Deployment/Delivery)
- [Describe deployment triggers and environments involved.]
- [Include staging vs. production differences.]

## Workflow Steps
1. [Code push]
2. [Run tests and linter]
3. [Build Docker image]
4. [Deploy to staging]
5. [Deploy to production upon approval]

## Key Tools and Integrations
- [Version control system (e.g., GitHub)]
- [Containerization (e.g., Docker)]
- [Cloud/infra services used (e.g., AWS ECS, Azure, etc.)]

## Failure Recovery
[Describe rollback strategy, test coverage, or alerting systems.]
"""
