# Data Model · MIG (`journey-os-migrations`)

> MIG owns **no business tables**. Business tables are authored by each module as
> `V<N>__<module>_<description>.sql` migration files and are documented in that module's
> own `data-model.md`. MIG's own DDL is the **platform bootstrap**: PostgreSQL extensions
> and the global schema baseline that every other migration depends on.
>
> The `scripts/be-migration-generator.py` extracts the ```sql``` blocks below, in order,
> routing each block by its `-- schema:` first-line comment.

## 0. Extensions

Enabled once in the global schema. `pgvector` is required by LEAD/INTL embeddings;
`uuid-ossp`/`pgcrypto` back UUID primary keys; `pg_trgm`/`unaccent` back text search.

```sql
-- schema: global
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS pgcrypto;
CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE EXTENSION IF NOT EXISTS unaccent;
CREATE EXTENSION IF NOT EXISTS vector;
```

**Invariants:** extensions are cluster/database-scoped and created idempotently
(`IF NOT EXISTS`); re-running the migration is safe.

## 1. Conventions (platform-wide, set by MIG)
- **PK strategy:** `UUID` primary keys (`gen_random_uuid()` via `pgcrypto`) unless a
  module justifies otherwise.
- **Timestamps:** `TIMESTAMPTZ` columns `created_at` / `updated_at`, UTC.
- **Soft-delete:** `deleted_at TIMESTAMPTZ NULL` where a module needs it (per-module choice).
- **Encoding:** database `UTF8`, collation deterministic per environment.
- **Naming:** `snake_case` tables/columns; migration files `V<N>__<module>_<description>.sql`.

## 2. MIG-owned entities
**None.** MIG manages only Flyway's `flyway_schema_history` table (created and owned by
Flyway itself, per schema). It is not modeled as a JPA entity.

## 3. Schema-level mapping

| Table | Schema | Owner |
|-------|--------|-------|
| `flyway_schema_history` | global + each `empresa` | Flyway (auto) |
| _(business tables)_ | per module's data-model | the owning module (WRKS/LEAD/…) |

## 4. Migration plan — reserved version ranges

To keep one ordered, collision-free version sequence across modules, version ranges are
reserved per owner. MIG bootstrap occupies the lowest range.

| Range | Owner | Schema target |
|-------|-------|---------------|
| `V1..V9` | MIG (bootstrap: extensions, baseline) | global |
| `V10..V99` | WRKS (workspace/identity/tenant registry) | global + empresa |
| `V100..V199` | LEAD | empresa |
| `V200..V299` | ASST | empresa |
| `V300..V399` | JRNY | empresa |
| `V400..V499` | COMM | empresa |
| `V500..V599` | SALE | empresa |
| `V600..V699` | INTL | global + empresa |

> Ranges are a coordination convention, not a hard constraint enforced by Flyway. The
> per-tenant set (`db/migration/empresa/`) and global set (`db/migration/global/`) each
> maintain their own ordered sequence (ADR-003).

## 5. Relations (ASCII)
```
journeyos_global ──(extensions, shared/reference tables, tenant registry [WRKS])
       │
       └── empresa_<tenantId> ──(tenant-scoped business tables, one schema per empresa)
```
