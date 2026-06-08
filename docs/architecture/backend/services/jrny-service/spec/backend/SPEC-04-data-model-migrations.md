# SPEC-04 — Data Model & Migrations

> Contrato: `contracts/data-model.md` (blocos SQL canônicos). ADR-004 (multi-tenancy), ADR-005
> (versionamento + decision log imutável). EARS guide: `docs/architecture/backend/standards/ears-notation.md`.

## Objetivo

Definir o modelo de dados de JRNY no schema `emp_<slug>` e a estratégia de migrations centralizada
(MIG/Flyway), com o `empresa_id` guard explícito e a imutabilidade da `decisao_roteamento`.

## Escopo

- **In:** tabelas `jornada`, `estagio`, `regra_roteamento`, `inscricao_jornada`, `decisao_roteamento`; constraints/índices; mapeamento schema-aware; gramática de `condicao`.
- **Out:** outbox/processed_events (migração compartilhada); índices Elastic `journey-events`/`routing-decisions` (projeção, SPEC-10).

## Decisões técnicas

- Schema-per-tenant **com `empresa_id` guard explícito** em toda tabela (= `EmpresaContextHolder.require()`) — ADR-004; doc 05 §2; doc 03 §5 invariante 7.
- `ddl-auto=validate`; DDL gerado por `be-migration-generator.py` a partir dos blocos SQL → `db/migration/empresa/V<N>__jrny_*.sql`.
- PK UUID (`gen_random_uuid()`); timestamps `TIMESTAMPTZ`; `condicao`/`config`/`snapshot_entrada` `JSONB`.
- `decisao_roteamento` **imutável**: sem caminho de UPDATE/DELETE no domínio (ADR-005).
- Unicidade parcial `inscricao_jornada (lead_id, jornada_id) WHERE estado='ATIVA'`; unicidade `estagio (jornada_id, ordem)`.
- `lead_id` e `estagio.asset_ref_id` são **referências lógicas** (sem FK física cross-schema).

## Implementação

- Entities JPA em `infrastructure/persistence/entity`; adapters implementam os `*RepositoryPort`.
- Mapeamento entity↔domain (sem expor entity na API).
- `@Version` (optimistic) em `inscricao_jornada` para concorrência de avanço (SPEC-05).

## Casos de borda

- `(jornada_id, ordem)` duplicado → violação de unicidade (mapear para `jrny.estagio.ordem-duplicada`).
- Segunda inscrição ATIVA do mesmo lead na mesma jornada → bloqueada pelo índice parcial.
- `resultado='ROTEADO'` sem `estagio_alvo_id` → bloqueado pelo CHECK.

## Critérios de aceite (EARS)

- `THE SYSTEM SHALL persist jornada, estagio, regra_roteamento, inscricao_jornada and decisao_roteamento in the tenant schema emp_<slug>.`
- `THE SYSTEM SHALL set empresa_id = EmpresaContextHolder.require() on every row of every JRNY table.`
- `THE SYSTEM SHALL enforce a unique (jornada_id, ordem) on estagio.`
- `THE SYSTEM SHALL enforce at most one inscricao_jornada with estado=ATIVA per (lead_id, jornada_id) via a partial unique index.`
- `IF resultado = ROTEADO, THEN THE SYSTEM SHALL require estagio_alvo_id to be non-null (DB CHECK).`
- `THE SYSTEM SHALL never UPDATE or physically DELETE a decisao_roteamento row (the decision log is immutable; archival of journeys/enrolments is logical).`
- `THE SYSTEM SHALL treat lead_id and estagio.asset_ref_id as logical references with no physical FK to another schema or service.`
- `THE SYSTEM SHALL run with ddl-auto=validate AND SHALL NOT create or alter schema at boot.`
