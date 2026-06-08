---
service: wrks-service
module: WRKS
type: standard
package: com.journeyos.wrks
gradleKey: ":services:wrks-service"
port: 8081
status: draft
specSet: full
ears: true
sourceVision:
  - 01-architectural-vision.md
  - 02-architecture-blueprint.md
  - 03-initial-domain-framing.md
  - 04-backend-architecture-direction.md
  - 05-persistence-model.md
  - 06-risks-gaps-assumptions.md
adrs:
  - adr/ADR-001-hexagonal-architecture.md
  - adr/ADR-002-identity-authority.md
  - adr/ADR-003-messaging-strategy.md
  - adr/ADR-004-multitenant-strategy.md
  - adr/ADR-005-token-session-model.md
---

# WRKS — Workspace & Identity Spec (wrks-service)

> **Full spec set.** WRKS is the **foundation** service: owner of identity, RBAC and
> multi-tenancy. It is the only business service that writes to the IAM subset of
> `journeyos_global`, issues the platform JWT (RS256), exposes `AccessDecision`, and
> orchestrates tenant provisioning via MIG.
> EARS notation guide: `docs/architecture/backend/standards/ears-notation.md`.

## Purpose

Provide one authority for *who can do what, in which workspace*: workspaces (`empresa`),
org structure (business units, teams), users, the canonical RBAC model (roles, permissions),
and identity/session (login via Keycloak OIDC, JWT issuance, access evaluation). Every other
Journey OS module depends on WRKS for tenant context and authorization.

## Spec map

| SPEC | Theme | Status |
|---|---|---|
| [SPEC-01](spec/backend/SPEC-01-api-surface.md) | API surface (`/api/v1/iam/**`) | draft |
| [SPEC-02](spec/backend/SPEC-02-identity-session.md) | Identity & session (core orchestration) | draft |
| [SPEC-03](spec/backend/SPEC-03-rbac-access-decision.md) | RBAC & AccessDecision (sub-feature) | draft |
| [SPEC-04](spec/backend/SPEC-04-data-model-migrations.md) | Data model + migrations | draft |
| [SPEC-05](spec/backend/SPEC-05-idempotency-concurrency.md) | Idempotency + concurrency | draft |
| [SPEC-06](spec/backend/SPEC-06-security.md) | Security (JWT, OIDC, anti-escalation) | draft |
| [SPEC-07](spec/backend/SPEC-07-observability-health.md) | Observability + health | draft |
| [SPEC-08](spec/backend/SPEC-08-bdd-test-scenarios.md) | BDD test scenarios | draft |
| [SPEC-09](spec/backend/SPEC-09-messaging-architecture.md) | Messaging (Kafka) + audit consumer | draft |
| [SPEC-10](spec/backend/SPEC-10-integrations.md) | Integrations (Keycloak, Redis, MIG, Elastic) | draft |

## Contracts

- `contracts/api-contract.md` — REST surface + ProblemDetail errors
- `contracts/data-model.md` — IAM DDL (`-- schema: global`)
- `contracts/event-contracts.md` — produced/consumed events
- `contracts/hub-integration.md` — inter-service (GWY, MIG, all services)
- `contracts/integration-contracts.md` — external systems (Keycloak, Redis, Elastic)
- `contracts/techlab-ai-integration.md` — **none** (WRKS uses no AI)

## Key references

- `docs/architecture/shared/rbac/{modelo,papeis,permissoes,session-policy,enforcement,data-scope}.md`
- `docs/architecture/shared/multi-empresa.md`, `docs/architecture/shared/modelo-dados/{global-schema,empresa}.md`
- `docs/architecture/shared/contratos/error-model.md`
