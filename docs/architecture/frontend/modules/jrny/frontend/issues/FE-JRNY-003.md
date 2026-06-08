## [FE-JRNY-003] Registro do módulo no Shell (descriptor)

**Status:** 🔲 ABERTA
**GitHub:** [#TBD]

**Status:** INTACT — pos-validacao 2026-06-05
**Maturidade:** 15 — Inicial
**Done/Total:** 0/1 itens

**Outcome:**
`JRNY_MODULE_DESCRIPTOR` (de `@journeyos/jrny`) registrado em
`apps/journey-os-web/src/app/config/module-descriptors.ts`; o item de menu "Jornadas" aparece no Shell
com `loadChildren` lazy e flags/permissões. `build`+`lint journey-os-web` verdes com o módulo registrado.

**Context / Problem statement:**
- Espelha o padrão WRKS/ASST/INTL/LEAD/COMM: registro efetivo no Shell é tarefa de P1.
- Fonte: SPEC-06. Depende do descriptor gerado no scaffold.

**Approach (execution path):**
1) Importar `JRNY_MODULE_DESCRIPTOR` em `module-descriptors.ts` e adicioná-lo à lista.
2) Verificar menu/route/perms/flags expostos.
3) `nx build journey-os-web` + `nx lint journey-os-web`.

**Non-goals:** registro em runtime (INT-FE-JRNY-005); guards (FE-JRNY-017).

**Layer(s):** frontend / `apps/journey-os-web` (Shell) + `libs/jrny/shell-entry`
**Bounded context:** jrny

**Service execution spec(s):** `frontend-spec/SPEC-06-shell-integration.md` §1

**Architecture alignment:** ADR-004 (module registry); ADR-006 (entry como library).

**Implementation checklist (by file):**
- 🔲 `apps/journey-os-web/src/app/config/module-descriptors.ts` (+ import `@journeyos/jrny`) (MISSING — MODULE_DESCRIPTORS contém só WRKS; JRNY_MODULE_DESCRIPTOR não importado/registrado. Nota: o descriptor existe em `libs/jrny/shell-entry/src/lib/jrny.descriptor.ts` e o path `@journeyos/jrny` está mapeado em tsconfig.base.json — falta só o wiring no Shell)

**Tests**
- 🔲 `nx build journey-os-web` PASS (MISSING) · 🔲 `nx lint journey-os-web` PASS (MISSING)

**Milestone:** Wave P1 / Foundation
**Labels:** type:feature · layer:frontend · scope:jrny · priority:P1

**Acceptance criteria:**
- `npx nx build/lint journey-os-web` PASS com `JRNY_MODULE_DESCRIPTOR` registrado
- Item de menu "Jornadas" visível (sujeito a permissão)

**Dependencies:** FE-JRNY-001, FE-JRNY-002
**API / Contract impact:** nenhum.
**Risks / Notes:** manter ordem de descriptors estável; não duplicar registro com o runtime (INT-005).
