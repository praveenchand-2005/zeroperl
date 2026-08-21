# Recovery Intelligence Platform

GitHub-native implementation of the V1–V4 Recovery Intelligence SaaS.

## Current implementation

- **V1:** multi-tenant recovery case foundation, authentication/RBAC, case management, audit, field/recovery architecture.
- **V2:** source registry, scoped scraping jobs, HTTP/browser acquisition, document parsing, evidence provenance, content hashing and background worker pipeline.
- **V3:** public/government/regulatory intelligence primitives, connector planning, evidence graph, address/temporal analysis, contradiction detection and human review.
- **V4:** public/professional profile candidates, employment records, company intelligence, organizational relationships and dedicated V4 API/UI.

## Security boundary

This platform is case-scoped and authorization-scoped. Public/authorized source acquisition must not bypass authentication, private access controls, CAPTCHAs, rate limits, or restricted systems. Public social/professional data is treated as evidence and must remain distinguishable from verified identity or employment facts.

## Validation

GitHub Actions CI is configured for the web, API, scraper and workers. The current GitHub integration is not reporting workflow runs yet, so CI status must be verified on GitHub before the branch is considered production-ready.
