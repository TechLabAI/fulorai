# INT-WRKS-003 -- Integração Redis (sessão + AccessDecision + blacklist) com fallback

## Contexto
Cache Redis/Valkey para sessão, AccessDecision e blacklist de logout — otimização, não verdade.

## Spec de referencia
- integration-contracts.md §2
- SPEC-03-rbac-access-decision

## Escopo
- Adapters `SessionCachePort`/`AccessDecisionCachePort`/`BlacklistPort`.
- Keys: `journey-os:sessao:{id}`, `journey-os:access:{usuarioId}:{empresaId}`, `journey-os:blacklist:{jti}`.
- Fallback ao PostgreSQL quando Redis indisponível.

## Resultado esperado
Cache acelera caminho crítico; queda do Redis degrada para PostgreSQL sem perda funcional.

## Criterios de aceite
- [ ] Hit/miss corretos; TTLs por papel/5min.
- [ ] Redis down → avaliação via PostgreSQL; logout limpa cookie mesmo sem Redis.

## Dependencias
- WRKS-005, WRKS-012

## Estimativa
M

## Prioridade
P5
