# ADRs — COMM · Frontend

> Decisões arquiteturais do módulo COMM (FE). Status: `proposed` | `accepted` | `superseded by ADR-YYY`.

## Índice

| ADR | Título | Status |
|---|---|---|
| [ADR-001](ADR-001-module-pattern.md) | Padrão module-pattern (slicing canônico de libs) | accepted |
| [ADR-002](ADR-002-signals-first-state.md) | Estado Signals-first (sem NgRx) | accepted |
| [ADR-003](ADR-003-lazy-module-entry.md) | Entry lazy do módulo (shell-entry como library) | accepted |
| [ADR-004](ADR-004-shell-integration-via-module-registry.md) | Integração com Shell via module registry | accepted |
| [ADR-005](ADR-005-delivery-status-tracking.md) | Rastreio do ciclo de vida da mensagem por polling com backoff | accepted |

## Mapa de Relações

```
ADR-001 (module-pattern)  ──base estrutural──▶ ADR-003 (lazy entry) ──▶ ADR-004 (shell integration)
ADR-002 (signals)  ──estado──────────▶ ADR-005 (delivery tracking / polling como signal)
ADR-005 depende do contrato BE (GET /messages/{id}/events + estados de entrega) e da ausência de
        endpoint de streaming (callbacks de provedor chegam ao BE de forma assíncrona via webhooks).
```

## Processo

- Toda decisão com tradeoff visível vira ADR (não texto solto).
- `proposed` → discutido → `accepted`. Mudança posterior cria novo ADR que marca o anterior como
  `superseded by ADR-YYY`.
- ADRs do módulo são consistentes com os ADRs **globais FE**, com os ADRs do `comm-service` (BE) e
  com o `module-pattern` canônico.

> **Nota:** o master plan FE pré-brief antecipava ADR-005 = `rich-text-template-editor`. Como o brief
> autoritativo coloca **editor visual/WYSIWYG rico fora do MVP** (o MVP é editor de texto/HTML com
> placeholders `{{variavel}}`), ADR-005 trata da decisão crítica real do COMM FE: como refletir o
> **ciclo de vida de entrega em tempo quase real** sem endpoint de streaming no BE (polling com
> backoff). A degradação graciosa do Template Studio (IA) segue o padrão já estabelecido e aceito no
> ASST (ADR-005 do ASST) e é registrada como **princípio** (01 §6.4, 04, 05 §5), não ADR próprio, por
> não introduzir tradeoff novo. Um editor rich-text/WYSIWYG, se entrar pós-MVP, ganhará ADR próprio.
