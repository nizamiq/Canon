---
id: canon-context-v1
title: "Canon: AI Agent Context"
description: "Primary entry point for AI agents working on the Canon prompt registry."
tags: [context, canon, prompt-registry, agents]
status: DRAFT
last_audited: "2026-02-23"
authoritative_source: "CONTEXT.md"
version: 1.0.0
---

# CONTEXT.md

**LAST UPDATED:** 2026-02-23

## 1. System Architecture

Canon is the centralized AI agent prompt registry for the NizamIQ ecosystem. It provides a single, authoritative, version-controlled, and auditable source of truth for all prompts, personas, and configurations used by AI agents.

**Core Purpose:** Eliminate prompt fragmentation and duplication, enforce governance, and accelerate the development of reliable AI-powered services.

## 2. Dependency Map

- **Languages:** Python 3.12+
- **Frameworks:** FastAPI, SQLAlchemy 2.0 (async), Alembic
- **Databases:** PostgreSQL 16+ (Neon Serverless)
- **Authorization:** Aegis SDK
- **Authentication:** Zitadel (OIDC/JWT)
- **Deployment:** Plinth (Kubernetes/Helm)

## 3. Execution Commands

| Action | Command |
| :--- | :--- |
| **Install Dependencies** | `pip install -e packages/canon-service` |
| **Run Tests** | `pytest packages/canon-service/tests/` |
| **Run Linter** | `ruff check packages/canon-service/` |
| **Format** | `black packages/canon-service/` |
| **Run Locally** | `uvicorn canon_service.app:app --reload` |
| **Database Migration** | `alembic upgrade head` |

## 4. CI/CD Pipeline

This repository uses the **NizamIQ Golden Pipeline** standard:

| Gate | Name | Description |
| :--- | :--- | :--- |
| 1 | **Code Quality** | Ruff linting, Black formatting |
| 2 | **Verifiable Truth** | Pytest with coverage > 80% |
| 3 | **AI Autonomous Review** | CodeRabbit deep review |
| 4 | **Build & Security** | Trivy vulnerability scan |

## 5. Project Structure

```
Canon/
├── src/
│   └── canon/
│       ├── api/              # FastAPI routes
│       ├── core/             # Business logic
│       ├── models/           # SQLAlchemy models
│       └── sdk/              # canon-sdk package
├── docs/
│   ├── architecture/         # System design
│   ├── api/                  # OpenAPI specs
│   ├── governance/           # Agent instructions
│   └── planning/             # Phase definitions
├── tests/                    # Test suite
├── CONTEXT.md               # This file
├── README.md                # Human overview
└── AGENTS.md                # Agent guidelines
```

## 6. Key Features

- **Centralized Prompt Storage:** Single repository for all prompt types
- **Semantic Versioning:** Stable, reproducible agent behavior
- **Governance Workflow:** Aegis-enforced RBAC (draft → review → active)
- **Immutable Audit Trail:** Complete chain of custody
- **Lightweight SDK:** Easy integration for consumer services

## 7. Current Phase

**Phase 00: Project Initialization**

See [manifest.json](./docs/planning/manifest.json) for phase tracking.

## 8. Integration Points

| Service | Integration |
| :--- | :--- |
| Aegis | Authorization for prompt CRUD operations |
| Zitadel | JWT validation for API access |
| Atlas | Consumer - uses prompts for analytics agents |
| Recce | Consumer - uses prompts for research agents |
| CI/CD Pipeline | Consumer - uses prompts for CodeX review |

## 9. ADR Reference

This project is defined by [ADR-004: Centralized AI Agent Prompt Registry](https://github.com/nizamiq/nizamiq-strategy/blob/main/docs/architecture/ADR_004_Prompt_Registry.md)

## Out of Scope

The following are explicit boundaries for this repository. Agents must not implement, refactor, or propose work in these areas without explicit operator authorisation:

- No prompt execution — prompt registry only; does not run prompts
- No application source code — prompt definitions and manifests only
- No AI inference — Canon stores, does not execute
- No user-facing UI — all presentation is Meridian or Arnold's responsibility
