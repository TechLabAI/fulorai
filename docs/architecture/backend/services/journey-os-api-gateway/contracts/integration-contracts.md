# Integration Contracts — GWY (API Gateway)

> Sistemas dos quais o gateway depende em runtime. Acceptance criteria em EARS.

## 1. REG — Eureka (Service Discovery)

| Aspecto | Valor |
|---|---|
| Tipo | Spring Cloud Netflix Eureka Client |
| Endpoint | `${GWY_EUREKA_SERVICE_URL}` (ex.: `http://localhost:8761/eureka/`) |
| Uso | Registro do próprio gateway + descoberta de alvos `lb://<service-id>` |
| Auth | rede interna (sem auth no MVP local) |
| Fallback | cache local de registry no cliente; health check |

**EARS:**
- THE SYSTEM SHALL registrar-se no Eureka com `spring.application.name = journey-os-api-gateway`.
- WHEN o registry estiver temporariamente indisponível, THE SYSTEM SHALL usar o cache local de instâncias.
- IF um `service-id` não tiver instância saudável, THEN THE SYSTEM SHALL responder `503` para rotas que o referenciam.

## 2. WRKS — Validação de JWT (JWKS / chave pública)

| Aspecto | Valor |
|---|---|
| Tipo | Confiança (não-Feign); busca de chave pública/JWKS |
| Endpoint | `${GWY_JWT_JWKS_URI}` |
| Uso | Verificar assinatura do JWT na borda (ADR-003) |
| Cache | chaves em memória, refresh periódico; tolerância a múltiplas chaves (rotação) |
| Fallback | manter última chave válida em cache; alarmar em falha de refresh |

**EARS:**
- THE SYSTEM SHALL validar a assinatura do JWT usando a(s) chave(s) pública(s) obtida(s) do JWKS do WRKS.
- WHILE o JWKS não puder ser atualizado, THE SYSTEM SHALL continuar validando com a última chave em cache.
- IF o `kid` do JWT não casar nenhuma chave conhecida, THEN THE SYSTEM SHALL tentar um refresh do JWKS uma vez antes de rejeitar com `401`.

## 3. Redis — Rate-limiter distribuído

| Aspecto | Valor |
|---|---|
| Tipo | Spring Data Redis Reactive (backing store do `RequestRateLimiter`) |
| Endpoint | `${GWY_REDIS_HOST}:${GWY_REDIS_PORT}` |
| Uso | Token bucket distribuído (ADR-005) |
| Política de falha | **fail-open com alarme** (default proposto; confirmar em ops) |

**EARS:**
- WHEN o limite de uma chave é excedido, THE SYSTEM SHALL responder `429` com `Retry-After`.
- IF o Redis estiver indisponível, THEN THE SYSTEM SHALL aplicar a política de falha configurada (default: fail-open) e emitir alarme/métrica.

## 4. Serviços de negócio (alvos de rota)

| Service-id | Módulo |
|---|---|
| `wrks-service` | WRKS |
| `lead-service` | LEAD |
| `jrny-service` | JRNY |
| `asst-service` | ASST |
| `comm-service` | COMM |
| `sale-service` | SALE |
| `intl-service` | INTL |

**EARS:**
- THE SYSTEM SHALL encaminhar requisições aos serviços de negócio **somente** via `lb://<service-id>` (nunca host:porta fixo).
- WHEN encaminha, THE SYSTEM SHALL aplicar timeouts de conexão e resposta configurados por classe de rota.
- IF o downstream exceder o timeout de resposta, THEN THE SYSTEM SHALL responder `504`.

## 5. Resiliência (alto nível)

- Timeouts por rota (connect/response).
- (Pós-MVP) Circuit-breaker por `service-id` via Resilience4j — ver `06-risks-gaps-assumptions.md`.
- Retentativa **não** aplicada a métodos não-idempotentes (ver SPEC-05).
