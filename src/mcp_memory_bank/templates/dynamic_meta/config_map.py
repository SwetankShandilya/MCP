"""Config Map Template"""

TEMPLATE = """# Configuration & Secrets Map

---
title: Config Map
tags: [config, env_vars, secrets, setup]
description: Configuration variables and secret mapping
memory_type: short_term
category: metadata
priority: medium
---

environment:
  - key: [ENV_VAR_NAME]
    description: [What this env var controls]
    default: [default value if any]
    is_secret: [true | false]

parameters:
  - key: [PARAM_NAME]
    description: [Description of the parameter]
    default: [default value]

notes:
  - [Any special instructions, formats, or validation notes]
"""
