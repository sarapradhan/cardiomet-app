# Security Policy

CardioMet Lens is an educational prototype (see [Project status](./README.md#project-status)). It does not store patient values server-side, but it does handle sensitive health inputs in transit and in the browser, so security reports are welcome and taken seriously.

## Reporting a vulnerability

Please report suspected vulnerabilities privately rather than opening a public issue:

- Open a [GitHub private security advisory](../../security/advisories/new) for this repository, or
- Email the maintainer directly (see the GitHub profile for contact info) with a description, reproduction steps, and impact assessment.

Please do not include real patient or personal health data in a report — use synthetic values.

## Scope

In scope: the FastAPI backend (`api/`, `sahc_risklens/`), the Next.js frontend (`frontend/`), the CardioSafeBench harness (`cardiosafebench/`), and the deployment/CI configuration (`.github/workflows/`, `Dockerfile`).

Out of scope: third-party services this project depends on (report those upstream), and denial-of-service reports against demo/staging infrastructure.

## Current known gaps (tracked, not hidden)

This project has not yet completed a formal security review. Known open items — dependency audit triage, rate limiting, CORS lock to production domain, dependency/container scanning, branch protection — are tracked in `docs/PHASE2_ROADMAP.md`. If you find something not already listed there, please report it.

## Supported versions

Pre-1.0, single-branch development. Only `main` receives fixes.
