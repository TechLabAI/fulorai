# ADRs — GWY (API Gateway)

> Decisões arquiteturais do serviço `journey-os-api-gateway` (`com.journeyos.gwy`).
> Status possíveis: `proposed` | `accepted` | `superseded by ADR-YYY`.

## Índice

| ADR | Título | Status |
|-----|--------|--------|
| [ADR-001](ADR-001-hexagonal-architecture.md) | Hexagonal architecture no edge reativo | accepted |
| [ADR-002](ADR-002-gateway-routing-strategy.md) | Estratégia de roteamento (descoberta dinâmica via Eureka) | accepted |
| [ADR-003](ADR-003-auth-filter.md) | Autenticação na borda via filtro global de JWT | accepted |
| [ADR-004](ADR-004-multitenant-strategy.md) | Multi-tenancy: resolução e propagação de `empresa` | accepted |
| [ADR-005](ADR-005-rate-limiting.md) | Rate-limiting distribuído com Redis | accepted |

## Mapa de Relações

```
ADR-001 (hexagonal) ──base──> ADR-002, ADR-003, ADR-004, ADR-005
ADR-003 (auth) ──produz claims──> ADR-004 (tenant context)
ADR-003 (auth) ──fornece chave de rate-limit──> ADR-005 (rate-limit por usuário/tenant)
ADR-002 (routing) ──depende──> REG (Eureka)
```

## Processo

- Toda decisão com tradeoff visível vira ADR (não texto solto nos docs 01–06).
- ADRs nascem `proposed`; ao serem aceitas na revisão da vision passam a `accepted`.
- Decisões substituídas: marcar `superseded by ADR-YYY` e referenciar a sucessora.
- ADRs de domínio de negócio **não se aplicam** ao GWY (módulo de infraestrutura).
