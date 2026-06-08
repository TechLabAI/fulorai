# Hub Integration — JRNY (inter-service)

> Inter-service contracts within Journey OS. Sync calls use Feign over Eureka discovery through
> the platform's standard Resilience4j config. EARS for behavior.

## 1. Depends on (outbound, sync)

### WRKS — identity & authorization
- `AccessEvaluateClient` `@FeignClient(name = "wrks-service")` → `POST /api/v1/iam/access/evaluate`.
- JWKS: validate incoming JWT against `WRKS_JWKS_URI`.
- `WHEN a request arrives with a valid JWT, THE SYSTEM SHALL resolve the AccessDecision (role + jrny.* permissions + data scope) from WRKS, caching it until modelo_acesso_versao changes.`
- `IF the JWT is missing/invalid, THEN THE SYSTEM SHALL reject with 401 error.code 'jrny.auth.token-invalido'.`
- `IF the AccessDecision lacks the required jrny.* permission, THEN THE SYSTEM SHALL reject with 403 error.code 'jrny.acesso.permissao-negada'.`

### ASST — published stage content
- `AssetQueryClient` `@FeignClient(name = "asst-service")` → `GET /api/v1/assets/{id}/published`.
- `WHEN a stage with a non-null asset_ref_id is read, THE SYSTEM SHALL resolve the current published asset via AssetQueryClient and SHALL expose only published versions (never drafts).`
- `IF ASST is unreachable, THEN THE SYSTEM SHALL serve the last-known stage content reference and SHALL NOT fail journey definition or routing (content resolution is non-blocking to the decision).`

### MIG — tenant schema provisioning
- Precondition only: `emp_<slug>` must exist before JRNY serves the tenant. No direct call; JRNY reacts to `journey-os.empresa.provisionada`.

## 2. Provides (inbound, sync) — consumed by COMM / SALE

### `JourneyQueryClient` (provider = `jrny-service`)
- Surface: `GET /api/v1/routing/leads/{leadId}/journey`, `GET /api/v1/routing/leads/{leadId}/decisions`.
- `THE SYSTEM SHALL expose a lead's current journey state (active enrolment + current stage) and its routing decision log to consuming services as stable DTOs, never JPA entities.`
- `THE SYSTEM SHALL never return a journey state or decision belonging to another empresa.`
- Consumers: COMM (act on the current stage — send message), SALE (create opportunity on OFERTA/FECHAMENTO).

## 3. Async (events)

- **Produces:** `journey-os.jornada.publicada`, `journey-os.lead.roteado` (**anchor**), `journey-os.estagio.transicionado`, `journey-os.jornada.concluida` (see `event-contracts.md`).
- **Consumes:** `journey-os.lead.qualificado` / `lead.score.atualizado` / `lead.segmento.alterado` (LEAD), `journey-os.asset.versao.publicada` (ASST), `journey-os.modelo.acesso.alterado` / `journey-os.empresa.provisionada` (WRKS).
- `WHEN a consumer service needs to act on a routed lead, THE SYSTEM SHALL allow it to subscribe to journey-os.lead.roteado / journey-os.estagio.transicionado rather than polling.`
- `THE SYSTEM SHALL decide and signal only — it SHALL NOT execute channel (COMM) or sales (SALE) actions; those services react to the events.`

## 4. Discovery & resilience

- Registered in Eureka (REG) as `jrny-service`; reached through GWY at `/api/v1/journeys/**` and `/api/v1/routing/**`.
- Feign calls wrapped with Resilience4j (timeout, circuit breaker, retry) per `platform-patterns.md`.
- `IF WRKS is unreachable for AccessDecision AND a valid cached decision exists, THEN THE SYSTEM SHALL serve from cache until its modelo_acesso_versao TTL expires.`
- `THE SYSTEM SHALL NOT perform a synchronous Feign call (WRKS/ASST) inside a Kafka event consumer (anti-pattern — see SPEC-09); content/authorization resolution for the consume path uses cached/last-known data.`
