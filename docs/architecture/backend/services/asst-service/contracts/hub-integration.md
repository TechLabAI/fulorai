# Hub Integration — ASST (inter-service)

> Inter-service contracts within Journey OS. Sync calls use Feign over Eureka discovery through
> the platform's standard Resilience4j config. EARS for behavior.

## 1. Depends on (outbound, sync)

### WRKS — identity & authorization
- `AccessEvaluateClient` `@FeignClient(name = "wrks-service")` → `POST /api/v1/iam/access/evaluate`.
- JWKS: validate incoming JWT against `WRKS_JWKS_URI`.
- `WHEN a request arrives with a valid JWT, THE SYSTEM SHALL resolve the AccessDecision (role + asst.* permissions + data scope) from WRKS, caching it until modelo_acesso_versao changes.`
- `IF the JWT is missing/invalid, THEN THE SYSTEM SHALL reject with 401 error.code 'asst.auth.token-invalido'.`
- `IF the AccessDecision lacks the required asst.* permission, THEN THE SYSTEM SHALL reject with 403 error.code 'asst.acesso.permissao-negada'.`

### MIG — tenant schema provisioning
- Precondition only: `emp_<slug>` must exist before ASST serves the tenant. No direct call; ASST reacts to `journey-os.empresa.provisionada`.

## 2. Provides (inbound, sync) — consumed by COMM / JRNY / SALE

### `AssetQueryClient` (provider = `asst-service`)
- Surface: `GET /api/v1/assets/{id}/published`, `GET /api/v1/assets?tipo=&tag=&estado=PUBLICADO`.
- `THE SYSTEM SHALL expose only published asset versions to consuming services, never drafts or rejected versions.`
- `THE SYSTEM SHALL return a stable DTO (AssetQueryResponse), never a JPA entity.`
- Consumers: COMM (message templates), JRNY (stage content), SALE (offer copy).

## 3. Async (events)

- **Produces:** `journey-os.asset.criado`, `journey-os.asset.aprovado`, `journey-os.asset.rejeitado`, `journey-os.asset.versao.publicada` (see `event-contracts.md`).
- **Consumes:** `journey-os.modelo.acesso.alterado` (WRKS), `journey-os.empresa.provisionada` (WRKS).
- `WHEN a consumer service needs to react to new published content, THE SYSTEM SHALL allow it to subscribe to journey-os.asset.versao.publicada rather than polling.`

## 4. Discovery & resilience

- Registered in Eureka (REG) as `asst-service`; reached through GWY at `/api/v1/assets/**`.
- Feign calls wrapped with Resilience4j (timeout, circuit breaker, retry) per `platform-patterns.md`.
- `IF WRKS is unreachable for AccessDecision AND a valid cached decision exists, THEN THE SYSTEM SHALL serve from cache until its modelo_acesso_versao TTL expires.`
