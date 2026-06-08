# ADR-003 — Entry lazy do módulo como library (`@journeyos/jrny`) — JRNY

- **Status:** accepted
- **Transversal:** sim (alinhado a ADR-006 global: module-entry como library)

## Contexto

O Shell `journey-os-web` carrega cada módulo de domínio sob demanda. O padrão evoluiu (ADR-006 global)
de "entry dentro de `apps/<mod>`" para **entry como library** `libs/<mod>/shell-entry` com importPath
`@journeyos/<mod>`, permitindo que o Shell faça `loadChildren` da library e registre o descriptor sem
acoplar ao app host.

## Decisão

O entry do JRNY é a library **`libs/jrny/shell-entry`** (importPath **`@journeyos/jrny`**), contendo:

- `jrny.routes.ts` — `MODULE_ROUTES[]` com `loadComponent` por feature.
- `jrny.contract.ts` — `ModuleMenuMetadata` (key `jrny`, route `/jrny/journeys`, deep links: builder,
  regras, decisões, analytics).
- `jrny.permission-map.ts` · `jrny.feature-flags.ts` · `jrny.nav.config.ts` · `jrny.bootstrap.ts`.
- `jrny.descriptor.ts` — `JRNY_MODULE_DESCRIPTOR` exportado para o Shell.

`apps/jrny/` permanece como **host fino** (alvo de build/serve isolado e base do `apps/jrny-e2e`),
carregando `@journeyos/jrny` via `loadChildren`. NgModule **apenas** se o entry exigir; features são
`standalone` + `OnPush`.

## Alternativas consideradas

- **Entry dentro de `apps/jrny`** — superada pelo ADR-006 (acoplava registro ao app host).
- **Sem host `apps/jrny`** — rejeitada: o host fino habilita build/serve/e2e isolados do módulo.

## Consequências

**Positivas:** Shell registra o módulo via importPath estável; build/e2e isolados; lazy real.
**Negativas:** uma library extra (`shell-entry`) — padronizada pelo gerador.

## Referências

- ADR-006 global (master plan FE) · ADR-003 de WRKS/ASST/INTL/LEAD/COMM · `standards/module-pattern.md`
