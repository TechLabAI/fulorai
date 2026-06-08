## [FE-WRKS-003] Registro no Shell (module-descriptor + shell-routes)

**Status:** 🔲 ABERTA
**GitHub:** [#TBD]
**Status:** NEAR-CLOSED — pos-validacao 2026-06-05
**Maturidade:** 65 — Consistente
**Done/Total:** 1/2 itens

**Outcome:**
Entrada do WRKS em `module-descriptors.ts` e `shell-routes.ts` do `journey-os-web`, com `loadChildren` para `@journeyos/wrks`, metadata e flags — Shell conhece a module em build-time (fallback estático, ADR-004).

**Context / Problem statement:**
- WRKS é fundação: o Shell precisa direcionar para suas rotas pré-contexto no boot.
- Fonte: SPEC-06. Depende de FE-WRKS-001/002.

**Approach (execution path):**
1) Adicionar descriptor `wrks` (key, loadChildren, metadata, flags).
2) Registrar rota raiz do módulo em `shell-routes.ts`.
3) Marcar WRKS como rota de boot (login/empresa-select).

**Non-goals:** registro runtime via service (INT-FE-WRKS-005).

**Layer(s):** frontend / apps/journey-os-web config
**Bounded context:** wrks

**Service execution spec(s):** `frontend-spec/SPEC-06-shell-integration.md`

**Architecture alignment:** ADR-004 (descriptor estático + runtime).

**Implementation checklist (by file):**
- ✅ `apps/journey-os-web/src/app/config/module-descriptors.ts` (entrada wrks) — real: importa `WRKS_MODULE_DESCRIPTOR` de `@journeyos/wrks`, registra em `MODULE_DESCRIPTORS` com `loadChildren`→`WrksModule`, `metadata`, `flags`, `permissionMap` (build-time / ADR-004).
- 🔲 `apps/journey-os-web/src/app/config/shell-routes.ts` (MISSING) — arquivo não existe; o roteamento equivalente vive em `app.routes.ts` (`AppShellComponent` + `...moduleRoutes`) e em `moduleRoutes` derivado dentro de `module-descriptors.ts`. Intenção (Shell conhece o módulo em build-time via descriptor + rota lazy) atendida, porém: rotas pré-contexto (`/login`, `/empresa-select`) NÃO estão cabeadas (dependem de FE-WRKS-002, cujo `wrks.routes.ts` está vazio) → boot-to-`/login` ainda não materializado.

**Tests**
- 🔲 `nx test journey-os-web` PASS (MISSING — só `app.component.spec.ts` default stub) · 🔲 `nx lint journey-os-web` PASS (MISSING)

**Milestone:** Wave P1 / Foundation
**Labels:** type:feature · layer:frontend · scope:web · priority:P1

**Acceptance criteria:**
- `npx nx build journey-os-web` PASS com WRKS lazy
- Boot direciona a `/login` quando sem sessão

**Dependencies:** FE-WRKS-001, FE-WRKS-002
**API / Contract impact:** nenhum direto.
**Risks / Notes:** evitar barrel que arraste o grafo do WRKS para o bundle inicial do Shell.
