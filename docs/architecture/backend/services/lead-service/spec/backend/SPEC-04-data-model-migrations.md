# SPEC-04 — Data Model & Migrations (LEAD)

## Objective
Define the persistence model and migration strategy for `lead-service` in the tenant schema `emp_<slug>`.

## Scope
- **In:** the 12 LEAD tables, constraints, indexes, schema-per-tenant routing, seeds.
- **Out:** global schema (WRKS-owned); Elastic mapping (SPEC-10).

## Technical decisions
- Schema-per-tenant (ADR-004): all tables in `emp_<slug>`, authored in `contracts/data-model.md`
  as `-- schema: empresa` blocks → extracted into `db/migration/empresa/` by `be-migration-generator.py`.
- LEAD runs `ddl-auto=validate`, `open-in-view=false` (RULE-08). `gen_random_uuid()` via `pgcrypto` (MIG/global).
- Default `regra_qualificacao` + `segmento` seeded per tenant on `empresa.provisionada` consume (not a global migration).

## Implementation & acceptance criteria (EARS)
- `THE SYSTEM SHALL persist all lead data in the empresa schema resolved by EmpresaContextHolder and never in journeyos_global.`
- `THE SYSTEM SHALL enforce a unique chave_natural per empresa schema (dedup).`
- `IF an insert would create a second active qualification rule, THEN THE SYSTEM SHALL reject it (partial unique index uq_regra_ativa).`
- `THE SYSTEM SHALL store at most one current maturity_score per lead and at most six score_dimensao rows per score.`
- `IF a maturity_score references a versao_regra with no matching regra_qualificacao, THEN THE SYSTEM SHALL reject the write.`
- `WHEN a lead is anonymized, THE SYSTEM SHALL null PII columns while preserving maturity_score/score_dimensao rows.`

## Migration plan
See `contracts/data-model.md` §5. Ranges assigned by `journey-os-migrations` to avoid cross-module collisions;
files named `V<N>__lead_<theme>.sql`.

## Edge cases
- Tenant provisioned but seed not yet applied → qualify returns `lead.qualification.sem-regra-ativa` until seed completes.

## References
- ADR-004; `contracts/data-model.md`; CLAUDE.md (centralized Flyway).
