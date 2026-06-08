# INT-GWY-003 -- Integração Redis (RedisRateLimiter adapter)

## Contexto
Adapter Redis reativo que serve de backing store ao `RequestRateLimiter`, garantindo limite
distribuído consistente entre réplicas do gateway (ADR-005).

## Spec de referencia
- contracts/integration-contracts.md (§3)
- SPEC-05-idempotency-concurrency
- adr/ADR-005-rate-limiting

## Escopo
- `infrastructure/ratelimit/RedisRateLimiter` implementando `RateLimiterPort`.
- Spring Data Redis Reactive; config `${GWY_REDIS_HOST}/${GWY_REDIS_PORT}`.
- Política de falha (default fail-open) + métrica de indisponibilidade.

## Resultado esperado
Token bucket distribuído operacional.

## Criterios de aceite
- [ ] Contador persistido no Redis com TTL de janela.
- [ ] Limite agregado verificável com ≥2 instâncias apontando ao mesmo Redis.
- [ ] Redis fora → política de falha aplicada + métrica emitida.
- [ ] Teste de integração com Redis (Testcontainers).

## Dependencias
- GWY-006 (ports)

## Estimativa
M

## Prioridade
P6
