# SPEC-04 — Data Model & Migrations

> EARS guide linkado. Fonte: `contracts/data-model.md`. Schema `emp_<slug>` (tenant), DDL via MIG.

## Objetivo

Definir as tabelas operacionais de COMM no schema `emp_<slug>` e como o DDL é gerado/aplicado
pelo `journey-os-migrations` (centralizado), garantindo isolamento por schema e imutabilidade da
trilha de entrega.

## Escopo

- **In:** `template_mensagem`, `mensagem`, `evento_entrega`, `regra_roteamento`, `config_canal`; índices; constraints CHECK/UNIQUE; plano de migration.
- **Out:** `outbox_event`/`processed_events` (migration compartilhada da plataforma); projeção Elastic (SPEC-10).

## Decisões técnicas

- **Schema-per-tenant:** tabelas sem coluna `empresa_id` — o schema isola o tenant (`search_path`). `ddl-auto=validate` (RULE-08 `open-in-view=false`).
- **PK:** UUID `gen_random_uuid()` (`pgcrypto` via MIG). Timestamps `criado_em`/`atualizado_em`.
- **Imutabilidade:** `mensagem.conteudo_renderizado` congelado; `evento_entrega` append-only.
- **Idempotência:** `UNIQUE (chave_idempotencia)` em `mensagem`.
- **Naming:** `V<N>__comm_*.sql` em `db/migration/empresa/`; faixa de V alocada por MIG.
- `be-migration-generator.py` extrai os blocos ```sql``` de `contracts/data-model.md` em ordem.

## Implementação

- Entities JPA em `infrastructure/persistence/entity` (mapeiam para POJOs do domínio via adapter/MapStruct).
- Repositories Spring Data + adapters implementando os ports `out`.
- CHECK constraints replicam o enum no banco (defesa em profundidade).

## Casos de borda

- Inserção concorrente com mesma `chave_idempotencia` → a 2ª viola UNIQUE → tratada como replay (SPEC-05), retorna a existente.
- `template_id` nulo (disparo ad-hoc) permitido; FK `ON DELETE SET NULL` preserva a mensagem se o template for removido.
- `config_canal` duplicada `(canal, provedor)` → viola UNIQUE → `409 comm.canal.duplicado`.

## Critérios de aceite (EARS)

- `THE SYSTEM SHALL persist all COMM operational tables in the tenant schema emp_<slug> without an empresa_id column.`
- `IF an INSERT would duplicate chave_idempotencia, THEN THE SYSTEM SHALL treat it as an idempotent replay rather than creating a second message.`
- `THE SYSTEM SHALL never issue UPDATE/DELETE against evento_entrega in normal operation (append-only).`
- `IF a config_canal already exists for (canal, provedor), THEN THE SYSTEM SHALL reject the new config with 409 error.code 'comm.canal.duplicado'.`
- `THE SYSTEM SHALL run with ddl-auto=validate, relying on journey-os-migrations for DDL.`
