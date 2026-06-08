# LEAD-012 -- JWT resource server + lead.* authorization

## Contexto
Validação de JWT (emitido por WRKS) e autorização por permissões `lead.*` via `AccessDecision`,
com cache invalidável.

## Spec de referencia
- SPEC-06-security
- SPEC-10-integrations

## Escopo
- Spring Security resource server valida RS256 via JWKS de WRKS (`WRKS_JWKS_URI`).
- Autorização por permissão `lead.*` a partir do `AccessDecision` (cache via `AccessDecisionCachePort`).
- Rejeita versão de modelo de acesso desatualizada (401 `iam.sessao.versao-desatualizada`).
- Filtros em `infrastructure.security`.

## Resultado esperado
Endpoints exigem JWT válido + permissão `lead.*`; sem JWT → 401, sem permissão → 403.

## Criterios de aceite
- [ ] Requisição sem JWT válido → 401 (`iam.*`).
- [ ] Permissão `lead.*` exigida por endpoint (via AccessDecision).
- [ ] `modelo_acesso_versao` defasado → 401 `iam.sessao.versao-desatualizada`.
- [ ] WRKS indisponível sem cache → fail-closed 503.

## Dependencias
- INT-LEAD-002 (AccessEvaluate client)
- INT-LEAD-004 (cache + invalidação)

## Estimativa
M

## Prioridade
P5
