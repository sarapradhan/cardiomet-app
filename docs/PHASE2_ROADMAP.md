# SAHC RiskLens — Phase 2 Production Roadmap
# Begins after Phase 1 complete + physician review + all-reviewer approval.

## Gate Before Phase 2
- [ ] All P5 release items complete
- [ ] Physician review documented in reports/physician_review_notes.md
- [ ] All three reviewer subagents approve Phase 2 plan

## P2.0 Clinical & Legal
- Physician review: licensed physician reviews Phase 1 output, findings addressed
- FDA CDS: legal counsel documents non-device CDS determination under 21st Century Cures Act
- Privacy policy + Terms of Service drafted and published
- HIPAA analysis: stateless tool, no PHI stored — document determination

## P2.1 Security
- Rate limiting: 100 req/hour per IP (slowapi)
- Request logging: method/path/status/timing only — NOT biomarker values
- CORS locked to production domain
- pip-audit + npm audit: no high/critical vulnerabilities
- Error messages: no biomarker values or stack traces to clients

## P2.2 Authentication (Optional)
Stateless (no login) strongly preferred — eliminates HIPAA complexity.
If needed: Clerk (easiest Next.js integration) or NextAuth.js.
Never store biomarker values server-side.

## P2.3 Infrastructure
Option A (recommended): Vercel Pro ($20/mo) + Railway Hobby ($5/mo)
Option B (scale): AWS ECS Fargate + Vercel Pro

## P2.4 CI/CD (GitHub Actions)
On PR: pytest, tsc --noEmit, ruff, npm run build
On merge to main: deploy staging
On tag: deploy production

## P2.5 Observability
Sentry (frontend + backend) · uptime monitoring · Plausible analytics (no cookies, no biomarkers)

## P2.6 Accessibility (WCAG 2.1 AA)
Keyboard navigation · ARIA labels · color contrast >= 4.5:1 (no red/green alone) ·
mobile responsive at 375px · Lighthouse score >= 90

## Phase 2 Release Criteria
All Phase 1 criteria + physician review documented + FDA CDS documented +
privacy policy published + CI/CD passing + security clean + WCAG audit complete
