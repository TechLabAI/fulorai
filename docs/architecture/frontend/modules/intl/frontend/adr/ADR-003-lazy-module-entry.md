# ADR-003 — Entry lazy como library (`@journeyos/intl`)

- **Status:** accepted

## Contexto

O Shell (`journey-os-web`) carrega cada módulo lazy e registra seu descriptor. A decisão global
**ADR-006 FE** estabeleceu que o entry do módulo é uma **library** (não um `NgModule` dentro da
app), para que o Shell possa importar o descriptor sem acoplar ao host.

## Decisão

O entry de INTL é a **library** `@journeyos/intl` em `libs/intl/shell-entry`, contendo:
`intl.contract.ts`, `intl.routes.ts` (`MODULE_ROUTES[]`), `intl.permission-map.ts`,
`intl.feature-flags.ts`, `intl.nav.config.ts`, `intl.bootstrap.ts` e `intl.descriptor.ts`
(`INTL_MODULE_DESCRIPTOR`). O `apps/intl` é um **host fino** que carrega esse entry-lib via
`loadChildren`. **Não há `NgModule` de domínio**; features e componentes são `standalone` + `OnPush`.

## Alternativas consideradas

- **`NgModule` lazy dentro de `apps/intl`** (padrão antigo, pré-ADR-006) — rejeitada: o Shell
  precisaria acoplar à app; WRKS já foi migrado para entry-lib.
- **Standalone routes sem entry-lib dedicada** — rejeitada: perde o ponto único de contrato/descriptor
  que o registry do Shell consome.

## Consequências

- **Positivas:** Shell importa `INTL_MODULE_DESCRIPTOR` de `@journeyos/intl` sem acoplar ao host;
  consistente com WRKS e com o gerador `@journeyos/internal:module`.
- **Negativas:** uma lib a mais (`shell-entry`); o host `apps/intl` é quase vazio (aceitável —
  serve de alvo de build/serve e base do e2e).

## Referências

- ADR-006 global FE (module-entry como library) · WRKS ADR-003 (espelho)
- `docs/architecture/frontend/plans/architecture-master-plan.md` (decisão ADR-006, 2026-06-05)
