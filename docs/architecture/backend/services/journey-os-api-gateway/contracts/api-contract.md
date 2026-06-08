# API Contract — GWY (API Gateway)

> O gateway **não expõe API de negócio própria**; expõe (a) endpoints operacionais (Actuator) e
> (b) atua como **proxy reativo** para a superfície agregada dos serviços de negócio sob `/api/v1/**`.
> Acceptance criteria em EARS — ver `docs/architecture/backend/standards/ears-notation.md`.

## 1. Superfície operacional (próprios endpoints)

| Path | Verbo | Descrição | Auth |
|---|---|---|---|
| `/actuator/health` | GET | Liveness/readiness do gateway | pública |
| `/actuator/info` | GET | Metadados de build | pública |
| `/actuator/gateway/routes` | GET | Rotas resolvidas (debug/ops) | restrita (ops) |
| `/actuator/prometheus` | GET | Métricas Micrometer | restrita (scrape interno) |

**Invariantes (EARS):**
- THE SYSTEM SHALL expose `/actuator/health` returning `200` quando o gateway estiver apto a rotear.
- WHILE o Eureka client não tiver completado o primeiro registro, THE SYSTEM SHALL reportar readiness `OUT_OF_SERVICE`.
- WHERE o perfil não for de produção, THE SYSTEM SHALL expor `/actuator/gateway/routes`.
- IF um endpoint Actuator restrito for acessado sem autorização de ops, THEN THE SYSTEM SHALL responder `403`.

## 2. Superfície de proxy (roteamento)

Todo tráfego de negócio entra sob o prefixo versionado e é roteado por `service-id` via Eureka
(ver `SPEC-01-api-surface.md` para a tabela completa de rotas):

| Prefixo de path | Destino (`lb://`) | Módulo |
|---|---|---|
| `/api/v1/workspaces/**`, `/api/v1/users/**`, `/auth/**` | `lb://wrks-service` | WRKS |
| `/api/v1/leads/**` | `lb://lead-service` | LEAD |
| `/api/v1/journeys/**`, `/api/v1/routing/**` | `lb://jrny-service` | JRNY |
| `/api/v1/assets/**` | `lb://asst-service` | ASST |
| `/api/v1/messages/**`, `/api/v1/templates/**`, `/webhooks/comm/**` | `lb://comm-service` | COMM |
| `/api/v1/sales/**`, `/api/v1/offers/**`, `/webhooks/sale/**` | `lb://sale-service` | SALE |
| `/api/v1/intelligence/**`, `/api/v1/copilot/**` | `lb://intl-service` | INTL |

**Invariantes de roteamento (EARS):**
- WHEN uma requisição casa um predicado de rota, THE SYSTEM SHALL encaminhá-la ao `service-id` correspondente resolvido via Eureka.
- IF nenhuma rota casar o path, THEN THE SYSTEM SHALL responder `404` com ProblemDetail.
- IF o `service-id` alvo não tiver instâncias saudáveis no Eureka, THEN THE SYSTEM SHALL responder `503`.
- THE SYSTEM SHALL preservar método, query string e corpo da requisição ao encaminhar.

## 3. Headers obrigatórios

### Entrada (do cliente)
| Header | Obrigatório | Observação |
|---|---|---|
| `Authorization: Bearer <jwt>` | sim (rotas não-públicas) | Validado na borda (ADR-003). |
| `X-Correlation-Id` | opcional | Gerado se ausente. |

### Saída (para downstream — injetados pelo gateway)
| Header | Origem | Observação |
|---|---|---|
| `X-Correlation-Id` | gerado/propagado | Sempre presente. |
| `X-Empresa-Id` | claim `empresaId` do JWT | **Nunca** do header do cliente (anti-spoofing). |
| `X-Tenant-Schema` | derivado de `empresaId` | Opcional, conforme contrato com serviços. |
| `X-Principal-Id` | claim `sub` do JWT | Identidade do usuário autenticado. |

**Invariantes de headers (EARS):**
- WHEN uma requisição é encaminhada, THE SYSTEM SHALL incluir `X-Correlation-Id` (gerado se ausente na entrada).
- WHEN uma requisição autenticada é encaminhada, THE SYSTEM SHALL definir `X-Empresa-Id` a partir do claim `empresaId` do JWT.
- IF o cliente enviar `X-Empresa-Id`, `X-Tenant-Schema` ou `X-Principal-Id`, THEN THE SYSTEM SHALL descartá-los antes do encaminhamento (anti-spoofing).

## 4. Autenticação (OAuth2 / JWT)

- Esquema: **Bearer JWT** emitido pelo WRKS; validação de assinatura via JWKS (ADR-003).
- Rotas públicas (allowlist): `/auth/login`, `/auth/refresh`, `/actuator/health`, `/actuator/info`,
  webhooks assinados (`/webhooks/**` com verificação de assinatura no serviço de destino).

**Invariantes de auth (EARS):**
- IF uma requisição a rota não-pública não contiver `Authorization: Bearer`, THEN THE SYSTEM SHALL responder `401`.
- IF o JWT tiver assinatura inválida, estiver expirado ou tiver `iss`/`aud` incorretos, THEN THE SYSTEM SHALL responder `401`.
- IF o JWT for válido mas não contiver o claim `empresaId`, THEN THE SYSTEM SHALL responder `403`.
- WHERE a rota estiver na allowlist pública, THE SYSTEM SHALL encaminhar sem exigir JWT.

## 5. Erros (RFC 7807 — ProblemDetail)

O gateway normaliza erros de borda como `application/problem+json`:

| Status | `type` (sufixo) | Quando |
|---|---|---|
| `401` | `/errors/unauthenticated` | JWT ausente/inválido |
| `403` | `/errors/forbidden` | claim ausente / endpoint ops sem permissão / tenant inválido |
| `404` | `/errors/route-not-found` | nenhum predicado casou |
| `429` | `/errors/rate-limited` | rate-limit excedido (inclui `Retry-After`) |
| `503` | `/errors/no-instances` | sem instância saudável no Eureka |
| `504` | `/errors/upstream-timeout` | timeout de resposta do downstream |

**Invariantes de erro (EARS):**
- WHEN o gateway gera um erro de borda, THE SYSTEM SHALL responder com `Content-Type: application/problem+json`.
- WHEN responde `429`, THE SYSTEM SHALL incluir o header `Retry-After`.
- THE SYSTEM SHALL incluir `X-Correlation-Id` em toda resposta de erro.
