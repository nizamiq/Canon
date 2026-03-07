---
id: canon-governance-ai-agent-instructions
title: "Canon AI Agent Instructions"
description: "Operating instructions for AI agents working in the Canon prompt registry repository."
tags: ["governance", "agents", "canon", "instructions"]
status: STABLE
last_audited: "2026-03-05"
authoritative_source: "AGENTS.md"
version: "1.0.0"
---

# Canon AI Agent Instructions

## ⚠️ MANDATORY SCOPE CHECK

Before performing any work, verify this repository is in-scope:
- **Human-readable:** [nizamiq-strategy/SCOPE.md](https://github.com/nizamiq/nizamiq-strategy/blob/main/SCOPE.md)
- **Machine-readable:** [nizamiq-strategy/ECOSYSTEM.json](https://github.com/nizamiq/nizamiq-strategy/blob/main/ECOSYSTEM.json)

## Repository Purpose

Canon is the centralized AI agent prompt registry. It stores, versions, and serves prompts to all NizamIQ agents.

## Development Guidelines

### Code Standards
- Python 3.12+ with type hints
- FastAPI for API endpoints
- Pydantic v2 for models
- pytest for testing (target >90% coverage)

### Prompt Management
- All prompts must be versioned
- Use semantic versioning for prompt changes
- Tag prompts by domain and purpose
- Validate prompts before storage

### SDK Development
- Maintain backward compatibility
- Document all public methods
- Include usage examples

## CI/CD

All PRs must pass the Golden Pipeline:
1. Code Quality (linting, formatting)
2. Verifiable Truth (tests)
3. AI Autonomous Review
4. Build & Security

## Key Files

- `src/canon/` - Main application code
- `canon-sdk/` - Python SDK package
- `tests/` - Test suite
- `docs/` - Documentation
