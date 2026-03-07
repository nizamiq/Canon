---
id: canon-architecture-system-design
title: "Canon System Design"
description: "High-level architecture of the Canon AI agent prompt registry, including component diagrams, data flow, and integration patterns."
tags: ["architecture", "canon", "system-design", "prompt-registry"]
status: STABLE
last_audited: "2026-03-05"
authoritative_source: "src/canon/"
version: "1.0.0"
---

# Canon System Design

## Overview

Canon is the centralized AI agent prompt registry for the NizamIQ ecosystem. It provides a single, authoritative source of truth for all prompts, personas, and configurations used by AI agents.

## Core Components

### 1. Prompt Registry Service
- **Technology:** FastAPI (Python 3.12+)
- **Purpose:** RESTful API for prompt CRUD operations
- **Key Features:**
  - Versioned prompt storage
  - Tag-based categorization
  - Full-text search
  - Prompt validation

### 2. SDK (canon-sdk)
- **Technology:** Python package
- **Purpose:** Client library for integration
- **Key Features:**
  - LRU caching with TTL
  - Retry logic with exponential backoff
  - Type-safe prompt retrieval

### 3. Storage Layer
- **Primary:** PostgreSQL (prompt metadata)
- **Cache:** Redis (hot prompts)
- **Search:** Elasticsearch (full-text search)

## Data Flow

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│   Client    │────▶│  Canon API   │────▶│    Cache    │
│  (SDK/HTTP) │     │   (FastAPI)  │     │   (Redis)   │
└─────────────┘     └──────────────┘     └──────┬──────┘
                          │                      │
                          ▼                      ▼
                   ┌──────────────┐     ┌─────────────┐
                   │  PostgreSQL  │     │Elasticsearch│
                   │  (Metadata)  │     │   (Search)  │
                   └──────────────┘     └─────────────┘
```

## Integration Points

- **Aegis:** Authentication/authorization
- **Plaza:** Tool registration
- **Recce:** Agent prompt retrieval
- **Atlas:** Analytics on prompt usage

## Architecture Decisions

See ADR-004 in `docs/architecture/ADR_004_Prompt_Registry.md`
