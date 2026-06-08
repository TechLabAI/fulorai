# ADR-002 — WRKS como autoridade de identidade (Keycloak = IdP, RBAC do Journey OS)

**Status:** accepted

## Contexto

É preciso decidir **quem é dono da autorização**. Keycloak oferece roles/groups nativos, e seria
tentador usá-lo como fonte de papéis. Porém o Journey OS tem papéis canônicos do grupo
(`INFOPRODUTOR`/`HEAD_GROWTH`/`SDR`), permissões `<modulo>.<recurso>.<acao>`, data_scope e
multi-empresa — semântica de negócio que precisa ser auditável e versionada (`modelo_acesso_versao`).

## Decisão

**Separar autenticação de autorização:**

- **Keycloak = IdP** apenas para **autenticação** (OIDC login, credenciais, futuramente MFA).
- **WRKS = autoridade de autorização**: dono de `papel`, `permissao`, `papel_permissao`, `usuario_empresa`, e **emissor do JWT** do Journey OS (com claims `empresa_id`, `papel`, `modelo_acesso_versao`, `data_scope`).
- WRKS é **single service** que concentra IAM (identidade + RBAC + workspace + org structure).

Demais serviços e GWY confiam no JWT emitido por WRKS e/ou chamam `AccessDecision`.

## Alternativas consideradas

- **Keycloak como fonte de papéis/permissões**: acopla a semântica de negócio ao IdP, dificulta versão/auditoria e multi-empresa com data_scope. Rejeitada (anti-pattern explícito em `rbac/modelo.md` §8).
- **Serviço de auth separado do serviço de workspace/usuários**: dois serviços fortemente acoplados (toda decisão de acesso cruza ambos). Rejeitada para o MVP — coesão favorece single service.

## Consequências

**Positivas:** autorização auditável e versionada; troca de IdP sem perder o modelo de acesso; multi-empresa + data_scope nativos; um único ponto de verdade.

**Negativas:** WRKS torna-se componente crítico (SPOF lógico) — mitigado por cache (Redis) e por JWT stateless validável via JWKS sem chamar WRKS a cada request.

## Referências

- `docs/architecture/shared/rbac/{modelo,papeis,session-policy}.md`
- `_brief.md` (itens 2, 6, 7) · ADR-005 (token/sessão)
