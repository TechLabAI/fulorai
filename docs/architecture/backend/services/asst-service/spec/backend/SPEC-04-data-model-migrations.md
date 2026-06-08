# SPEC-04 — Data Model & Migrations

> Contrato: `contracts/data-model.md` (blocos SQL canônicos). ADR-004/ADR-005. EARS guide linkado.

## Objetivo

Definir o modelo de dados de ASST no schema `emp_<slug>` e a estratégia de migrations
centralizada (MIG/Flyway).

## Escopo

- **In:** tabelas `asset`, `versao_asset`, `aprovacao`, `tag_asset`; constraints/índices; mapeamento schema-aware.
- **Out:** outbox/processed_events (migração compartilhada); índice Elastic `assets` (projeção, SPEC-10).

## Decisões técnicas

- Schema-per-tenant: tabelas **sem `empresa_id`** (o schema isola — `shared/modelo-dados/empresa.md`); ADR-004.
- `ddl-auto=validate`; DDL gerado por `be-migration-generator.py` a partir dos blocos SQL → `db/migration/empresa/V<N>__asst_*.sql`.
- PK UUID (`gen_random_uuid()`); timestamps `TIMESTAMPTZ`; conteúdo `JSONB`.
- Versão imutável: sem caminho de UPDATE em `versao_asset` (ADR-005).

## Implementação

- Entities JPA em `infrastructure/persistence/entity`; adapters implementam `AssetRepositoryPort`.
- Mapeamento entity↔domain (sem expor entity na API).

## Casos de borda

- `(asset_id, numero)` duplicado → violação de unicidade (mapear para erro de domínio).
- FK órfã (versão sem asset) impossível (FK + cascade).

## Critérios de aceite (EARS)

- `THE SYSTEM SHALL persist asset, versao_asset, aprovacao and tag_asset in the tenant schema emp_<slug> with no empresa_id column.`
- `IF a versao_asset with the same (asset_id, numero) already exists, THEN THE SYSTEM SHALL reject the insert (unique constraint).`
- `THE SYSTEM SHALL assign versao_asset.numero as the next contiguous integer per asset starting at 1.`
- `IF origem='ASSET_STUDIO', THEN THE SYSTEM SHALL require a non-null brief_composicao.`
- `THE SYSTEM SHALL run with ddl-auto=validate AND SHALL NOT create or alter schema at boot.`
- `THE SYSTEM SHALL never physically delete asset, versao_asset or aprovacao rows (archival is logical).`
