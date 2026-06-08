# SPEC-07 — Observability & Health · MIG

## Objective
Make migration runs observable and the service's readiness reliably reportable.

## Scope
- **In:** structured logging, applied-migration log, actuator health/info/flyway, MDC.
- **Out:** distributed tracing of business requests (no business requests), metrics SLAs.

## Technical decisions
- **SLF4J via `@Slf4j`** (Lombok); never `System.out` (CLAUDE.md rule).
- **MDC correlation** on each run with a generated `runId` for log correlation.
- **Actuator** `health`, `info`, `flyway` expose run state and applied versions.

## Implementation
- Log run start/end with: target schemas, count applied, count pending, duration, `runId`.
- On failure: log the failing migration (version, file, schema) at `ERROR`.
- `info` endpoint includes build info + highest applied version per schema target.
- Health readiness `UP` only after a successful run (or no pending work).

## Edge cases
- Long-running per-tenant fan-out → emit periodic progress logs per schema.
- One-shot job mode (actuator off) → rely on structured logs + exit code.

## Acceptance criteria (EARS)
- WHEN a migration run starts, THE SYSTEM SHALL log the targeted schemas and a unique `runId`.
- WHEN a migration is applied, THE SYSTEM SHALL log its version, file, and schema.
- IF a migration fails, THEN THE SYSTEM SHALL log the failing version/file/schema at ERROR
  and exit non-zero.
- THE SYSTEM SHALL report `/actuator/flyway` with applied and pending migrations when enabled.
- THE SYSTEM SHALL use SLF4J logging and SHALL NOT use `System.out`/`System.err`.

> EARS guide: `docs/architecture/backend/standards/ears-notation.md`.
