# Architecture Master Plan — Journey OS Frontend

> Rastreia a camada de arquitetura (Layer 1 — Architect) de cada módulo FE, do vision à validação e2e.
> Atualizado automaticamente pelo `/fe-architecture-autopilot` a cada etapa concluída.
> **Não editar à mão durante uma corrida do autopilot** — é um espelho de progresso, nunca a fonte
> da verdade (a verdade são os arquivos em `docs/architecture/frontend/...` e `apps/`/`libs/`).
>
> **Ordem de execução recomendada:** shared libs → WRKS → ASST + INTL → LEAD + COMM → JRNY + SALE.
> **Pipeline por módulo:** Vision → Specs → Backlog → Scaffold → E2E-Validate → Implement (loop).
> **Padrão de paths (autopilot):** `docs/architecture/frontend/modules/<tool>/frontend/...` (vision/specs/backlog),
> `apps/<tool>` + `libs/<tool>/*` + `apps/<tool>-e2e` (scaffold).

---

## Visão Geral — Status por Módulo

| # | Prefixo | Lib Nx | Tipo | Vision | Specs | Specs-Val | Backlog | Scaffold | E2E-Val | Implement |
|---|---------|--------|------|--------|-------|-----------|---------|----------|---------|-----------|
| 1 | **WRKS** | `libs/wrks/` | fundação de domínio | ✅ | ✅ | ✅* | ✅ | ✅ | ✅ | ⬜ |
| 2 | **ASST** | `libs/asst/` | domínio independente | ✅ | ✅ | ✅* | ✅ | ✅ | ✅ | ⬜ |
| 3 | **INTL** | `libs/intl/` | plataforma transversal | ✅ | ✅ | ✅* | ✅ | ✅ | ✅ | ⬜ |
| 4 | **LEAD** | `libs/lead/` | domínio núcleo | ✅ | ✅ | ✅* | ✅ | ✅ | ✅ | ⬜ |
| 5 | **COMM** | `libs/comm/` | domínio núcleo | ✅ | ✅ | ✅* | ✅ | ✅ | ✅ | ⬜ |
| 6 | **JRNY** | `libs/jrny/` | orquestrador | ✅ | ✅ | ✅* | ✅ | ✅ | ✅ | ⬜ |
| 7 | **SALE** | `libs/sale/` | orquestrador | ✅ | ✅ | ✅* | ✅ | ✅ | ✅ | ⬜ |

Legenda: ⬜ pendente · 🔄 em andamento · ✅ concluído · 🚫 bloqueado · N/A não se aplica
> **Specs-Val (EARS gate, C4):** ✅* para todos os módulos de domínio (`*` = OK com gaps não-bloqueantes
> que viram entrada de backlog/hardening). WRKS (fundação) foi o último: por preceder o gate, suas
> SPEC-01..07 receberam **backfill** das seções `## Critérios de aceite (EARS)` em 2026-06-05 (43 cláusulas;
> Gate-1 sintaxe PASS, Gate-2 cobertura 18/25 comportamentais + 18 estruturais INFO, 7 gaps). Roda no
> `/fe-architecture-autopilot <M>` (A2.5) ou avulso via `/fe-architect-specs-validate <M>`.

> **GWY, REG, MIG** são módulos backend-only — sem FE Vision (sem features/e2e de negócio).
>
> **✅ Toolchain de scaffold RESOLVIDO (2026-06-05):** gerador Nx local **`@journeyos/internal:module`**
> em `frontend/libs/internal-nx-plugin/internal` (gerador `module`, idempotente). Invocar de `frontend/`:
> `npx nx g @journeyos/internal:module <mod>`. Compõe `@nx/angular` app+lib + `@nx/playwright` e2e,
> aplica tags `scope:<mod>`+`type:*`, escreve a **entry como library** `libs/<mod>/shell-entry`
> (importPath `@journeyos/<mod>`, ADR-006) + descriptor a partir do `generator-config.yml`, gera
> `apps/<mod>-e2e` (specs dos `.feature`) e o host fino `apps/<mod>`. **WRKS scaffoldado e verde:**
> lint+test+build + e2e --list (18 testes/6 specs). **Shell** (`journey-os-web`) é app Nx e **registra
> o WRKS** via `@journeyos/wrks` em `config/module-descriptors.ts` (build+lint verdes). Ver
> `framework-improvements.md` e `fe-scaffold-toolchain-absent`.
>
> **Nomenclatura:** ✅ vocabulário herdado `tool/@hub/tax-map` migrado para `module/@journeyos/module-pattern`
> (ver `standards/module-pattern.md`). Comandos `fe-architect-*` + artefatos WRKS renomeados (432 substituições,
> 4 arquivos: ADR-001-module-pattern, ADR-003-lazy-module-entry, ADR-004-...-module-registry, SPEC-05-module-contract).

---

## Ledger de gates diferidos

> Gates FE (`feChecks` = nx lint/test/build; `e2eValidate` = nx e2e --list) que **não puderam
> rodar** por toolchain ausente (Nx/`node_modules`). Cada linha traz o comando de recuperação.
> Replay quando houver toolchain:
> `python scripts/be-gates-replay.py --ledger docs/architecture/frontend/plans/architecture-master-plan.md --run --update`.
> O Passo 0.5 (`scripts/preflight.py`) do `/fe-architecture-autopilot` popula esta tabela.

| Data | Escopo | Gate | Comando de recuperação | Status |
|---|---|---|---|---|

_(vazio — toolchain FE resolvido em 2026-06-05; WRKS rodou lint+test+build + e2e --list. Novos
módulos cujo gate não puder rodar registram a linha aqui.)_

---

## Mapa de Dependências

```
libs/shared/ (cross-cutting — pré-condição de todos)
    └── WRKS (auth · empresa-context · RBAC — fundação de domínio)
            ├── ASST (assets · studio · aprovação — domínio independente)
            │       └── COMM (templates · campanhas — consome assets)
            │               └── JRNY (Journey Builder · Routing Engine — orquestrador)
            ├── INTL (AI Copilot · knowledge · analytics — plataforma transversal)
            │       └── SALE (CRM · SDR/closer · LTV — consome analytics)
            └── LEAD (leads · scoring · surveys — núcleo de dados)
                    ├── JRNY (routing decisions baseadas em leads)
                    └── SALE (CRM começa com lead qualificado)
```

---

## Artefatos Globais — Shared Libs (pré-condição de todos os módulos)

### Standards FE (já existentes)

- [x] `docs/architecture/frontend/standards/nx-boundaries.md`
- [x] `docs/architecture/frontend/standards/access-layer-contracts.md`
- [x] `docs/architecture/frontend/standards/bootstrap-flow.md`
- [x] `docs/architecture/frontend/standards/feature-architect-workflow.md`
- [x] `docs/architecture/frontend/standards/asset-driven-ui.md`
- [x] `docs/architecture/frontend/adr/README.md`
- [x] `docs/architecture/shared/blueprint-core.md`

### Toolchain FE

- [x] `frontend/` — Nx workspace inicializado (`nx.json`, `package.json`, `tsconfig.base.json`)
- [x] `frontend/node_modules` — **`npm install` OK (nx v19.8.14, Angular 18)** + `@nx/plugin`, `@nx/playwright`, `@angular-eslint/*`, `eslint-plugin-playwright`
- [x] **Gerador `@journeyos/internal:module`** ✅ — `libs/internal-nx-plugin/internal` (gera app host + libs + entry lib `@journeyos/<mod>` + e2e)

### ADRs globais FE (a criar — transversais)

- [ ] `docs/architecture/frontend/adr/ADR-001-angular-standalone-signals.md`
- [ ] `docs/architecture/frontend/adr/ADR-002-nx-monorepo-boundaries.md`
- [ ] `docs/architecture/frontend/adr/ADR-003-access-layer-contracts.md`
- [ ] `docs/architecture/frontend/adr/ADR-004-lazy-loading-strategy.md`
- [ ] `docs/architecture/frontend/adr/ADR-005-design-tokens-ui-library.md`

### Shared libs — scaffold (antes de qualquer módulo) ✅ Wave-0 (2026-06-05)

> 9 libs criadas com tags `scope:shared` + superfície de API pública (stubs que typecheck clean).
> Wiring real = ciclo de implement de cada lib. `nx lint` ✅ + `tsc --noEmit` ✅ nas 9.

- [x] `libs/shared/auth-session/` — `@journeyos/shared/auth-session` (`AuthSessionService`)
- [x] `libs/shared/empresa-context/` — `@journeyos/shared/empresa-context` (`EmpresaContextService`)
- [x] `libs/shared/access-decision/` — `@journeyos/shared/access-decision` (`AccessDecisionService`, `PermissionService`, `NavigationService`)
- [x] `libs/shared/access-http-base/` — `@journeyos/shared/access-http-base` (`provideHttpBase`)
- [x] `libs/shared/ui-tokens/` — `@journeyos/shared/ui-tokens` (`tokens`)
- [x] `libs/shared/ui-components/` — `@journeyos/shared/ui-components` (`JosCardComponent`)
- [x] `libs/shared/ui-feedback/` — `@journeyos/shared/ui-feedback` (`JosLoading/EmptyState/Error`)
- [x] `libs/shared/error-model/` — `@journeyos/shared/error-model` (`AppError`, `toAppError`)
- [x] `libs/shared/observability/` — `@journeyos/shared/observability` (`ObservabilityService`)
- [ ] `libs/shared/contracts/` — `@journeyos/shared/contracts` (gerado de OpenAPI — quando o BE expor)

### App Shell — pré-condição de routing ✅ Wave-0 (2026-06-05)

> `journey-os-web` promovido a **app Nx de verdade** (era stub não-Nx): `project.json` + targets
> build/serve/test/lint. Componentes do shell (app-shell/sidebar/topbar/ai-panel) preservados e
> com selector `jos-*`. `nx build` ✅ + `nx lint` ✅ + `nx test` ✅. Importa `@journeyos/shared/
> access-http-base` (`provideHttpBase`) — valida o wiring de shared lib num build real.

- [x] `apps/journey-os-web/src/app/app.routes.ts` — usa `AppShellComponent` + `moduleRoutes` (registry)
- [x] `apps/journey-os-web/src/app/app.component.ts` — root mínimo (`<router-outlet/>`, OnPush)
- [x] `apps/journey-os-web/src/app/app.config.ts` — `provideRouter` + `provideHttpBase`
- [x] `apps/journey-os-web/src/app/config/module-descriptors.ts` — registry **populado com WRKS** via `@journeyos/wrks`
- [x] **Registro efetivo dos módulos** ✅ — §4.4 **resolvido** (ADR-006: module-entry como library). `build`+`lint journey-os-web` verdes com `WRKS_MODULE_DESCRIPTOR` registrado.

---

## Módulo 1 — WRKS (Workspace & Identity)

> Tool: `wrks` · Lib Nx: `libs/wrks/` · App lazy: `apps/wrks/` · Issue prefix: `FE-WRKS-NNN` · Scope: `scope:wrks`
> **Fundação de domínio FE** — todos os módulos dependem de auth, empresa-context e RBAC.
> Brief sincronizado do BE (`wrks-service`); permissões alinhadas ao `api-contract.md` (`/api/v1/iam`).

### Etapa A1 — Vision (`/fe-architect-vision WRKS`) ✅

- [x] `docs/architecture/frontend/modules/wrks/_brief.md` _(sync do BE)_
- [x] `docs/architecture/frontend/modules/wrks/frontend/01-architectural-vision.md`
- [x] `docs/architecture/frontend/modules/wrks/frontend/02-architecture-blueprint.md`
- [x] `docs/architecture/frontend/modules/wrks/frontend/03-domain-framing-frontend.md`
- [x] `docs/architecture/frontend/modules/wrks/frontend/04-frontend-architecture-direction.md`
- [x] `docs/architecture/frontend/modules/wrks/frontend/05-state-and-data-flow.md`
- [x] `docs/architecture/frontend/modules/wrks/frontend/06-risks-gaps-assumptions.md`
- [x] `docs/architecture/frontend/modules/wrks/frontend/adr/README.md`
- [x] `docs/architecture/frontend/modules/wrks/frontend/adr/ADR-001-module-pattern.md`
- [x] `docs/architecture/frontend/modules/wrks/frontend/adr/ADR-002-signals-first-state.md`
- [x] `docs/architecture/frontend/modules/wrks/frontend/adr/ADR-003-lazy-module-entry.md`
- [x] `docs/architecture/frontend/modules/wrks/frontend/adr/ADR-004-shell-integration-via-module-registry.md`
- [x] `docs/architecture/frontend/modules/wrks/frontend/adr/ADR-005-multi-empresa-context.md`

### Etapa A2 — Specs (`/fe-architect-specs WRKS`) ✅

- [x] `docs/architecture/frontend/modules/wrks/frontend/frontend-spec/SPEC-01-route-map.md`
- [x] `docs/architecture/frontend/modules/wrks/frontend/frontend-spec/SPEC-02-component-hierarchy.md`
- [x] `docs/architecture/frontend/modules/wrks/frontend/frontend-spec/SPEC-03-view-models.md`
- [x] `docs/architecture/frontend/modules/wrks/frontend/frontend-spec/SPEC-04-data-access.md`
- [x] `docs/architecture/frontend/modules/wrks/frontend/frontend-spec/SPEC-05-module-contract.md`
- [x] `docs/architecture/frontend/modules/wrks/frontend/frontend-spec/SPEC-06-shell-integration.md`
- [x] `docs/architecture/frontend/modules/wrks/frontend/frontend-spec/SPEC-07-error-handling.md`
- [x] `docs/architecture/frontend/modules/wrks/frontend/frontend-spec/SPEC-08-e2e-scenarios.md`
- [x] `docs/architecture/frontend/modules/wrks/frontend/frontend-spec/generator-config.yml`
- [x] `docs/architecture/frontend/modules/wrks/frontend/contracts/backend-api-cross-link.md`
- [x] `docs/architecture/frontend/modules/wrks/frontend/contracts/design-tokens.md`
- [x] `docs/architecture/frontend/modules/wrks/frontend/e2e/login-and-empresa-select.feature`
- [x] `docs/architecture/frontend/modules/wrks/frontend/e2e/user-administration.feature`
- [x] `docs/architecture/frontend/modules/wrks/frontend/e2e/empresa-switch-isolation.feature`
- [x] `docs/architecture/frontend/modules/wrks/frontend/e2e/entitlement-denied.feature`
- [x] `docs/architecture/frontend/modules/wrks/frontend/e2e/deep-link.feature`

### Etapa A2.5 — Specs-Validate (EARS gate, C4) ✅* (OK com gaps) — backfill 2026-06-05

> WRKS precedeu o gate EARS, então suas SPEC-01..07 não tinham critérios de aceite EARS (eram
> Gherkin-first). Esta etapa **backfillou** as seções `## Critérios de aceite (EARS)` derivadas do
> conteúdo das specs + os 5 `.feature` existentes (sem inventar critério). Read-only sobre código.

- [x] **Gate 1 (sintaxe EARS):** PASS — `be-validate-ears.py --strict` → 0 issues em SPEC-01..07.
  **43 cláusulas** (16 ubíq · 14 event `WHEN` · 1 state `WHILE` · 5 optional `WHERE` · 7 unwanted `IF..THEN`).
  Detecção confirmada via cláusula malformada (validador acusa `WHEN` sem vírgula).
- [x] **Gate 2 (cobertura EARS→Gherkin):** 13 cenários / 5 features, ~0 órfãos. 18 cláusulas estruturais
  (INFO, não-e2e) + 25 comportamentais → **18 cobertas, 7 gaps não-bloqueantes**.
- [x] **7 gaps → hardening/P9 do implement** (não bloqueiam): list-load-failure retry (SPEC-04),
  `wrks.rbac-viewer` flag-off (SPEC-05), reset de breadcrumb/re-deriva nav na troca de empresa +
  mudança de `modelo_acesso_versao` (SPEC-06), banner de login-fail + redirect em `iam.refresh-invalido`
  + toast de troca-de-empresa negada (SPEC-07).

### Etapa A3 — Backlog (`/fe-architect-backlog WRKS`) ✅

- [x] `docs/architecture/frontend/modules/wrks/frontend/issues/FE-WRKS-001.md` .. `FE-WRKS-020.md` (20 funcionais)
- [x] `docs/architecture/frontend/modules/wrks/frontend/issues/INT-FE-WRKS-001.md` .. `INT-FE-WRKS-006.md` (6 integração)
- [x] `docs/architecture/frontend/modules/wrks/frontend/issues/issues_map.md`
- [x] `docs/architecture/frontend/modules/wrks/frontend/plans/plan-FE-WRKS.md`

### Etapa A4 — Scaffold (`npx nx g @journeyos/internal:module wrks`) ✅

- [x] `libs/wrks/shell-entry/` — **entry como library** (importPath `@journeyos/wrks`, ADR-006): contract, module, routes, permission-map, feature-flags, bootstrap, nav.config, descriptor + barrel (`MODULE_*` + permissões reais)
- [x] `apps/wrks/` — host fino: `app.routes` carrega `@journeyos/wrks` (alvo build/serve + base do e2e)
- [x] `libs/wrks/access/` · `data-access/` · `integration/` · `navigation/` · `ui/` · `styles/`
- [x] `libs/wrks/feature-login/` · `feature-empresa-select/` · `feature-workspace/` · `feature-users/` · `feature-rbac-viewer/`
- [x] Tags Nx corretas em todos (`scope:wrks` + `type:{app,feature,data-access,domain,ui}`)
- [x] **Gates pós-scaffold VERDES** — `nx lint` ✅ · `nx test` ✅ · `nx build` ✅
- [x] `apps/wrks-e2e/` — Playwright project + 5 spec stubs (de cada `.feature`) + `nx lint wrks-e2e` ✅
- [x] **Registro no Shell** ✅ — `journey-os-web` importa `WRKS_MODULE_DESCRIPTOR` de `@journeyos/wrks`; `build`+`lint journey-os-web` verdes (§4.4 resolvido).

### Etapa A5 — E2E-Validate (gate inline) ✅ OK (pending)

- [x] `apps/wrks-e2e/` descoberto e compilando — `npx nx e2e wrks-e2e --list` → 18 testes / 6 specs (chromium/firefox/webkit), 0 erro de compilação. Execução real dos fluxos = `/fe-implement` P9.

### Etapa B — Implement (`/fe-validator FE-WRKS-001` → `/fe-autopilot FE-WRKS-001`)

- [ ] Baseline — `/fe-validator FE-WRKS-001` BASELINE
- [ ] `plan-FE-WRKS.md` com P1..P9 definidas _(já criado no A3)_
- [ ] P1 — Tool entry + registro no Shell (FE-WRKS-001..003)
- [ ] P2 — Data-access (FE-WRKS-004..008)
- [ ] P3 — Features (FE-WRKS-009..015)
- [ ] P4 — Integrações Access Layer/Shell (INT-FE-WRKS-001..006)
- [ ] P5 — Guards (FE-WRKS-016)
- [ ] P6 — Navegação/breadcrumbs (FE-WRKS-017)
- [ ] P7 — UX polish (FE-WRKS-018)
- [ ] P8 — Observability (FE-WRKS-019)
- [ ] P9 — e2e Playwright + hardening (FE-WRKS-020)
- [ ] `npx nx lint wrks-*` PASS · `npx nx test wrks-*` PASS · `npx nx build wrks-*` PASS

---

## Módulo 2 — ASST (Asset Hub)

> Tool: `asst` · Lib Nx: `libs/asst/` · Issue prefix: `FE-ASST-NNN` · Scope: `scope:asst`
> **Dependência FE:** WRKS (auth). Independente de LEAD, COMM, JRNY. ADR-005: `asset-studio-ai-composition`
> (composição assistida + degradação graciosa). ⚠️ **Correção de escopo:** o placeholder pré-brief
> `chunked-upload-strategy`/`feature-asset-upload` foi **deferido para pós-MVP** — o brief BE autoritativo
> coloca upload/hospedagem de binário fora do MVP (binários referenciados por URL).

### Etapa A1 — Vision (`/fe-architect-vision ASST`) ✅

- [x] `docs/architecture/frontend/modules/asst/_brief.md` _(derivado do BE `asst-service`)_
- [x] `docs/architecture/frontend/modules/asst/frontend/01-architectural-vision.md` .. `06-risks-gaps-assumptions.md`
- [x] `docs/architecture/frontend/modules/asst/frontend/adr/README.md` + `ADR-001..005` (ADR-005: `asset-studio-ai-composition`)
- [x] Features previstas: `feature-asset-library` · `feature-asset-detail` · `feature-asset-studio` · `feature-approval-workflow`

### Etapa A2 — Specs (`/fe-architect-specs ASST`) ✅

- [x] `frontend-spec/SPEC-01..08` + `generator-config.yml` (4 features, 8 perms `asst.*`, 2 flags; YAML válido)
- [x] `contracts/backend-api-cross-link.md` (+ `design-tokens.md`) + 6 `e2e/*.feature`
  (asset-lifecycle, asset-studio-degradation, approval-workflow, empresa-isolation, entitlement-denied, deep-link)

### Etapa A2.5 — Specs-Validate (EARS gate) ✅* (com gaps) — backfill 2026-06-05

> ASST passou pelo autopilot **antes** do A2.5 existir; SPEC-01..07 não tinham critérios EARS (validador
> passava vacuamente, 0 cláusulas). Backfill via `/fe-architecture-autopilot ASST --until=specs-validate`.

- [x] **Gate-1 (sintaxe EARS) PASS** — `be-validate-ears.py --strict` → 0 issues nas 7 SPECs. **37 cláusulas** adicionadas em seções `## Critérios de aceite (EARS)` (SPEC-01:7, 02:3, 03:3, 04:10, 05:4, 06:3, 07:7). Distribuição: 8 ubíq / 17 event / 3 state / 1 optional / 8 unwanted. Convenção clause-wrapped-in-backticks (sem prefixo dentro das crases, sem backtick interno → sem skip silencioso).
- [x] **Gate-2 (cobertura EARS→Gherkin)** — 20 scenarios / 6 features, **0 órfãos**. 25 cláusulas comportamentais cobertas, 9 arquiteturais (INFO, não-e2e), **3 gaps não-bloqueantes → backlog**: G1 redirect-raiz `/asst` (A-01.2), G2 validação-422-inline (A-07.3), G3 reload-em-409-transicao-invalida (A-07.5).
- Derivação read-only do conteúdo existente das SPECs + `.feature` (sem comportamento novo). Scaffold (A4) e e2e-validate (A5) já estavam ✅ — não reexecutados.

### Etapa A3 — Backlog (`/fe-architect-backlog ASST`) ✅

- [x] `issues/FE-ASST-001..020.md` (20 funcionais) + `INT-FE-ASST-001..006.md` (6 integração) + `issues/issues_map.md` + `plans/plan-FE-ASST.md` (P1..P9)

### Etapa A4 — Scaffold (`npx nx g @journeyos/internal:module asst`) ✅

- [x] `apps/asst/` + `apps/asst-e2e/` (6 specs) + `libs/asst/{shell-entry,access,data-access,integration,navigation,ui,styles,feature-asset-library,feature-asset-detail,feature-asset-studio,feature-approval-workflow}`
- [x] **Gates pós-scaffold VERDES** — `nx lint`+`nx test` (13 projetos) ✅ · `nx build asst` (250kB) ✅
- [ ] Registro no Shell (`config/module-descriptors.ts`) — deferido para FE-ASST-003 (P1 implement), igual ao WRKS

### Etapa A5 — E2E-Validate ✅ OK (pending)

- [x] `apps/asst-e2e/` descoberto e compilando — `nx e2e asst-e2e --list` → 21 testes / 7 specs (6 dos `.feature` + example; chromium/firefox/webkit), 0 erro de compilação. Execução real dos fluxos = `/fe-implement` P9.

### Etapa B — Implement ⬜ → `/fe-validator FE-ASST-001`

---

## Módulo 3 — INTL (Intelligence & Platform)

> Tool: `intl` · Lib Nx: `libs/intl/` · Issue prefix: `FE-INTL-NNN` · Scope: `scope:intl`
> **Dependência FE:** WRKS. Provê AI Copilot e analytics. ADR-005: `ai-copilot-streaming`.

### Etapa A1 — Vision ✅

- [x] `_brief.md` (sync do BE `intl-service`) + `frontend/01..06` + `adr/README` + `ADR-001..005`
  (ADR-005: render request/response no MVP; streaming SSE diferido — sem endpoint no BE)

### Etapa A2 — Specs ✅ · A2.5 — Specs-Validate ✅ (com gaps) · A3 — Backlog ✅ · A4 — Scaffold ✅ · A5 — E2E-Validate ✅ OK (pending) · B — Implement ⬜

- [x] **A2.5 backfill (specs-val):** EARS adicionado a SPEC-01..07 (38 cláusulas, convertidas do conteúdo
  existente). Gate 1 PASS (`be-validate-ears.py --strict`, 0 issues; detecção confirmada). Gate 2: 7 cenários,
  0 órfãos; ~23 comportamentais cobertas + 9 arquiteturais (INFO). **6 gaps não-bloqueantes → implement:**
  empresaGuard sem-empresa (SPEC-01), copilot cancel-flow (SPEC-04), analytics flag-off (SPEC-05),
  copilot-streaming flag-on/pós-MVP (SPEC-05), transport-ERRO retry (SPEC-07), 404 empty-state (SPEC-07).

- [x] `npx nx e2e intl-e2e --list` → **24 testes / 8 specs** (7 dos `.feature` + example), 0 erro de
  compilação (chromium/firefox/webkit). Execução real dos fluxos = `/fe-implement` P9.

- [x] `npx nx g @journeyos/internal:module intl`: `apps/intl` + 10 libs (`shell-entry`, `data-access`,
  `access`, `integration`, `navigation`, `ui`, `styles`, `feature-copilot/-knowledge/-analytics`) + `apps/intl-e2e`
  (7 spec stubs dos `.feature`). **Gates VERDES:** `nx lint intl` ✅ · `nx run-many lint+test scope:intl` ✅ (12 proj) · `nx build intl` ✅.
  > Registro do `INTL_MODULE_DESCRIPTOR` no Shell = tarefa do implement P1 (FE-INTL-003), como no WRKS.

- [x] `frontend-spec/SPEC-01..08` + `generator-config.yml` + `contracts/{backend-api-cross-link,design-tokens}.md`
  + 7 `e2e/*.feature` (copilot-grounded/degraded, knowledge-curation, analytics-read, entitlement-denied,
  empresa-switch-isolation, deep-link)
- [x] Backlog: 20 `FE-INTL-001..020` + 6 `INT-FE-INTL-001..006` (26 issues) + `issues_map.md` + `plans/plan-FE-INTL.md` (P1..P9)
- [ ] Features (recorte FE do MVP): `feature-copilot` (chat + citações + degradação),
  `feature-knowledge` (CRUD/indexar/arquivar nós), `feature-analytics` (funil + uso do copiloto, read-only)
  > Nota: `feature-event-platform` e `feature-integrations` ficam **fora do MVP FE** (governança Elastic
  > e Integration Hub não têm UI de domínio no MVP — ver `_brief.md` §5 e `01` §5).

---

## Módulo 4 — LEAD (Lead Intelligence & Qualification)

> Tool: `lead` · Lib Nx: `libs/lead/` · Issue prefix: `FE-LEAD-NNN` · Scope: `scope:lead`
> **Dependência FE:** WRKS. Consumido por JRNY e SALE. ADR-005: `maturity-score-visualization`.

### Etapa A1 — Vision ✅

- [x] `_brief.md` (FE, espelho BE `lead-service`) + `frontend/01..06` + `adr/README` + `ADR-001..005` (13 artefatos). ADR-005=`maturity-score-visualization` (radar 6D explicável; nunca o número agregado sozinho; degradação graciosa do assist IA como badge neutro "score determinístico"; a11y obrigatória)

### Etapa A2 — Specs ✅ · A2.5 — Specs-Validate ✅* (OK com gaps) · A3 — Backlog ✅ · A4 — Scaffold ✅ · A5 — E2E-Validate ✅ OK (pending) · B — Implement ⬜

- [x] **Scaffold:** `npx nx g @journeyos/internal:module lead` → `apps/lead` + 12 libs (`shell-entry`/`data-access`/`access`/`integration`/`navigation`/`ui`/`styles` + 6 `feature-*`) + `apps/lead-e2e` (9 specs dos `.feature` + example). **Gates VERDES:** `nx lint` (15 proj) ✅ · `nx test` (14 proj) ✅ · `nx build lead` (250.54 kB initial) ✅. Shell-registration (`LEAD_MODULE_DESCRIPTOR`) deferido p/ implement P1 (FE-LEAD-003).
- [x] **E2E-Validate:** `nx e2e lead-e2e --list` → **30 testes / 10 specs** (9 dos `.feature` + example; chromium/firefox/webkit), 0 erro de compilação. Pipeline A1→A5 do LEAD COMPLETO. Próxima ação manual: `/fe-validator FE-LEAD-001`.

- [x] **Backlog:** 22 `FE-LEAD-001..022` + 6 `INT-FE-LEAD-001..006` (28 issues, P1..P9) + `issues_map.md` + `plans/plan-FE-LEAD.md`. Os 9 gaps do specs-validate mapeados em issues (G1→019/022, G2/G3→020, G4→012/020, G5→004/011/022, G6→008/019, G7→019, G8→002/022, G9→017/INT-002/022). Caminho crítico 001→002→INT-001→004→008→011→012(ADR-005)→019→020→022.

- [x] **Specs-validate (EARS gate):** Gate-1 sintaxe **PASS** (`be-validate-ears.py` → 0 issues; 32 cláusulas: 9 ubíq/11 event/3 state/2 opt/7 unwanted). Gate-2 cobertura: 17 cenários/9 features, **0 órfãos**; 11 cláusulas estruturais (sem Gherkin), 12/21 comportamentais cobertas, **9 gaps não-bloqueantes** → backlog: G1 lead-not-found, G2/G3 feature-flag-disabled, G4 radar-a11y, G5 profile-refetch, G6 list-error, G7 retry-policy, G8 redirect-root, G9 empresa-guard.

- [x] `frontend-spec/SPEC-01..08` + `generator-config.yml` (6 features lead-list/lead-detail/maturity-score/segmentation/survey/qualification-rules; 4 resources; 17 perms `lead.*`; 2 flags `lead.maturity-score`/`lead.qualification-rules`) + `contracts/{backend-api-cross-link,design-tokens}.md` + 9 `e2e/*.feature`. EARS em SPEC-01..07 pré-validado (0 issues); YAML válido. Assist IA = BE-side, refletido no badge `assistIa` (FE nunca chama IA).
- [ ] Features (recorte FE): `feature-lead-list`, `feature-lead-detail`, `feature-maturity-score`, `feature-segmentation`, `feature-survey`, `feature-qualification-rules`

---

## Módulo 5 — COMM (Communication Hub)

> Tool: `comm` · Lib Nx: `libs/comm/` · Issue prefix: `FE-COMM-NNN` · Scope: `scope:comm`
> **Dependência FE:** WRKS + ASST (templates usam assets, **só via API BE** — sem import `scope:asst`). Consumido por JRNY/SALE/LEAD via API.
> ⚠️ **Correção de escopo (brief autoritativo):** ADR-005 pré-brief era `rich-text-template-editor`, mas editor visual/WYSIWYG rico está **fora do MVP** (MVP = editor texto/HTML com placeholders `{{variavel}}`). ADR-005 real = **`delivery-status-tracking`** (rastreio do ciclo de vida por polling com backoff — sem endpoint de streaming no BE). `feature-campaign` (campaign manager avançado) **deferido pós-MVP**; `feature-history` absorvido em `feature-messages`.

### Etapa A1 — Vision (`/fe-architect-vision COMM`) ✅

- [x] `_brief.md` (FE, derivado do BE `comm-service`) + `frontend/01..06` + `adr/README` + `ADR-001..005` (ADR-005: `delivery-status-tracking`)
- [x] Features previstas: `feature-template-catalog` (catálogo+CRUD+editor+estado) · `feature-template-studio` (IA, degradação graciosa) · `feature-routing-rules` · `feature-messages` (disparo 1:1 + timeline de entrega via polling) · `feature-channel-config`

### Etapa A2 — Specs ✅

- [x] `frontend-spec/SPEC-01..08` + `generator-config.yml` (5 features; 5 data_access; 13 perms `comm.*`; 2 flags `comm.template-studio`/`comm.delivery-tracking`) + `contracts/{backend-api-cross-link,design-tokens}.md` + 9 `e2e/*.feature`. Critérios EARS em SPEC-01..07. Endpoints espelham `comm-service` (`/templates`,`/messages`,`/routing-rules`,`/channels`; webhooks server-to-server, sem UI).

### Etapa A2.5 — Specs-Validate (EARS gate) ✅ (com gaps)

- [x] Gate-1 sintaxe **PASS** (`be-validate-ears.py` → 0 issues; 43 cláusulas: 14 ubíq/12 event/7 state/10 unwanted). Critérios reformatados para *clause-wrapped-in-backticks* (convenção BE) — validação real, sem skip silencioso.
- [x] Gate-2 cobertura: 26 cenários/9 features, **0 órfãos**; comportamentais cobertas, **2 gaps não-bloqueantes** → backlog: C-05.4 (delivery-tracking flag off = refresh manual), C-06.4 (parar polling no destroy/navigate-away).

### Etapa A3 — Backlog (`/fe-architect-backlog COMM`) ✅

- [x] 20 `FE-COMM-001..020` + 6 `INT-FE-COMM-001..006` (26 issues) + `issues_map.md` + `plans/plan-FE-COMM.md` (P1..P9). Caminho crítico 001→002→INT-001→007→013→014→018→020. Gaps A2.5 mapeados (C-05.4, C-06.4).

### Etapa A4 — Scaffold (`npx nx g @journeyos/internal:module comm`) ✅

- [x] `apps/comm` + `apps/comm-e2e` (9 specs) + 13 libs (`shell-entry`/`access`/`data-access`/`integration`/`navigation`/`ui`/`styles` + 5 features). **Gates VERDES:** `nx lint comm` · `run-many lint+test scope:comm` (9 proj/17 tasks) · `nx build comm` (250.54 kB) · `lint comm-e2e`. Shell-registration (`COMM_MODULE_DESCRIPTOR`) deferido p/ FE-COMM-003 (P1).

### Etapa A5 — E2E-Validate ✅ OK (pending)

- [x] `nx e2e comm-e2e --list` → **30 testes / 10 specs** (9 dos `.feature` + example; chromium/firefox/webkit), 0 erro de compilação. Execução real dos fluxos = `/fe-implement` P9.

### Etapa B — Implement ⬜ → `/fe-validator FE-COMM-001`

- [ ] Recorte FE = 5 features. FE só conhece `canal` (nunca provedor); config de canal expõe só `credencialRef` mascarada.

---

## Módulo 6 — JRNY (Journey & Routing)

> Tool: `jrny` · Lib Nx: `libs/jrny/` · Issue prefix: `FE-JRNY-NNN` · Scope: `scope:jrny`
> **Dependência FE:** WRKS + ASST + COMM + LEAD + INTL (soft). Módulo mais complexo. ADR-005: `canvas-builder-rendering`.

### Etapa A1 — Vision ✅

- [x] `_brief.md` (FE, espelho BE `jrny-service`) + `frontend/01..06` + `adr/README` + `ADR-001..005` (13 artefatos). ADR-005=`canvas-builder-rendering` (editor estruturado de estágios ordenados; **sem** lib de canvas no MVP; flag `journey-builder-canvas` off reservada p/ pós-MVP; imutabilidade do publicado na UI). 6 features. **Decide e sinaliza** (UI não executa canal/venda, sem botão "rotear agora"). IA=assist BE-side refletido (badge `assistIa`), FE nunca chama IA.

### Etapa A2 — Specs ✅

- [x] `frontend-spec/SPEC-01..08` + `generator-config.yml` (6 features, 4 resources, 11 perms `jrny.*`, 2 flags; YAML válido, bate com schema do `@journeyos/internal:module`) + `contracts/{backend-api-cross-link,design-tokens}.md` + 7 `e2e/*.feature`.
- [x] Features: `feature-journey-list`, `feature-journey-builder`, `feature-stage-editor`, `feature-routing-engine`, `feature-decision-log`, `feature-journey-analytics`.
- [x] Gaps registrados (não-bloqueantes → backlog A3): **G1** endpoint de analytics/funil (proposto, atrás da flag `jrny.journey-analytics`); **G2** label do `assetRefId` (ASST cross-link); **G3** `temRegrasSaindo` (client-side); **G4** reorder em lote (otimista+rollback). `assistIa` ternário (USADO/IGNORADO/INDISPONIVEL) — badge neutro p/ IGNORADO|INDISPONIVEL.

### Etapa A2.5 — Specs-Validate ✅ (com gaps)

- [x] Gate 1 (sintaxe EARS) **PASS** — `be-validate-ears.py` 0 issues em SPEC-01..07 (39 cláusulas: 22 ubiq/9 event/4 state/1 optional/3 unwanted; `--strict` limpo). Detecção confirmada via teste de cláusula malformada (validador pega clause-wrapped-in-backticks).
- [x] Gate 2 (cobertura EARS→Gherkin) — 25 cenários/7 features, **0 órfãos**; ~25 cláusulas comportamentais cobertas + 9 arquiteturais (INFO, não-e2e). **5 gaps não-bloqueantes → backlog A3:** empresaGuard "sem empresa ativa", `condicaoResumo` render, canvas-flag-enabled (pós-MVP), reorder-failure rollback, read-failure retry.

### Etapa A3 — Backlog ✅

- [x] `issues/FE-JRNY-001..022.md` (22 funcionais) + `INT-FE-JRNY-001..006.md` (6 integração) + `issues/issues_map.md` + `plans/plan-FE-JRNY.md` (P1..P9). Caminho crítico 001→002→INT-001→004→005→010→016→019→020→022 (builder + sortable a11y + rollback = núcleo). Gaps A2.5 (G-a..G-e) + cross-link (G1-G4) mapeados a issues. Paths ADR-006 (`libs/jrny/shell-entry`).

### Etapa A4 — Scaffold ✅

- [x] `npx nx g @journeyos/internal:module jrny` → `apps/jrny` + `apps/jrny-e2e` (7 specs) + 13 libs (`shell-entry`/`data-access`/`access`/`integration`/`navigation`/`ui`/`styles` + 6 features). **Gates VERDES:** `nx lint` ✅ (15 proj) · `nx test` ✅ (13 libs Jest) · `nx build jrny` ✅ (250.54 kB, lazy `jrny-module` chunk). Shell-registration (`JRNY_MODULE_DESCRIPTOR`) deferido p/ implement P1 (FE-JRNY-003), igual aos demais.

### Etapa A5 — E2E-Validate ✅ OK (pending)

- [x] `nx e2e jrny-e2e --list` → **24 testes / 8 specs** (7 dos `.feature` + example; chromium/firefox/webkit), 0 erro de compilação. Pipeline A1..A5 do JRNY **COMPLETO**. Execução real dos fluxos = `/fe-implement` P9.

### Etapa B — Implement ⬜ → `/fe-validator FE-JRNY-001`

- [ ] Recorte FE = 6 features (orquestrador). **Decide e sinaliza** (UI não executa canal/venda, sem botão "rotear agora"); decision log explicável (badge `assistIa` ternário, IA-off neutro); editor estruturado de estágios (sem canvas — ADR-005).

---

## Módulo 7 — SALE (Sales & Revenue)

> Tool: `sale` · Lib Nx: `libs/sale/` · Issue prefix: `FE-SALE-NNN` · Scope: `scope:sale`
> **Dependência FE:** WRKS + LEAD + INTL (soft). ADR-005: `kanban-pipeline-rendering`.

### Etapa A1 — Vision (`/fe-architect-vision SALE`) ✅

- [x] `_brief.md` (FE, espelho do BE `sale-service`) + `frontend/01..06` + `adr/README` + `ADR-001..005` (13 artefatos). ADR-005=`kanban-pipeline-rendering` (Angular CDK DragDrop + optimistic move/rollback; espelha `409 sale.oportunidade.ja-fechada`)
- [x] **SEM TechLab AI no MVP** — atribuição de receita + LTV são determinísticos/explicáveis (FE nunca chama IA; sem badge de IA, contraste com LEAD/ASST/COMM)
- [x] Deps FE: WRKS (auth/empresa/RBAC) + LEAD (soft) + INTL (soft) — cross-módulo só via API BE (sem import `scope:lead`/`scope:intl`)

### Etapa A2 — Specs (`/fe-architect-specs SALE`) ✅

- [x] `frontend-spec/SPEC-01..08` + `generator-config.yml` (YAML válido, shape JRNY/schema `@journeyos/internal:module`: 6 features, 5 data_access, 15 perms `sale.*`, 2 flags) + `contracts/{backend-api-cross-link,design-tokens}.md` + 8 `e2e/*.feature` (33 scenarios, pt-BR). Critérios EARS clause-wrapped-in-backticks em SPEC-01..07; `be-validate-ears.py` 0 erros (Gate1 pré-validado). Endpoints espelham `sale-service` api-contract (/oportunidades,/ofertas,/compras,/atribuicao,/ltv)
- [x] Features (recorte FE): `feature-pipeline` (Kanban `/sale/pipeline`), `feature-opportunity` (`/sale/opportunities/:id`), `feature-offer` (`/sale/offers`), `feature-purchase` (`/sale/purchases` — read + estornar/cancelar; `POST /compras` server-to-server), `feature-attribution` (`/sale/attribution`), `feature-revenue-dashboard` (`/sale/dashboard`, flag-gated)
- [x] Flags: `sale.revenue-dashboard` (enabled) · `sale.attribution-multitouch` (disabled — default last-touch). Gaps não-bloqueantes → backlog: G1 endpoint funil de receita, G2 título do card, G3 nome do responsável, G4 multi-touch atrás de flag

### Etapa A2.5 — Specs-Validate (`/fe-architect-specs-validate SALE`) ✅*

- [x] Gate1 EARS sintaxe: `be-validate-ears.py` 0 issues em cada SPEC-01..07 (23 cláusulas SHALL clause-wrapped-in-backticks). Gate2 cobertura: 29 scenarios em 8 `e2e/*.feature` cobrem as cláusulas (traceability em SPEC-08, 0 órfãos). Gaps de contrato **G1-G4** (não-bloqueantes) → backlog A3.

### Etapa A3 — Backlog (`/fe-architect-backlog SALE`) ✅

- [x] 23 `FE-SALE-001..023` + 6 `INT-FE-SALE-001..006` (29 issues) + `issues_map.md` + `plans/plan-FE-SALE.md` (P1..P9). Centerpiece **FE-SALE-010** (Kanban CDK DragDrop, optimistic move + rollback no `409 sale.oportunidade.ja-fechada`, ADR-005). Caminho crítico `001→002→INT-001→005→010→020→021→022→023`. Compra read+estornar/cancelar (sem create — server-to-server). Gaps G1-G4 mapeados em issues (008/015, 005/016, 001/017). Paths ADR-006 (`libs/sale/shell-entry`)

### Etapa A4 — Scaffold (`npx nx g @journeyos/internal:module sale`) ✅

- [x] `apps/sale` + `apps/sale-e2e` (9 specs: 8 dos `.feature` + example) + 13 libs (`shell-entry` + `access`/`data-access`/`integration`/`navigation`/`ui`/`styles` + `feature-pipeline`/`-opportunity`/`-offer`/`-purchase`/`-attribution`/`-revenue-dashboard`)
- [x] **Gates pós-scaffold VERDES** — `nx run-many -t lint -p tag:scope:sale` (15 proj) ✅ · `nx run-many -t test -p tag:scope:sale` (14 proj) ✅ · `nx build sale` (250.54 kB) ✅
- [ ] Registro no Shell (`SALE_MODULE_DESCRIPTOR` em `config/module-descriptors.ts`) — deferido para FE-SALE-003/004 (P1 implement), igual COMM/INTL/ASST

### Etapa A5 — E2E-Validate (gate inline) ✅ OK (pending)

- [x] `apps/sale-e2e/` descoberto e compilando — `npx nx e2e sale-e2e --list` → **27 testes / 9 specs** (8 dos `.feature` + example; chromium/firefox/webkit), 0 erro de compilação. Correspondência 1:1 `.feature`→spec confirmada. Execução real dos fluxos = `/fe-implement` P9. **Pipeline A1..A5 do SALE COMPLETO.**

### Etapa B — Implement ⬜ → `/fe-validator FE-SALE-001`

---

## Referência de pipeline FE

| Comando | Etapa | Pré-requisito |
|---------|-------|---------------|
| `/fe-architect-vision <M>` | A1 | Brief do módulo + waves anteriores |
| `/fe-architect-specs <M>` | A2 | Vision completa (01..06 + ≥4 ADRs) |
| `/fe-architect-backlog <M>` | A3 | Specs + `generator-config.yml` + ≥1 `.feature` |
| `/fe-architect-scaffold <M>` | A4 | `generator-config.yml` + issues + plan + **gerador `@hub/internal:tool`** |
| `/fe-architecture-autopilot <M>` | A1→A5 | encadeia tudo; PARA na e2e-validate |
| `/fe-validator <M>` | B1 BASELINE | Scaffold executável |
| `/fe-autopilot <M>` | A→B | Detecta estado e encadeia |

### Checklist por wave

```
Wave 0 — Fundação        [✅ docs WRKS] [🚫 scaffold WRKS — toolchain]
Wave 1 — ASST + INTL     [🔄 ASST: A1..A5 ✅ (pronto p/ implement FE-ASST-001) · INTL em paralelo]
Wave 2 — LEAD + COMM     [✅ A1..A5 ambos (prontos p/ implement FE-LEAD-001 / FE-COMM-001)]
Wave 3 — JRNY + SALE     [🔄 JRNY: A1..A5 ✅ (pronto p/ implement FE-JRNY-001) · SALE em andamento]
```

---

## Log cronológico

- 2026-06-05T00:43:58Z -- WRKS -- vision -- OK -- _brief.md (sync BE) + docs 01..06 + adr README + ADR-001..005 (13 artefatos)
- 2026-06-05T00:43:58Z -- WRKS -- specs -- OK -- SPEC-01..08 + generator-config.yml + contracts (cross-link, tokens) + 5 e2e .feature
- 2026-06-05T00:43:58Z -- WRKS -- backlog -- OK -- 20 FE-WRKS + 6 INT-FE-WRKS (26 issues) + issues_map + plan-FE-WRKS (P1..P9)
- 2026-06-05T00:43:58Z -- WRKS -- scaffold -- bloqueado -- toolchain FE ausente (sem node_modules + sem plugin @hub/internal:tool); A4/A5 deferidos
- 2026-06-05T00:43:58Z -- WRKS -- scaffold -- bloqueado (atualizado) -- npm install OK (nx 19.8.14 funcional); resta so o gerador @hub/internal:tool
- 2026-06-05T00:43:58Z -- (estrutura) -- master-plan -- reestruturado ao padrao do backend (status table + Etapa A1..A5/B por modulo + log); fe-vision-master-plan.md aposentado e removido (conteudo absorvido aqui)
- 2026-06-05T01:30:20Z -- (toolchain) -- plugin -- OK -- construido @journeyos/internal:module (libs/internal-nx-plugin); blocker de scaffold resolvido; instalado @nx/plugin + @angular-eslint/*
- 2026-06-05T01:30:20Z -- WRKS -- scaffold -- parcial (verde) -- npx nx g @journeyos/internal:module wrks: apps/wrks + 11 libs; lint+test+build PASS (12 proj). Pendente: shell-registration + apps/wrks-e2e (gerador v2)
- 2026-06-05T01:30:20Z -- (nomenclatura) -- rename -- OK -- frente B: tool/@hub/tax-map -> module/@journeyos/module-pattern em 10 comandos fe-* + 21 artefatos WRKS (432 subst) + 4 arquivos renomeados; standards/module-pattern.md canonico
- 2026-06-05T01:50:28Z -- WRKS -- scaffold -- OK -- frente A: gerador v2 (idempotente + e2e + descriptor); re-run wrks: + apps/wrks-e2e (5 specs) + wrks.descriptor.ts; build wrks + lint wrks-e2e PASS. Instalado @nx/playwright, @playwright/test, eslint-plugin-playwright
- 2026-06-05T01:50:28Z -- WRKS -- e2e-validate -- OK (pending) -- nx e2e wrks-e2e --list: 18 testes/6 specs, 0 erro compilacao. Pipeline A1..A5 do WRKS COMPLETO (unico deferido: mutacao do Shell stub)
- 2026-06-05T02:07:29Z -- (wave-0) -- shared-libs -- OK -- 9 libs @journeyos/shared/* (tags scope:shared + API stub); nx lint + tsc --noEmit verdes
- 2026-06-05T02:07:29Z -- (wave-0) -- shell -- OK -- journey-os-web promovido a app Nx (build/lint/test verdes); registry module-descriptors; provideHttpBase wired
- 2026-06-05T02:20:00Z -- (decisao) -- ADR-006 -- OK -- module-entry como library (@journeyos/<mod>); gerador v3; WRKS migrado (apps/wrks/.../wrks-module -> libs/wrks/shell-entry); §4.4 resolvido
- 2026-06-05T02:20:00Z -- (wave-0) -- shell-registration -- OK -- journey-os-web registra WRKS via @journeyos/wrks (WRKS_MODULE_DESCRIPTOR); build+lint verdes. WAVE-0 COMPLETA
- 2026-06-05T05:47:14Z -- ASST -- preflight -- OK -- toolchain Nx presente; gates feChecks + e2eValidate runnable (A4/A5 rodam de verdade, sem deferimento)
- 2026-06-05T05:47:14Z -- ASST -- vision -- OK -- _brief.md (derivado do BE asst-service) + docs 01..06 + adr README + ADR-001..005 (13 artefatos). ADR-005=asset-studio-ai-composition (substitui placeholder chunked-upload; upload binário deferido pós-MVP, brief BE = referência por URL). Features: asset-library/-detail/-studio/-approval-workflow
- 2026-06-05T05:48:11Z -- INTL -- preflight -- OK -- toolchain Nx presente; gates feChecks + e2eValidate runnable (A4/A5 rodam de verdade, sem deferimento)
- 2026-06-05T05:48:11Z -- INTL -- vision -- OK -- _brief.md (sync do BE intl-service) + docs 01..06 + adr README + ADR-001..005 (13 artefatos). ADR-005=ai-copilot-streaming: render request/response no MVP (estado "pensando" otimista + cancelamento); streaming SSE diferido (sem endpoint no BE, citações só ao final). Recorte FE = 3 features: feature-copilot, feature-knowledge, feature-analytics (event-platform/integrations fora do MVP FE)
- 2026-06-05T05:48:11Z -- INTL -- specs -- OK -- SPEC-01..08 + generator-config.yml (3 features: copilot/knowledge/analytics; 3 recursos data-access; 5 perms intl.*) + contracts (backend-api-cross-link, design-tokens) + 7 e2e .feature. Endpoints espelham intl-service api-contract (/copilot,/knowledge,/analytics)
- 2026-06-05T05:54:39Z -- ASST -- specs -- OK -- SPEC-01..08 + generator-config.yml (YAML válido; 4 features asset-library/-detail/-studio/-approval-workflow, 8 perms asst.*, 2 flags asst.asset-studio/approval-workflow, 6 e2e) + contracts (backend-api-cross-link, design-tokens) + 6 e2e .feature (Gherkin pt-BR). Config bate com os campos lidos pelo @journeyos/internal:module
- 2026-06-05T05:55:00Z -- INTL -- backlog -- OK -- 20 FE-INTL-001..020 + 6 INT-FE-INTL-001..006 (26 issues) + issues_map.md + plans/plan-FE-INTL.md (P1..P9). Caminho crítico contract→routes→http-base→copilot api→facade→conversation→badges/citations→polish→hardening→e2e. Top risco R2 (render degradado como fato) concentrado em FE-INTL-011 + e2e copilot-degraded
- 2026-06-05T06:05:00Z -- ASST -- backlog -- OK -- 20 FE-ASST + 6 INT-FE-ASST = 26 issues (P1..P9) + issues_map + plan-FE-ASST. Caminho crítico 001→002→INT-001→004→005→007→011→012→015→018→020; ramo Studio 006→013. Paths ADR-006 (libs/asst/shell-entry)
- 2026-06-05T06:06:00Z -- INTL -- scaffold -- OK -- npx nx g @journeyos/internal:module intl: apps/intl + 10 libs (shell-entry/data-access/access/integration/navigation/ui/styles/feature-copilot/-knowledge/-analytics) + apps/intl-e2e (7 spec stubs). Gates VERDES: nx lint intl + run-many lint+test scope:intl (12 proj) + nx build intl. Shell-registration (INTL_MODULE_DESCRIPTOR) deferido p/ implement P1 (FE-INTL-003)
- 2026-06-05T06:08:00Z -- INTL -- e2e-validate -- OK (pending) -- nx e2e intl-e2e --list: 24 testes/8 specs (7 dos .feature + example), 0 erro de compilacao (chromium/firefox/webkit). Pipeline A1..A5 do INTL COMPLETO. Proxima acao manual: /fe-validator FE-INTL-001
- 2026-06-05T06:15:00Z -- ASST -- scaffold -- OK -- npx nx g @journeyos/internal:module asst: apps/asst + apps/asst-e2e (6 specs) + 11 libs. Gates VERDES: lint+test 13 projetos + build asst (250kB). Shell-registration deferido para FE-ASST-003 (P1)
- 2026-06-05T06:20:00Z -- ASST -- e2e-validate -- OK (pending) -- nx e2e asst-e2e --list: 21 testes/7 specs (6 dos .feature + example), 0 erro compilação. Pipeline A1..A5 do ASST COMPLETO. Próxima ação manual: /fe-validator FE-ASST-001
- 2026-06-05T09:42:26Z -- LEAD -- preflight -- OK -- toolchain Nx presente; gates feChecks + e2eValidate runnable (A4/A5 rodam de verdade, sem deferimento). BE lead-service docs completos (brief sync source pronto)
- 2026-06-05T09:42:26Z -- LEAD -- vision -- inicio -- fresh start; A1 via /fe-architect-vision LEAD
- 2026-06-05T09:42:26Z -- LEAD -- vision -- OK -- _brief.md (FE) + frontend/01..06 + adr/README + ADR-001..005 (13 artefatos). ADR-005=maturity-score-visualization. 6 features (lead-list/lead-detail/maturity-score/segmentation/survey/qualification-rules). IA = assist BE-side refletido (badge assistIa), FE nunca chama IA
- 2026-06-05T09:42:26Z -- LEAD -- specs -- OK -- SPEC-01..08 + generator-config.yml (6 features, 4 resources, 17 perms, 2 flags) + contracts (backend-api-cross-link, design-tokens) + 9 e2e .feature. EARS SPEC-01..07 = 0 issues (be-validate-ears); YAML valido. Endpoints espelham lead-service api-contract (/leads,/surveys,/qualification,/segments)
- 2026-06-05T09:42:26Z -- LEAD -- specs-validate -- OK (com gaps) -- Gate1 EARS sintaxe PASS (0 issues, 32 clausulas). Gate2 cobertura: 17 cenarios/9 features, 0 orfaos; 12/21 comportamentais cobertas, 9 gaps nao-bloqueantes (lead-not-found, 2x feature-flag-disabled, radar-a11y, profile-refetch, list-error, retry-policy, redirect-root, empresa-guard) -> backlog A3. Primeiro modulo FE com Specs-Val executado
- 2026-06-05T09:42:26Z -- LEAD -- backlog -- OK -- 22 FE-LEAD + 6 INT-FE-LEAD = 28 issues (P1..P9) + issues_map + plan-FE-LEAD. 9 gaps do specs-validate mapeados em issues. Caminho critico 001->002->INT-001->004->008->011->012->019->020->022; no de maior valor/risco = FE-LEAD-012 (ScoreBreakdown/Radar, ADR-005)
- 2026-06-05T09:42:26Z -- LEAD -- scaffold -- OK -- npx nx g @journeyos/internal:module lead: apps/lead + 12 libs (6 features + shell-entry/data-access/access/integration/navigation/ui/styles) + apps/lead-e2e (9 specs). Gates VERDES: lint 15 proj + test 14 proj + build lead (250.54 kB). Shell-registration deferido p/ FE-LEAD-003 (P1)
- 2026-06-05T09:42:26Z -- LEAD -- e2e-validate -- OK (pending) -- nx e2e lead-e2e --list: 30 testes/10 specs (9 dos .feature + example; chromium/firefox/webkit), 0 erro compilacao. Pipeline A1..A5 do LEAD COMPLETO. Proxima acao manual: /fe-validator FE-LEAD-001
- 2026-06-05T09:43:14Z -- COMM -- preflight -- OK -- toolchain Nx presente; gates feChecks + e2eValidate runnable (A4/A5 rodam de verdade, sem deferimento). Dependencias FE: WRKS + ASST (templates usam assets)
- 2026-06-05T09:43:14Z -- COMM -- vision -- inicio -- fresh start; A1 via /fe-architect-vision COMM
- 2026-06-05T09:43:14Z -- COMM -- vision -- OK -- _brief.md (FE, derivado do BE comm-service) + frontend/01..06 + adr/README + ADR-001..005 (13 artefatos). ADR-005=delivery-status-tracking (polling com backoff; corrige placeholder pre-brief rich-text-template-editor -> editor rich-text fora do MVP). 5 features: feature-template-catalog/-template-studio/-routing-rules/-messages/-channel-config. IA delegada ao BE (Template Studio degrada gracioso); FE so conhece canal (nunca provedor)
- 2026-06-05T10:30:00Z -- JRNY -- preflight -- OK -- toolchain Nx presente; gates feChecks + e2eValidate runnable (A4/A5 rodam de verdade, sem deferimento). BE jrny-service docs completos (brief sync source: 01..06 + api-contract /journeys+/routing + ADR-005 routing-engine-model)
- 2026-06-05T10:30:00Z -- JRNY -- vision -- inicio -- fresh start; A1 via /fe-architect-vision JRNY. Modulo mais complexo (orquestrador: Journey Builder + Routing Engine + decision log). 6 features previstas; ADR-005=canvas-builder-rendering
- 2026-06-05T09:43:14Z -- COMM -- specs -- OK -- SPEC-01..08 + generator-config.yml (YAML valido: 5 features, 5 data_access, 13 perms comm.*, 2 flags) + contracts (backend-api-cross-link, design-tokens) + 9 e2e .feature. Criterios EARS embutidos em SPEC-01..07. Endpoints espelham comm-service api-contract (/templates,/messages,/routing-rules,/channels; webhooks = server-to-server, sem UI)
- 2026-06-05T09:43:14Z -- COMM -- specs-validate -- OK (com gaps) -- Gate1 EARS sintaxe PASS (be-validate-ears.py, 0 issues em SPEC-01..07; 43 clausulas: 14 ubiq/12 event/7 state/10 unwanted). Reformatei criterios para clause-wrapped-in-backticks (convencao BE): prefixo **C-X** quebrava o anchor ^WHEN/WHILE e backticks internos causavam skip silencioso -> agora todas as clausulas sao validadas de fato. Gate2 cobertura: 26 cenarios/9 features, 0 orfaos; comportamentais cobertas, 2 gaps nao-bloqueantes -> A3 backlog: C-05.4 (delivery-tracking flag off=refresh manual), C-06.4 (stop polling no destroy/navigate-away)
- 2026-06-05T11:05:00Z -- JRNY -- specs -- OK -- SPEC-01..08 + generator-config.yml (YAML valido: 6 features, 4 data_access, 11 perms jrny.*, 2 flags journey-analytics/journey-builder-canvas) + contracts (backend-api-cross-link com gaps G1-G4, design-tokens) + 7 e2e .feature. Criterios EARS clause-wrapped-in-backticks em SPEC-01..07. Endpoints espelham jrny-service api-contract (/journeys CRUD+publicar/arquivar/nova-versao, /routing/rules, /routing/leads/{id}/journey+decisions). assistIa ternario USADO/IGNORADO/INDISPONIVEL; condicao grammar (data-model §5) no ConditionBuilder estruturado
- 2026-06-05T11:20:00Z -- JRNY -- specs-validate -- OK (com gaps) -- Gate1 EARS sintaxe PASS (be-validate-ears.py, 0 issues em SPEC-01..07; 39 clausulas: 22 ubiq/9 event/4 state/1 optional/3 unwanted; --strict limpo). Deteccao CONFIRMADA via teste de clausula malformada (validador pega clause-wrapped-in-backticks; sem prefixo C-X nem backtick interno). Gate2 cobertura: 25 cenarios/7 features, 0 orfaos; ~25 comportamentais cobertas + 9 arquiteturais(INFO nao-e2e), 5 gaps nao-bloqueantes -> A3 backlog: empresaGuard sem-empresa, condicaoResumo render, canvas-flag-enabled (pos-MVP), reorder-failure rollback, read-failure retry
- 2026-06-05T11:45:00Z -- JRNY -- backlog -- OK -- 22 FE-JRNY-001..022 + 6 INT-FE-JRNY-001..006 (28 issues) + issues_map.md + plan-FE-JRNY.md (P1..P9). Caminho critico 001->002->INT-001->004->005->010->016->019->020->022 (builder + sortable a11y + rollback = nucleo de esforco/risco). Gaps A2.5 (G-a..G-e) + cross-link (G1-G4) mapeados a issues. Paths ADR-006 (libs/jrny/shell-entry). Ramos paralelos pos-P2: lista/stage-editor/regras/decision-log/analytics
- 2026-06-05T12:00:00Z -- JRNY -- scaffold -- OK -- npx nx g @journeyos/internal:module jrny: apps/jrny + apps/jrny-e2e (7 specs dos .feature) + 13 libs (shell-entry/data-access/access/integration/navigation/ui/styles + feature-journey-list/-journey-builder/-stage-editor/-routing-engine/-decision-log/-journey-analytics). Gates VERDES: nx lint 15 proj + nx test 13 libs (Jest) + nx build jrny (250.54 kB, lazy jrny-module chunk). Shell-registration (JRNY_MODULE_DESCRIPTOR) deferido p/ FE-JRNY-003 (P1)
- 2026-06-05T12:05:00Z -- JRNY -- e2e-validate -- OK (pending) -- nx e2e jrny-e2e --list: 24 testes/8 specs (7 dos .feature + example; chromium/firefox/webkit), 0 erro compilacao. Pipeline A1..A5 do JRNY COMPLETO. Proxima acao manual: /fe-validator FE-JRNY-001
- 2026-06-05T07:01:24Z -- SALE -- preflight -- OK -- toolchain Nx presente; gates feChecks + e2eValidate runnable (A4/A5 rodam de verdade, sem deferimento). BE sale-service docs completos (brief sync source: 01..06 + api-contract /oportunidades+/ofertas+/compras+/atribuicao+/ltv + ADR-005 revenue-attribution-model)
- 2026-06-05T07:01:24Z -- SALE -- vision -- inicio -- fresh start; A1 via /fe-architect-vision SALE. Orquestrador (CRM/pipeline + ofertas + compras/receita + atribuicao + LTV). 6 features previstas; ADR-005=kanban-pipeline-rendering
- 2026-06-05T07:01:24Z -- SALE -- vision -- OK -- _brief.md (FE, espelho do BE sale-service) + frontend/01..06 + adr/README + ADR-001..005 (13 artefatos). ADR-005=kanban-pipeline-rendering (Angular CDK DragDrop + optimistic move/rollback; espelha 409 sale.oportunidade.ja-fechada). 6 features: pipeline/opportunity/offer/purchase/attribution/revenue-dashboard. SEM TechLab AI no MVP (atribuicao/LTV deterministicos/explicaveis; FE nunca chama IA). Deps FE: WRKS + LEAD(soft) + INTL(soft), cross-modulo so via API BE. feature-purchase = read + estornar/cancelar (ingestao POST /compras server-to-server)
- 2026-06-05T09:43:14Z -- COMM -- backlog -- OK -- 20 FE-COMM-001..020 + 6 INT-FE-COMM-001..006 (26 issues) + issues_map + plan-FE-COMM (P1..P9). Caminho critico 001->002->INT-001->007->013->014->018->020; ramos paralelos templates(004->009->010->005->011)/roteamento(006->012)/canais(008->015). No de maior valor/risco = FE-COMM-007/014 (disparo+polling de entrega, ADR-005). Gaps A2.5 mapeados: C-05.4 (014/020), C-06.4 (007/014/INT-005/020)
- 2026-06-05T09:43:14Z -- COMM -- scaffold -- OK -- npx nx g @journeyos/internal:module comm: apps/comm + apps/comm-e2e (9 specs dos .feature + example) + 13 libs (shell-entry/access/data-access/integration/navigation/ui/styles + 5 features template-catalog/-template-studio/-routing-rules/-messages/-channel-config). Gates VERDES: lint comm + run-many lint+test scope:comm (9 proj/17 tasks) + build comm (250.54 kB) + lint comm-e2e. Shell-registration (COMM_MODULE_DESCRIPTOR) deferido p/ implement P1 (FE-COMM-003)
- 2026-06-05T09:43:14Z -- COMM -- e2e-validate -- OK (pending) -- nx e2e comm-e2e --list: 30 testes/10 specs (9 dos .feature + example; chromium/firefox/webkit), 0 erro de compilacao. Pipeline A1..A5 do COMM COMPLETO. Proxima acao manual: /fe-validator FE-COMM-001
- 2026-06-05T07:01:24Z -- SALE -- specs -- OK -- SPEC-01..08 + generator-config.yml (YAML valido shape JRNY/schema: 6 features, 5 data_access, 15 perms sale.*, 2 flags revenue-dashboard/attribution-multitouch) + contracts (backend-api-cross-link com gaps G1-G4, design-tokens) + 8 e2e .feature (33 scenarios pt-BR). Criterios EARS clause-wrapped-in-backticks em SPEC-01..07; be-validate-ears.py 0 erros (Gate1 pre-validado). Endpoints espelham sale-service api-contract (/oportunidades,/ofertas,/compras,/atribuicao,/ltv). feature-purchase sem create no FE (POST /compras server-to-server)
- 2026-06-05T07:01:24Z -- SALE -- specs-validate -- OK -- Gate1 EARS sintaxe PASS (be-validate-ears.py, 0 issues em cada SPEC-01..07; 23 clausulas SHALL clause-wrapped-in-backticks). Gate2 cobertura: 29 scenarios/8 e2e .feature cobrem as clausulas (traceability em SPEC-08, 0 orfaos). Gaps de contrato G1-G4 (nao-bloqueantes, do A2) -> backlog A3
- 2026-06-05T10:27:42Z -- WRKS -- specs-validate -- OK (com gaps) -- BACKFILL (--until=specs-validate): WRKS precedeu o gate EARS, suas SPEC-01..07 nao tinham criterios EARS (Gherkin-first). Adicionadas secoes "## Criterios de aceite (EARS)" derivadas das specs + 5 .feature existentes (sem inventar). Gate1 sintaxe PASS (be-validate-ears.py --strict, 0 issues; 43 clausulas: 16 ubiq/14 event/1 state/5 optional/7 unwanted; deteccao confirmada via clausula malformada). Gate2 cobertura: 13 cenarios/5 features, ~0 orfaos; 18 clausulas estruturais (INFO non-e2e) + 25 comportamentais (18 cobertas, 7 gaps nao-bloqueantes -> hardening/P9: list-load-retry SPEC-04, rbac-viewer flag-off SPEC-05, breadcrumb/nav re-derive + modelo_acesso_versao SPEC-06, login-fail banner + refresh-invalido redirect + switch-denied toast SPEC-07). WRKS = ultimo modulo de dominio a fechar Specs-Val; todos os 7 agora ✅*. Proxima acao manual: /fe-validator FE-WRKS-001
- 2026-06-05T10:30:44Z -- ASST -- specs-validate -- OK (com gaps) -- BACKFILL (--until=specs-validate): ASST precedeu o gate EARS, SPEC-01..07 sem criterios EARS (validador passava vacuamente, 0 clausulas). Adicionadas secoes "## Criterios de aceite (EARS)" derivadas das specs + 6 .feature existentes (read-only, sem comportamento novo). Gate1 sintaxe PASS (be-validate-ears.py --strict, 0 issues; 37 clausulas: 8 ubiq/17 event/3 state/1 optional/8 unwanted). Gate2 cobertura: 20 scenarios/6 features, 0 orfaos; 25 comportamentais cobertas + 9 arquiteturais (INFO non-e2e), 3 gaps nao-bloqueantes -> backlog: G1 redirect-raiz /asst (A-01.2), G2 validacao-422-inline (A-07.3), G3 reload-em-409-transicao-invalida (A-07.5). Scaffold (A4)+e2e-validate (A5) ja ✅, nao reexecutados. --until=specs-validate atingido. Proxima acao manual: /fe-validator FE-ASST-001
- 2026-06-05T07:01:24Z -- SALE -- backlog -- OK -- 23 FE-SALE-001..023 + 6 INT-FE-SALE-001..006 (29 issues) + issues_map + plan-FE-SALE (P1..P9). Centerpiece FE-SALE-010 (Kanban CDK DragDrop, optimistic move + rollback no 409 sale.oportunidade.ja-fechada, ADR-005). Caminho critico 001->002->INT-001->005->010->020->021->022->023. Compra read+estornar/cancelar (sem create, server-to-server; sale.compra.registrar fora do mapa FE). Gaps G1-G4 viraram backlog (008/015, 005/016, 001/017). Paths ADR-006 (libs/sale/shell-entry)
- 2026-06-05T12:30:00Z -- INTL -- specs-validate -- OK (com gaps) -- BACKFILL (specs-val): INTL precedeu o gate EARS, SPEC-01..07 sem criterios EARS (0 clausulas, validador passava vacuamente). Adicionadas secoes "## Criterios de aceite (EARS)" derivadas do conteudo existente das specs + 7 .feature (read-only, sem inventar requisitos). Gate1 sintaxe PASS (be-validate-ears.py --strict, 0 issues; 38 clausulas; deteccao confirmada via clausula malformada injetada). Gate2 cobertura: 7 cenarios .feature, 0 orfaos; ~23 comportamentais cobertas + 9 arquiteturais (INFO non-e2e), 6 gaps nao-bloqueantes -> implement: empresaGuard sem-empresa (SPEC-01), copilot cancel-flow abort+restore (SPEC-04), analytics flag-off omite rota/menu (SPEC-05), copilot-streaming flag-on (SPEC-05, pos-MVP), transport-ERRO bubble+retry (SPEC-07), 404 empty-state+voltar (SPEC-07). Backlog(A3)+scaffold(A4)+e2e-validate(A5) ja ✅, nao reexecutados. Todos os 7 modulos de dominio agora Specs-Val ✅*. Proxima acao manual: /fe-validator FE-INTL-001
- 2026-06-05T07:01:24Z -- SALE -- scaffold -- OK -- npx nx g @journeyos/internal:module sale: apps/sale + apps/sale-e2e (9 specs: 8 dos .feature + example) + 13 libs (shell-entry/access/data-access/integration/navigation/ui/styles + 6 features pipeline/opportunity/offer/purchase/attribution/revenue-dashboard). Gates VERDES: nx lint run-many scope:sale (15 proj) + nx test scope:sale (14 proj) + nx build sale (250.54 kB). Shell-registration (SALE_MODULE_DESCRIPTOR) deferido p/ implement P1 (FE-SALE-003/004)
- 2026-06-05T07:01:24Z -- SALE -- e2e-validate -- OK (pending) -- nx e2e sale-e2e --list: 27 testes/9 specs (8 dos .feature + example; chromium/firefox/webkit), 0 erro de compilacao. Correspondencia 1:1 .feature->spec. Pipeline A1..A5 do SALE COMPLETO. SALE = ultimo modulo de dominio (wave 3). Proxima acao manual: /fe-validator FE-SALE-001

## Referências

- `docs/architecture/backend/plans/architecture-master-plan.md` — master plan do backend (espelho do padrão)
- `docs/architecture/shared/blueprint-core.md` · `frontend/standards/nx-boundaries.md` · `access-layer-contracts.md`
