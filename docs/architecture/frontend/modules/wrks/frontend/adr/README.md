# ADRs — WRKS · Frontend

> Decisões arquiteturais do módulo WRKS (FE). Status: `proposed` | `accepted` | `superseded by ADR-YYY`.

## Índice

| ADR | Título | Status |
|---|---|---|
| [ADR-001](ADR-001-module-pattern.md) | Padrão module-pattern (slicing canônico de libs) | accepted |
| [ADR-002](ADR-002-signals-first-state.md) | Estado Signals-first (sem NgRx) | accepted |
| [ADR-003](ADR-003-lazy-module-entry.md) | `wrks.module.ts` lazy (NgModule só no entry) | accepted |
| [ADR-004](ADR-004-shell-integration-via-module-registry.md) | Integração com Shell via module registry | accepted |
| [ADR-005](ADR-005-multi-empresa-context.md) | Contexto multi-empresa e troca em runtime | accepted |

## Mapa de Relações

```
ADR-001 (module-pattern)  ──base estrutural──▶ ADR-003 (lazy module) ──▶ ADR-004 (shell integration)
ADR-002 (signals)  ──estado──────────▶ ADR-005 (multi-empresa context)
ADR-005 depende da Access Layer (@journeyos/shared/empresa-context + access-decision)
```

## Processo

- Toda decisão com tradeoff visível vira ADR (não texto solto).
- `proposed` → discutido → `accepted`. Mudança posterior cria novo ADR que marca o anterior como
  `superseded by ADR-YYY`.
- ADRs do módulo são consistentes com os ADRs **globais FE** e com os ADRs do `wrks-service` (BE).
