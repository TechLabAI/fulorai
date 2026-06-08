# ADR-001 — Padrão `module-pattern` (slicing canônico de libs) — SALE

- **Status:** accepted
- **Transversal:** sim (alinhado a `docs/architecture/frontend/standards/module-pattern.md`)

## Contexto

O Journey OS FE é um workspace Nx com múltiplos módulos de domínio (WRKS, ASST, INTL, LEAD, COMM,
SALE, …). Cada módulo precisa de fronteiras claras, lazy-loading, e regras de dependência verificáveis
(ESLint Nx boundaries). WRKS, ASST, INTL, LEAD e COMM já adotaram o `module-pattern` canônico.

## Decisão

SALE replica **100%** o slicing canônico do `module-pattern`:

```
apps/sale/                          # host fino (type:app, scope:sale)
libs/sale/
  shell-entry/   (type:app)         # entry como library @journeyos/sale
  feature-*/     (type:feature)     # uma lib por feature (pipeline, opportunity, offer, purchase,
                                     #   attribution, revenue-dashboard)
  data-access/   (type:data-access) # services HTTP + facades de signal
  access/        (type:domain)      # guards do módulo
  integration/   (type:domain)      # ModuleShellIntegrationService
  navigation/    (type:domain)      # breadcrumb/menu state
  ui/            (type:ui)          # componentes locais (kanban-board, attribution-breakdown, etc.)
  styles/        (type:ui)          # SCSS isolado
```

Tags Nx: `scope:sale` em todas as libs + `type:{app,feature,domain,data-access,ui}`. Direções de
dependência conforme `nx-boundaries.md`. Proibido importar `scope:` de outro módulo — as dependências
soft de LEAD/INTL são lidas **só via API BE**, nunca por import de `scope:lead`/`scope:intl`.

## Alternativas consideradas

- **Lib única `libs/sale`** com tudo dentro — rejeitada: impede lazy granular e enfraquece boundaries.
- **Slicing ad-hoc por SALE** — rejeitada: quebra a uniformidade entre módulos e o gerador
  `@journeyos/internal:module`.

## Consequências

**Positivas:** uniformidade entre módulos; boundaries verificáveis por lint; geração automatizada pelo
plugin Nx; lazy por feature. **Negativas:** mais libs/boilerplate por módulo (mitigado pelo gerador).

## Referências

- `docs/architecture/frontend/standards/module-pattern.md` · `nx-boundaries.md`
- ADR-001 dos módulos WRKS/ASST/INTL/LEAD/COMM (mesmo padrão)
