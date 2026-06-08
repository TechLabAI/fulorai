# 06 — Risks, Gaps & Assumptions · MIG (`journey-os-migrations`)

## 1. Risks
- **R1 — Per-tenant fan-out cost:** applying migrations across many `empresa` schemas
  can be slow / partially fail mid-run. Mitigation: ordered, per-schema execution with
  fail-fast and clear logging of the last successful schema.
- **R2 — Privilege escalation surface:** MIG needs DDL + `CREATE EXTENSION` rights.
  Mitigation: dedicated migration role, credentials via `${VAR_NAME}`, never reused by
  runtime services.
- **R3 — Checksum drift:** editing an already-applied migration breaks Flyway checksums.
  Mitigation: forward-only policy, CI validation gate, immutability of applied files.
- **R4 — Ordering hazard across modules:** cross-module FKs require a global version
  ordering. Mitigation: single centralized version sequence + path-based schema targeting.
- **R5 — Tenant enumeration source:** MIG must know which `empresa` schemas exist.
  Mitigation: define the enumeration source explicitly in specs (catalog table vs.
  schema introspection) — see Gap G1.

## 2. Known Gaps
- **G1 — Tenant schema discovery:** the authoritative list of tenant schemas (and who
  creates a new one) is not yet specified. Likely a `journeyos_global` tenant registry
  table owned by WRKS; MIG reads it to know which schemas to migrate.
- **G2 — New-tenant provisioning trigger:** how/when a brand-new tenant schema is created
  and brought to current version (boot-time batch vs. on-demand) is undefined for MVP.
- **G3 — Rollback policy:** forward-only is assumed; no defined remediation for a bad
  migration beyond a corrective forward migration.

## 3. Assumptions to Validate
- **A1** — `schema-per-tenant` with shared `journeyos_global` is final (per
  `project-context.json.multiTenancy`).
- **A2** — `pgvector` is required and provisioned centrally by MIG in the global schema.
- **A3** — All services will be configured with `ddl-auto=validate` (enforced by convention).
- **A4** — MIG runs as a boot-time step (not a long-lived runtime service), though it
  may stay up to expose health.

## 4. Critical Dependencies
- **PostgreSQL 15+ (RDS/Aurora)** reachable with a DDL-capable migration role.
- **`pgvector`** extension available on the cluster.
- **Tenant registry** (G1) — needed before per-tenant migration can be fully automated;
  for MVP a single global schema + a sample tenant schema is sufficient.
