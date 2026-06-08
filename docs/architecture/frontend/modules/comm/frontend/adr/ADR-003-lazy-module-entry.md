# ADR-003 — Entry lazy do módulo (shell-entry como library)

- **Status:** accepted

## Contexto

O COMM é carregado sob demanda pelo Shell (`journey-os-web`). Precisa de um ponto de entrada lazy
único, sem arrastar as features para o bundle inicial, e compatível com o registro no Shell via
module registry (ADR-004) e com a decisão global ADR-006 (module-entry como library).

## Decisão

1. O entry do módulo é a **library `libs/comm/shell-entry`** (importPath `@journeyos/comm`),
   carregada pelo Shell via `loadChildren` — seguindo o padrão consolidado no WRKS/ASST/INTL
   (ADR-006 global). `apps/comm` é um **host fino** (alvo de build/serve e base do e2e).
2. O `shell-entry` concentra `comm.contract.ts`, `comm.routes.ts` (`COMM_ROUTES[]`),
   `comm.bootstrap.ts`, `comm.permission-map.ts`, `comm.feature-flags.ts`, `comm.nav.config.ts` +
   barrel.
3. **Todas as features e componentes são `standalone` + `OnPush`**; sub-rotas carregam via
   `loadComponent`. Não há `NgModule` espalhado pelas features.
4. Guards aplicados nas rotas: `authGuard`, `empresaGuard`, `accessGuard('comm.<perm>')`.

## Alternativas consideradas

1. **Entry como `NgModule` dentro de `apps/comm`** — rejeitada: ADR-006 global moveu o entry para
   library (`@journeyos/<mod>`) para registro limpo no Shell; COMM segue o mesmo.
2. **Features como `NgModule`s** — rejeitada: standalone é o padrão Angular atual e evita boilerplate.
3. **Carregamento eager do módulo** — rejeitada: infla o bundle inicial; COMM não é precondição de
   bootstrap (diferente da Access Layer).

## Consequências

- **Positivas:** bundle inicial enxuto; registro no Shell uniforme (`@journeyos/comm`); paridade total
  com WRKS/ASST/INTL; lazy por feature.
- **Negativas:** uma indireção a mais (host fino + entry library); exige o generator
  `@journeyos/internal:module` para manter a estrutura consistente.

## Referências

- `04-frontend-architecture-direction.md` §2, §5
- ADR-004 (shell integration) · ADR-006 global (module-entry como library)
- WRKS ADR-003 + migração shell-entry (master plan, 2026-06-05)
