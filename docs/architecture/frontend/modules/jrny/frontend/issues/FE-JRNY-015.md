## [FE-JRNY-015] libs/jrny/ui — componentes locais (badges, chips, funnel)

**Status:** 🔲 ABERTA
**GitHub:** [#TBD]

**Status:** INTACT — pos-validacao 2026-06-05
**Maturidade:** 25 — Inicial
**Done/Total:** 0/6 itens

**Outcome:**
Componentes locais reusáveis em `libs/jrny/ui`: `StageTypeBadgeComponent`, `JourneyStateChipComponent`,
`AssistBadgeComponent`, `FunnelChartComponent` (SVG/CSS). Tipo/estado/assist sempre com **rótulo
textual** (nunca só cor); contraste AA (ADR-005, design-tokens).

**Context / Problem statement:**
- Reuso entre builder/decision-log/analytics; a11y é requisito (ADR-005).
- Fonte: SPEC-02, `contracts/design-tokens.md`.

**Approach (execution path):**
1) `AssistBadge`: USADO→"IA ✓"; IGNORADO/INDISPONIVEL→neutro "roteamento determinístico".
2) `StageTypeBadge`/`JourneyStateChip` com token + ícone + rótulo textual.
3) `FunnelChart` leve (SVG), valores numéricos visíveis.

**Non-goals:** consumo nas features (P3 nas respectivas issues).

**Layer(s):** frontend / `libs/jrny/ui`
**Bounded context:** jrny

**Service execution spec(s):** `SPEC-02` · `contracts/design-tokens.md` · `adr/ADR-005`

**Architecture alignment:** Standalone + OnPush; presentational puro (`input()`/`output()`); tag `type:ui`.

**Implementation checklist (by file):**
- 🔲 `libs/jrny/ui/src/lib/stage-type-badge.component.ts` (MISSING)
- 🔲 `libs/jrny/ui/src/lib/journey-state-chip.component.ts` (MISSING)
- 🔲 `libs/jrny/ui/src/lib/assist-badge.component.ts` (MISSING)
- 🔲 `libs/jrny/ui/src/lib/funnel-chart.component.ts` (MISSING)

**Tests**
- 🔲 `nx test jrny-ui` PASS (MISSING) · 🔲 `nx lint jrny-ui` PASS (MISSING)

**Milestone:** Wave P3 / Feature libs
**Labels:** type:ui · layer:frontend · scope:jrny · priority:P3

**Acceptance criteria:**
- `npx nx test/lint/build jrny-ui` PASS
- Nenhum estado depende só de cor; AA; badge neutro p/ IA-off

**Dependencies:** — (consumido por 010/013/014)
**API / Contract impact:** nenhum.
**Risks / Notes:** sem lib de chart pesada (ADR-005).
