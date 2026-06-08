# ADR-003 — Entry lazy do módulo como library (`@journeyos/sale`) — SALE

- **Status:** accepted
- **Transversal:** sim (alinhado a ADR-006 global: module-entry como library)

## Contexto

O Shell `journey-os-web` carrega cada módulo de domínio sob demanda. O padrão evoluiu (ADR-006 global)
de "entry dentro de `apps/<mod>`" para **entry como library** `libs/<mod>/shell-entry` com importPath
`@journeyos/<mod>`, permitindo que o Shell faça `loadChildren` da library e registre o descriptor sem
acoplar ao app host.

## Decisão

O entry do SALE é a library **`libs/sale/shell-entry`** (importPath **`@journeyos/sale`**), contendo:

- `sale.routes.ts` — `SALE_ROUTES[]` com `loadComponent` por feature.
- `sale.contract.ts` — `ModuleMenuMetadata` (key `sale`, route `/sale/pipeline`, deep links).
- `sale.permission-map.ts` · `sale.feature-flags.ts` · `sale.nav.config.ts` · `sale.bootstrap.ts`.
- `sale.descriptor.ts` — `SALE_MODULE_DESCRIPTOR` exportado para o Shell.

`apps/sale/` permanece como **host fino** (alvo de build/serve isolado e base do `apps/sale-e2e`),
carregando `@journeyos/sale` via `loadChildren`. NgModule **apenas** se o entry exigir; features são
`standalone` + `OnPush`.

## Alternativas consideradas

- **Entry dentro de `apps/sale`** — superada pelo ADR-006 (acoplava registro ao app host).
- **Sem host `apps/sale`** — rejeitada: o host fino habilita build/serve/e2e isolados do módulo.

## Consequências

**Positivas:** Shell registra o módulo via importPath estável; build/e2e isolados; lazy real.
**Negativas:** uma library extra (`shell-entry`) — padronizada pelo gerador.

## Referências

- ADR-006 global (master plan FE) · ADR-003 de WRKS/ASST/INTL/LEAD/COMM · `standards/module-pattern.md`
