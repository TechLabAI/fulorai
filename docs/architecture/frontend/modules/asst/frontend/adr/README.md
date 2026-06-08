# ADRs — ASST · Frontend

> Decisões arquiteturais do módulo ASST (FE). Status: `proposed` | `accepted` | `superseded by ADR-YYY`.

## Índice

| ADR | Título | Status |
|---|---|---|
| [ADR-001](ADR-001-module-pattern.md) | Padrão module-pattern (slicing canônico de libs) | accepted |
| [ADR-002](ADR-002-signals-first-state.md) | Estado Signals-first (sem NgRx) | accepted |
| [ADR-003](ADR-003-lazy-module-entry.md) | Entry lazy do módulo (NgModule/shell-entry) | accepted |
| [ADR-004](ADR-004-shell-integration-via-module-registry.md) | Integração com Shell via module registry | accepted |
| [ADR-005](ADR-005-asset-studio-ai-composition.md) | Asset Studio — composição assistida síncrona com degradação graciosa | accepted |

## Mapa de Relações

```
ADR-001 (module-pattern)  ──base estrutural──▶ ADR-003 (lazy entry) ──▶ ADR-004 (shell integration)
ADR-002 (signals)  ──estado──────────▶ ADR-005 (Asset Studio / studioState)
ADR-005 depende do contrato BE /studio/compose (asst-service) e da degradação graciosa da IA
```

## Processo

- Toda decisão com tradeoff visível vira ADR (não texto solto).
- `proposed` → discutido → `accepted`. Mudança posterior cria novo ADR que marca o anterior como
  `superseded by ADR-YYY`.
- ADRs do módulo são consistentes com os ADRs **globais FE**, com os ADRs do `asst-service` (BE) e
  com o `module-pattern` canônico.

> **Nota:** o master plan FE pré-brief antecipava ADR-005 = `chunked-upload-strategy`. Como o brief
> autoritativo coloca upload de binário fora do MVP (referência por URL), ADR-005 trata da decisão
> crítica real do ASST FE: a composição assistida do Asset Studio e sua degradação graciosa. Upload
> chunked é roadmap pós-MVP e ganhará ADR próprio quando entrar.
