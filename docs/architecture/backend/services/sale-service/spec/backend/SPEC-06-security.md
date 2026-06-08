# SPEC-06 — Security (SALE)

## Objective
Define authentication, authorization, tenant isolation and LGPD handling for `sale-service`.

## Scope
- **In:** JWT resource server, `sale.*` permissions via WRKS AccessDecision, tenant isolation, buyer PII/LGPD, service-token purchase ingestion.
- **Out:** token issuance (WRKS), gateway routing (GWY).

## Technical decisions
- Spring Security resource server validates WRKS-issued RS256 JWT via JWKS (SPEC-10).
- Authorization via WRKS `AccessEvaluateClient` (Feign), cached in Redis; cache invalidated by `journey-os.modelo.acesso.alterado`.
- Tenant resolved from `empresa_id` claim → `EmpresaContextHolder`; writes require `require()`.
- Revenue is the most sensitive tenant data → strict cross-empresa guard.

## Implementation & acceptance criteria (EARS)
- `THE SYSTEM SHALL reject any business request without a valid WRKS-issued JWT with 401.`
- `IF the caller lacks the required sale.<recurso>.<acao> permission, THEN THE SYSTEM SHALL respond 403 application/problem+json.`
- `THE SYSTEM SHALL resolve the tenant solely from the JWT empresa_id claim and SHALL never read sale data across empresas.`
- `WHILE the WRKS AccessDecision circuit is open, THE SYSTEM SHALL deny by default.`
- `THE SYSTEM SHALL require a service token (not anonymous) for POST /compras ingestion.`
- `WHEN a compra is anonymized for LGPD, THE SYSTEM SHALL clear buyer PII columns and retain revenue/aggregate rows.`
- `THE SYSTEM SHALL NOT log buyer PII (MDC carries correlationId/empresaId, never nome/email).`

## Edge cases
- Purchase from checkout with a service token still resolves a tenant; no cross-empresa leakage.
- LGPD purge removes rows except those under fiscal retention obligation (configurable).

## References
- ADR-004; WRKS `contracts/` (AccessDecision, JWKS); `shared/multi-empresa.md`; `_extensions.compliance.lgpd`.
