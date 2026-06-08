# Module Pattern (Journey OS Frontend)

> **Status:** padrão obrigatório. Substitui o vocabulário herdado do projeto-modelo ("hub/tool/tax-map").
> Este documento é a **fonte canônica** da estrutura e da nomenclatura de um módulo FE do Journey OS.

## Por que este documento existe

A camada de arquitetura FE foi inicialmente templada a partir de um projeto-modelo ("Hub SaaS")
que usava o conceito de **"tool"**, o scope npm **`@hub`** e o rótulo de padrão **"tax-map"**.
Isso **conflita** com o Journey OS, cujo `CLAUDE.md` determina: _"Never introduce 'tool/PREFIX'
concept -- here only MODULE exists"_ e cujo npmScope é **`@journeyos`**.

Este standard **aposenta** esse vocabulário e fixa o do Journey OS: a unidade é o **MÓDULO**
(`WRKS`, `LEAD`, …), o scope é **`@journeyos`**, e o esqueleto é gerado pelo plugin Nx local
**`@journeyos/internal:module`**.

## Rosetta — de "hub/tool" para "module/journeyos"

| Herdado (hub/bosq) | Journey OS (canônico) |
|---|---|
| "tool" (unidade) | **module** (módulo) |
| gerador `@hub/internal:tool` | **`@journeyos/internal:module`** |
| `@hub/shared/*` | **`@journeyos/shared/*`** |
| `@hub/patterns-*`, `@hub/observability` | `@journeyos/shared/*` (promovido) |
| padrão **"tax-map"** | **"module pattern"** (este doc) |
| pasta `tool-module/` | **`<module>-module/`** (ex.: `wrks-module/`) |
| `tool.module.ts` | **`<module>.module.ts`** |
| `tool.contract.ts` | **`<module>.contract.ts`** |
| `tool.bootstrap.ts` / `tool.routes.ts` / `tool.permission-map.ts` / `tool.feature-flags.ts` / `tool.nav.config.ts` | `<module>.{bootstrap,routes,permission-map,feature-flags,nav.config}.ts` |
| `TOOL_KEY` | **`MODULE_KEY`** |
| `ToolMenuMetadata` | **`ModuleMenuMetadata`** |
| `ToolPermissionMap` | **`ModulePermissionMap`** |
| `ToolFeatureFlags` | **`ModuleFeatureFlags`** |
| `ToolShellIntegration` / `<Tool>ShellIntegrationService` | **`ModuleShellIntegration`** / **`<Module>ShellIntegrationService`** |
| `tool-descriptors.ts` (Shell) | **`module-descriptors.ts`** |
| `toolGuard` | **`moduleGuard`** (ou guard específico do módulo) |
| `apps/<tool>` · `libs/<tool>/*` | **`apps/<module>` · `libs/<module>/*`** |
| `service:` no generator-config | **`module:`** |

> Em prosa, usar "**módulo**" (pt-BR) ou "module" (en-US técnico) — nunca "tool".

## Estrutura canônica de um módulo (module slicing)

```
libs/<module>/shell-entry/   (type:app)         # ENTRY como library — importPath @journeyos/<module> (ADR-006)
└── src/lib/
    ├── <module>.module.ts                      # único NgModule do módulo
    ├── <module>.contract.ts                    # MODULE_KEY + ModuleMenuMetadata + permissions + flags
    ├── <module>.bootstrap.ts                   # init/destroy lifecycle
    ├── <module>.routes.ts                      # <MODULE>_ROUTES[]
    ├── <module>.permission-map.ts              # ModulePermissionMap
    ├── <module>.feature-flags.ts               # ModuleFeatureFlags (defaultState)
    ├── <module>.nav.config.ts                  # navegação/breadcrumb
    └── <module>.descriptor.ts                  # <MODULE>_MODULE_DESCRIPTOR (consumido pelo Shell)

apps/<module>/             (type:app)           # host fino: app.routes carrega @journeyos/<module>
libs/<module>/                                  # libs do módulo
├── access/            (type:domain)            # guards específicos
├── data-access/       (type:data-access)       # *ApiService + facades signals
├── feature-<X>/       (type:feature)           # uma por feature
├── integration/       (type:domain)            # <Module>ShellIntegrationService
├── navigation/        (type:domain)            # breadcrumbs/menu state
├── ui/                (type:ui, opcional)       # componentes locais
└── styles/            (type:ui)                 # SCSS isolado

apps/<module>-e2e/                              # Playwright (specs dos .feature)
```

> **Por que a entry é uma library (ADR-006):** o Shell precisa importar o `<module>.descriptor.ts`
> para registrar o módulo, mas apps Nx não importam outros apps. Logo a entry vive numa lib com
> `importPath @journeyos/<module>`; `apps/<module>` é só um host fino (`nx serve/build` + base do e2e).

Tags Nx: `scope:<module>` + `type:{feature|data-access|domain|ui}` (ver `nx-boundaries.md`).
Regras: standalone + OnPush + Signals; `NgModule` **apenas** no `<module>.module.ts`; módulo só
importa `scope:<module>` + `scope:shared`.

## O gerador `@journeyos/internal:module`

- **Plugin Nx local:** `frontend/libs/internal-nx-plugin` (npm `@journeyos/internal`).
- **Invocação:** `npx nx g @journeyos/internal:module --name=<module>`.
- **Document-driven:** lê `docs/architecture/frontend/modules/<module>/frontend/frontend-spec/generator-config.yml`
  e deriva: entry lib `libs/<module>/shell-entry` (`@journeyos/<module>`) + libs do módulo + host `apps/<module>`
  + `apps/<module>-e2e`. Idempotente. O Shell registra o módulo importando `@journeyos/<module>`.
- **Gates pós-scaffold:** `nx lint <module>` → `nx test <module>` → `nx build <module>`.

> Pré-condição: as **shared libs** (`@journeyos/shared/*`) e o **App Shell** precisam existir antes
> de scaffoldar qualquer módulo — senão o código gerado não compila (imports não resolvidos).

## Relação com o backend

O BE usa **scripts Python** (`be-module-generator.py`) para o mesmo papel. O FE escolheu um
**plugin Nx local** (idiomático ao workspace Angular/Nx). Ambos são document-driven a partir do
`generator-config.yml` do módulo. A unidade conceitual ("MÓDULO") e o prefixo de issue
(`<MODULE>` / `FE-<MODULE>`) são compartilhados.

## Referências

- `docs/architecture/frontend/standards/nx-boundaries.md` — tags + direções
- `docs/architecture/frontend/standards/access-layer-contracts.md` — Access Layer
- `docs/architecture/shared/blueprint-core.md` — modelo mental App + módulos + shared
- `CLAUDE.md` — "only MODULE exists" (regra que este doc concretiza no FE)
