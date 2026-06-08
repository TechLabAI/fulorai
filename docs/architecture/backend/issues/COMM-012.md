# COMM-012 -- Security: JWT + comm.* AccessDecision + tenant guard + webhook signature

## Contexto
Autenticação de usuário (JWT/JWKS WRKS), autorização `comm.*`, isolamento multi-tenant e
autenticação de webhooks por assinatura do provedor.

## Spec de referencia
- SPEC-06-security
- SPEC-01-api-surface

## Escopo
- Resource server OAuth2 (RS256, JWKS WRKS); `EmpresaContextHolder.require()` fixa o schema do claim.
- Autorização `comm.*` via `AccessDecisionPort` (INT-COMM-002); cache invalidado por `modelo.acesso.alterado`.
- `WebhookController`: verificação de assinatura/segredo do provedor; tenant resolvido da `mensagem`, nunca do payload.
- Erros: 401 `comm.auth.token-invalido`, 403 `comm.acesso.permissao-negada`, 401 `comm.webhook.assinatura-invalida`.

## Resultado esperado
Nenhum acesso cross-empresa; webhooks só de provedores autenticados.

## Criterios de aceite
- [ ] JWT inválido → 401; permissão ausente → 403.
- [ ] Webhook sem assinatura válida → 401, sem mutação de mensagem.
- [ ] Tenant do webhook resolvido da mensagem referenciada (não do payload).

## Dependencias
- COMM-003 (precede)
- INT-COMM-002 (WRKS)

## Estimativa
M

## Prioridade
P5
