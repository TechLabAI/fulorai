# ADR-001 — Padrão `module-pattern` (slicing canônico de libs) — JRNY

- **Status:** accepted
- **Transversal:** sim (alinhado a `docs/architecture/frontend/standards/module-pattern.md`)

## Contexto

O Journey OS FE é um workspace Nx com múltiplos módulos de domínio (WRKS, ASST, INTL, LEAD, COMM,
JRNY, …). Cada módulo precisa de fronteiras claras, lazy-loading, e regras de dependência verificáveis
(ESLint Nx boundaries). WRKS, ASST, INTL, LEAD e COMM já adotaram o `module-pattern` canônico.

## Decisão

JRNY replica **100%** o slicing canônico do `module-pattern`:

```
apps/jrny/                          # host fino (type:app, scope:jrny)
libs/jrny/
  shell-entry/   (type:domain)      # entry como library @journeyos/jrny
  feature-*/     (type:feature)     # uma lib por feature (journey-list, journey-builder, stage-editor,
                                     #   routing-engine, decision-log, journey-analytics)
  data-access/   (type:data-access) # services HTTP + facades de signal
  access/        (type:domain)      # guards do módulo (jrny.*)
  integration/   (type:domain)      # ModuleShellIntegrationService
  navigation/    (type:domain)      # breadcrumb/menu state
  ui/            (type:ui)          # componentes locais (stage-list, decision-timeline, etc.)
  styles/        (type:ui)          # SCSS isolado
```

Tags Nx: `scope:jrny` em todas as libs + `type:{app,feature,domain,data-access,ui}`. Direções de
dependência conforme `nx-boundaries.md`. Proibido importar `scope:` de outro módulo.

## Alternativas consideradas

- **Lib única `libs/jrny`** com tudo dentro — rejeitada: impede lazy granular e enfraquece boundaries.
- **Slicing ad-hoc por JRNY** — rejeitada: quebra a uniformidade entre módulos e o gerador
  `@journeyos/internal:module`.

## Consequências

**Positivas:** uniformidade entre módulos; boundaries verificáveis por lint; geração automatizada pelo
plugin Nx; lazy por feature. **Negativas:** mais libs/boilerplate por módulo (mitigado pelo gerador) —
JRNY é o módulo com mais features (6), então a uniformidade paga ainda mais.

## Referências

- `docs/architecture/frontend/standards/module-pattern.md` · `nx-boundaries.md`
- ADR-001 dos módulos WRKS/ASST/INTL/LEAD/COMM (mesmo padrão)
