# SPEC-04 — Data Model & Migrations (SALE)

## Objective
Define the persistence model in `emp_<slug>` and how migrations are produced/applied.

## Scope
- **In:** tables `oportunidade`, `historico_estagio`, `oferta`, `compra`, `item_compra`, `modelo_atribuicao`, `atribuicao`, `campanha`, `ltv`; constraints, indices, schema routing.
- **Out:** global IAM schema (WRKS), Elastic projections (SPEC-10).

## Technical decisions
- Authoritative DDL lives in `contracts/data-model.md` as `-- schema: empresa` SQL blocks; extracted by `be-migration-generator.py` into `db/migration/empresa/` (centralized Flyway in `journey-os-migrations`).
- SALE runs `ddl-auto=validate` and `open-in-view=false` (RULE-08); never owns Flyway.
- Money is `NUMERIC(15,2)` + `moeda CHAR(3)`; never float.

## Implementation & acceptance criteria (EARS)
- `THE SYSTEM SHALL persist all SALE data in the per-tenant emp_<slug> schema and SHALL NOT write to journeyos_global.`
- `THE SYSTEM SHALL enforce UNIQUE(id_externo, origem) on compra (purchase idempotency).`
- `THE SYSTEM SHALL enforce at most one active modelo_atribuicao via a partial unique index.`
- `IF item_compra rows do not sum to compra.valor_total, THEN THE SYSTEM SHALL reject the purchase (revenue conservation).`
- `THE SYSTEM SHALL keep historico_estagio append-only (no update/delete).`
- `THE SYSTEM SHALL boot with ddl-auto=validate and fail fast if the schema is absent.`

## Edge cases
- Anonymization clears `compra.nome_comprador`/`email_comprador` but keeps `valor_total`/aggregates.
- `compra.oportunidade_id` is nullable (direct sale) and `ON DELETE SET NULL`.

## Acceptance
- `architectureCheck` green; migration applies cleanly to a fresh `emp_<slug>`; constraints verified by integration tests.

## References
- ADR-004; `contracts/data-model.md`; `journey-os-migrations` (MIG).
