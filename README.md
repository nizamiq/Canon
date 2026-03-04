---
id: canon-readme-v1
title: "Canon: AI Agent Prompt Registry"
description: "Human-readable overview of the Canon prompt registry."
tags: [readme, canon, prompt-registry, overview, architecture, oac]
status: STABLE
last_audited: "2026-03-04"
authoritative_source: "README.md"
version: 1.0.0
---

# Canon

**The Centralized AI Agent Prompt Registry for the NizamIQ Ecosystem**

## Overview

Canon provides a single, authoritative, version-controlled, and auditable source of truth for all prompts, personas, and configurations used by AI agents in the NizamIQ ecosystem.

## Place in the Ecosystem

Canon occupies **Layer 5 (L5) - Prompt Registry** within the [NizamIQ 7-Layer Agentic Architecture](https://github.com/nizamiq/nizamiq-strategy/blob/main/03_technical/agentic_architecture.md). Its primary responsibility is to act as a version-controlled, governed source of truth for all agent prompts. By ensuring all agents utilize approved prompts, Canon prevents prompt drift and guarantees consistent behavior across the ecosystem. It interacts closely with **Mem0 (L4)**, which provides long-term semantic memory, and supplies prompts to various consumers, including specialized pipelines like **Atlas (L6)** and **Recce (L6)**.

Furthermore, Canon plays a crucial role in the [ADR-011 Declarative Organisation as Code (OaC) Framework](https://github.com/nizamiq/nizamiq-strategy/blob/main/docs/architecture/ADR_011_Declarative_OaC.md). The version-controlled prompts managed by Canon are integral to the declarative `Playbook` manifests, which define business use cases and agent workflows within the OaC framework. This ensures that the underlying intelligence driving these automated processes is consistent, auditable, and aligned with architectural standards.

## Problem Statement

A comprehensive audit revealed that AI agent prompts are fragmented across:
- Hardcoded Python strings (anchorlink)
- YAML configuration files (Fireside)
- JSON "reference packs" (Atlas)
- Duplicated markdown files (CI/CD review prompts)

This leads to:
- **Inconsistency:** Different agents use different prompts for similar tasks
- **No Governance:** No approval workflow for prompt changes
- **No Audit Trail:** Cannot track who changed what and why
- **Difficult Iteration:** Prompt updates require code redeployment

## Solution

Canon solves this by providing:

| Feature | Benefit |
| :--- | :--- |
| **Centralized Storage** | All prompts in one place |
| **Semantic Versioning** | Stable, reproducible behavior |
| **Governance Workflow** | draft → review → active approval |
| **Immutable Audit Log** | Complete chain of custody |
| **Lightweight SDK** | Easy integration for services |

## Quick Start

```python
from canon_sdk import CanonClient

# Initialize client
client = CanonClient(
    base_url="https://canon.nizamiq.com",
    api_key="your-api-key"
)

# Get a prompt
prompt = client.get_prompt("code-review", version="1.2.0")
print(prompt.content)

# Create a new prompt (requires approval)
client.create_prompt(
    name="analytics-summary",
    content="Summarize the following data: {{data}}",
    variables=["data"]
)
```

## Architecture

```
┌─────────────────┐
│   Consumers     │
│  (Atlas, Recce) │
└────────┬────────┘
         │ canon-sdk
         ▼
┌─────────────────┐     ┌─────────────────┐
│  Canon Service  │────▶│  Aegis (Authz)  │
│    (FastAPI)    │     └─────────────────┘
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   PostgreSQL    │
│  (Prompts DB)   │
└─────────────────┘
```

## Roadmap

| Phase | Description | Status |
| :--- | :--- | :--- |
| 00 | Project Initialization | IN_PROGRESS |
| 01 | Core Service & API | PENDING |
| 02 | SDK Development | PENDING |
| 03 | First Integration | PENDING |

## Documentation

- [CONTEXT.md](./CONTEXT.md) - AI agent entry point
- [AGENTS.md](./AGENTS.md) - Agent scope check and guidelines
- [ADR-004](https://github.com/nizamiq/nizamiq-strategy/blob/main/docs/architecture/ADR_004_Prompt_Registry.md) - Architecture Decision Record

## Status

**Phase:** 00 - Project Initialization  
**Status:** INITIALIZING

---

*Canon - The canonical library from which all agents speak.*
