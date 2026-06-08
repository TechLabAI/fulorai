# SPEC-01 — API Surface & Routing Pipeline — GWY

> Acceptance criteria em EARS (`docs/architecture/backend/standards/ears-notation.md`).
> ADRs relacionados: ADR-001 (hexagonal), ADR-002 (routing), ADR-003 (auth), ADR-004 (tenant), ADR-005 (rate-limit).

## Objetivo

Definir a superfície de borda do gateway: o **pipeline de filtros globais** aplicado a toda
requisição e a **tabela de rotas** que mapeia paths → `service-id` via Eureka.

## Escopo

**In:** filtros globais (correlação, auth, tenant, rate-limit), tabela de rotas, predicados,
ordem de execução, endpoints operacionais.
**Out:** lógica de negócio, agregação de respostas, terminação TLS, emissão de tokens.

## Pipeline de filtros globais (ordem)

```
[1] CorrelationFilter      → garante X-Correlation-Id (gera se ausente), insere no MDC reativo
[2] SecurityHeaderStrip    → remove headers de identidade vindos do cliente (anti-spoofing)
[3] AuthFilter             → valida JWT (assinatura+claims) salvo rota pública (ADR-003)
[4] TenantPropagationFilter→ injeta X-Empresa-Id / X-Tenant-Schema / X-Principal-Id (ADR-004)
[5] RateLimitFilter        → RequestRateLimiter + KeyResolver + Redis (ADR-005)
[6] RouteFilter (SCG)      → casa predicado, resolve lb://<service-id>, encaminha
```

**Acceptance criteria (EARS):**
- THE SYSTEM SHALL aplicar os filtros globais na ordem `[1]→[6]` para toda requisição roteável.
- WHEN uma requisição entra sem `X-Correlation-Id`, THE SYSTEM SHALL gerar um e propagá-lo downstream e na resposta.
- THE SYSTEM SHALL executar o `SecurityHeaderStrip` **antes** do `TenantPropagationFilter` (anti-spoofing).
- WHERE a rota estiver na allowlist pública, THE SYSTEM SHALL pular o `AuthFilter` mas manter rate-limit por IP.
- IF qualquer filtro produzir uma decisão `DENY`, THEN THE SYSTEM SHALL interromper o pipeline e responder o status correspondente (401/403/429) sem encaminhar.

## Tabela de rotas (declarativa)

| id | Predicado (Path) | Target | Pública? |
|---|---|---|---|
| `wrks-auth` | `/auth/**` | `lb://wrks-service` | sim (login/refresh) |
| `wrks-core` | `/api/v1/workspaces/**`, `/api/v1/users/**` | `lb://wrks-service` | não |
| `lead` | `/api/v1/leads/**` | `lb://lead-service` | não |
| `jrny` | `/api/v1/journeys/**`, `/api/v1/routing/**` | `lb://jrny-service` | não |
| `asst` | `/api/v1/assets/**` | `lb://asst-service` | não |
| `comm` | `/api/v1/messages/**`, `/api/v1/templates/**` | `lb://comm-service` | não |
| `comm-webhook` | `/webhooks/comm/**` | `lb://comm-service` | sim (assinatura no destino) |
| `sale` | `/api/v1/sales/**`, `/api/v1/offers/**` | `lb://sale-service` | não |
| `sale-webhook` | `/webhooks/sale/**` | `lb://sale-service` | sim (assinatura no destino) |
| `intl` | `/api/v1/intelligence/**`, `/api/v1/copilot/**` | `lb://intl-service` | não |

**Acceptance criteria (EARS):**
- WHEN uma requisição casa exatamente um predicado, THE SYSTEM SHALL encaminhá-la ao target indicado.
- IF múltiplos predicados casarem, THEN THE SYSTEM SHALL aplicar o de maior especificidade/ordem definida.
- IF nenhum predicado casar, THEN THE SYSTEM SHALL responder `404` com ProblemDetail.

## Implementação (componentes)

- `infrastructure/config/GatewayRoutesConfig` — `RouteLocator` programático ou `application.yml`.
- `infrastructure/filter/*` — `GlobalFilter` reativos (ordem via `getOrder()`).
- `application/service/*` — políticas testáveis (`AuthenticateRequest`, `ResolveTenant`, `RateLimitDecision`).
- `api/exception/GatewayErrorHandler` — `ErrorWebExceptionHandler` → ProblemDetail.

## Casos de borda

- Path versionado ausente (`/leads/...` sem `/api/v1`): `404`.
- Requisição `OPTIONS` (preflight CORS): respondida pelo gateway sem encaminhar.
- Upgrade WebSocket/SSE: fora do MVP; declarar rota explícita se necessário.

## Critérios de aceite (resumo)

- THE SYSTEM SHALL expor `/actuator/gateway/routes` listando todas as rotas resolvidas (perfis não-prod).
- THE SYSTEM SHALL resolver 100% dos targets via `lb://` (zero host:porta hardcoded).
