# 02 — Architecture Blueprint — GWY (API Gateway)

> Serviço: `journey-os-api-gateway` · Pacote: `com.journeyos.gwy` · Tipo: **infra (gateway)**

## 1. System Boundary

O GWY é o **edge** do Journey OS: tudo o que entra via HTTP público passa por ele; nada de
negócio é decidido nele. Fronteira:

- **Dentro:** roteamento, autenticação de borda (validação de JWT), resolução/propagação de
  tenant, rate-limiting, CORS, cabeçalhos de segurança, correlação de requisições, observabilidade
  de borda.
- **Fora:** regras de negócio, persistência de domínio, emissão de tokens, terminação TLS,
  agregação de respostas.

## 2. External Actors and Systems

| Ator / Sistema | Direção | Papel |
|---|---|---|
| SPA `journey-os-web` | entrada | Cliente primário da API. |
| Integrações externas (Hotmart, Meta, ActiveCampaign) | entrada | Webhooks/clients de API pública. |
| **REG (Eureka)** | saída (descoberta) | Resolução de `service-id` → instâncias (`lb://`). |
| **WRKS** | dependência de confiança | Emissor do JWT; fonte da chave pública/JWKS. |
| **Redis** | saída (estado distribuído) | Backing store do rate-limiter. |
| Serviços de negócio (LEAD, JRNY, ASST, COMM, SALE, INTL, WRKS) | saída (roteamento) | Alvos das rotas. |
| ALB/Ingress (AWS) | infra à frente | Terminação TLS, balanceamento L4/L7 externo. |

## 3. End-to-End Flows

### Golden path — requisição autenticada
1. Cliente → ALB → **GWY** com `Authorization: Bearer <jwt>`.
2. Filtro global de correlação: gera/propaga `X-Correlation-Id`.
3. Filtro global de auth: valida assinatura (chave pública WRKS) + claims (exp, iss, aud).
4. Resolução de tenant: extrai `empresaId` do claim → injeta `X-Empresa-Id` e `X-Tenant-Schema`.
5. Rate-limiter: avalia chave (tenant/usuário) contra Redis; se exceder → `429`.
6. Predicate de rota casa o path → resolve `lb://<service-id>` via Eureka.
7. Encaminha ao serviço downstream com headers enriquecidos; devolve a resposta ao cliente.

### Alternativas
- **JWT ausente/ inválido:** filtro de auth responde `401`/`403` sem encaminhar.
- **Rota pública (allowlist):** ex. `/auth/login`, webhooks assinados → pula auth, mantém
  rate-limit por IP.
- **Service-id sem instâncias no Eureka:** `503` (sem destino saudável).
- **Rate-limit excedido:** `429` com `Retry-After`.

## 4. Internal Boundaries (camadas hexagonais)

Mesmo sendo infra, aplica-se a separação hexagonal (ver ADR-001):

- **api/** — configuração de rotas e tratadores de erro de borda (`@RestControllerAdvice`
  reativo / `ErrorWebExceptionHandler` → ProblemDetail RFC 7807).
- **application/** — políticas de borda como casos de uso testáveis: `AuthenticateRequest`,
  `ResolveTenant`, `RateLimitDecision`; ports `in`/`out`.
- **domain/** — modelos puros de borda: `JwtClaims`, `TenantContext`, `RateLimitKey`,
  `RoutePolicy` (zero Spring).
- **infrastructure/** — `GlobalFilter`s do Spring Cloud Gateway, configuração de rotas
  (`RouteLocator`), cliente Eureka, adaptador Redis do rate-limiter, validação de JWT, security.

## 5. Cross-cutting Concerns

- **Security:** validação de JWT na borda; CORS central; cabeçalhos de segurança; allowlist de
  rotas públicas; nenhum segredo hardcoded (`${VAR}` em `application.yml`).
- **Observability:** Actuator (`health`, `gateway/routes`), métricas Micrometer por rota, logs
  estruturados com `correlationId` no MDC reativo, propagação de trace.
- **Multi-tenancy:** o gateway **resolve** o `empresa` do JWT e **propaga**; não acessa schemas
  nem o banco (ver ADR-004).
- **Resiliência:** timeouts de conexão/resposta por rota; (futuro) circuit-breaker via
  Resilience4j por `service-id`.
