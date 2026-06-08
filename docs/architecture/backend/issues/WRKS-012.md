# WRKS-012 -- AccessDecision evaluate + cache Redis + invalidação por versão

## Contexto
Serve `AccessDecision` para GWY e todos os serviços, com cache Redis e invalidação rápida
cross-serviço quando o RBAC muda.

## Spec de referencia
- SPEC-03-rbac-access-decision
- SPEC-05-idempotency-concurrency

## Escopo
- `AvaliarAcessoService`: lookup cache (`AccessDecisionCachePort`, key `{usuarioId}:{empresaId}`)
  → miss: carrega associação + bundle do papel + versão → `AccessDecisionResponse` → cache 5 min.
- Fallback ao PostgreSQL se Redis cair.
- `POST /api/v1/iam/access/evaluate` (token de serviço, não JWT de usuário).

## Resultado esperado
Evaluate p95 < 30ms com cache quente; consistência via versão; fallback resiliente.

## Criterios de aceite
- [ ] Retorna papel + lista explícita de permissões + data_scope + `modelo_acesso_versao`.
- [ ] Cache válido (versão bate) servido do Redis sem tocar PostgreSQL.
- [ ] Associação inativa/ausente → 404 `wrks.usuario.associacao-nao-encontrada`.
- [ ] Redis indisponível → avalia via PostgreSQL.

## Dependencias
- WRKS-007 (persistência), WRKS-011 (versão/claim), INT-WRKS-003 (Redis)

## Estimativa
L

## Prioridade
P5
