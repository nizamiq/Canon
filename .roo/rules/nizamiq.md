---
id: nizamiq-roo-code-config
title: "NizamIQ — Roo Code Configuration (.roo/rules/nizamiq.md)"
description: "Custom instructions file that configures Roo Code to discover and enforce NizamIQ ecosystem governance."
status: STABLE
last_audited: "2026-02-22"
authoritative_source: "https://github.com/nizamiq/nizamiq-methodology/blob/main/tools/.roo/rules/nizamiq.md"
version: 2.0.0
---

# NizamIQ Governance Rules — Roo Code

These rules configure Roo Code to operate within the NizamIQ ecosystem governance framework.
All rules are mandatory and non-negotiable.

---

## Rule 1: Governance Bootstrap (AGIP)

Before taking any action in a NizamIQ repository, read `AGENTS.md` at the repository root.
If `AGENTS.md` is absent, fetch it and run the AGIP bootstrap:

```bash
# Fetch the canonical AGENTS.md
curl -fsSL https://raw.githubusercontent.com/nizamiq/nizamiq-methodology/main/tools/AGENTS.md -o AGENTS.md

# Run the AGIP governance bootstrap
curl -fsSL https://raw.githubusercontent.com/nizamiq/documentation-standard/main/scripts/agip_bootstrap.sh | bash
```

After bootstrap, read the following files before proceeding:
- `governance/standard/UDS.md`
- `governance/standard/AGIP.md`
- `governance/templates/governance/AI_AGENT_INSTRUCTIONS.md`

---

## Rule 2: Mandatory Onboarding Sequence

At the start of every session, read in this exact order:

1. `CONTEXT.md` (repository root)
2. `docs/planning/manifest.json`
3. `docs/planning/AGENTS.md`
4. The active phase YAML at `docs/planning/phases/phase_XX_<name>.yaml`

Do not begin any work until this sequence is complete.

---

## Rule 3: State Block on Every Response

Begin every response with:

```
[STATE: Phase XX | STEP: XX.X | DEPS: OK/STALE/BLOCKED]
```

---

## Rule 4: Plan-First Execution

Never propose or write application code without first:

1. Reading `manifest.json` to understand the current phase.
2. Reading the active `phase_XX.yaml` file.
3. Verifying your actions align with the documented plan.

---

## Rule 5: Verifiable Truth Protocol

Never mark a YAML step as `COMPLETED` based on generating code alone. You must:

1. Execute the `verification_method` command from the phase YAML.
2. Capture the full terminal output.
3. Paste it into the `proof_of_work` field.
4. Only then set `status: COMPLETED`.

---

## Rule 6: Sub-Agent Persona Activation

When a task maps to a specific sub-agent role, activate that persona and respect its permission boundaries:

| Persona | Write Access | Read-Only Access |
| :--- | :--- | :--- |
| Test Engineer | `/tests` | `/src` |
| Execution Engine | `/src` | `/tests` |
| Documentation Enforcer | `/docs` | All other paths |
| DevOps Agent | `.github/`, CI config files | All other paths |

---

## Rule 7: Circuit Breaker

If you fail to complete a step after three attempts:

1. Stop all execution immediately.
2. Set the step `status: BLOCKED` in the phase YAML.
3. Write a detailed explanation in the `observation` field.
4. Request human intervention from the AI Orchestrator.

---

## Rule 8: Out-of-Scope Handling

If a user requests work outside the active phase YAML, do not refuse outright. Instead:

1. Pause current execution.
2. Switch to "Discovery & Planning" mode.
3. Propose an update to `manifest.json` and a new phase YAML.
4. Await human authorization before proceeding.

---

## Authoritative Sources

| Standard | URL |
| :--- | :--- |
| Methodology Entry Point | `https://raw.githubusercontent.com/nizamiq/nizamiq-methodology/main/CONTEXT.md` |
| Code Generation Standards | `https://raw.githubusercontent.com/nizamiq/nizamiq-methodology/main/standards/01_code_generation_standards.md` |
| Agent Framework Integration | `https://raw.githubusercontent.com/nizamiq/nizamiq-methodology/main/protocols/02_agent_framework_integration.md` |
| Unified Documentation Standard | `https://raw.githubusercontent.com/nizamiq/documentation-standard/main/standard/UDS.md` |
| AGIP | `https://raw.githubusercontent.com/nizamiq/documentation-standard/main/standard/AGIP.md` |
