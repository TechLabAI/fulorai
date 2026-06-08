# ADR-006 — Module entry como library (`@journeyos/<mod>`)

- **Status:** accepted (2026-06-05)
- **Escopo:** global FE (todos os módulos)
- **Supersede:** ajusta o `module-pattern.md` (a entry deixa de viver em `apps/<mod>`)

> ADRs globais FE 001–005 (angular-standalone-signals, nx-boundaries, access-layer, lazy-loading,
> design-tokens) estão **reservados/pendentes**; este é o primeiro ADR global materializado.

## Contexto

No padrão de módulo, a *entry* (contract, module, routes, permission-map, feature-flags, bootstrap,
nav.config, descriptor) vivia em `apps/<mod>/src/app/<mod>-module/`. Ao montar o **registro de
módulos no Shell** (`journey-os-web`), descobriu-se um bloqueio estrutural:

- O Shell precisa **importar** o `<mod>.descriptor.ts` para registrar o módulo (menu, lazy route).
- Mas **apps Nx não importam outros apps** (boundary `@nx/enforce-module-boundaries`) e um app **não
  tem `importPath`** — logo `@journeyos/<mod>` não existia e o Shell não conseguia importar a entry.

## Decisão

A **entry do módulo vira uma library**: `libs/<mod>/shell-entry`, com `importPath` **`@journeyos/<mod>`**
e tag `scope:<mod>` `type:app`. Ela exporta (barrel `index.ts`) contract + module + routes +
permission-map + feature-flags + bootstrap + nav.config + **`<MOD>_MODULE_DESCRIPTOR`**.

- O **Shell** importa `@journeyos/<mod>` em `config/module-descriptors.ts` e popula `MODULE_DESCRIPTORS`
  (boundary `scope:web → scope:<mod>` é permitido).
- `apps/<mod>` permanece como **host fino**: seu `app.routes.ts` apenas `loadChildren: () =>
  import('@journeyos/<mod>').then(m => m.<Mod>Module)`. Serve de alvo buildável/serveável (`nx serve/
  build <mod>`) e base do web-server do e2e.

## Alternativas consideradas

1. **Manter a entry em `apps/<mod>` + lib-ponte só para o descriptor** — rejeitada: mantém um app
   carregando outro, mais indireção, não resolve o `importPath` de forma limpa.
2. **Shell carrega a entry por path relativo a `apps/<mod>`** — rejeitada: viola boundary e acopla o
   Shell ao layout de outro app.

## Consequências

- **Positivas:** Shell importa `@journeyos/<mod>` de forma limpa; registro de módulos automatizável
  (gerador v3); boundaries respeitadas; o módulo é reusável/testável como lib.
- **Negativas:** um app-host fino por módulo (custo pequeno); módulos já scaffoldados (WRKS) exigem
  migração leve da entry `apps/<mod>/.../<mod>-module` → `libs/<mod>/shell-entry` (feita para WRKS).

## Implementação

- Gerador `@journeyos/internal:module` **v3**: gera `libs/<mod>/shell-entry` (importPath
  `@journeyos/<mod>`), escreve a entry lá + barrel, e (re)escreve o `app.routes.ts` do host.
- WRKS migrado e verde: `build wrks` ✅, `build/lint journey-os-web` ✅ (com `WRKS_MODULE_DESCRIPTOR`
  registrado), `lint wrks-shell-entry` ✅.

## Referências

- `docs/architecture/frontend/standards/module-pattern.md` (atualizado)
- `docs/architecture/frontend/plans/framework-improvements.md` §4.4
- `frontend/libs/internal-nx-plugin/internal/src/generators/module/generator.ts`
