# Issues Map — MIG (`journey-os-migrations`)

Total: **8 funcionais** (MIG-001..008) + **2 integração** (INT-MIG-001..002) = **10 issues**.

> MIG é infra (Flyway centralizado). Conjunto enxuto vs. módulos de domínio — não há
> agregados/eventos/CRUD de negócio.

## Por prioridade

| P | Issues |
|---|--------|
| P1 | MIG-001, MIG-002, INT-MIG-001 |
| P2 | MIG-003, MIG-004, MIG-005 |
| P3 | MIG-006, INT-MIG-002 |
| P5 | MIG-007 |
| P7 | MIG-008 |

## Por SPEC

| SPEC | Issues |
|------|--------|
| SPEC-01 (API surface / actuator) | MIG-001, MIG-008 |
| SPEC-04 (data model & migrations) | MIG-001, MIG-002, MIG-003, MIG-004, MIG-005, INT-MIG-002 |
| SPEC-05 (idempotency & concurrency) | MIG-004, MIG-006 |
| SPEC-06 (security) | MIG-007, INT-MIG-001 |
| SPEC-07 (observability & health) | MIG-008 |
| integration-contracts / hub-integration | INT-MIG-001, INT-MIG-002, MIG-005 |

## Por camada hexagonal

| Camada | Issues |
|--------|--------|
| api (actuator/health) | MIG-008 (parcial) |
| application (service) | MIG-004 |
| domain (model) | (mínimo — SchemaTarget/MigrationVersion em MIG-004) |
| infrastructure (config/persistence) | MIG-001, MIG-002, MIG-003, MIG-005, MIG-006, MIG-007, INT-MIG-001, INT-MIG-002 |

## Grafo de dependências
```
MIG-001 ──┬─▶ MIG-002 ──▶ INT-MIG-002
          ├─▶ MIG-003 ──▶ MIG-004 ──┬─▶ MIG-006
          ├─▶ MIG-005 ─────────────┘  └─▶ MIG-008
          ├─▶ MIG-007
          └─▶ INT-MIG-001 ──▶ INT-MIG-002
```

## Numeração
Sem saltos. MIG-001..008 contíguos; INT-MIG-001..002 contíguos.
