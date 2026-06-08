# ADR-004 — Multi-tenancy: schema-per-tenant (`emp_<slug>`)

**Status:** accepted

## Contexto

O Journey OS adota `schema-per-tenant` (decisão global — `shared/multi-empresa.md`, termo
`empresa`, schema global `journeyos_global`). ASST é um serviço de negócio que manipula dados
operacionais (assets, versões, aprovações) que **devem** ser isolados por empresa.

## Decisão

ASST lê/escreve **exclusivamente** no schema operacional `emp_<slug>` do tenant corrente,
resolvido em runtime via `EmpresaContextHolder.require()` (preenchido pelo filtro de segurança a
partir do JWT emitido por WRKS). ASST **nunca** escreve em `journeyos_global`. Todo registro
carrega `empresa_id` como guarda redundante; queries e adapters validam o tenant ativo.

- DDL do schema do tenant é responsabilidade de **MIG** (`journey-os-migrations`); ASST usa
  `ddl-auto=validate`.
- O índice Elastic `assets` é particionado/filtrado por `empresa_id` (sem vazamento na busca).

## Alternativas consideradas

- **Discriminator column (single schema):** mais simples operacionalmente, mas contraria a decisão global e enfraquece o isolamento (LGPD, backup por tenant). Rejeitada.
- **Database-per-tenant:** isolamento máximo, mas custo operacional incompatível com o volume de empresas previsto. Rejeitada (alinhado ao global).

## Consequências

**Positivas:** isolamento forte; backup/retenção/expurgo LGPD por empresa; alinhado à plataforma.

**Negativas:** resolução de schema em runtime e cuidado nos adapters (search/persistence) para sempre fixar o tenant; testes de isolamento obrigatórios.

## Referências

- `docs/architecture/shared/multi-empresa.md` (ADR-001 global schema-per-empresa)
- `docs/architecture/shared/modelo-dados/empresa.md`
- ADR global: `docs/architecture/backend/adr/ADR-003-multi-tenancy.md`
