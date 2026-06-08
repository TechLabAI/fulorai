# Integration Contracts — SALE (external systems)

> External (non-Journey-OS) systems SALE talks to. SALE has a deliberately small external surface:
> it does **not** call AI providers (no TechLab AI in MVP) nor payment gateways directly.
> EARS where behaviour is testable. Guide: `docs/architecture/backend/standards/ears-notation.md`.

## 1. Elasticsearch (`revenue-events`, `campaign-events`)

| Aspect | Value |
|---|---|
| Purpose | Fact projections for revenue funnel, ROI by source/campaign, sales analytics |
| Indices | `revenue-events`, `campaign-events` (class *fact*, domainContext SALE) |
| Mode | `direct-java-client` (ingest); query for funnel/revenue dashboards |
| Auth | API key (`ELASTIC_API_KEY`) |
| Failure | Indexing is best-effort/async; a failed index **does not** roll back revenue recognition |

- `WHEN a compra is confirmed or revenue is attributed, THE SYSTEM SHALL project a document to revenue-events asynchronously.`
- `IF Elasticsearch is unavailable, THEN THE SYSTEM SHALL retain the transactional record and retry indexing without failing the request.`

## 2. Checkout / payment gateway (external — mediated, not direct)

| Aspect | Value |
|---|---|
| Examples | Hotmart, payment link, external checkout |
| Integration (MVP) | Inbound only: confirmed order pushed to `POST /api/v1/compras` (service token via GWY) |
| Integration (post-MVP) | INTL Event Platform normalizes the webhook → SALE consumes an integration event |
| Idempotency | `(id_externo, origem)` — duplicate webhooks never double-count revenue |
| Out of scope | Payment processing, antifraud, card capture, refunds execution (gateway-side) |

- `THE SYSTEM SHALL treat an incoming purchase as already-confirmed and SHALL NOT contact the gateway to charge.`
- `IF the same order is delivered more than once, THEN THE SYSTEM SHALL return the existing compra without recognizing revenue again.`

## 3. TechLab AI — not used in MVP

SALE declares **no** TechLab AI capability in the MVP. Attribution and LTV are deterministic and
explainable (ADR-005). A post-MVP `analytics` capability (revenue insights / forecast) would be
added via a port in `application.port.out` and a client in `infrastructure.clients` (Resilience4j +
fallback) — **never** a direct AI provider call.

## 4. Resilience defaults

| Concern | Default |
|---|---|
| WRKS Feign (auth) | timeout 2s; circuit breaker; deny-by-default on open |
| Elastic indexing | async; retry with backoff; never blocks revenue |
| Purchase ingestion | idempotent; safe to retry |

## 5. References

- `docs/architecture/integrations/` (project integration contracts)
- `contracts/hub-integration.md` (inter-service) · `contracts/event-contracts.md`
- ADR-005 (deterministic attribution; no AI in MVP)
