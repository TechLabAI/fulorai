# SPEC-08 — BDD Test Scenarios (WRKS)

## Objective
Map EARS acceptance criteria to executable Cucumber features and document reusable steps.

## Feature files (`tests/cucumber/`)
| Feature | Covers |
|---|---|
| `login-and-session.feature` | SPEC-02, api §1 (login, switch, refresh, logout) |
| `access-decision.feature` | SPEC-03, api §2/§5 (evaluate, cache, version, JWKS) |
| `workspace-provisioning.feature` | SPEC-02/05, api §3 (saga, idempotency, duplicate slug) |
| `user-administration.feature` | SPEC-02/06, api §4 (CRUD, anti-escalation, cross-empresa) |

## Reusable step definitions (`WrksStepDefs`)
- `Given the empresa "<slug>" is ATIVA` — seeds empresa.
- `Given a usuario "<email>" exists` / `... associated with "<slug>" as "<papel>"`.
- `When a valid|invalid OIDC code is presented to "<path>"` — IdP stub.
- `Then the response status is <n>` / `Then the error code is "<code>"`.
- `Then the event "<topic>" is published` — Kafka test consumer assertion.
- `Given ... logged in scoped to "<slug>"` — issues a test JWT.

## Test infrastructure
- Testcontainers singleton (PostgreSQL, Redis, Kafka) — static initializer (never `@Container`).
- Keycloak + MIG stubbed (WireMock) for unit/integration; `application-bdd.properties` profile.
- `CucumberSpringContext` boots the Spring context once.

## Acceptance (EARS)
- `THE SYSTEM SHALL have one BDD scenario for every SHALL clause across SPEC-01..10 (D-218 gate).`
- `WHILE the scaffold is incomplete, the generated step defs SHALL throw PendingException (no false green).`

## References
- `testing-conventions.md`, `be-architect-specs-validate` (EARS→BDD), D-218.
