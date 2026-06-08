# ADR-004 — Multi-tenancy Híbrida (PG schema-per-tenant + Elastic compartilhado)

**Status:** accepted

## Contexto

INTL persiste dados relacionais por `empresa` (conhecimento, conversas) e também consulta/projeta
documentos Elastic que escalam linearmente (*facts*). A estratégia global do Journey OS é
`schema-per-tenant` (ADR-001 global, termo `empresa`, schema `emp_<slug>`), mas aplicá-la
literalmente ao Elasticsearch (um índice por tenant) explodiria a contagem de shards.

## Decisão

**Híbrida:**

- **PostgreSQL:** `schema-per-tenant` (`emp_<slug>`), resolvido por `EmpresaContextHolder`.
  Tabelas de domínio **sem** coluna `empresa_id` (o schema isola). Escrita só no schema resolvido.
- **Elasticsearch:** **índice compartilhado** por tipo de documento, com **campo discriminador
  `empresa`** + **routing** por `empresa`. **Toda** consulta (recuperação RAG e analítica)
  inclui filtro `empresa` obrigatório no nível da porta (`SearchPort`), reforçado por teste de
  isolamento. O bloco de rastreabilidade + `empresa` é obrigatório em toda indexação.

## Alternativas consideradas

- **Índice Elastic por-tenant:** isolamento físico forte, mas explosão de shards/custo para *facts*
  e dimensões pequenas; rejeitada para o universo de muitas `empresas`.
- **Sem discriminador (confiar só na app):** risco inaceitável de vazamento cross-tenant; rejeitada.
- **Schema único no PG com `empresa_id`:** contraria a decisão global `schema-per-tenant`; rejeitada.

## Consequências

**Positivas:** isolamento relacional forte; Elastic eficiente em shards; um único ponto (porta)
que injeta o filtro `empresa`.
**Negativas:** o isolamento Elastic é **lógico** (depende do filtro obrigatório) — exige testes de
isolamento e revisão de toda nova query; routing por `empresa` precisa ser consistente entre
escrita e leitura.

## Referências

- `docs/architecture/shared/multi-empresa.md` (ADR-001 global)
- `05-persistence-model.md` §1
- [[ADR-003-event-platform-indexing-strategy]]
