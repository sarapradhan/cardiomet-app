# Dependency audit disposition

Logged in response to an external repo review flagging `npm audit` findings with no documented triage. Updated 2026-08-09.

## `npm audit` — frontend (8 high severity)

All 8 findings trace to two packages: `next@14.2.35` and its bundled `postcss` (<=8.5.22).

| Advisory class | Count | Applies to this deployment? |
|---|---|---|
| Server Components / Server Actions DoS, SSRF, cache poisoning, Middleware bypass, Image Optimization API DoS, unauthenticated Server Function disclosure | 7 | **No, at runtime.** `frontend/next.config.js` sets `output: 'export'` — the app builds to a static `out/` directory and is served by FastAPI in production (see `Dockerfile`). No Next.js server process, Server Components runtime, Server Actions, Middleware, or Image Optimization API is running in production. These CVEs assume a live Next.js server handling the relevant request types; a static export has none of that surface. |
| PostCSS XSS in stringified output / arbitrary file read via `sourceMappingURL` / path traversal | 4 (rolled into the same 8) | **No, at runtime — yes, at build time.** PostCSS runs during `next build`, not in the served artifact. A compromised PostCSS could theoretically read files during a build on a compromised or adversarial build machine; it does not expose a runtime endpoint to site visitors. |

**Disposition:** accepted, not urgent, for the current static-export deployment model. **Not closed** — this analysis is only valid as long as the deployment stays a static export with no Next.js server process. If the app ever moves to `next start` / a Node runtime (e.g., to support real SSR, API routes, or Server Actions), re-triage before shipping — most of these advisories would become live again.

**Planned remediation:** upgrade to `next@16.3.0` (the version `npm audit fix --force` proposes) as a scheduled maintenance item, not an emergency patch — it's a two-major-version jump (14 → 16) with breaking changes that needs its own test pass across the App Router pages, not a blind force-upgrade. Track via Dependabot (`.github/dependabot.yml`) so this doesn't silently go stale.

## Backend (`pip-audit` / dependency review)

Not run as part of this pass — no `pip-audit` output was available to triage. Add to the Phase 2 Stage 1 security checklist: run `pip-audit` against `requirements.txt` and document disposition the same way as above.

## Process going forward

- `.github/dependabot.yml` is now configured for `pip` and `npm` weekly update checks, so new advisories surface automatically instead of accumulating silently.
- Re-run this disposition whenever `next.config.js`'s `output` mode changes, or at least quarterly.
