# ADRs — LEAD (Lead Intelligence & Qualification)

> Decisões arquiteturais do `lead-service`. Status: `proposed` | `accepted` | `superseded by ADR-YYY`.
> Skeleton da camada de visão; refinadas/confirmadas nas specs.

## Índice

| ADR | Título | Status |
|---|---|---|
| [ADR-001](ADR-001-hexagonal-architecture.md) | Hexagonal architecture (Ports & Adapters) | accepted |
| [ADR-002](ADR-002-single-service-boundary.md) | Single-service boundary (sem decomposição no MVP) | accepted |
| [ADR-003](ADR-003-messaging-strategy.md) | Messaging strategy — eventos `lead.*` via Kafka/AWS MSK | accepted |
| [ADR-004](ADR-004-multitenant-strategy.md) | Multi-tenancy — schema-per-tenant (`emp_<slug>`) | accepted |
| [ADR-005](ADR-005-maturity-score-model.md) | Maturity Score (6D) — determinístico, explicável, assist IA opcional | proposed |

## Mapa de Relações

```
ADR-001 (hexagonal) ── base de todas as demais
   ├── ADR-002 (single-service)  — fronteira do serviço
   ├── ADR-003 (messaging Kafka)  — porta out de eventos
   ├── ADR-004 (multi-tenancy)    — isolamento de persistência
   └── ADR-005 (Maturity Score)   — decisão crítica do domínio (depende de 001/003/004)
```

## Processo

- **proposed** → em discussão; pode mudar nas specs.
- **accepted** → vigente; mudanças exigem nova ADR (superseding).
- **superseded by ADR-YYY** → substituída; mantida para histórico.

ADR-005 está **proposed** porque a calibração final das 6 dimensões e o contrato da capacidade
`qualification` da TechLab AI dependem do sync upstream (P3) e da validação com growth.
