# ADR-004 — Multi-tenancy: schema-per-tenant + WRKS como orquestrador de provisionamento

**Status:** accepted (alinhado ao ADR-001 global em `shared/multi-empresa.md`)

## Contexto

O Journey OS adotou globalmente **schema-per-tenant** (`shared/multi-empresa.md`, ADR-001 global):
schema `journeyos_global` compartilhado + `emp_<slug>` por empresa. Falta definir **o papel de
WRKS** nesse modelo, já que ele é dono do catálogo de empresas e do IAM.

## Decisão

- WRKS é dono do subconjunto **IAM** de `journeyos_global` (usuario, papel, permissao, usuario_empresa, empresa, business_unit, team, modelo_acesso_versao, evento_auditoria) — **único serviço de negócio com escrita** nesse schema (além de MIG/seed).
- WRKS **orquestra o provisionamento** do tenant: ao criar uma `empresa`, registra a linha e **dispara MIG** para criar o schema `emp_<slug>` e rodar as migrations; confirma via evento `empresa.provisionada`.
- WRKS **não acessa** dados operacionais (`emp_<slug>.*`).
- Propagação de contexto: claim `empresa_id` no JWT (sync) / header `empresaId` (async); `EmpresaContextHolder.require()` em todo application service (RULE-07).

## Alternativas consideradas

- **Cada serviço provisiona seu próprio schema**: provisionamento descoordenado, sem dono do ciclo de vida do tenant. Rejeitada — WRKS é o dono natural do workspace.
- **tenant-id-column / database-per-tenant**: avaliadas e rejeitadas no ADR-001 global (risco de leak / custo de N pools). Mantida a decisão global.

## Consequências

**Positivas:** ciclo de vida do tenant centralizado e auditável; isolamento forte (backup/LGPD por empresa); um único ponto de escrita no IAM global reduz risco de drift.

**Negativas:** WRKS no caminho de criação de empresa (acopla a MIG) — mitigado por saga/idempotência (R-6); nova empresa = novo conjunto de migrations (operação explícita).

## Referências

- `docs/architecture/shared/multi-empresa.md` (ADR-001 global)
- `docs/architecture/shared/modelo-dados/{global-schema,empresa}.md`
- `05-persistence-model.md`
