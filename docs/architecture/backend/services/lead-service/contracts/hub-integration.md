# Hub / Inter-Service Integration — LEAD

> How `lead-service` integrates with other Journey OS services. Sync via Feign (Eureka discovery),
> async via Kafka. EARS where behaviour is testable.

## 1. Upstream dependencies (LEAD calls)

### WRKS — `AccessEvaluateClient` (`@FeignClient(name = "wrks-service")`)
- Operation: `POST /api/v1/iam/access/evaluate` → `AccessDecisionResponse` (papel, permissoes[], dataScope, modeloAcessoVersao, sessionPolicy).
- Used by the security layer to authorize `lead.*` permissions; result cached in Redis.
- `WHILE a cached AccessDecision matches the current modelo_acesso_versao, THE SYSTEM SHALL authorize from cache without calling WRKS.`
- `IF WRKS is unavailable AND no valid cache entry exists, THEN THE SYSTEM SHALL deny access with 503 (fail-closed for authorization).`
- JWT validation uses WRKS JWKS (`/.well-known/jwks.json`).

## 2. Downstream consumers (react to LEAD events)

| Consumer | Event(s) | Purpose |
|---|---|---|
| **JRNY** | `lead.qualificado`, `lead.score.atualizado`, `lead.segmento.alterado` | route/assign qualified leads to journeys/SDRs |
| **SALE** | `lead.qualificado`, `lead.score.atualizado` | prioritize pipeline / opportunity creation |
| **COMM** | `lead.qualificado`, `lead.segmento.alterado` | trigger segmented nurturing |
| **INTL** | `lead.capturado`, `lead.qualificado`, `lead.score.atualizado` | analytics, score time-series, knowledge |
| **WRKS** | `lead.*` (all) | consolidated audit (`evento_auditoria` + Elastic `audit-events`) |

LEAD does **not** call JRNY/SALE/COMM/INTL synchronously — integration downstream is event-only
(ADR-003), keeping LEAD decoupled from services that may not exist yet.

## 3. Platform dependencies

| Service | Role |
|---|---|
| **REG (Eureka)** | discovery for the WRKS Feign client |
| **GWY** | edge routing of authenticated calls into LEAD |
| **MIG** | prepares/owns `emp_<slug>` schema (LEAD runs `ddl-auto=validate`) |

## 4. Resilience

- Resilience4j circuit breaker + timeout on the WRKS Feign call; authorization fails closed.
- Outbox pattern for event publish (no lost/duplicated domain events).
