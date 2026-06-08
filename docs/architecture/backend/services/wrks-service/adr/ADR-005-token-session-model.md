# ADR-005 — Modelo de token/sessão: JWT RS256 + refresh rotation + invalidação por versão

**Status:** accepted

## Contexto

A credencial emitida por WRKS é usada por GWY e por todos os serviços para autorização. Precisa
ser (a) validável sem chamar WRKS a cada request (escala), (b) curta para limitar a janela de
vazamento, e (c) capaz de refletir mudanças de RBAC **em segundos**, sem invalidar tokens 1-a-1.

## Decisão

- **Access token = JWT RS256**, stateless, validável via **JWKS** publicado por WRKS (GWY valida na borda). Claims: `sub`, `empresa_id`, `papel`, `modelo_acesso_versao`, `data_scope`, `exp`. TTL curto por papel (session policy: ADMIN/INFOPRODUTOR mais curto).
- **Refresh token**: cookie `httpOnly`+`secure`+`sameSite=strict`, com **rotation** a cada uso; antigo invalidado.
- **Invalidação por versão**: mudança de RBAC incrementa `modelo_acesso_versao` + publica `modelo.acesso.alterado`. JWT com versão antiga → `401 iam.sessao.versao-desatualizada` → FE faz refresh → novo JWT com permissões atuais.
- **Logout**: apaga cookie + adiciona `sub`+`jti` à **blacklist Redis** (TTL = TTL restante do access token), pois JWT é stateless.
- **Cache Redis** de sessão e AccessDecision é otimização; source of truth = Postgres/JWT.

## Alternativas consideradas

- **Sessão server-side opaca (sem JWT)**: exige lookup central a cada request — gargalo e acopla todos a WRKS. Rejeitada.
- **JWT longo sem versão**: mudança de RBAC só reflete ao expirar — janela inaceitável. Rejeitada.
- **HS256 (segredo compartilhado)**: exige distribuir o segredo a todos os validadores. Rejeitada em favor de RS256 + JWKS (apenas chave pública distribuída).

## Consequências

**Positivas:** validação distribuída sem SPOF de leitura; propagação de RBAC < 5s; janela de vazamento curta; revogação efetiva via blacklist.

**Negativas:** complexidade (rotation + blacklist + versão); blacklist depende de Redis (se cair, revogação imediata degrada — token ainda expira pelo TTL curto).

## Referências

- `docs/architecture/shared/rbac/session-policy.md` (TTLs, fluxo de refresh, invalidação)
- `docs/architecture/shared/rbac/modelo.md` §5/§7 (AccessDecision + cache)
- ADR-002 (autoridade de identidade), ADR-003 (evento de invalidação)
