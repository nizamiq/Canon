---
id: nizamiq-claude-code-config
title: "NizamIQ — Claude Code Configuration (CLAUDE.md)"
description: "Hook file that configures Claude Code to discover and enforce NizamIQ ecosystem governance."
status: STABLE
last_audited: "2026-02-22"
authoritative_source: "https://github.com/nizamiq/nizamiq-methodology/blob/main/tools/CLAUDE.md"
version: 2.0.0
---

# NizamIQ Governance — Claude Code Configuration

This file configures Claude Code to operate within the NizamIQ ecosystem governance framework.
All instructions in this file are mandatory and non-negotiable.

---

## Governance Entry Point

Your complete operating instructions are defined in the `AGENTS.md` file at the root of this repository.
Read it now, before taking any other action.

If `AGENTS.md` is not present at the repository root, fetch the canonical version:

```bash
curl -fsSL https://raw.githubusercontent.com/nizamiq/nizamiq-methodology/main/tools/AGENTS.md -o AGENTS.md
```

---

## Remote Context Files

Load the following remote documents as authoritative context. These override any conflicting local assumptions.

@https://raw.githubusercontent.com/nizamiq/nizamiq-methodology/main/CONTEXT.md
@https://raw.githubusercontent.com/nizamiq/nizamiq-methodology/main/standards/01_code_generation_standards.md
@https://raw.githubusercontent.com/nizamiq/nizamiq-methodology/main/protocols/02_agent_framework_integration.md
@https://raw.githubusercontent.com/nizamiq/documentation-standard/main/standard/UDS.md

---

## Core Behavioural Rules

1. Begin every response with the state block: `[STATE: Phase XX | STEP: XX.X | DEPS: OK/STALE/BLOCKED]`
2. Never write application code without first reading `docs/planning/manifest.json` and the active phase YAML.
3. Never mark a step `COMPLETED` without providing the terminal output of the `verification_method` as proof.
4. Activate the correct sub-agent persona (Test Engineer, Execution Engine, etc.) based on the task type.
5. Invoke the circuit breaker after three failed attempts on any single step.
6. If a request falls outside the active phase, propose a plan update rather than freelancing.
