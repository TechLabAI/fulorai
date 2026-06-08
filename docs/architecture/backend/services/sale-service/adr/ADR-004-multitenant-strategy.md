# ADR-004 — Multi-tenancy — schema-per-tenant (`emp_<slug>`)

**Status:** accepted

## Contexto

Receita é o dado mais sensível de uma `empresa` cliente do Journey OS — vazamento cross-empresa de
faturamento/LTV é inaceitável (confidencialidade + LGPD). O Journey OS padronizou
`schema-per-tenant` (decisão global em `docs/architecture/shared/multi-empresa.md`), com schema
operacional `emp_<slug>` por empresa e `journeyos_global` exclusivo de WRKS/MIG.

## Decisão

SALE adota **schema-per-tenant**: todos os dados operacionais (pipeline, ofertas, compras,
atribuição, LTV) vivem no schema `emp_<slug>` da empresa. SALE **não** escreve em `journeyos_global`.

- `EmpresaContextHolder` resolve o schema corrente a partir do JWT em cada requisição e em cada
  consumo de evento (o evento carrega o tenant; o consumer estabelece o contexto antes de persistir).
- `application.service` chama `EmpresaContextHolder.require()` — escrita sem contexto é proibida.
- O schema é provisionado por **MIG** (Flyway centralizado); SALE roda `ddl-auto=validate` e
  `open-in-view=false` (RULE-08).
- Seed por tenant (pipeline/ofertas/modelo de atribuição default) é disparado por
  `journey-os.empresa.provisionada`.

## Alternativas consideradas

- **Discriminador `empresa_id` em tabela compartilhada**: maior risco de vazamento por filtro
  esquecido; rejeitada (decisão global do Journey OS).
- **Database-per-tenant**: isolamento máximo, mas custo operacional alto e incompatível com o
  padrão da plataforma. Rejeitada.

## Consequências

**Positivas:** isolamento forte de receita por empresa; consultas sem cláusula de tenant; alinhado
ao restante do monorepo.

**Negativas:** consumir eventos exige estabelecer o contexto de tenant antes de persistir; migrações
schema-aware. Aceito como padrão da plataforma.

## Referências

- `docs/architecture/shared/multi-empresa.md` (decisão global)
- `05-persistence-model.md` · RULE-08 (CLAUDE.md)
- ADR-003 (tenant no envelope do evento)
