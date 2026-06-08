## [FE-LEAD-012] ui: ScoreBreakdown + ScoreRadar (6D) + DimensionBar (ADR-005)

**Status (validação):** INTACT — pós-validação 2026-06-05
**Maturidade:** 10 — Inicial
**Done/Total:** 0/5 itens

**Status:** 🔲 ABERTA
**GitHub:** [#TBD]

**Outcome:**
Componentes de visualização do Maturity Score em `libs/lead/ui`: `ScoreBreakdownComponent`
(sempre 6 dimensões + `versaoRegra` + badge `assistIa`), `ScoreRadarComponent` (SVG/CSS + **tabela
alternativa a11y**), `DimensionBarComponent`. Núcleo do ADR-005.

**Context / Problem statement:**
- A decisão crítica do módulo: score explicável, nunca caixa-preta; degradação graciosa do assist IA.
- Cobre **G4** (radar-a11y). Fonte: ADR-005, SPEC-02. Consumido por FE-LEAD-011 e FE-LEAD-013.

**Approach (execution path):**
1) `ScoreBreakdownComponent` recebe `MaturityScoreVM`; renderiza as 6 dimensões + versão + badge.
2) `ScoreRadarComponent` (SVG/CSS leve) + `<table>` alternativa para leitores de tela.
3) `DimensionBarComponent` por dimensão; faixa com rótulo textual (não só cor).

**Non-goals:** dashboard de distribuição (FE-LEAD-013); chamada de IA (BE-side — nunca no FE).

**Layer(s):** frontend / `libs/lead/ui`
**Bounded context:** lead

**Service execution spec(s):** `adr/ADR-005-maturity-score-visualization.md` · `SPEC-02`

**Architecture alignment:** Standalone + OnPush; candidato a promoção shared; tag `scope:lead` `type:ui`.

**Implementation checklist (by file):**
- 🔲 `libs/lead/ui/src/lib/score-breakdown.component.ts` — _MISSING_
- 🔲 `libs/lead/ui/src/lib/score-radar.component.ts` — _MISSING_
- 🔲 `libs/lead/ui/src/lib/dimension-bar.component.ts` — _MISSING_

**Tests**
- 🔲 `nx test lead-ui` PASS — _MISSING_ · 🔲 `nx lint lead-ui` PASS — _MISSING_

**Milestone:** Wave P3 / Feature libs
**Labels:** type:feature · layer:frontend · scope:lead · priority:P3

**Acceptance criteria:**
- `npx nx test/lint/build lead-ui` PASS
- Score sempre exibe as 6 dimensões + versão + badge (SPEC-02 EARS); radar com tabela a11y (G4)
- Faixa exibida com rótulo textual além da cor (SPEC-03 EARS)

**Dependencies:** — (consome `MaturityScoreVM`)
**API / Contract impact:** nenhum (componente puro).
**Risks / Notes:** evitar lib de chart pesada (orçamento de bundle — R3); import dinâmico se necessário.
