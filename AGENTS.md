---
id: canon-agents-v1
title: "Canon: AI Agent Guidelines"
description: "Agent guidelines, scope checks, and governance directives for the Canon prompt registry."
tags: [agents, governance, canon, prompt-registry, scope]
status: DRAFT
last_audited: "2026-02-23"
authoritative_source: AGENTS.md
version: 1.0.0
---

# Canon: AI Agent Guidelines

---

## ⚠️ MANDATORY SCOPE CHECK — READ BEFORE ACTING

> **This repository is part of the NizamIQ ecosystem.**
>
> Before performing any work in any session, you **must** verify that the repository you are working on is listed as **in-scope** in the canonical ecosystem scope document:
>
> - **Human-readable:** [`nizamiq-strategy/SCOPE.md`](https://github.com/nizamiq/nizamiq-strategy/blob/main/SCOPE.md)
> - **Machine-readable:** [`nizamiq-strategy/ECOSYSTEM.json`](https://github.com/nizamiq/nizamiq-strategy/blob/main/ECOSYSTEM.json)
>
> **Canon Status:** `incubating` — Governance setup only, no phase execution without operator authorization.

**Active in-scope repositories:** `nizamiq-strategy`, `nizamiq.com`, `nizamiq-methodology`, `anchorlink`, `meridian`, `Fireside`, `Cornerstone`, `KubeClaw`, `Recce`, `Atlas`, `Aegis`, `gateway-config`, `documentation-standard`, `zitadel-config`, `Plaza`, `Canon`, `Charter`, `apex`, `tracer`, `Arnold`, `playbooks`

**Incubating:** `autonomous-product-studio`, `Axiom`

**Reference only (read-only):** `nizamiq-website`, `meridian-prime`

**Explicitly out of scope:** `sputnik-gateway` and any repository not listed above.


---

## Agent Entry Point

**Start here:** [CONTEXT.md](./CONTEXT.md)

## Current Phase

**Phase 00: Project Initialization**

See [manifest.json](./docs/planning/manifest.json) for detailed phase information.

## Project Purpose

Canon provides the centralized AI agent prompt registry for the NizamIQ ecosystem. It ensures:

1. **Single Source of Truth:** All prompts in one place
2. **Governance:** Aegis-enforced approval workflows
3. **Versioning:** Semantic version control for prompts
4. **Auditability:** Complete chain of custody

## ADR Reference

This project implements [ADR-004: Centralized AI Agent Prompt Registry](https://github.com/nizamiq/nizamiq-strategy/blob/main/docs/architecture/ADR_004_Prompt_Registry.md)

## Integration Points

| Consumer | Use Case |
| :--- | :--- |
| Atlas | Analytics agent prompts |
| Recce | Research agent prompts |
| CI/CD Pipeline | CodeX review prompts |
| meridian | Workflow automation prompts |

## Agent Responsibilities

When working on Canon:

1. **Verify Scope:** Check ECOSYSTEM.json before starting
2. **Follow UDS:** Adhere to the Unified Documentation Standard
3. **Update Manifest:** Record progress in phase YAML files
4. **Log Debt:** Document gaps in DEBT.md
5. **Governance First:** All prompt changes require Aegis authorization

## Planning Framework

This project uses the NizamIQ Planning Framework:

- **State Block Protocol:** Begin responses with `[STATE: Phase XX | STEP: XX.X | DEPS: OK/STALE]`
- **Verifiable Truth:** Provide proof of work for completed tasks
- **Linear Adherence:** Respect dependencies and execute sequentially
- **Manifest Updates:** Update manifest.json when phases complete

## Change Log

| Version | Date | Author | Changes |
| :--- | :--- | :--- | :--- |
| 1.0.0 | 2026-02-23 | Orchestrator Agent | Initial creation |

---

## ⚠️ Git Workflow — PR Mandate

- **Agents MUST open a Pull Request against `main` for every completed phase.** Direct pushes to `main` are not permitted.
- Branch naming: `phase/<phase-id>-<short-description>`, `fix/<short-description>`, or `chore/<short-description>`.
- The PR description must reference the completed phase YAML and summarise what was delivered.
- Do not merge your own PR — leave it open for human operator review and approval.

## ⚠️ Code Review Gate — CodeRabbit

- All CodeRabbit review findings **must be resolved** before a PR is eligible for merge.
- CodeRabbit is configured with `request_changes_workflow: true` — unresolved findings block merge via GitHub's Request Changes mechanism.
- All PR conversations must be marked resolved (`required_conversation_resolution` is enforced on `main` in branch protection).
- Do not dismiss or bypass CodeRabbit reviews without addressing the underlying finding.
