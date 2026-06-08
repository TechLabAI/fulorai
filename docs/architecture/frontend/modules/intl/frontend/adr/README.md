# ADRs — INTL · Frontend

> Decisões arquiteturais do módulo INTL (FE). Status: `proposed` | `accepted` | `superseded by ADR-YYY`.

## Índice

| ADR | Título | Status |
|---|---|---|
| [ADR-001](ADR-001-module-pattern.md) | Padrão module-pattern (slicing canônico de libs) | accepted |
| [ADR-002](ADR-002-signals-first-state.md) | Estado Signals-first (sem NgRx) | accepted |
| [ADR-003](ADR-003-lazy-module-entry.md) | Entry lazy como library (`@journeyos/intl`) | accepted |
| [ADR-004](ADR-004-shell-integration-via-module-registry.md) | Integração com Shell via module registry | accepted |
| [ADR-005](ADR-005-ai-copilot-streaming.md) | Render da resposta do Copilot: request/response no MVP; streaming (SSE) diferido | accepted |

## Mapa de Relações

```
ADR-001 (module-pattern)  ──base estrutural──▶ ADR-003 (entry-lib) ──▶ ADR-004 (shell integration)
ADR-002 (signals)  ──estado──────────▶ ADR-005 (copilot answer rendering)
ADR-005 depende do contrato síncrono do intl-service (api-contract.md, POST .../perguntar → 200)
ADR-003/004 alinhados ao ADR-006 global FE (module-entry como library)
```

## Processo

- Toda decisão com tradeoff visível vira ADR (não texto solto).
- `proposed` → discutido → `accepted`. Mudança posterior cria novo ADR que marca o anterior como
  `superseded by ADR-YYY`.
- ADRs do módulo são consistentes com os ADRs **globais FE** e com os ADRs do `intl-service` (BE),
  notadamente o ADR-005 BE (RAG fundamentado / degradação graciosa).
