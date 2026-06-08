# ADRs — COMM (Communication Hub)

> Decisões arquiteturais do serviço `comm-service`. Cada decisão com tradeoff visível é um ADR.

## Índice

| ADR | Título | Status |
|---|---|---|
| [ADR-001](ADR-001-hexagonal-architecture.md) | Arquitetura hexagonal (Ports & Adapters) | accepted |
| [ADR-002](ADR-002-single-service-boundary.md) | Fronteira: single service (template + roteamento + disparo + entrega coesos) | accepted |
| [ADR-003](ADR-003-messaging-strategy.md) | Mensageria + IA: disparo async (Kafka/outbox + worker) + composição sync resiliente (TechLab AI) | accepted |
| [ADR-004](ADR-004-multitenant-strategy.md) | Multi-tenancy: schema-per-tenant (`emp_<slug>`), COMM só lê/escreve no schema do tenant | accepted |
| [ADR-005](ADR-005-channel-adapter-pattern.md) | Channel adapter pattern: `CanalEnvioPort` + adapters por canal (provedor-agnóstico) | accepted |

## Mapa de Relações

```
ADR-001 (hexagonal) ── base de todos
ADR-002 (single service) ── fronteira do serviço; depende de ADR-001
ADR-004 (multi-tenancy) ── alinhado ao global shared/multi-empresa.md (ADR-001 global)
ADR-005 (channel adapter) ── núcleo do domínio; concretiza "provedor é detalhe de adapter" (princípio 2 de 01)
   └── ADR-003 (mensageria/IA) ── disparo desacoplado (outbox+worker) emite eventos; Template Studio chama TechLab AI resiliente
```

## Processo

- Status possíveis: `proposed` | `accepted` | `superseded by ADR-YYY`.
- ADRs locais do serviço **não** substituem os ADRs globais (`docs/architecture/backend/adr/` e `docs/architecture/shared/`); refinam decisões específicas de COMM alinhadas a eles.
- Mudança de decisão = novo ADR com `superseded by`, nunca edição destrutiva do aceito.
