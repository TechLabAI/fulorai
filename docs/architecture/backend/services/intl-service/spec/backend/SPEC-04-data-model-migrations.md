# SPEC-04 — Data Model + Migrations

> Ref: `contracts/data-model.md`. ADR-004. Migrada via MIG; `ddl-auto=validate`.

## Objetivo

Definir o modelo relacional de INTL (schema `emp_<slug>`) e o plano de migração centralizado.

## Escopo

**In:** 7 tabelas (`base_conhecimento`, `fonte_conhecimento`, `no_conhecimento`,
`conversa_copiloto`, `mensagem_copiloto`, `citacao`, `evento_indexado`); índices; constraints.
**Out:** `registro_indice` global (governança via config no MVP); índices Elastic (não-DDL SQL).

## Decisões técnicas

- PK `uuid` `gen_random_uuid()` (pgcrypto); timestamps `timestamptz`.
- Enums via `varchar` + `CHECK`. Embedding `vector(1536)` nullable (pgvector; dimensão TBD no P3).
- Soft-state por `status=ARQUIVADO` (sem hard-delete) em nós.
- DDL gerada por `be-migration-generator.py` a partir dos blocos ```sql``` (ordem preservada).

## Casos de borda

- Extensões `pgcrypto`/`vector` já criadas pela V1 global (não duplicar).
- Dimensão do embedding pode mudar no sync TechLab AI → reembedding/reprojeção.

## Critérios de aceite (EARS)

- THE SYSTEM SHALL criar as 7 tabelas no schema `emp_<slug>` via `V1__intl_create_initial_schema.sql`.
- THE SYSTEM SHALL impedir mais de uma `base_conhecimento` por `empresa`.
- IF `fonte.tipo = 'ASSET'` AND `referencia IS NULL`, THEN THE SYSTEM SHALL rejeitar a inserção.
- THE SYSTEM SHALL garantir `ordem` única por `conversa_id` em `mensagem_copiloto`.
- THE SYSTEM SHALL validar o schema em runtime (`ddl-auto=validate`) — falha de validação impede boot.
