---
id: nizamiq-kimi-cli-config
title: "NizamIQ — Kimi-CLI Configuration (kimi.md)"
description: "Hook file that configures Kimi-CLI to discover and enforce NizamIQ ecosystem governance."
status: STABLE
last_audited: "2026-02-22"
authoritative_source: "https://github.com/nizamiq/nizamiq-methodology/blob/main/tools/kimi.md"
version: 2.0.0
---

# NizamIQ Governance — Kimi-CLI Configuration

This file configures Kimi-CLI to operate within the NizamIQ ecosystem governance framework.
All instructions in this file are mandatory and non-negotiable.

---

## Governance Entry Point

Your complete operating instructions are defined in the `AGENTS.md` file at the root of this repository.
Read it now, before taking any other action.

If `AGENTS.md` is not present at the repository root, fetch the canonical version:

```bash
curl -fsSL https://raw.githubusercontent.com/nizamiq/nizamiq-methodology/main/tools/AGENTS.md -o AGENTS.md
```

Then run the AGIP governance bootstrap:

```bash
curl -fsSL https://raw.githubusercontent.com/nizamiq/documentation-standard/main/scripts/agip_bootstrap.sh | bash
```

---

## Authoritative Standards

The following documents define the complete operating standards. Fetch and read them at session start:

```bash
# Methodology entry point
curl -fsSL https://raw.githubusercontent.com/nizamiq/nizamiq-methodology/main/CONTEXT.md

# Code generation standards
curl -fsSL https://raw.githubusercontent.com/nizamiq/nizamiq-methodology/main/standards/01_code_generation_standards.md

# Agent framework integration protocol
curl -fsSL https://raw.githubusercontent.com/nizamiq/nizamiq-methodology/main/protocols/02_agent_framework_integration.md

# Unified Documentation Standard
curl -fsSL https://raw.githubusercontent.com/nizamiq/documentation-standard/main/standard/UDS.md
```

---

## Core Behavioural Rules

1. Begin every response with the state block: `[STATE: Phase XX | STEP: XX.X | DEPS: OK/STALE/BLOCKED]`
2. Never write application code without first reading `docs/planning/manifest.json` and the active phase YAML.
3. Never mark a step `COMPLETED` without providing the terminal output of the `verification_method` as proof.
4. Activate the correct sub-agent persona (Test Engineer, Execution Engine, etc.) based on the task type.
5. Invoke the circuit breaker after three failed attempts on any single step.
6. If a request falls outside the active phase, propose a plan update rather than freelancing.
