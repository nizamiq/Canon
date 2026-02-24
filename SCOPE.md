---
id: canon-scope
title: "Canon: Project Scope"
description: "Defines the explicit scope boundaries for the Canon project."
tags: ["canon", "scope", "governance"]
status: STABLE
last_audited: "2026-02-24"
authoritative_source: SCOPE.md
version: "1.0.0"
---

# Canon: Project Scope

## Purpose

AI prompt registry — provides a centralized, versioned registry for all AI prompts used across the ecosystem, enabling governance, A/B testing, and reusability.

## In Scope

The following capabilities and responsibilities are owned by this project:

- Centralized AI prompt registry
- Prompt versioning and governance
- A/B testing framework for prompts
- Prompt distribution API for all AI services

## Explicitly Out of Scope

AI inference and model execution (handled by individual AI engines). Identity and authentication (handled by Zitadel/Aegis). Infrastructure provisioning (handled by Plinth).

## Authoritative References

| Resource | Link |
| :--- | :--- |
| **Master Strategy** | [nizamiq/nizamiq-strategy](https://github.com/nizamiq/nizamiq-strategy) |
| **Ecosystem Map** | [ECOSYSTEM.json](https://github.com/nizamiq/nizamiq-strategy/blob/main/ECOSYSTEM.json) |
| **Architecture** | [ecosystem_architecture.md](https://github.com/nizamiq/nizamiq-strategy/blob/main/03_technical/ecosystem_architecture.md) |
