# ADRs — SALE (Sales & Revenue)

> Decisões arquiteturais do `sale-service`. Status: `proposed` | `accepted` | `superseded by ADR-YYY`.
> Skeleton da camada de visão; refinadas/confirmadas nas specs.

## Índice

| ADR | Título | Status |
|---|---|---|
| [ADR-001](ADR-001-hexagonal-architecture.md) | Hexagonal architecture (Ports & Adapters) | accepted |
| [ADR-002](ADR-002-single-service-boundary.md) | Single-service boundary (sem decomposição no MVP) | accepted |
| [ADR-003](ADR-003-messaging-strategy.md) | Messaging strategy — eventos `oportunidade.*`/`compra.*` via Kafka/AWS MSK | accepted |
| [ADR-004](ADR-004-multitenant-strategy.md) | Multi-tenancy — schema-per-tenant (`emp_<slug>`) | accepted |
| [ADR-005](ADR-005-revenue-attribution-model.md) | Atribuição de receita — determinística, explicável + idempotência de compra | proposed |

## Mapa de Relações

```
ADR-001 (hexagonal) ── base de todas as demais
   ├── ADR-002 (single-service)   — fronteira do serviço
   ├── ADR-003 (messaging Kafka)   — porta out de eventos
   ├── ADR-004 (multi-tenancy)     — isolamento de persistência
   └── ADR-005 (atribuição/receita) — decisão crítica do domínio (depende de 001/003/004)
```

## Processo

- **proposed** → em discussão; pode mudar nas specs.
- **accepted** → vigente; mudanças exigem nova ADR (superseding).
- **superseded by ADR-YYY** → substituída; mantida para histórico.

ADR-005 está **proposed** porque o conjunto final de modelos de atribuição, a definição de
`contato_ref` para LTV e o contrato da fonte de compra (checkout/INTL Event Platform) dependem
de validação nas specs.
