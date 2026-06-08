# SPEC-06 — Security (LEAD)

## Objective
Define authentication, authorization, tenant isolation and LGPD handling for `lead-service`.

## Scope
- **In:** JWT resource-server validation, `lead.*` permissions via AccessDecision, cross-empresa guard, PII/LGPD.
- **Out:** token issuance/RBAC source of truth (WRKS).

## Technical decisions
- Spring Security resource server validates WRKS-issued RS256 JWT via JWKS (SPEC-10). Authorization
  uses WRKS `AccessDecision` (Feign + Redis cache, invalidated by `modelo.acesso.alterado`).
  `EmpresaContextHolder` enforces tenant scope. Security filters in `infrastructure.security`.

## Permission catalogue (LEAD)
`lead.lead.{criar,read,editar,anonimizar,expurgar}`, `lead.survey.{read,criar,editar,responder}`,
`lead.qualification.{read,criar,ativar,executar}`, `lead.segment.{read,criar,editar,excluir}`.
These must be added to the canonical `permission-catalogue.arch.json` and bundled to roles
(SDR: read/queue; HEAD_GROWTH: rules/segments; INFOPRODUTOR: full).

## Acceptance criteria (EARS)
- `THE SYSTEM SHALL reject any request without a valid WRKS-issued JWT with 401 (iam.* codes).`
- `IF a JWT carries a modelo_acesso_versao lower than the current version, THEN THE SYSTEM SHALL reject with 401 'iam.sessao.versao-desatualizada'.`
- `THE SYSTEM SHALL authorize each endpoint against the required lead.* permission from the AccessDecision.`
- `THE SYSTEM SHALL scope every query and write to the empresa_id claim and SHALL NOT return data from another empresa.`
- `IF WRKS authorization is unavailable and no valid cache entry exists, THEN THE SYSTEM SHALL fail closed (503).`
- `THE SYSTEM SHALL require a base_legal for every lead and SHALL support anonymization and physical purge (LGPD).`
- `THE SYSTEM SHALL NOT write PII to logs (MDC carries identifiers only).`

## Edge cases
- Service-to-service capture (landing pages) uses a service token with `lead.lead.criar` only.
- Purge (right to be forgotten) physically removes rows and records the action in audit (no PII in the audit payload).

## References
- WRKS SPEC-03/06; `shared/rbac/`; ADR-004; `contracts/hub-integration.md`.
