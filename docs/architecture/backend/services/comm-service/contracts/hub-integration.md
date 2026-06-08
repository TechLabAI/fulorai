# Hub Integration — COMM (inter-service)

> Inter-service contracts within Journey OS. Sync calls use Feign over Eureka discovery through
> the platform's standard Resilience4j config. EARS for behavior.

## 1. Depends on (outbound, sync)

### WRKS — identity & authorization
- `AccessEvaluateClient` `@FeignClient(name = "wrks-service")` → `POST /api/v1/iam/access/evaluate`.
- JWKS: validate incoming JWT against `WRKS_JWKS_URI`.
- `WHEN a request arrives with a valid JWT, THE SYSTEM SHALL resolve the AccessDecision (role + comm.* permissions + data scope) from WRKS, caching it until modelo_acesso_versao changes.`
- `IF the JWT is missing/invalid, THEN THE SYSTEM SHALL reject with 401 error.code 'comm.auth.token-invalido'.`
- `IF the AccessDecision lacks the required comm.* permission, THEN THE SYSTEM SHALL reject with 403 error.code 'comm.acesso.permissao-negada'.`

### ASST — published assets as template source
- `AssetQueryClient` `@FeignClient(name = "asst-service")` → `GET /api/v1/assets/{id}/published`.
- `WHERE a template declares asset_origem_id, WHEN composing/refreshing the template, THE SYSTEM SHALL read the published asset version via AssetQueryClient and SHALL never read draft/rejected versions.`
- `IF ASST is unreachable, THEN THE SYSTEM SHALL allow template CRUD/dispatch to proceed using the last cached/embedded body (best-effort) AND SHALL surface a degraded-source warning.`

### MIG — tenant schema provisioning
- Precondition only: `emp_<slug>` must exist before COMM serves the tenant. No direct call; COMM reacts to `journey-os.empresa.provisionada`.

## 2. Inbound (sync) — triggered by JRNY / SALE / LEAD

### Dispatch request surface (`POST /api/v1/messages`)
- COMM exposes a **stable dispatch endpoint** that JRNY/SALE/LEAD call to request a send.
- `THE SYSTEM SHALL accept a dispatch from an authorized caller, validate it, and respond 202 ENFILEIRADA without performing the provider send synchronously.`
- `THE SYSTEM SHALL return a stable DTO (MensagemResponse), never a JPA entity.`
- Callers: JRNY (stage actions), SALE (offer/checkout notifications), LEAD (qualification triggers).

## 3. Async (events)

- **Produces:** `journey-os.mensagem.enfileirada`, `journey-os.mensagem.enviada` (anchor), `journey-os.mensagem.entregue`, `journey-os.mensagem.falhada` (see `event-contracts.md`).
- **Consumes:** `journey-os.modelo.acesso.alterado`, `journey-os.empresa.provisionada` (WRKS); `journey-os.asset.versao.publicada` (ASST); `journey-os.lead.segmento.alterado` (LEAD); `journey-os.lead.roteado`, `journey-os.estagio.transicionado` (JRNY); `journey-os.oportunidade.estagio.alterado` (SALE).
- `WHEN JRNY/SALE prefer event-driven nurture over a synchronous call, THE SYSTEM SHALL allow them to drive dispatch by emitting their domain events, which COMM consumes idempotently.`

## 4. Discovery & resilience

- Registered in Eureka (REG) as `comm-service`; reached through GWY at `/api/v1/{templates,messages,routing-rules,channels}/**` (webhooks via a dedicated edge route).
- Feign calls wrapped with Resilience4j (timeout, circuit breaker, retry) per `platform-patterns.md`.
- `IF WRKS is unreachable for AccessDecision AND a valid cached decision exists, THEN THE SYSTEM SHALL serve from cache until its modelo_acesso_versao TTL expires.`
