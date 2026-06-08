## [FE-COMM-018] UX polish — loading/empty/error + UI tokens

**Status:** INTACT -- pos-validacao 2026-06-05
**Maturidade:** 10 -- Inicial
**Done/Total:** 0/4 itens
**GitHub:** [#TBD]

**Outcome:**
Estados loading/empty/error consistentes (via `@journeyos/shared/ui-feedback`) em todas as pages;
`StateChipComponent`/`CanalBadgeComponent`/`DeliveryTimelineComponent` estilizados com tokens
(`contracts/design-tokens.md`); SCSS isolado em `libs/comm/styles`.

**Context / Problem statement:**
- Coerência visual e acessibilidade (cor+ícone+rótulo). Fonte: SPEC-07, design-tokens. Depende: P3.

**Approach:**
1) Padronizar empty/loading/error por feature.
2) Aplicar tokens de estado de entrega/template e badges de canal.
3) Garantir contraste/aria (não depender só de cor).

**Non-goals:** redesign; novos componentes de negócio.

**Layer(s):** frontend / `libs/comm/styles` (+ `libs/comm/ui`)
**Bounded context:** comm
**Service execution spec(s):** `SPEC-07`, `contracts/design-tokens.md`
**Architecture alignment:** tag `scope:comm` `type:ui`.

**Implementation checklist (by file):**
- 🔲 [MISSING] `libs/comm/styles/src/lib/_comm-theme.scss`
- 🔲 [MISSING] `libs/comm/ui/src/lib/*` (estilos dos chips/badges/timeline)

**Tests**
- 🔲 [MISSING] `nx test comm-ui` PASS · 🔲 [MISSING] `nx lint comm-styles` PASS

**Milestone:** Wave P7 / UX polish
**Labels:** type:feature · layer:frontend · scope:comm · priority:P7

**Acceptance criteria:**
- Estados loading/empty/error em todas as telas; tokens aplicados; a11y (cor+ícone+rótulo); `nx test/lint/build` PASS

**Dependencies:** FE-COMM-009..015
**API / Contract impact:** nenhum.
**Risks / Notes:** promover `--jos-channel-*` a shared se reutilizado.
