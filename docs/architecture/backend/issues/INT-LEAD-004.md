# INT-LEAD-004 -- AccessDecision cache (Redis) + modelo.acesso.alterado invalidation

## Contexto
Cache Redis das decisões de acesso (`AccessDecisionCachePort`), com invalidação dirigida por
`journey-os.modelo.acesso.alterado`.

## Spec de referencia
- SPEC-06-security
- SPEC-09-messaging-architecture
- integration-contracts.md

## Escopo
- `infrastructure` implementa `AccessDecisionCachePort` (Redis/Valkey), chaveado por (usuario, empresa) + `modelo_acesso_versao`.
- Serve decisão do cache enquanto a versão casa; invalida no evento `modelo.acesso.alterado` (LEAD-016).
- Config `REDIS_*` via `${VAR}`.

## Resultado esperado
Autorização rápida via cache; mudanças de RBAC propagam em segundos.

## Criterios de aceite
- [ ] Decisão servida do cache enquanto `modelo_acesso_versao` casa.
- [ ] `modelo.acesso.alterado` invalida entradas afetadas.
- [ ] Queda do Redis degrada para chamada direta a WRKS (não fail-open de autorização).

## Dependencias
- INT-LEAD-002 (AccessEvaluate)
- LEAD-016 (consumer de invalidação)

## Estimativa
M

## Prioridade
P5
