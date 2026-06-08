# ADR-003 — Entry lazy do módulo como library (`@journeyos/lead`) — LEAD

- **Status:** accepted
- **Transversal:** sim (alinhado a ADR-006 global: module-entry como library)

## Contexto

O Shell `journey-os-web` carrega cada módulo de domínio sob demanda. O padrão evoluiu (ADR-006 global)
de "entry dentro de `apps/<mod>`" para **entry como library** `libs/<mod>/shell-entry` com importPath
`@journeyos/<mod>`, permitindo que o Shell faça `loadChildren` da library e registre o descriptor sem
acoplar ao app host.

## Decisão

O entry do LEAD é a library **`libs/lead/shell-entry`** (importPath **`@journeyos/lead`**), contendo:

- `lead.routes.ts` — `MODULE_ROUTES[]` com `loadComponent` por feature.
- `lead.contract.ts` — `ModuleMenuMetadata` (key `lead`, route `/lead/leads`, deep links).
- `lead.permission-map.ts` · `lead.feature-flags.ts` · `lead.nav.config.ts` · `lead.bootstrap.ts`.
- `lead.descriptor.ts` — `LEAD_MODULE_DESCRIPTOR` exportado para o Shell.

`apps/lead/` permanece como **host fino** (alvo de build/serve isolado e base do `apps/lead-e2e`),
carregando `@journeyos/lead` via `loadChildren`. NgModule **apenas** se o entry exigir; features são
`standalone` + `OnPush`.

## Alternativas consideradas

- **Entry dentro de `apps/lead`** — superada pelo ADR-006 (acoplava registro ao app host).
- **Sem host `apps/lead`** — rejeitada: o host fino habilita build/serve/e2e isolados do módulo.

## Consequências

**Positivas:** Shell registra o módulo via importPath estável; build/e2e isolados; lazy real.
**Negativas:** uma library extra (`shell-entry`) — padronizada pelo gerador.

## Referências

- ADR-006 global (master plan FE) · ADR-003 de WRKS/ASST/INTL · `standards/module-pattern.md`
