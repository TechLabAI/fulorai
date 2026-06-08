# Hub Integration — SALE (inter-service)

> How `sale-service` integrates with other Journey OS services. Sync via Feign (WRKS), async via
> Kafka (LEAD upstream, downstream consumers). EARS where behaviour is testable.
> Guide: `docs/architecture/backend/standards/ears-notation.md`.

## 1. Upstream dependencies (SALE depends on)

| Service | Mode | Contract | Failure behaviour |
|---|---|---|---|
| **WRKS** | sync (Feign) | `AccessEvaluateClient` — `@FeignClient(name="wrks-service")`; evaluates `sale.*` permissions; JWKS for JWT validation | Resilience4j circuit breaker; deny-by-default on open circuit; 503 `sale.dependencia.indisponivel` |
| **WRKS** | async (consume) | `empresa.provisionada` (seed pipeline/ofertas/modelo), `modelo.acesso.alterado` (cache invalidation) | at-least-once; idempotent consumers |
| **LEAD** | async (consume) | `lead.qualificado` (create oportunidade), `lead.score.atualizado` (reprioritize) | at-least-once; idempotent by `leadId`; no hard dependency (oportunidade can be created via API) |
| **REG (Eureka)** | discovery | service registration/lookup for Feign | retry/backoff on registry unavailability |
| **MIG** | pre-condition | provisions `emp_<slug>` (SALE runs `ddl-auto=validate`) | boot fails fast if schema absent |

- `WHILE the WRKS circuit is open, THE SYSTEM SHALL deny sale.* authorization by default and respond 503 error.code 'sale.dependencia.indisponivel'.`
- `WHEN journey-os.lead.qualificado is consumed for a lead that already has an open oportunidade, THE SYSTEM SHALL update it rather than create a duplicate.`

## 2. Downstream consumers (depend on SALE — SALE does not know them)

| Consumer | Events consumed | Use |
|---|---|---|
| **INTL** | `compra.confirmada`, `receita.atribuida`, `oportunidade.*`, `ltv.atualizado` | revenue analytics, ROI, funnel (`revenue-events`/`campaign-events`) |
| **WRKS** | all `journey-os.*` | consolidated audit (`evento_auditoria` + `audit-events`) |
| **COMM** | `compra.confirmada` (post-sale), `oportunidade.estagio.alterado` | post-purchase / stage-based nurturing |
| **JRNY** | `oportunidade.criada` | funnel correlation (informational) |

- `THE SYSTEM SHALL NOT call INTL/COMM/JRNY synchronously; downstream integration is event-only (ADR-003).`

## 3. Purchase source (external, mediated)

| Source | Mode (MVP) | Mode (post-MVP) |
|---|---|---|
| Checkout / gateway (Hotmart, payment link) | `POST /api/v1/compras` with a service token (idempotent by `id_externo`+`origem`) | INTL Event Platform → consume an integration event |

- `THE SYSTEM SHALL NOT integrate a payment gateway directly nor execute payment; it records an already-confirmed order.`

## 4. Provided interfaces

SALE exposes **no** Feign client to other services in the MVP — downstream integration is
event-only. (Post-MVP: a `RevenueQueryClient` could expose read-only revenue/LTV to INTL if a sync
path is needed; not in scope.)

## 5. References

- `contracts/event-contracts.md` (payloads) · `contracts/integration-contracts.md` (external systems)
- `docs/architecture/backend/services/wrks-service/contracts/` (AccessDecision, WRKS events)
- `docs/architecture/backend/services/lead-service/contracts/event-contracts.md` (consumed `lead.*`)
- ADR-003 (messaging) · ADR-004 (multi-tenancy)
