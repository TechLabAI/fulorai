# ADR-001 — Padrão `module-pattern` (slicing canônico de libs) — LEAD

- **Status:** accepted
- **Transversal:** sim (alinhado a `docs/architecture/frontend/standards/module-pattern.md`)

## Contexto

O Journey OS FE é um workspace Nx com múltiplos módulos de domínio (WRKS, ASST, INTL, LEAD, …). Cada
módulo precisa de fronteiras claras, lazy-loading, e regras de dependência verificáveis (ESLint Nx
boundaries). WRKS, ASST e INTL já adotaram o `module-pattern` canônico.

## Decisão

LEAD replica **100%** o slicing canônico do `module-pattern`:

```
apps/lead/                          # host fino (type:app, scope:lead)
libs/lead/
  shell-entry/   (type:domain)      # entry como library @journeyos/lead
  feature-*/     (type:feature)     # uma lib por feature (lead-list, lead-detail, maturity-score,
                                     #   segmentation, survey, qualification-rules)
  data-access/   (type:data-access) # services HTTP + facades de signal
  access/        (type:domain)      # guards do módulo
  integration/   (type:domain)      # ModuleShellIntegrationService
  navigation/    (type:domain)      # breadcrumb/menu state
  ui/            (type:ui)          # componentes locais (score-radar, etc.)
  styles/        (type:ui)          # SCSS isolado
```

Tags Nx: `scope:lead` em todas as libs + `type:{app,feature,domain,data-access,ui}`. Direções de
dependência conforme `nx-boundaries.md`. Proibido importar `scope:` de outro módulo.

## Alternativas consideradas

- **Lib única `libs/lead`** com tudo dentro — rejeitada: impede lazy granular e enfraquece boundaries.
- **Slicing ad-hoc por LEAD** — rejeitada: quebra a uniformidade entre módulos e o gerador
  `@journeyos/internal:module`.

## Consequências

**Positivas:** uniformidade entre módulos; boundaries verificáveis por lint; geração automatizada pelo
plugin Nx; lazy por feature. **Negativas:** mais libs/boilerplate por módulo (mitigado pelo gerador).

## Referências

- `docs/architecture/frontend/standards/module-pattern.md` · `nx-boundaries.md`
- ADR-001 dos módulos WRKS/ASST/INTL (mesmo padrão)
