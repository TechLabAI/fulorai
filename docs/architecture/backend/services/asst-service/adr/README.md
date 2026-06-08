# ADRs — ASST (Asset Hub)

> Decisões arquiteturais do serviço `asst-service`. Cada decisão com tradeoff visível é um ADR.

## Índice

| ADR | Título | Status |
|---|---|---|
| [ADR-001](ADR-001-hexagonal-architecture.md) | Arquitetura hexagonal (Ports & Adapters) | accepted |
| [ADR-002](ADR-002-single-service-boundary.md) | Fronteira: single service (asset + studio + busca coesos) | accepted |
| [ADR-003](ADR-003-messaging-strategy.md) | Mensageria + IA: eventos async (Kafka) + composição sync resiliente (TechLab AI) | accepted |
| [ADR-004](ADR-004-multitenant-strategy.md) | Multi-tenancy: schema-per-tenant (`emp_<slug>`), ASST só lê/escreve no schema do tenant | accepted |
| [ADR-005](ADR-005-asset-versioning.md) | Versionamento imutável + máquina de estados de aprovação/publicação | accepted |

## Mapa de Relações

```
ADR-001 (hexagonal) ── base de todos
ADR-002 (single service) ── fronteira do serviço; depende de ADR-001
ADR-004 (multi-tenancy) ── alinhado ao global shared/multi-empresa.md (ADR-001 global)
ADR-005 (versionamento+aprovação) ── núcleo do domínio; concretiza as invariantes de 03
   └── ADR-003 (mensageria/IA) ── publicação emite evento; Asset Studio chama TechLab AI resiliente
```

## Processo

- Status possíveis: `proposed` | `accepted` | `superseded by ADR-YYY`.
- ADRs locais do serviço **não** substituem os ADRs globais (`docs/architecture/backend/adr/` e `docs/architecture/shared/`); refinam decisões específicas de ASST alinhadas a eles.
- Mudança de decisão = novo ADR com `superseded by`, nunca edição destrutiva do aceito.
