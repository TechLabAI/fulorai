# Hub / Inter-service Integration — WRKS

> How WRKS relates to the other Journey OS services. WRKS is **foundation**: it depends only
> on infra + MIG/REG and is consumed by GWY and every business service.

## 1. WRKS as provider

| Consumer | What | Mechanism |
|---|---|---|
| **GWY** (API Gateway) | JWT validation | Pulls JWKS from `GET /api/v1/iam/.well-known/jwks.json`; validates signature + claims at the edge. |
| **All services** (LEAD, JRNY, ASST, COMM, SALE, INTL) | AccessDecision | `@FeignClient(name="wrks-service")` → `POST /api/v1/iam/access/evaluate`; cache result in Redis keyed `journey-os:access:{usuarioId}:{empresaId}`. |
| **All services** | RBAC change signal | Consume `journey-os.modelo.acesso.alterado` → invalidate local AccessDecision cache. |

- `THE SYSTEM SHALL expose AccessDecision and JWKS such that no consumer needs direct access to journeyos_global IAM tables.`
- `WHILE Redis is available, consumers SHALL serve AccessDecision from cache; IF the cached modelo_acesso_versao is stale, THEN they SHALL re-evaluate.`

## 2. WRKS as consumer

| Provider | What | Mechanism |
|---|---|---|
| **MIG** (`journey-os-migrations`) | Provision schema `emp_<slug>` | `MigrationTriggerPort` → HTTP/Feign call; confirmation via `journey-os.empresa.provisionada`. |
| **REG** (Eureka) | Service discovery | Eureka client registration. |
| **All services** | Audit source | Consume `journey-os.*` for `evento_auditoria`. |

## 3. Feign clients

| Interface | Provider | `@FeignClient` |
|---|---|---|
| `MigrationTriggerClient` | MIG | `@FeignClient(name="journey-os-migrations")` |

## 4. Trust & tenancy

- WRKS is the **only** business service with write access to `journeyos_global` IAM tables (ADR-004).
- Service-to-service calls to `/access/evaluate` use a service token (client_credentials), not an end-user JWT.
- `EmpresaContextHolder.require()` enforced (RULE-07) on every application service touching empresa data.

## Cross-references

- `docs/architecture/backend/standards/services-catalog.md` (Feign registry, event catalog)
- `event-contracts.md`, `integration-contracts.md`
