# ADRs — SALE · Frontend

Decisões arquiteturais do módulo FE **SALE** (Sales & Revenue). Cada decisão com tradeoff visível é um
ADR — não texto solto.

## Índice

| ADR | Título | Status |
|---|---|---|
| [ADR-001](ADR-001-module-pattern.md) | Padrão `module-pattern` (slicing canônico de libs) | accepted |
| [ADR-002](ADR-002-signals-first-state.md) | Estado Signals-first (sem NgRx) | accepted |
| [ADR-003](ADR-003-lazy-module-entry.md) | Entry lazy do módulo como library (`@journeyos/sale`) | accepted |
| [ADR-004](ADR-004-shell-integration-via-module-registry.md) | Integração com o Shell via module registry | accepted |
| [ADR-005](ADR-005-kanban-pipeline-rendering.md) | Renderização do pipeline como Kanban (drag-and-drop + optimistic move) | accepted |

## Mapa de Relações

```
ADR-001 (module-pattern)
   ├── ADR-002 (signals-first)        # estado dentro do slicing
   ├── ADR-003 (lazy entry library)   # como a app é carregada
   │      └── ADR-004 (shell registry)# como o Shell descobre/registra o módulo
   └── ADR-005 (kanban-pipeline)      # decisão de domínio crítica do SALE (usa signals do ADR-002)
```

## Processo

Status possíveis: `proposed` | `accepted` | `superseded by ADR-YYY`.
ADR-001..004 são **transversais** (replicados em todos os módulos FE, alinhados ao
`standards/module-pattern.md`). ADR-005 é a **decisão crítica específica do SALE**, extraída do brief:
o pipeline é renderizado como **Kanban** com **drag-and-drop para mover estágio**, usando **optimistic
update + rollback** (espelha `409 sale.oportunidade.ja-fechada`).
