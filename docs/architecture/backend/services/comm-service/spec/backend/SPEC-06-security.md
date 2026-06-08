# SPEC-06 — Security

> EARS guide linkado. Relaciona `hub-integration.md` (WRKS), ADR-004 (tenant), SPEC-01 (webhooks).

## Objetivo

Definir autenticação (JWT de usuário + assinatura de provedor em webhooks), autorização
(`comm.*` via AccessDecision), isolamento multi-tenant e proteção de segredos de provedor.

## Escopo

- **In:** validação de JWT (JWKS WRKS); permissões `comm.*`; `EmpresaContextHolder` guard; verificação de assinatura de webhook; proteção de `credencial_ref`.
- **Out:** emissão de JWT (WRKS); modelo RBAC global (`shared/rbac`).

## Decisões técnicas

- **JWT:** RS256 emitido por WRKS, validado contra `WRKS_JWKS_URI`. Sem endpoints de usuário anônimos.
- **Permissões:** `comm.template.criar|editar|ler|publicar|arquivar`, `comm.studio.compor`, `comm.mensagem.enviar|ler`, `comm.roteamento.criar|editar|ler`, `comm.canal.configurar|ler` resolvidas via `AccessDecision` (cache curto, invalidado por `modelo.acesso.alterado`).
- **Tenant:** `empresa_id` vem do claim; `EmpresaContextHolder.require()` fixa o schema; zero cross-empresa.
- **Webhooks:** autenticados pela assinatura/segredo do provedor (HMAC/header), não por JWT de usuário; tenant resolvido a partir da `mensagem` referenciada, nunca de campo não confiável do payload.
- **Segredos:** `config_canal.credencial_ref` é referência a secret manager; segredo nunca persistido, retornado em API, nem logado.

## Casos de borda

- JWT expirado/ inválido → `401 comm.auth.token-invalido`.
- Permissão ausente → `403 comm.acesso.permissao-negada`.
- Webhook sem assinatura válida → `401 comm.webhook.assinatura-invalida`, sem mutação.
- WRKS fora + decisão em cache válida → serve do cache até TTL.

## Critérios de aceite (EARS)

- `IF a user request has a missing/invalid JWT, THEN THE SYSTEM SHALL reject with 401 error.code 'comm.auth.token-invalido'.`
- `IF the AccessDecision lacks the required comm.* permission, THEN THE SYSTEM SHALL reject with 403 error.code 'comm.acesso.permissao-negada'.`
- `THE SYSTEM SHALL resolve the tenant schema from the JWT claim via EmpresaContextHolder.require() and SHALL never read cross-empresa data.`
- `IF a provider webhook has a missing or invalid signature, THEN THE SYSTEM SHALL reject it with 401 error.code 'comm.webhook.assinatura-invalida' and SHALL NOT mutate any message.`
- `THE SYSTEM SHALL resolve the tenant for a webhook from the referenced message, never from untrusted webhook payload fields.`
- `THE SYSTEM SHALL store provider credentials only as credencial_ref and SHALL never persist, return, or log the raw secret.`
