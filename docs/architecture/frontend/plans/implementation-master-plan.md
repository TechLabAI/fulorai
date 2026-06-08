# Implementation Master Plan — Journey OS Frontend

> Rastreia a camada de **execução (Layer 2 — Implement)** de cada módulo FE, do **baseline** à
> **maturidade ≥ 80** com checklist 100% DONE. É o documento-irmão do
> [`architecture-master-plan.md`](./architecture-master-plan.md): aquele cobre o Architect
> (vision→specs→specs-validate→backlog→scaffold→e2e-validate); **este cobre o ciclo
> validator-driven** que evolui o módulo (Angular + Nx).
>
> Atualizado a cada transição de etapa pelo `/fe-autopilot FE-<MODULO>-NNN` (e pelos
> sub-commands `/fe-validator`, `/fe-planner`, `/fe-implement` quando rodados isoladamente).
> **Não é fonte da verdade** — é um espelho de progresso. A verdade são:
> as **issue specs** (`docs/architecture/frontend/modules/<mod>/frontend/issues/<ISSUE>.md`) com
> seu checklist + bloco de status, os `plan-FE-<MODULO>.md` (estratégia por prioridade)
> e o código em `frontend/apps/` + `frontend/libs/`.
>
> **Pré-condição:** Layer 1 (Architect) 100% concluída para os 7 módulos de domínio (A1→A5) —
> ver `architecture-master-plan.md`. ✅ Todos scaffoldados + e2e-validate em 2026-06-05.

---

## Ciclo de execução (Layer 2) — recordatório

```
F1 BASELINE  (fe-validator Modo 1)  → consolida estado real do checklist, calcula score
F2 DECISÃO   (fe-validator Modo 2)  → PLANNER | IMPLEMENTADOR | VALIDAR | ENCERRAR
F3 PLANNER   (fe-planner)           → plan-FE-<MODULO>.md (prioridades P1..P9) — já existem
F4 IMPLEMENT (fe-implement <ISSUE> fase-N) → UMA fase/prioridade por vez (escreve código Angular)
F5 VALIDAÇÃO (fe-validator Modo 3)  → gates nx lint/test/build + boundaries + e2e + delta na issue
        └── loop F2→F5 até checklist 100% DONE e score ≥ 80
```

Orquestrador: `/fe-autopilot FE-<MODULO>-NNN` (Pipeline B — resolver issue) encadeia F1→F5 com
detecção de estado. As issues de um módulo são agrupadas em **prioridades P1..P9** pelo
`plan-FE-<MODULO>.md`; a ordem do plano define a sequência de execução.

---

## ✅ Toolchain de validação — DISPONÍVEL (sem bloqueador transversal)

> **Contraste com o backend:** o Implementation Master Plan do BE difere os gates B5 por ausência de
> toolchain Gradle (`[[gradle-toolchain-absent]]`). **No FE não há esse bloqueio.** O toolchain Nx
> foi **resolvido em 2026-06-05** (`[[fe-scaffold-toolchain-absent]]` — RESOLVIDO):
> `npm install` OK (nx 19.8.14, Angular 18), gerador `@journeyos/internal:module` funcional, e os
> gates já rodaram de verdade no Layer 1 (WRKS: lint+test+build + `nx e2e --list`; demais idem).

Consequências para a Layer 2:

- **F4 (fe-implement) roda Nx** — escreve código e o desenvolvedor/validator pode rodar
  `nx lint|test|build <project>` localmente a cada fase.
- **F5 (fe-validator Modo 3) executa os gates de verdade:**
  `nx lint <project>` (boundaries Nx + ESLint custom), `nx test <project>` (Jest unit),
  `nx build <project>` (TS compila), `nx affected -t lint,test` (fases multi-project) e,
  no P9, `nx e2e <mod>-e2e` (Playwright — execução real dos fluxos, não só `--list`).
- **Nenhuma prioridade fica com gate diferido** — cada P fecha com gate verde antes de
  `CODE-DONE → DONE`. (Se em algum ambiente futuro o Nx faltar, registrar no ledger abaixo.)

### Ledger de gates de implementação diferidos

> Append-only. Vazio por padrão — toolchain FE disponível. Só recebe linha se, em algum
> ambiente, `nx lint/test/build/e2e` não puder rodar (registrar o comando de recuperação).

| Data | Módulo | Prioridade | Gate diferido | Comando de recuperação | Status |
|---|---|---|---|---|---|
| — | — | — | — | _(vazio — gates FE runnable)_ | — |

---

## Ordem de execução por ondas (respeita dependências)

> Dependências extraídas do `architecture-master-plan.md` (Mapa de Dependências) e da
> [[project-fe-vision-plan]]. Toda dependência cross-módulo no FE é **soft, só via API BE**
> (sem import `scope:<outro-mod>` — `[[fe-module-framework]]`/`nx-boundaries.md`). O acoplamento
> real é a **Access Layer** (`@journeyos/shared/*`) e o **Shell registry**, ambos provisionados
> por WRKS na Onda 1.

| Onda | Módulos | Pré-requisito de início | Paralelizável? |
|------|---------|--------------------------|----------------|
| **0 — Fundação compartilhada** | shared libs (`@journeyos/shared/*`) + Shell (`journey-os-web`) | nenhum (fundação) | ✅ **já concluída na Layer 1 (Wave-0, 2026-06-05)** |
| **1 — Fundação de domínio** | **WRKS** | shared libs + Shell | não (todos dependem dele) |
| **2 — Núcleo / plataforma** | **ASST** ∥ **INTL** | WRKS (auth/empresa/RBAC) | sim (sem dep mútua) |
| **3 — Domínio de dados / comunicação** | **LEAD** ∥ **COMM** | WRKS (+ ASST p/ COMM, via API) | sim |
| **4 — Orquestradores** | **JRNY** ∥ **SALE** | WRKS+LEAD+ASST+COMM (JRNY) · WRKS+LEAD+INTL (SALE) | sim (mais complexos) |

```
        ┌──────── Onda 0 (fundação compartilhada — ✅ DONE Layer 1) ────────┐
        libs/shared/* (auth-session, empresa-context, access-decision, …)
                  + journey-os-web (Shell + module registry)
          │
          ▼
        WRKS  ── Onda 1 (fundação de identidade FE: auth · empresa-context · RBAC)
          │
     ┌────┴────┐
     ▼         ▼
   ASST      INTL     ── Onda 2 (domínio independente ∥ plataforma transversal)
     │         │
     ▼         ▼
   COMM      (SALE consome INTL soft)
     │
   LEAD               ── Onda 3 (núcleo de dados ∥ comunicação)
     │
     └────┬────┐
          ▼    ▼
        JRNY  SALE    ── Onda 4 (orquestradores — mais complexos)
```

---

## Visão Geral — Status de Execução por Módulo

Legenda: ⬜ pendente · 🔄 em andamento · 🟢 CODE-DONE (gate pendente de re-run) · ✅ DONE (gate verde) · 🚫 bloqueado · **N/A** não se aplica

| Onda | Módulo | F1 | P1 | P2 | P3 | P4 | P5 | P6 | P7 | P8 | P9 | Gates F5 | Score | Estado |
|---|---|----|----|----|----|----|----|----|----|----|----|----|----|----|
| 1 | **WRKS** | ✅ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ✅ runnable | ~31 Inicial | 🔄 |
| 2 | **ASST** | ✅ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ✅ runnable | ~16 Inicial | 🔄 |
| 2 | **INTL** | ✅ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ✅ runnable | ~20 Inicial | 🔄 |
| 3 | **LEAD** | ✅ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ✅ runnable | ~12 Inicial | 🔄 |
| 3 | **COMM** | ✅ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ✅ runnable | ~16 Inicial | 🔄 |
| 4 | **JRNY** | ✅ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ✅ runnable | ~24 Inicial | 🔄 |
| 4 | **SALE** | ✅ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ✅ runnable | ~12 Inicial | 🔄 |
| | **Total** | 7/7 | 0/7 | 0/7 | 0/7 | 0/7 | 0/7 | 0/7 | 0/7 | 0/7 | 0/7 | — | — | **0/63** |

> `F1` = baseline (fe-validator Modo 1) executado. Todos os 7 módulos têm a **mesma forma P1..P9**
> (9 prioridades cada → **63 prioridades** no total). `Gates F5 ✅ runnable` = toolchain Nx
> disponível; cada P fecha com `nx lint/test/build` verde (e2e Playwright no P9). Todos os
> `plan-FE-<MODULO>.md` já existem (gerados no Architect A3).
>
> **GWY, REG, MIG** são backend-only — sem execução FE.

---

## Pré-condições globais de execução

- [x] **Onda 0 (shared libs + Shell) concluída** — 9 libs `@journeyos/shared/*` + `journey-os-web`
      como app Nx com module registry; `nx lint/test/build` verdes (Layer 1, 2026-06-05).
- [x] **Toolchain Nx disponível** — `frontend/node_modules` instalado (nx 19.8.14, Angular 18),
      gerador `@journeyos/internal:module` funcional. (Contrasta com BE — sem bloqueio.)
- [x] **Scaffold + e2e-validate (A4/A5) de todos os 7 módulos** — `apps/<mod>` + `apps/<mod>-e2e`
      + `libs/<mod>/*` gerados e compilando (`nx e2e <mod>-e2e --list` verde).
- [ ] **Registro efetivo de cada módulo no Shell** — `WRKS_MODULE_DESCRIPTOR` já registrado;
      os demais (`ASST/INTL/LEAD/COMM/JRNY/SALE_MODULE_DESCRIPTOR`) ficam para o **P1** de cada
      módulo (FE-<MOD>-003), como previsto no scaffold.
- [ ] **BE expõe contratos consumidos** — cada `INT-FE-<MOD>-NNN` depende do endpoint BE
      correspondente estar disponível (mock profile `/api/v0/` cobre o desenvolvimento isolado).
- [ ] **`@journeyos/shared/contracts`** (DTOs gerados de OpenAPI) — pendente do BE expor o
      OpenAPI; até lá, os data-access usam tipos locais por módulo.

### Modelo de score de maturidade (fe-validator §Score)

Consolidado no bloco de status de cada issue (0–100). Heurística (somar):

| Pts | Dimensão | Fechada por (tipicamente) |
|---|---|---|
| 30 | **STRUCTURAL** — spec validada + esqueleto de libs + tags Nx ok + boundaries verdes | P1 |
| 30 | **FUNCTIONAL** — features/data-access entregues (components, services, facades operam) | P2, P3 |
| 20 | **QUALITY** — Jest unit passando + `nx lint` sem warnings | P3, P7 |
| 10 | **E2E** — cenário principal Playwright verde | P9 |
| 10 | **OBSERVABILITY + A11Y + MULTI-EMPRESA** — MDC/telemetria, a11y, `X-Empresa-Id` enforce | P5, P8 |

Faixas: `0–39 Inicial` · `40–59 Parcial` · `60–79 Consistente` · `80–100 Maduro`.
**Definition of Done de um módulo:** checklist 100% DONE **e** score ≥ 80 **e** boundaries Nx
verdes (`nx lint`) **e** multi-empresa enforcement OK.

### Mapa prioridade → camada (comum aos 7 módulos)

| Prioridade | Foco | Issues (faixa típica) |
|---|---|---|
| **P1** | Module entry (`libs/<mod>/shell-entry`, ADR-006) + contrato + descriptor + registro no Shell | FE-<MOD>-001..003/004 |
| **P2** | Data-access (services + facades signals-readonly + error mapper) | FE-<MOD>-004..008/009 |
| **P3** | Feature libs (components standalone OnPush + UI local) | FE-<MOD>-009..015/017 |
| **P4** | Integrações Access Layer + Shell runtime | INT-FE-<MOD>-001..006 |
| **P5** | Guards (auth/empresa/access) + multi-empresa enforce | FE-<MOD>-016..018 |
| **P6** | Navegação / breadcrumbs | +1 issue |
| **P7** | UX polish (loading/empty/error states + flags + a11y) | +1–2 issues |
| **P8** | Observability | +1 issue |
| **P9** | e2e Playwright (execução real) + hardening | +1 issue |

---

## Onda 1 — Fundação de identidade

### Módulo WRKS — `libs/wrks/` + `apps/wrks/`

> Scope `scope:wrks` · fundação de domínio · **dep:** shared libs + Shell · **dependentes:** TODOS
> · fonte: `plan-FE-WRKS.md`. 20 FE + 6 INT = 26 issues. ADR-005: `multi-empresa-context`.
> **Entrada do ciclo:** `/fe-validator FE-WRKS-001` → `/fe-autopilot FE-WRKS-001`.

- [x] **F1 Baseline** (2026-06-05) — **26 issues consolidadas** (20 FE + 6 INT) via sweep completo (fe-validator Modo 1). Distribuição: 🟢 NEAR-CLOSED ×1 (FE-WRKS-003 descriptor real ligado ao Shell, score 65) · 🟡 REDUCED ×4 (FE-WRKS-001/002 P1 estrutural; FE-WRKS-017 nav stub; FE-WRKS-020 5 specs `test.fixme`) · ⚪ INTACT ×21. Maturidade média **~31 (Inicial)**; **3/110 itens DONE** (só P1 shell-entry: feature-flags + module.ts + descriptor). Status block + marcas DONE/PARTIAL/MISSING aplicados em cada issue. Gates não executados (Modo 1 não roda nx). ⚠️ **Achados:** (a) divergência de paths — checklists citam `apps/wrks/src/app/wrks-module/` mas o real segue ADR-006 module-as-library em `libs/wrks/shell-entry/`; reconciliar antes de F4; (b) fachadas `@journeyos/shared/*` ainda Wave-0 stubs → INT-FE-WRKS-* bloqueadas em cascata; (c) `provideHttpBase({})` no-op → **multi-empresa enforcement NÃO ativo** (R-2/LGPD em aberto). **Próxima:** F2 DECISÃO → P1 (FE-WRKS-001..003).
- [ ] **P1 — Module entry + registro no Shell** · FE-WRKS-001..003 · entry lib `@journeyos/wrks`, descriptor, lazy route
- [ ] **P2 — Data-access (5 resources) + erros** · FE-WRKS-004..008 · services + facades signals-readonly + error mapper
- [ ] **P3 — Features** · FE-WRKS-009..015 · login, empresa-select, workspace, users, rbac-viewer
- [ ] **P4 — Integrações Access Layer + Shell** · INT-FE-WRKS-001..006 · http-base, auth, empresa-context, access-decision, shell, error-model
- [ ] **P5 — Guards (empresa/access)** · FE-WRKS-016 · multi-empresa enforce (`X-Empresa-Id`)
- [ ] **P6 — Navegação/breadcrumbs** · FE-WRKS-017 · re-deriva nav na troca de empresa (gap A2.5)
- [ ] **P7 — UX polish (states)** · FE-WRKS-018 · login-fail banner, switch-denied toast (gaps A2.5)
- [ ] **P8 — Observability** · FE-WRKS-019 · métricas `journey-os_iam_session_*`, telemetria
- [ ] **P9 — e2e Playwright + hardening** · FE-WRKS-020 · 6 specs (18 testes), execução real dos fluxos
- [ ] **F5 gates** · `nx lint/test/build wrks-*` + `nx e2e wrks-e2e` · **DoD** · checklist 100% + score ≥ 80

---

## Onda 2 — Núcleo de domínio ∥ plataforma (ASST ∥ INTL — paralelo)

### Módulo ASST — `libs/asst/` + `apps/asst/`

> Scope `scope:asst` · domínio independente · **dep:** WRKS · fonte: `plan-FE-ASST.md`
> 20 FE + 6 INT = 26 issues. ADR-005: `asset-studio-ai-composition` (degradação graciosa).

- [x] **F1 Baseline** (2026-06-05) — **26 issues consolidadas** (20 FE + 6 INT); todas **INTACT / Inicial** (post-scaffold, pre-implementation). Maturidade média ~16; ~6/115 itens DONE (só stubs P1 shell-entry: feature-flags completo, contract/permission-map estruturais). Status block + checklist marcados em cada issue. Gates não rodados (Modo 1). ⚠️ INT-FE-ASST-003 (invalidação empresa-context / R-2 LGPD) ainda MISSING. **Próxima:** P1 (FE-ASST-001..003).
- [ ] **P1 — Foundation** · FE-ASST-001..003 · contract, routes/module, descriptor + registro Shell
- [ ] **P2 — Data access** · FE-ASST-004..008 · Asset/Versão/Studio/Workflow services + facades + erros
- [ ] **P3 — Feature libs** · FE-ASST-009..015 · library, detail, studio (degradação IA), approval
- [ ] **P4 — Hub integrations** · INT-FE-ASST-001..006 · http-base, auth, empresa-context, access-decision, shell, error-model
- [ ] **P5 — Access guards** · FE-ASST-016 · RULE multi-empresa
- [ ] **P6 — Navegação/breadcrumbs** · FE-ASST-017
- [ ] **P7 — UX polish** · FE-ASST-018 · loading/empty/error; gaps A2.5 (redirect `/asst`, 422-inline, 409-reload)
- [ ] **P8 — Observability** · FE-ASST-019
- [ ] **P9 — e2e Playwright + hardening** · FE-ASST-020 · 6 specs (21 testes)
- [ ] **F5 gates** · `nx lint/test/build asst-*` + `nx e2e asst-e2e` · **DoD** · 100% + score ≥ 80

### Módulo INTL — `libs/intl/` + `apps/intl/`

> Scope `scope:intl` · plataforma transversal · **dep:** WRKS · fonte: `plan-FE-INTL.md`
> 20 FE + 6 INT = 26 issues. ADR-005: `ai-copilot-streaming` (render request/response no MVP).
> Recorte FE = 3 features (copilot/knowledge/analytics); event-platform/integrations fora do MVP FE.

- [x] **F1 Baseline** (2026-06-05) — **26 issues consolidadas** (20 FE + 6 INT) via sweep completo (fe-validator Modo 1, 5 sub-agentes por onda). Distribuição: 🟡 REDUCED ×3 (FE-INTL-001 P1 contract, score 50; FE-INTL-016 nav.config stub, 20; FE-INTL-019 7 specs `test.fixme` compilam, 28) · ⚪ INTACT ×23. Maturidade média **~20 (Inicial)**; **2/117 itens DONE** (só FE-INTL-001 shell-entry: `permission-map` 5 perms + `feature-flags` 4 flags, ambos escritos pelo gerador do `generator-config.yml`). Status block + marcas DONE/PARTIAL/MISSING aplicados em cada issue. Gates não executados (Modo 1 não roda nx). ⚠️ **Achados:** (a) `intl.contract.ts` parcial — rota `/intl` (esperado `/intl/copilot`) + `deepLinks: []`; (b) `INTL_ROUTES` vazio e **INTL ausente em `module-descriptors.ts`** (registro no Shell = P1/FE-INTL-003); (c) data-access/features só placeholders standalone+OnPush, zero lógica; (d) multi-empresa enforcement ausente (INT-FE-INTL-002/004 — R-2/LGPD aberto). **Próxima:** F2 DECISÃO → P1 (FE-INTL-001 → 002 → 003).
- [ ] **P1 — Foundation** · FE-INTL-001..003 · contract, routes, Shell descriptor
- [ ] **P2 — Data access** · FE-INTL-004..008 · 3 services + 3 facades + error mapper
- [ ] **P3 — Feature libs** · FE-INTL-009..014 · copilot (chat+citações+degradação), knowledge, analytics
- [ ] **P4 — Hub integrations** · INT-FE-INTL-001..006 · auth/empresa/access/http-base/shell/error
- [ ] **P5 — Access guards** · FE-INTL-015 · empresaGuard sem-empresa (gap A2.5)
- [ ] **P6 — Navegação/breadcrumbs** · FE-INTL-016
- [ ] **P7 — UX polish** · FE-INTL-017 · loading/empty/error; copilot cancel-flow, analytics flag-off (gaps A2.5)
- [ ] **P8 — Observability** · FE-INTL-018
- [ ] **P9 — e2e (7 specs) + hardening** · FE-INTL-019, 020 · 24 testes; render degradado nunca como fato (R2)
- [ ] **F5 gates** · `nx lint/test/build intl-*` + `nx e2e intl-e2e` · **DoD** · 100% + score ≥ 80

---

## Onda 3 — Núcleo de dados ∥ comunicação (LEAD ∥ COMM — paralelo)

### Módulo LEAD — `libs/lead/` + `apps/lead/`

> Scope `scope:lead` · núcleo de dados · **dep:** WRKS · consumido por JRNY/SALE (via API) · fonte: `plan-FE-LEAD.md`
> 22 FE + 6 INT = 28 issues. ADR-005: `maturity-score-visualization` (radar 6D explicável, a11y obrigatória).

- [x] **F1 Baseline** (2026-06-05) — **28 issues consolidadas** (22 FE + 6 INT). P1 (FE-LEAD-001..003) **REDUCED / Parcial** (esqueletos module-pattern em `shell-entry`: descriptor+flags presentes, mas `LEAD_ROUTES=[]`, `lead.bootstrap` vazio, `LEAD_PERMISSION_MAP` com arrays de papéis vazios, route `/lead`≠`/lead/leads`, deepLinks vazios, e **LEAD ausente em `module-descriptors.ts`**). Demais 25 issues **INTACT / Inicial** (stubs default Nx). Maturidade média ~12; 3/~115 itens DONE. Status block + checklist marcados em cada issue. Gates não rodados (Modo 1). ⚠️ multi-empresa enforcement ausente (INT-FE-LEAD-001/002). **Próxima:** P1 (FE-LEAD-001 → 002 → 003).
- [ ] **P1 — Foundation (entry + descriptor + Shell)** · FE-LEAD-001..003
- [ ] **P2 — Data access (4 recursos + erros)** · FE-LEAD-004..008
- [ ] **P3 — Feature libs (6 features + score UI)** · FE-LEAD-009..016 · centerpiece FE-LEAD-012 (ScoreBreakdown/Radar)
- [ ] **P4 — Hub integrations** · INT-FE-LEAD-001..006
- [ ] **P5 — Access guards** · FE-LEAD-017 · empresa-guard (gap G9)
- [ ] **P6 — Navegação/breadcrumbs** · FE-LEAD-018
- [ ] **P7 — UX polish (states + flags + a11y)** · FE-LEAD-019, 020 · radar-a11y, flag-disabled, list-error, retry (gaps)
- [ ] **P8 — Observability** · FE-LEAD-021
- [ ] **P9 — e2e + hardening** · FE-LEAD-022 · 9 specs (30 testes)
- [ ] **F5 gates** · `nx lint/test/build lead-*` + `nx e2e lead-e2e` · **DoD** · 100% + score ≥ 80

### Módulo COMM — `libs/comm/` + `apps/comm/`

> Scope `scope:comm` · **dep:** WRKS + ASST (templates usam assets, **só via API BE**) · fonte: `plan-FE-COMM.md`
> 20 FE + 6 INT = 26 issues. ADR-005: `delivery-status-tracking` (polling com backoff).
> FE só conhece `canal` (nunca provedor); config expõe só `credencialRef` mascarada.

- [x] **F1 Baseline** (2026-06-05) — **26 issues consolidadas** (20 FE + 6 INT); todas **INTACT / Inicial** (post-scaffold, pre-implementation). Maturidade média ~16; só stubs P1 shell-entry (feature-flags completo; contract `deepLinks=[]`, permission-map 13 chaves com arrays `[]`, routes `[]`; descriptor pronto mas Shell registra só WRKS). Status block + checklist marcados em cada issue. Gates não rodados (Modo 1). ⚠️ INT-FE-COMM-002 (isolamento cross-empresa / stop-polling na troca — R-2 LGPD) e UINV-6 (FE-COMM-015 `credencialRef` mascarada) ainda MISSING. **Próxima:** P1 (FE-COMM-001..003).
- [ ] **P1 — Foundation** · FE-COMM-001..003 · contract, routes/lazy, descriptor + registro Shell
- [ ] **P2 — Data access** · FE-COMM-004..008 · Template/Studio/Routing/Message/Channel facades + erro
- [ ] **P3 — Features** · FE-COMM-009..015 · catálogo, editor, studio (degradação IA), roteamento, mensagens, canais
- [ ] **P4 — Integrações Hub** · INT-FE-COMM-001..006 · http-base, auth/empresa, access-decision, navigation, shell-runtime, error-model
- [ ] **P5 — Access guards** · FE-COMM-016
- [ ] **P6 — Navegação/breadcrumbs** · FE-COMM-017
- [ ] **P7 — UX polish** · FE-COMM-018 · loading/empty/error + tokens; delivery-tracking flag-off (gap C-05.4)
- [ ] **P8 — Observability** · FE-COMM-019
- [ ] **P9 — e2e Playwright + perf/a11y** · FE-COMM-020 · 9 specs (30 testes); stop-polling no destroy (gap C-06.4)
- [ ] **F5 gates** · `nx lint/test/build comm-*` + `nx e2e comm-e2e` · **DoD** · 100% + score ≥ 80

---

## Onda 4 — Orquestradores (JRNY ∥ SALE — paralelo, mais complexos)

### Módulo JRNY — `libs/jrny/` + `apps/jrny/`

> Scope `scope:jrny` · orquestrador (mais complexo) · **dep:** WRKS+ASST+COMM+LEAD+INTL(soft), via API · fonte: `plan-FE-JRNY.md`
> 22 FE + 6 INT = 28 issues. ADR-005: `canvas-builder-rendering` (editor estruturado de estágios; sem lib de canvas no MVP).
> **Decide e sinaliza** (UI não executa canal/venda); decision log explicável (badge `assistIa` ternário).

- [x] **F1 Baseline** (2026-06-05) — **28 issues consolidadas** (22 FE + 6 INT) via sweep completo (fe-validator Modo 1, 5 sub-agentes por onda). Tags: 1×🟡 REDUCED (FE-JRNY-001 contract score 45, route `/jrny`≠`/jrny/journeys` + deepLinks vazios) · 27×⚪ INTACT. Maturidade média **~24 (Inicial)** — abaixo do WRKS porque **JRNY_MODULE_DESCRIPTOR existe na lib mas NÃO está registrado** em `module-descriptors.ts` (só WRKS está → FE-JRNY-003 INTACT) e os 7 specs e2e são `test.fixme`. **3/115 itens DONE** (P1 shell-entry: feature-flags + permission-map + index export). Status block + marcas DONE/PARTIAL/MISSING aplicados em cada issue. Gates não executados (Modo 1 não roda nx). ✅ **Sem divergência de path** — as issues P1 já citam `libs/jrny/shell-entry/` (alinhadas a ADR-006, contraste com WRKS). ⚠️ **Achados:** (a) `JRNY_ROUTES = []` vazio (FE-JRNY-002); (b) data-access/6 features = stubs default Nx (sem services/facades/componentes reais); (c) fachadas `@journeyos/shared/*` Wave-0 stubs → INT-FE-JRNY-* bloqueadas em cascata (INT-002→001/004, etc.); (d) multi-empresa enforcement ausente (INT-FE-JRNY-002, R-2/LGPD aberto); (e) tag menor: shell-entry `project.json` usa `type:app` vs `type:domain` citado nas issues. **Próxima:** F2 DECISÃO → P1 (FE-JRNY-001..003).
- [ ] **P1 — Module entry + contrato + registro Shell** · FE-JRNY-001..003
- [ ] **P2 — Data access (journey/stage/rule/query) + erros** · FE-JRNY-004..008
- [ ] **P3 — 6 features + ui local + sortable** · FE-JRNY-009..016 · núcleo: builder + sortable a11y
- [ ] **P4 — Integrações Access Layer + runtime** · INT-FE-JRNY-001..006
- [ ] **P5 — Guards (auth/empresa/access)** · FE-JRNY-017 · empresaGuard sem-empresa (gap A2.5)
- [ ] **P6 — Navegação/breadcrumbs** · FE-JRNY-018
- [ ] **P7 — UX polish + flags + a11y** · FE-JRNY-019, 020 · reorder-failure rollback, canvas-flag pós-MVP, read-failure retry (gaps)
- [ ] **P8 — Observability** · FE-JRNY-021
- [ ] **P9 — e2e + hardening** · FE-JRNY-022 · 7 specs (24 testes)
- [ ] **F5 gates** · `nx lint/test/build jrny-*` + `nx e2e jrny-e2e` · **DoD** · 100% + score ≥ 80

### Módulo SALE — `libs/sale/` + `apps/sale/`

> Scope `scope:sale` · orquestrador · **dep:** WRKS + LEAD(soft) + INTL(soft), via API · fonte: `plan-FE-SALE.md`
> 23 FE + 6 INT = 29 issues. ADR-005: `kanban-pipeline-rendering` (CDK DragDrop + optimistic move/rollback).
> **SEM TechLab AI no MVP** (atribuição/LTV determinísticos; FE nunca chama IA, sem badge de IA).

- [x] **F1 Baseline** (2026-06-05) — **29 issues consolidadas** (23 FE + 6 INT). P1 (FE-SALE-001..004) **REDUCED / Inicial** (esqueletos module-pattern em `shell-entry`: descriptor+flags presentes, mas `SALE_ROUTES=[]`, `sale.bootstrap` vazio, `SALE_PERMISSION_MAP` 15 chaves com arrays vazios, route `/sale`≠`/sale/pipeline`, deepLinks vazios; **SALE ausente em `module-descriptors.ts`** → registro runtime no Shell MISSING; `integration` lib é stub default). Demais 25 issues **INTACT / Inicial** (stubs default Nx). Maturidade média ~12; 3/~135 itens DONE. Status block + checklist marcados em cada issue. Gates não rodados (Modo 1). ⚠️ centerpiece Kanban (FE-SALE-010, ADR-005) não iniciado; e2e (FE-SALE-023) tem 8 `.spec.ts` como `test.fixme` (zero cenários); multi-empresa enforcement ausente (INT-FE-SALE-001/002). **Próxima:** P1 (FE-SALE-001 → 002 → 003 → 004).
- [ ] **P1 — Module entry + contrato + descriptor + registro Shell + integration/bootstrap** · FE-SALE-001..004
- [ ] **P2 — Data access (oportunidade/oferta/compra/atribuição+ltv) + erros** · FE-SALE-005..009
- [ ] **P3 — 6 features + ui local + flag multi-touch** · FE-SALE-010..017 · centerpiece FE-SALE-010 (Kanban CDK DragDrop, rollback no `409 ja-fechada`)
- [ ] **P4 — Integrações Access Layer + runtime + erro + observability** · INT-FE-SALE-001..006
- [ ] **P5 — Guards (auth/empresa/access)** · FE-SALE-018
- [ ] **P6 — Navegação/breadcrumbs** · FE-SALE-019
- [ ] **P7 — UX polish + rollback UX + a11y/perf do board** · FE-SALE-020, 021
- [ ] **P8 — Observability** · FE-SALE-022
- [ ] **P9 — e2e (8 specs) + hardening** · FE-SALE-023 · 27 testes; compra read+estornar/cancelar (sem create — server-to-server)
- [ ] **F5 gates** · `nx lint/test/build sale-*` + `nx e2e sale-e2e` · **DoD** · 100% + score ≥ 80

---

## Sequenciamento cross-módulo (acoplamento FE)

> Diferente do BE (eventos), o FE não consome eventos entre módulos. O acoplamento é **soft, só via
> API BE** (sem import `scope:<outro>`). A ordem das ondas garante que, quando um módulo entra, a
> **Access Layer** (`@journeyos/shared/*`, provida pela maturação de WRKS) e os **contratos BE** que
> ele consome já estão estáveis.

| Consumidor FE | Depende de (FE, soft via Access Layer/API) | Onda do pré-requisito | INT issues |
|---|---|---|---|
| WRKS | shared libs + Shell | 0 (✅ done) | INT-FE-WRKS-* |
| ASST | WRKS (auth/empresa/RBAC) | 1 | INT-FE-ASST-* |
| INTL | WRKS | 1 | INT-FE-INTL-* |
| LEAD | WRKS | 1 | INT-FE-LEAD-* |
| COMM | WRKS + ASST (assets via API BE) | 1, 2 | INT-FE-COMM-* |
| JRNY | WRKS + LEAD + ASST + COMM + INTL (soft) | 1, 2, 3 | INT-FE-JRNY-* |
| SALE | WRKS + LEAD + INTL (soft) | 1, 2, 3 | INT-FE-SALE-* |

---

## Resumo de contagem (prioridades + issues por módulo)

| Módulo | Prioridades | Issues func. | Issues INT | Total issues | Plan |
|--------|-------------|--------------|------------|--------------|------|
| WRKS | 9 (P1–P9) | 20 | 6 | 26 | ✅ |
| ASST | 9 (P1–P9) | 20 | 6 | 26 | ✅ |
| INTL | 9 (P1–P9) | 20 | 6 | 26 | ✅ |
| LEAD | 9 (P1–P9) | 22 | 6 | 28 | ✅ |
| COMM | 9 (P1–P9) | 20 | 6 | 26 | ✅ |
| JRNY | 9 (P1–P9) | 22 | 6 | 28 | ✅ |
| SALE | 9 (P1–P9) | 23 | 6 | 29 | ✅ |
| **Total** | **63** | **147** | **42** | **189** | **7/7** |

---

## Referências de pipeline (Layer 2)

| Comando | Etapa | Pré-requisito |
|---------|-------|---------------|
| `/fe-validator FE-<M>-001` | F1 BASELINE | Scaffold executável (Layer 1 done) |
| `/fe-validator FE-<M>-NNN` | F2 DECISÃO | Issue spec + checklist consistente |
| `/fe-planner FE-<M>-NNN` | F3 | Baseline calculado (plan já existe) |
| `/fe-implement FE-<M>-NNN fase-<P>` | F4 | Plano com prioridade definida — UMA por vez |
| `/fe-validator FE-<M>-NNN` | F5 VALIDAÇÃO | Implementação concluída + **toolchain Nx** ✅ |
| `/fe-autopilot FE-<M>-NNN` | F1→F5 | Pipeline B — detecta estado e encadeia |

### Documentos de referência (ler antes de implementar)

- `plan-FE-<MODULO>.md` — estratégia detalhada por prioridade (objetivo/issues/sequência/aceite/riscos)
- `docs/architecture/frontend/modules/<mod>/frontend/issues/<ISSUE>.md` — checklist + critério de aceite atômico (fonte da verdade operacional)
- `docs/architecture/frontend/standards/{module-pattern,nx-boundaries,access-layer-contracts,bootstrap-flow,asset-driven-ui}.md`
- `docs/architecture/shared/blueprint-core.md` — modelo mental app+módulos+shared

---

## Log cronológico da execução

> Append-only. Uma linha por transição de etapa do ciclo F1→F5 (por módulo/prioridade).
> Formato: `<ISO-8601> -- <MODULO> -- <etapa> -- <resultado> -- <notas>`

- 2026-06-05 -- (todos) -- plano-criado -- Implementation Master Plan FE gerado a partir do architecture-master-plan FE (Layer 1 A1..A5 100% nos 7 módulos de domínio; Layer 2 não iniciada). Contraste com BE: gates F5 NÃO diferidos — toolchain Nx disponível (fe-scaffold-toolchain-absent RESOLVIDO). 63 prioridades (7×P1..P9), 189 issues.
- 2026-06-05 -- ASST -- F1-baseline -- DONE -- fe-validator Modo 1 (BASELINE) rodado em lote sobre as 26 issues ASST (20 FE + 6 INT). Todas INTACT/Inicial (post-scaffold, pre-implementation); maturidade média ~16; ~6/115 itens DONE. Status block + marcas DONE/PARTIAL/MISSING aplicados em cada issue. Gates não executados (Modo 1 não roda nx). Bloqueio LGPD em aberto: INT-FE-ASST-003 (invalidação na troca de empresa, R-2). Próxima ação: ciclo de implementação do P1 (FE-ASST-001 → 002 → 003).
- 2026-06-05 -- LEAD -- F1-baseline -- DONE -- fe-validator Modo 1 (BASELINE) rodado em lote sobre as 28 issues LEAD (22 FE + 6 INT). P1 (FE-LEAD-001..003) REDUCED/Parcial (esqueletos module-pattern em shell-entry com lacunas: LEAD_ROUTES vazio, bootstrap vazio, permission-map sem papéis, route /lead≠/lead/leads, deepLinks vazios, LEAD fora de module-descriptors.ts); demais 25 INTACT/Inicial (stubs default Nx). Maturidade média ~12; 3/~115 itens DONE. Status block + marcas DONE/PARTIAL/MISSING aplicados em cada issue. Gates não executados (Modo 1 não roda nx). ⚠️ multi-empresa enforcement ausente (INT-FE-LEAD-001/002). Próxima ação: ciclo de implementação do P1 (FE-LEAD-001 → 002 → 003).
- 2026-06-05 -- WRKS -- F1-baseline -- DONE -- fe-validator Modo 1 (BASELINE) sweep completo sobre as 26 issues WRKS (20 FE + 6 INT). Tags: 1×NEAR-CLOSED (FE-WRKS-003) / 4×REDUCED (FE-WRKS-001,002,017,020) / 21×INTACT. Maturidade média ~31 (Inicial); 3/110 itens DONE (P1 shell-entry: feature-flags + module.ts + descriptor). Status block + marcas DONE/PARTIAL/MISSING aplicados em cada issue. Gates não executados (Modo 1 não roda nx). ⚠️ Achados: (a) paths checklist `apps/wrks/src/app/wrks-module/` × ADR-006 module-as-library `libs/wrks/shell-entry/` a reconciliar; (b) fachadas `@journeyos/shared/*` Wave-0 stubs → INT-FE-WRKS-* bloqueadas; (c) `provideHttpBase({})` no-op → multi-empresa enforce inativo (R-2/LGPD aberto). Próxima ação: ciclo de implementação do P1 (FE-WRKS-001 → 002 → 003).
- 2026-06-05 -- INTL -- F1-baseline -- DONE -- fe-validator Modo 1 (BASELINE) sweep completo sobre as 26 issues INTL (20 FE + 6 INT), via 5 sub-agentes por onda (P1/P2/P3/P4/P5-P9). Tags: 3×REDUCED (FE-INTL-001 contract score 50, FE-INTL-016 nav.config stub 20, FE-INTL-019 7 specs test.fixme compilam 28) / 23×INTACT. Maturidade média ~20 (Inicial); 2/117 itens DONE (só FE-INTL-001 shell-entry: permission-map 5 perms + feature-flags 4 flags, gerados do generator-config.yml). Status block + marcas DONE/PARTIAL/MISSING aplicados em cada issue. Gates não executados (Modo 1 não roda nx). ⚠️ Achados: (a) intl.contract.ts parcial (rota /intl≠/intl/copilot, deepLinks vazio); (b) INTL_ROUTES vazio + INTL ausente em module-descriptors.ts (registro Shell = P1/FE-INTL-003); (c) data-access/features só placeholders standalone+OnPush; (d) multi-empresa enforcement ausente (INT-FE-INTL-002/004, R-2/LGPD aberto). Próxima ação: ciclo de implementação do P1 (FE-INTL-001 → 002 → 003).
- 2026-06-05 -- COMM -- F1-baseline -- DONE -- fe-validator Modo 1 (BASELINE) rodado em lote (5 sub-agentes) sobre as 26 issues COMM (20 FE + 6 INT). Tags: 3×REDUCED (FE-COMM-001 contract+permission-map stubs 30, FE-COMM-002 host loadChildren wired/COMM_ROUTES vazio 28, FE-COMM-003 descriptor pronto mas Shell registra só WRKS 25) / 23×INTACT. Maturidade média ~16 (Inicial); ~3/~115 itens DONE (P1 shell-entry: feature-flags 2 flags + descriptor + host route). Status block + marcas DONE/PARTIAL/MISSING aplicados em cada issue. Gates não executados (Modo 1 não roda nx). ⚠️ Achados: (a) permission-map 13 chaves com arrays `[]`; (b) data-access/features só placeholders standalone+OnPush (sem services/facades/error-mapper); (c) 9 specs comm-e2e são test.fixme stubs; (d) INT-FE-COMM-002 isolamento cross-empresa + stop-polling na troca (R-2/LGPD) e UINV-6 FE-COMM-015 `credencialRef` mascarada ainda MISSING. Próxima ação: ciclo de implementação do P1 (FE-COMM-001 → 002 → 003).
- 2026-06-05 -- JRNY -- F1-baseline -- DONE -- fe-validator Modo 1 (BASELINE) sweep completo (5 sub-agentes por onda) sobre as 28 issues JRNY (22 FE + 6 INT). Tags: 1×REDUCED (FE-JRNY-001 contract score 45) / 27×INTACT. Maturidade média ~24 (Inicial) — abaixo do WRKS: JRNY_MODULE_DESCRIPTOR existe na lib mas NÃO registrado em module-descriptors.ts (FE-JRNY-003 INTACT) e os 7 specs e2e são test.fixme. 3/115 itens DONE (P1 shell-entry: feature-flags + permission-map + index export). Status block + marcas DONE/PARTIAL/MISSING aplicados em cada issue. Gates não executados (Modo 1 não roda nx). ✅ Sem divergência de path (issues P1 já em libs/jrny/shell-entry, alinhadas a ADR-006). ⚠️ Achados: (a) JRNY_ROUTES=[] vazio (FE-JRNY-002); (b) data-access/6 features = stubs default Nx; (c) fachadas @journeyos/shared/* Wave-0 stubs → INT-FE-JRNY-* bloqueadas em cascata; (d) multi-empresa enforcement ausente (INT-FE-JRNY-002, R-2/LGPD aberto); (e) tag menor shell-entry type:app vs type:domain. Próxima ação: ciclo de implementação do P1 (FE-JRNY-001 → 002 → 003).
- 2026-06-05 -- SALE -- F1-baseline -- DONE -- fe-validator Modo 1 (BASELINE) sweep completo (6 sub-agentes por onda) sobre as 29 issues SALE (23 FE + 6 INT). Tags: 4×REDUCED (FE-SALE-001 contract+perm-map 35, FE-SALE-002 SALE_ROUTES vazio 30, FE-SALE-003 descriptor pronto mas Shell registra só WRKS 35, FE-SALE-004 integration stub 10) / 25×INTACT. Maturidade média ~12 (Inicial); 3/~135 itens DONE (P1 shell-entry: feature-flags 2 flags + descriptor + index export). Status block + marcas DONE/PARTIAL/MISSING aplicados em cada issue. Gates não executados (Modo 1 não roda nx). ⚠️ Achados: (a) contract route /sale≠/sale/pipeline + deepLinks vazio; SALE_PERMISSION_MAP 15 chaves com arrays []; (b) SALE ausente em module-descriptors.ts → registro runtime Shell MISSING (FE-SALE-003/INT-FE-SALE-003); (c) data-access/6 features = stubs default Nx (sem services/facades/mappers); (d) centerpiece Kanban FE-SALE-010 (ADR-005, CDK DragDrop + optimistic/rollback) não iniciado; (e) 8 specs sale-e2e são test.fixme stubs (FE-SALE-023); (f) multi-empresa enforcement ausente (INT-FE-SALE-001/002, R-2/LGPD aberto). SALE sem TechLab AI no MVP (determinístico). Próxima ação: ciclo de implementação do P1 (FE-SALE-001 → 002 → 003 → 004).
