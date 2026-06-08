# ADR-004 — Multi-tenancy: schema-per-tenant (`emp_<slug>`)

**Status:** accepted

## Contexto

O Journey OS adota `schema-per-tenant` (decisão global — `shared/multi-empresa.md`, termo
`empresa`, schema global `journeyos_global`). JRNY é um serviço de negócio que manipula dados
operacionais (jornadas, estágios, regras, inscrições, decisões de roteamento) que **devem** ser
isolados por empresa — incluindo o decision log, que carrega snapshots de atributos de leads.

## Decisão

JRNY lê/escreve **exclusivamente** no schema operacional `emp_<slug>` do tenant corrente,
resolvido em runtime via `EmpresaContextHolder.require()` (preenchido pelo filtro de segurança a
partir do JWT emitido por WRKS, **ou** pelo contexto de empresa extraído do payload/header do
evento Kafka no caminho de consumo). JRNY **nunca** escreve em `journeyos_global`. Todo registro
carrega `empresa_id` como guarda redundante; queries, adapters e consumidores validam o tenant
ativo.

- DDL do schema do tenant é responsabilidade de **MIG** (`journey-os-migrations`); JRNY usa
  `ddl-auto=validate`.
- Os índices Elastic `journey-events`/`routing-decisions` são particionados/filtrados por
  `empresa_id` (sem vazamento na telemetria/auditoria).

## Alternativas consideradas

- **Discriminator column (single schema):** mais simples operacionalmente, mas contraria a decisão global e enfraquece o isolamento (LGPD do decision log, backup por tenant). Rejeitada.
- **Database-per-tenant:** isolamento máximo, mas custo operacional incompatível com o volume de empresas previsto. Rejeitada (alinhado ao global).

## Consequências

**Positivas:** isolamento forte; backup/retenção/expurgo LGPD por empresa (relevante ao decision log); alinhado à plataforma.

**Negativas:** resolução de schema em runtime tanto no caminho HTTP quanto no consumo de eventos (cuidado extra para fixar o tenant antes de processar a mensagem); testes de isolamento obrigatórios.

## Referências

- `docs/architecture/shared/multi-empresa.md` (ADR-001 global schema-per-empresa)
- `docs/architecture/shared/modelo-dados/empresa.md`
- ADR global: `docs/architecture/backend/adr/ADR-003-multi-tenancy.md`
