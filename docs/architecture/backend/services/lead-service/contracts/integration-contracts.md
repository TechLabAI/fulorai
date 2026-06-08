# Integration Contracts — LEAD (external systems)

> External (non-Journey-OS) systems LEAD integrates with. Auth, limits, fallback, retry.

## 1. TechLab AI (capability `qualification`)

See `contracts/techlab-ai-integration.md` for the full contract. Summary:

- **Protocol:** HTTP (Docker image `ghcr.io/DaniloAmaral-Dev/techlab-ai:latest`, port 8090 local).
  Client lives in `infrastructure.clients` behind `TechLabQualificationPort`. **Never** a direct
  AI-provider call (CLAUDE.md rule).
- **Auth:** service JWT (`TECHLAB_AI_JWT_ENABLED`); correlationId/empresaId/principalId propagated as headers.
- **Resilience:** Resilience4j circuit breaker + timeout (short) + at most 1 retry. On any failure
  the score is computed deterministically (assist_ia=false). **Fail-open** for assist (unlike WRKS auth).
- **DTOs:** generated from `integrations/techlab-ai/openapi.json` (not hand-written). **Blocked** until
  P3 sync completes (snapshot currently empty) — feature is behind a config flag until then.

## 2. Elasticsearch (index `leads`, class *dimension*)

- **Protocol:** Java client (`direct-java-client`, `stack.elastic.ingestMode`).
- **Purpose:** prioritized queue, filtering and segmentation reads; mirror of the transactional lead.
- **Auth:** Elastic Cloud API key / basic (env `ELASTIC_URIS`, `ELASTIC_API_KEY`).
- `WHEN a lead's score or segment changes, THE SYSTEM SHALL (re)index the lead document in the leads index.`
- `IF Elasticsearch is unavailable, THEN THE SYSTEM SHALL keep the transactional write and queue/retry the index update (read path degrades, write path does not).`
- No PII beyond controlled fields is indexed (LGPD).

## 3. PostgreSQL + pgvector

- Operational store for `emp_<slug>`. pgvector available; **embeddings for profile similarity are
  post-MVP** (not used in the MVP score).

## Rate limits / SLA

| System | SLA target | Strategy |
|---|---|---|
| TechLab AI | p95 < 800 ms assist; timeout 1.5 s | circuit breaker, fail-open to deterministic |
| Elasticsearch | index lag < 5 s | async retry queue |
| WRKS (sync) | p95 < 30 ms cached | cache + fail-closed |
