# ADRs — JRNY · Frontend

Decisões arquiteturais do módulo FE **JRNY** (Journey & Routing). Cada decisão com tradeoff visível é
um ADR — não texto solto.

## Índice

| ADR | Título | Status |
|---|---|---|
| [ADR-001](ADR-001-module-pattern.md) | Padrão `module-pattern` (slicing canônico de libs) | accepted |
| [ADR-002](ADR-002-signals-first-state.md) | Estado Signals-first (sem NgRx) | accepted |
| [ADR-003](ADR-003-lazy-module-entry.md) | Entry lazy do módulo como library (`@journeyos/jrny`) | accepted |
| [ADR-004](ADR-004-shell-integration-via-module-registry.md) | Integração com o Shell via module registry | accepted |
| [ADR-005](ADR-005-canvas-builder-rendering.md) | Renderização do Journey Builder (estruturado, não canvas livre) | accepted |

## Mapa de Relações

```
ADR-001 (module-pattern)
   ├── ADR-002 (signals-first)        # estado dentro do slicing
   ├── ADR-003 (lazy entry library)   # como a app é carregada
   │      └── ADR-004 (shell registry)# como o Shell descobre/registra o módulo
   └── ADR-005 (builder rendering)    # decisão de domínio crítica do JRNY
```

## Processo

Status possíveis: `proposed` | `accepted` | `superseded by ADR-YYY`.
ADR-001..004 são **transversais** (replicados em todos os módulos FE, alinhados ao
`standards/module-pattern.md`). ADR-005 é a **decisão crítica específica do JRNY**, extraída do brief:
como renderizar o Journey Builder no MVP sem investir num canvas drag-and-drop livre (o canvas é
pós-MVP por construção — o BE expõe API/modelo, não o desenho visual).
