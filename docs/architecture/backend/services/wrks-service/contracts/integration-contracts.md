# Integration Contracts — WRKS (external systems)

> External (non-Journey-OS) systems WRKS integrates with. Resilience4j for retry/circuit-breaker.

## 1. Keycloak (OIDC IdP)

| Aspect | Value |
|---|---|
| Role | Authentication only (WRKS owns authorization — ADR-002) |
| Protocol | OIDC Authorization Code |
| Auth | confidential client (`client_id`/`client_secret`) |
| Operations | exchange code→tokens; fetch userinfo/`sub`; validate IdP token |
| Mapping | Keycloak `sub` → `journeyos_global.usuario.idp_subject` |
| Fallback | **No bypass.** `IF Keycloak is unreachable, THEN THE SYSTEM SHALL reject login with 502 upstream_error AND existing valid JWTs SHALL keep working until expiry.` |
| Resilience | circuit-breaker on token endpoint; timeout 2s; no retry on auth (fail fast) |

## 2. Redis / Valkey

| Use | Key | TTL |
|---|---|---|
| Session cache | `journey-os:sessao:{sessionId}` | access-token TTL |
| AccessDecision cache | `journey-os:access:{usuarioId}:{empresaId}` | 5 min (pub/sub invalidation) |
| Logout blacklist | `journey-os:blacklist:{jti}` | remaining access-token TTL |

- `WHILE Redis is unavailable, THE SYSTEM SHALL fall back to PostgreSQL for AccessDecision (cache is optimization, not source of truth).`
- `IF Redis is unavailable at logout, THEN THE SYSTEM SHALL still clear the refresh cookie; revocation degrades to natural token expiry (short TTL).`

## 3. Elasticsearch (`audit-events`)

| Aspect | Value |
|---|---|
| Client | direct Java client (`ingestMode=direct-java-client`) |
| Index | `audit-events` (domainContext WRKS) |
| Write | async, after `evento_auditoria` row persisted |
| Fallback | `IF Elastic write fails, THEN THE SYSTEM SHALL retry with backoff AND the PostgreSQL row remains the source of truth.` |

## 4. PostgreSQL

`journeyos_global` (IAM). `ddl-auto=validate`; `open-in-view=false` (RULE-08). Schema prepared by MIG.

## 5. SLAs / rate limits

| Dependency | Timeout | Retry | Circuit breaker |
|---|---|---|---|
| Keycloak | 2s | none (login) | yes |
| MIG (provision) | 30s | 3 (backoff) | yes |
| Redis | 2s | none (fallback to DB) | n/a |
| Elastic | 5s | 3 (backoff) | yes |
