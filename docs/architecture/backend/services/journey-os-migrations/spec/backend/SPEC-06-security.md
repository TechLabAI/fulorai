# SPEC-06 — Security · MIG

## Objective
Define the security posture of a service that holds elevated DDL privileges over the
entire platform database.

## Scope
- **In:** credential handling, migration role privileges, actuator exposure, least-privilege.
- **Out:** OAuth2/business authz (no business API), mTLS to external APIs (none).

## Technical decisions
- **Dedicated migration role** with DDL + `CREATE EXTENSION` rights, used **only** by MIG.
  Runtime services use a separate, lower-privilege role that cannot alter schema.
- **No hardcoded secrets** — all credentials via `${VAR_NAME}` env config (CLAUDE.md rule).
- **Actuator network-restricted** — not exposed to the public internet.

## Implementation
- JDBC URL/user/password from environment (e.g. `${MIG_DB_URL}`, `${MIG_DB_USER}`,
  `${MIG_DB_PASSWORD}`); no defaults committed.
- `cleanDisabled=true` so the privileged role still cannot trigger a destructive wipe.
- Run MIG in CI/CD with the migration role injected from the secrets manager.

## Edge cases
- Missing env credentials → fail fast at startup with a clear error.
- Migration role accidentally reused by a runtime service → blocked by policy/review; the
  runtime role lacks DDL grants.

## Acceptance criteria (EARS)
- THE SYSTEM SHALL read all database credentials from environment variables, never from
  committed configuration.
- IF any required credential env var is absent, THEN THE SYSTEM SHALL fail to start with a
  configuration error.
- THE SYSTEM SHALL keep Flyway `clean` disabled in every environment.
- THE SYSTEM SHALL NOT expose actuator endpoints to untrusted networks.
- THE SYSTEM SHALL use a migration role distinct from the runtime services' role.

> EARS guide: `docs/architecture/backend/standards/ears-notation.md`. Related: ADR-005.
