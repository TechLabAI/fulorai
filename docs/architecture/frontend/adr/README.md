# Frontend ADRs (globais / transversais)

> Decisões arquiteturais que valem para **todo o frontend** (não específicas de um módulo).
> ADRs por módulo vivem em `docs/architecture/frontend/modules/<module>/frontend/adr/`.

## Índice

| ADR | Título | Status |
|---|---|---|
| ADR-001 | Angular standalone + Signals | _reservado_ |
| ADR-002 | Nx monorepo boundaries | _reservado_ |
| ADR-003 | Access Layer contracts | _reservado_ |
| ADR-004 | Lazy-loading strategy | _reservado_ |
| ADR-005 | Design tokens / UI library | _reservado_ |
| [ADR-006](ADR-006-module-entry-as-library.md) | Module entry como library (`@journeyos/<mod>`) | **accepted** |

> Slots 001–005 estão reservados para os ADRs transversais planejados (ainda não materializados).
> ADR-006 foi o primeiro materializado por necessidade (registro Shell↔módulo).

## Processo

- `proposed` → discutido → `accepted`. Mudança posterior cria novo ADR que marca o anterior como
  `superseded by ADR-YYY`.
- ADRs globais são consistentes com `docs/architecture/frontend/standards/*` e com os ADRs de módulo.
