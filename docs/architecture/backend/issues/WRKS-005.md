# WRKS-005 -- Sessão: trocar-empresa, refresh (rotation), logout (blacklist), restore

## Contexto
Ciclo de vida da sessão após o login: troca de empresa sem re-login, refresh com rotation,
logout com blacklist e restore via cookie.

## Spec de referencia
- SPEC-02-identity-session
- SPEC-05-idempotency-concurrency
- SPEC-06-security

## Escopo
- `TrocarEmpresaService`: valida associação ativa → reemite JWT (novo `empresa_id`).
- `RefreshService`: valida refresh (não blacklisted), rotaciona, invalida anterior.
- `LogoutService`: limpa cookie + blacklist `sub`+`jti` (TTL = restante do access token).
- `RestoreService`: restaura sessão a partir do refresh cookie.
- Publica `journey-os.sessao.encerrada` no logout.

## Resultado esperado
Troca de empresa sem re-login; refresh seguro com rotation; logout revoga; restore funciona.

## Criterios de aceite
- [ ] trocar-empresa para associação ativa → novo JWT; sem acesso → 403 `wrks.empresa.acesso-negado`.
- [ ] refresh rotaciona e invalida o anterior; reuso → 401 `iam.refresh-invalido`.
- [ ] logout adiciona `jti` à blacklist e limpa cookie.

## Dependencias
- WRKS-004 (precede), INT-WRKS-003 (Redis)

## Estimativa
M

## Prioridade
P2
