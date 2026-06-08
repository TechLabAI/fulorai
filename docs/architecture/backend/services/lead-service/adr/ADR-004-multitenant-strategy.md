# ADR-004 — Multi-Tenancy (schema-per-tenant `emp_<slug>`)

**Status:** accepted

## Contexto

O Journey OS é multi-tenant com estratégia global **schema-per-tenant** (`journeyos_global` +
`emp_<slug>`), decidida em `docs/architecture/shared/multi-empresa.md`. LEAD armazena PII de leads
e dados de qualificação que **não podem** vazar entre empresas. A identidade/contexto de tenant é
de WRKS.

## Decisão

LEAD adere ao **schema-per-tenant**:

- Todos os dados operacionais (lead, perfil, surveys, regras, score, segmentos) vivem no schema
  `emp_<slug>` da empresa. LEAD **nunca** escreve em `journeyos_global` (exclusivo de WRKS/MIG).
- `EmpresaContextHolder` resolve o schema corrente a partir do JWT emitido por WRKS, tanto em
  requisições HTTP quanto no consumo de eventos.
- `application.service` chama `EmpresaContextHolder.require()` antes de qualquer operação de dados.
- Autorização por `AccessDecision` (WRKS) garante que o usuário só opere na sua empresa; cache
  invalidado por `modelo.acesso.alterado`.
- Schema provisionado por **MIG**; serviço com `ddl-auto=validate` + `open-in-view=false`.

## Alternativas consideradas

- **Discriminator column (`empresa_id`) em schema único**: maior risco de vazamento por query mal
  filtrada e mistura de PII de tenants. Rejeitada (contraria a decisão global).
- **Database-per-tenant**: isolamento máximo, mas custo operacional alto e desalinhado da plataforma.
  Rejeitada.

## Consequências

**Positivas:** isolamento forte de PII (LGPD por tenant); backup/retenção/expurgo por empresa;
consistência com WRKS e demais serviços.

**Negativas:** dependência de provisionamento (MIG) e de resolução de contexto correta em todo ponto
de entrada (HTTP e eventos). Mitigado por `EmpresaContextHolder.require()` e testes de cross-empresa guard.

## Referências

- `docs/architecture/shared/multi-empresa.md`
- WRKS `ADR-004-multitenant-strategy.md`
- `05-persistence-model.md`
