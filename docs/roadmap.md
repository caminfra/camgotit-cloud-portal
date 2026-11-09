# Phased execution checklist

## Phase 0 — read-only subscription and governance checks
- [ ] Confirm CamGotIT-Lab subscription billing offer, state, ownership, and spending limitations
- [ ] Confirm Entra MFA/Security Defaults and licenses; never rely on assumed P1/P2 trials
- [ ] Confirm East US 2 free SQL tier is available to this subscription (auto-pause when free allowance exhausted)
- [ ] Confirm Container Apps **Consumption** plan, scale-to-zero and cost conditions before creation; no Dedicated workload profile
- [ ] Create Azure Cost Management budget: $30 monthly, alerts at $15 and $24, plus detailed billing review (budget is not a hard cap)
- [ ] Confirm GitHub CLI access and create `caminfra/camgotit-cloud-portal` repository under the intended owner
- [ ] Confirm developer Mac versions and iOS build tooling

## Phase 1 — local owner-only ticket prototype (starter implements basic workflow)
- [x] FastAPI local ticket creation, listing, and status updates and persistent local SQLite
- [x] React dashboard and internal ticket event alerts
- [x] Manual Lead Scout capture and draft templates
- [x] Add isolated API workflow tests
- [ ] Add CI workflow
- [ ] Add Entra login to SPA and JWT validation in the API
- [ ] Model ticket ownership, allowed roles and request audit history

## Phase 2 — Azure live DEV environment (synthetic data only)
- [ ] Terraform for rg, Azure Static Web Apps Free, Container Apps Consumption min replicas=0, Azure SQL Free tier
- [ ] GitHub OIDC, Azure RBAC least privilege, no client secrets
- [ ] DB schema migration + SQL TLS; restrict access as practical
- [ ] Deploy one API and one SPA; log API health and errors
- [ ] Add Azure Monitor operational alert email
- [ ] Add ticket-created **business event email** with retries, deduplication and audit log

## Phase 3 — iOS and original MVP acceptance test
- [ ] SwiftUI owner-only app with Entra token sign-in
- [ ] Create ticket on web and see it in iOS
- [ ] Update from iOS and confirm web reflects update from same API
- [ ] Alert and CI end-to-end test; test scale-to-zero and estimate costs

## Phase 4 — Lead Scout, marketing & onboarding
- [ ] Keep Lead Scout as a separate local/$0 prototype until authorized feeds are available
- [ ] Request Nextdoor developer access (if worthwhile) or continue manual lead capture
- [ ] Human-approved classification/draft/reply flow; never scrape or send unsolicited outreach
- [ ] Nextdoor business flyer and dedicated QR-tagged landing URL
- [ ] NFC card links to camgotit.com; optional contact download (vCard)

## Phase 5 — customer assistant
- [ ] Publish FAQ and prices from approved source-of-truth
- [ ] Begin with scripted intake; AI responses only after test, approved templates and budget cap
- [ ] Agent can recommend services and create a draft ticket, but not quote complex work or promise appointment slots
- [ ] Owner review and escalation for uncertain, urgent, or data-sensitive conversations

**Go-live gate**: independent business compliance/authorization, secure web + API auth, privacy/security review and customer communication policies. Google Business Profile verification is not an Azure dependency.
