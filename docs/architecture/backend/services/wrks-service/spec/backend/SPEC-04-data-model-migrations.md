# SPEC-04 — Data Model & Migrations (WRKS)

## Objective
Define the IAM persistence in `journeyos_global` and how it is migrated.

## Scope
- **In:** empresa, business_unit, team, usuario, usuario_team, papel, permissao, papel_permissao,
  usuario_empresa, modelo_acesso_versao, evento_auditoria.
- **Out:** operational `emp_<slug>` tables (owned by business services); extensions (MIG).

## Technical decisions
- Schema-per-tenant (ADR-004). WRKS owns IAM in `journeyos_global`; runs `ddl-auto=validate`;
  `open-in-view=false` (RULE-08). Centralized Flyway in `journey-os-migrations`.
- Canonical pt-BR identifiers (matches `shared/rbac/modelo.md`). DDL: `contracts/data-model.md`.

## Implementation
- `contracts/data-model.md` ```sql``` blocks (`-- schema: global`) → extracted to
  `db/migration/global/V000X__iam_*.sql` by `be-migration-generator.py`.
- Seeds: papel (INFOPRODUTOR/HEAD_GROWTH/SDR) + permissao bundles from `rbac.arch.json` /
  `permission-catalogue.arch.json`; `modelo_acesso_versao` singleton initialized to 1.

## Acceptance criteria (EARS)
- `THE SYSTEM SHALL store all IAM entities in schema journeyos_global.`
- `IF an empresa_id does not match ^emp_[a-z0-9_]+$, THEN THE SYSTEM SHALL reject it (CHECK constraint).`
- `THE SYSTEM SHALL enforce uniqueness of usuario.email, papel.codigo, permissao.codigo, and empresa_id.`
- `THE SYSTEM SHALL keep modelo_acesso_versao as a singleton row (id=1) with a monotonically increasing versao.`
- `THE SYSTEM SHALL soft-delete via ativo=false and SHALL NOT physically delete IAM rows.`
- `WHEN a usuario_empresa.papel is set, THE SYSTEM SHALL reference an existing papel.codigo (FK).`

## Edge cases
- Migration order: V0001 roles/permissions before V0002 associations (FK on papel.codigo). `evento_auditoria` is FK-free (append-only).

## References
- `contracts/data-model.md`, `shared/modelo-dados/{global-schema,empresa}.md`, ADR-004.
