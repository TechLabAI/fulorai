# SPEC-06 — Security (OAuth2, Multi-tenancy, LGPD)

> Ref: `contracts/api-contract.md`, `contracts/hub-integration.md §1`. ADR-004.

## Objetivo

Garantir autenticação (JWT RS256/JWKS de WRKS), autorização (`intl.*` via AccessDecision),
isolamento de tenant inviolável e conformidade LGPD.

## Escopo

**In:** validação JWT; AccessDecision por endpoint; resolução de `empresa`; filtro de tenant em PG
(schema) e Elastic (discriminador); PII/LGPD em conversas e nós.
**Out:** emissão de token (WRKS); gestão de papéis (WRKS).

## Decisões técnicas

- JWT validado contra JWKS de WRKS; claim `empresa` → `EmpresaContextHolder`.
- `AccessEvaluateClient` autoriza permissões `intl.copilot.use/read`, `intl.knowledge.read/write`,
  `intl.analytics.read`; cache invalidado por `modelo.acesso.alterado`; **fail-closed**.
- Elastic: filtro `empresa` injetado no `SearchPort` (não opcional); teste de isolamento.
- LGPD: `base_legal`/consentimento em PII; anonimização/expurgo; citações restritas ao tenant.

## Casos de borda

- JWT válido mas sem permissão → `403`.
- AccessDecision indisponível → fail-closed (`403`/`503`), nunca fail-open.
- Tentativa de recuperar evidência de outra `empresa` → bloqueada pelo filtro.

## Critérios de aceite (EARS)

- IF o JWT é inválido/ausente, THEN THE SYSTEM SHALL responder `401`.
- IF o AccessDecision nega a permissão, THEN THE SYSTEM SHALL responder `403`.
- THE SYSTEM SHALL resolver o tenant exclusivamente do claim `empresa` do JWT.
- THE SYSTEM SHALL incluir filtro `empresa` em toda consulta Elastic (recuperação e analítica).
- THE SYSTEM SHALL nunca incluir citação/documento de outra `empresa` numa resposta.
- WHERE há solicitação LGPD de expurgo, THE SYSTEM SHALL anonimizar/remover a PII de conversas e nós da `empresa`.
