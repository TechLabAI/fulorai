# Issues Map — SALE (Sales & Revenue)

> Mapa de rastreabilidade: issue ↔ SPEC ↔ prioridade ↔ camada hexagonal.
> 19 issues funcionais (`SALE-001..019`) + 5 de integração (`INT-SALE-001..005`).

## Por prioridade

| P | Foco | Issues |
|---|---|---|
| P1 | Scaffold + API CRUD agregados | SALE-001, SALE-002, SALE-003, SALE-004 |
| P2 | Orquestração do domínio (âncora `compra.confirmada`) | SALE-005, SALE-006, SALE-007, SALE-008 |
| P3 | Persistência + migrations | SALE-009, SALE-010 |
| P4 | Integrações externas | SALE-011, SALE-012, INT-SALE-003, INT-SALE-004 |
| P5 | Security + multi-tenancy + LGPD | SALE-013, SALE-014, INT-SALE-001 |
| P6 | Messaging (producers/consumers) | SALE-015, SALE-016, INT-SALE-002, INT-SALE-005 |
| P7 | Observability + health | SALE-017 |
| P8 | BDD end-to-end | SALE-018 |
| P9 | Hardening | SALE-019 |

## Por SPEC

| SPEC | Issues |
|---|---|
| SPEC-01 (API surface) | SALE-001, SALE-002, SALE-003, SALE-004 |
| SPEC-02 (pipeline orchestration) | SALE-005, SALE-006 |
| SPEC-03 (attribution + LTV) | SALE-007, SALE-008, SALE-019 |
| SPEC-04 (data model + migrations) | SALE-009, SALE-010 |
| SPEC-05 (idempotency) | SALE-004, SALE-006, INT-SALE-004 |
| SPEC-06 (security) | SALE-013, SALE-014, INT-SALE-001 |
| SPEC-07 (observability) | SALE-017 |
| SPEC-08 (BDD) | SALE-018 |
| SPEC-09 (messaging) | SALE-015, SALE-016, INT-SALE-002, INT-SALE-005 |
| SPEC-10 (integrations) | SALE-011, SALE-012, INT-SALE-003, INT-SALE-004 |

## Por camada hexagonal

| Camada | Issues |
|---|---|
| api | SALE-002, SALE-003, SALE-004 |
| application | SALE-005, SALE-006, SALE-007, SALE-008 |
| domain | SALE-005 (PipelineService), SALE-007 (AttributionEngine), SALE-008 (LtvCalculator) |
| infrastructure | SALE-009, SALE-010, SALE-011, SALE-012, SALE-013, SALE-015, SALE-016 |
| cross-cutting | SALE-001, SALE-014, SALE-017, SALE-018, SALE-019 |

## Dependências (DAG resumido)

```
SALE-001 ─┬─ SALE-002 ─ SALE-005 ─┐
          ├─ SALE-003              ├─ SALE-006 ─ SALE-008
          └─ SALE-004 ─ SALE-007 ─┘            └─ SALE-009 ─ SALE-010
SALE-011 ─ SALE-013 ─ SALE-014 ; SALE-012
SALE-015 ─ SALE-016 ; SALE-017 ; SALE-018 ; SALE-019
INT-SALE-001..005 anexam aos respectivos blocos
```
