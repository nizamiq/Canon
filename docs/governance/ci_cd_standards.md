---
id: canon-governance-ci-cd-standards
title: "Canon CI/CD Standards"
description: "Continuous integration and deployment standards for the Canon repository."
tags: ["governance", "ci-cd", "canon", "standards"]
status: STABLE
last_audited: "2026-03-05"
authoritative_source: ".github/workflows/"
version: "1.0.0"
---

# Canon CI/CD Standards

## Golden Pipeline

All pull requests must pass these 4 gates:

### Gate 1: Code Quality
- **Tools:** ruff, mypy
- **Checks:** Linting, formatting, type checking
- **Threshold:** Zero errors

### Gate 2: Verifiable Truth
- **Tools:** pytest
- **Checks:** Unit tests, integration tests
- **Threshold:** >90% coverage, all tests pass

### Gate 3: AI Autonomous Review
- **Tools:** CodeRabbit, CodeX
- **Checks:** Semantic review, security analysis
- **Threshold:** Zero blockers, <3 major issues

### Gate 4: Build & Security
- **Tools:** Docker, Trivy
- **Checks:** Container build, vulnerability scan
- **Threshold:** No critical/high vulnerabilities

## Workflows

- `.github/workflows/ci.yml` - Main CI pipeline
- `.github/workflows/nizamiq_standard.yml` - Golden Pipeline

## Deployment

- Staging: Automatic on merge to main
- Production: Manual approval required
