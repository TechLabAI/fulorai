# ADR-003 — Entry lazy do módulo (shell-entry como library)

- **Status:** accepted

## Contexto

O ASST é carregado sob demanda pelo Shell (`journey-os-web`). Precisa de um ponto de entrada lazy
único, sem arrastar as features para o bundle inicial, e compatível com o registro no Shell via
module registry (ADR-004) e com a decisão global ADR-006 (module-entry como library).

## Decisão

1. O entry do módulo é a **library `libs/asst/shell-entry`** (importPath `@journeyos/asst`),
   carregada pelo Shell via `loadChildren` — seguindo o padrão consolidado no WRKS (ADR-006 global).
   `apps/asst` é um **host fino** (alvo de build/serve e base do e2e).
2. O `shell-entry` concentra `asst.contract.ts`, `asst.routes.ts` (`ASST_ROUTES[]`),
   `asst.bootstrap.ts`, `asst.permission-map.ts`, `asst.feature-flags.ts`, `asst.nav.config.ts` +
   barrel.
3. **Todas as features e componentes são `standalone` + `OnPush`**; sub-rotas carregam via
   `loadComponent`. Não há `NgModule` espalhado pelas features.
4. Guards aplicados nas rotas: `authGuard`, `empresaGuard`, `accessGuard('asst.<perm>')`.

## Alternativas consideradas

1. **Entry como `NgModule` dentro de `apps/asst`** — rejeitada: ADR-006 global moveu o entry para
   library (`@journeyos/<mod>`) para registro limpo no Shell; ASST segue o mesmo.
2. **Features como `NgModule`s** — rejeitada: standalone é o padrão Angular atual e evita boilerplate.
3. **Carregamento eager do módulo** — rejeitada: infla o bundle inicial; ASST não é precondição de
   bootstrap (diferente da Access Layer).

## Consequências

- **Positivas:** bundle inicial enxuto; registro no Shell uniforme (`@journeyos/asst`); paridade total
  com WRKS; lazy por feature.
- **Negativas:** uma indireção a mais (host fino + entry library); exige o generator
  `@journeyos/internal:module` para manter a estrutura consistente.

## Referências

- `04-frontend-architecture-direction.md` §2, §5
- ADR-004 (shell integration) · ADR-006 global (module-entry como library)
- WRKS ADR-003 + migração shell-entry (master plan, 2026-06-05)
