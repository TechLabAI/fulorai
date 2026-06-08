## [FE-JRNY-020] Feature flags + a11y (analytics/canvas + condicaoResumo/sortable)

**Status:** 🔲 ABERTA
**GitHub:** [#TBD]

**Status:** INTACT — pos-validacao 2026-06-05
**Maturidade:** 12 — Inicial
**Done/Total:** 0/5 itens (1 PARTIAL)

**Outcome:**
Comportamento das flags: `jrny.journey-analytics` off → omite rota `/jrny/analytics` + item de menu;
`jrny.journey-builder-canvas` off (padrão) → renderiza o **editor estruturado** (canvas reservado
pós-MVP, gap G-c). A11y: `condicaoResumo` legível por leitor de tela (gap G-b); sortable de estágios
com nome acessível; contraste AA; tipo/estado/assist com rótulo textual.

**Context / Problem statement:**
- Fecha os gaps de flag/a11y do Specs-Validate.
- Fonte: SPEC-05 (flags), SPEC-02 (a11y), ADR-005. Cobre gaps G-b, G-c.

**Approach (execution path):**
1) Condicionar rota/menu de analytics à flag; canvas-flag off → editor estruturado.
2) `condicaoResumo` com texto acessível; sortable com `aria` + nome do estágio.
3) Auditoria de contraste AA nos badges/chips.

**Non-goals:** implementar o canvas (pós-MVP).

**Layer(s):** frontend / `libs/jrny/shell-entry` + `feature-routing-engine`/`feature-journey-builder` + `libs/jrny/ui`
**Bounded context:** jrny

**Service execution spec(s):** `SPEC-05` · `SPEC-02` · `adr/ADR-005`

**Architecture alignment:** module-pattern; a11y; tags conforme lib.

**Implementation checklist (by file):**
- 🟡 `libs/jrny/shell-entry/src/lib/jrny.feature-flags.ts` (gating efetivo) (PARTIAL) (arquivo existe com keys/defaults corretos — analytics:enabled, canvas:disabled — mas SEM gating efetivo de rota/menu nem switch canvas→editor estruturado)
- 🔲 a11y em `condition-builder.component.ts` + `stage-list.component.ts` (MISSING) (arquivos inexistentes)
- 🔲 auditoria AA em `libs/jrny/ui` (MISSING) (apenas stub default)

**Tests**
- 🔲 `nx test` libs afetadas PASS (MISSING) · 🔲 `nx lint` PASS (MISSING)

**Milestone:** Wave P7 / UX polish
**Labels:** type:feature · layer:frontend · scope:jrny · priority:P7

**Acceptance criteria:**
- `npx nx test/lint/build` libs afetadas PASS
- Flag analytics off → rota/menu omitidos (EARS #7/#25); canvas off → editor estruturado (EARS #26, gap G-c)
- `condicaoResumo` acessível (gap G-b); sortable a11y

**Dependencies:** FE-JRNY-001, FE-JRNY-012, FE-JRNY-016
**API / Contract impact:** nenhum.
**Risks / Notes:** canvas pós-MVP só por flag + import dinâmico (ADR-005).
