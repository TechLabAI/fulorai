# Issues Map — GWY (API Gateway)

> 12 issues funcionais (`GWY-001..012`) + 4 de integração (`INT-GWY-001..004`).
> Módulo de infraestrutura (gateway): sem persistência (P3) e sem BDD-domínio (P8).

## Por prioridade

| P | Foco (adaptado a gateway) | Issues |
|---|---|---|
| P1 | Bootstrap + roteamento | GWY-001, GWY-002, INT-GWY-001 |
| P2 | Pipeline de borda (correlação, erro, anti-spoofing, domínio) | GWY-003, GWY-004, GWY-005, GWY-006 |
| P4 | Roteamento downstream + resiliência | INT-GWY-004 |
| P5 | Segurança (auth, tenant, allowlist, CORS) | GWY-007, GWY-008, GWY-009, GWY-010, INT-GWY-002 |
| P6 | Rate-limiting distribuído | GWY-011, INT-GWY-003 |
| P7 | Observabilidade + health | GWY-012 |

> Prioridades não usadas: **P3** (sem persistência), **P8** (sem domínio de negócio para BDD),
> **P9** (hardening: circuit-breaker tratado como pós-MVP em INT-GWY-004).

## Por SPEC

| SPEC | Issues |
|---|---|
| SPEC-01-api-surface | GWY-001, GWY-002, GWY-003, GWY-004, GWY-006, INT-GWY-001 |
| SPEC-05-idempotency-concurrency | GWY-011, INT-GWY-003, INT-GWY-004 |
| SPEC-06-security | GWY-005, GWY-006, GWY-007, GWY-008, GWY-009, GWY-010, INT-GWY-002 |
| SPEC-07-observability-health | GWY-001, GWY-004, GWY-012 |
| integration-contracts | INT-GWY-001, INT-GWY-002, INT-GWY-003, INT-GWY-004 |

## Por camada hexagonal

| Camada | Issues |
|---|---|
| api (exception) | GWY-003 |
| application (políticas + ports) | GWY-006, GWY-007, GWY-008, GWY-011 |
| domain (model) | GWY-006 |
| infrastructure (filtros/config/adapters) | GWY-001, GWY-002, GWY-004, GWY-005, GWY-009, GWY-010, GWY-012, INT-GWY-001..004 |

## Grafo de dependências (resumo)

```
GWY-001 ─┬─> GWY-002 ─┬─> INT-GWY-004
         │            └─> GWY-012
         ├─> GWY-003
         ├─> GWY-004
         ├─> GWY-005 ─> GWY-008
         ├─> GWY-006 ─┬─> GWY-007 ─┬─> GWY-008
         │            │            └─> GWY-009
         │            └─> GWY-011 ─> GWY-012
         └─> GWY-010
INT-GWY-001 ─> GWY-002 / INT-GWY-004
INT-GWY-002 ─> GWY-007
INT-GWY-003 ─> GWY-011
```
