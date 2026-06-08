# ADR-005 — Rate-limiting distribuído com Redis

- **Status:** accepted

## Contexto

A API pública precisa de proteção contra abuso (clientes externos, webhooks, scraping) e de
fairness entre tenants. O gateway roda em múltiplas instâncias atrás do ALB, então um limite
em memória local seria inconsistente entre réplicas.

## Decisão

Usar o **`RequestRateLimiter`** do Spring Cloud Gateway com backing store **Redis** (token
bucket), garantindo um limite **distribuído e consistente** entre instâncias:

- **`KeyResolver`** define a chave (`RateLimitKey`): por **tenant** (`empresaId` do claim) para
  fairness; por **usuário** (`sub`) e por **IP** para rotas públicas/anônimas.
- Parâmetros `replenishRate` / `burstCapacity` configuráveis por classe de rota.
- Resposta ao exceder: `429 Too Many Requests` com `Retry-After`.
- A política de **falha do Redis** (fail-open vs fail-closed) será fixada na spec; default
  proposto: **fail-open com alarme** (disponibilidade > limitação) — a confirmar na A2.

## Alternativas consideradas

1. **Rate-limit em memória por instância:** inconsistente com N réplicas; rejeitado.
2. **Rate-limit no ALB/WAF apenas:** protege contra volume bruto mas não conhece tenant/usuário;
   complementar, não substituto. Mantido como camada externa adicional.
3. **Bucket4j local + sincronização:** complexidade extra sem ganho sobre Redis+Gateway nativo.
   Rejeitado.

## Consequências

**Positivas:** limite consistente entre réplicas; chave flexível (tenant/usuário/IP);
integração nativa com o gateway. **Negativas:** dependência de runtime do Redis (R-5); latência
adicional por checagem (mitigada por stack reativa e Redis próximo/ElastiCache).

## Referências

- Spring Cloud Gateway — `RequestRateLimiter` GatewayFilter Factory (Redis)
- `docs/architecture/backend/services/journey-os-api-gateway/06-risks-gaps-assumptions.md` (R-5)
