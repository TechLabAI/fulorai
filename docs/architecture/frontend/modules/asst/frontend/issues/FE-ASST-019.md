## [FE-ASST-019] Observability (telemetry events)

**Status:** INTACT -- pos-validacao 2026-06-05
**Maturidade:** 10 -- Inicial
**Done/Total:** 0/3 itens
**GitHub:** [#TBD]

**Outcome:**
Eventos de telemetria via `@journeyos/shared/observability`: timing de composição do Studio,
taxa de aprovação/rejeição, latência do catálogo e conclusão do golden path.

**Context / Problem statement:**
- Success signals de `01-architectural-vision.md §7`. Fonte: `02-architecture-blueprint.md §5`. Depende de FE-ASST-006, FE-ASST-009, FE-ASST-015.
- Bloqueia: —.

**Approach (execution path):**
1) Instrumentar `AssetStudioFacade.compose` (duração + sucesso/degradação).
2) Instrumentar `ApprovalFacade` (aprovado/rejeitado) e `AssetCatalogFacade.list` (latência p95).
3) Evento de conclusão do golden path (criar→...→publicar).

**Non-goals:** dashboards (BE/observability platform).

**Layer(s):** frontend / `libs/asst/data-access` (instrumentação nas facades)
**Bounded context:** asst

**Service execution spec(s):** `01-architectural-vision.md §7` · `02-architecture-blueprint.md §5`

**Architecture alignment:** `@journeyos/shared/observability` (recomendado).

**Implementation checklist (by file):**
- 🔲 [MISSING] instrumentação em `asset-studio.facade.ts`, `approval.facade.ts`, `asset-catalog.facade.ts`

**Tests**
- 🔲 [MISSING] `nx test asst-data-access` PASS · 🔲 [MISSING] `nx lint asst-data-access` PASS

**Milestone:** Wave P8 / Observability
**Labels:** type:feature · layer:frontend · scope:asst · priority:P8

**Acceptance criteria:**
- Eventos emitidos sem PII; nomes consistentes com a convenção do Shell

**Dependencies:** FE-ASST-006, FE-ASST-009, FE-ASST-015
**API / Contract impact:** nenhum.
**Risks / Notes:** não vazar conteúdo de asset nos eventos (LGPD).
