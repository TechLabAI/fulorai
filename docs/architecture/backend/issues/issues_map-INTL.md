# Issues Map — INTL (intl-service)

> 17 issues funcionais (`INTL-001..017`) + 6 de integração (`INT-INTL-001..006`).

## Por prioridade

| P | Foco | Issues |
|---|---|---|
| P1 | Scaffold + API surface | INTL-001, INTL-002, INTL-003, INTL-004 |
| P2 | Orquestração do domínio (golden path) | INTL-005, INTL-006 |
| P3 | Persistência + migrations | INTL-007, INTL-008 |
| P4 | Integrações externas | INTL-009, INTL-010, INTL-011, INT-INTL-002, INT-INTL-003, INT-INTL-004 |
| P5 | Security + multi-tenancy | INTL-012, INT-INTL-001 |
| P6 | Messaging | INTL-013, INTL-014, INT-INTL-005, INT-INTL-006 |
| P7 | Observability + health | INTL-015 |
| P8 | BDD end-to-end | INTL-016 |
| P9 | Hardening | INTL-017 |

## Por SPEC

| SPEC | Issues |
|---|---|
| SPEC-01 (API surface) | INTL-001, INTL-002, INTL-003, INTL-004 |
| SPEC-02 (Copilot orchestration) | INTL-005, INTL-006 |
| SPEC-03 (Knowledge & Event Platform) | INTL-004, INTL-010, INTL-011, INTL-014, INT-INTL-003, INT-INTL-004, INT-INTL-006 |
| SPEC-04 (Data model + migrations) | INTL-007, INTL-008 |
| SPEC-05 (Idempotency + concurrency) | INTL-011, INTL-014, INT-INTL-005, INT-INTL-006 |
| SPEC-06 (Security) | INTL-012, INT-INTL-001 |
| SPEC-07 (Observability) | INTL-015, INTL-017 |
| SPEC-08 (BDD) | INTL-016 |
| SPEC-09 (Messaging) | INTL-013, INT-INTL-005 |
| SPEC-10 (Integrations) | INTL-009, INTL-010, INT-INTL-002, INT-INTL-003, INT-INTL-004 |

## Por camada hexagonal

| Camada | Issues |
|---|---|
| api | INTL-002, INTL-003, INTL-004 |
| application | INTL-005, INTL-006, INTL-011, INTL-014, INT-INTL-006 |
| domain | INTL-006 (RankingFundamentacao), INTL-010 (TraceabilityValidator) |
| infrastructure | INTL-001, INTL-007, INTL-008, INTL-009, INTL-010, INTL-012, INTL-013, INTL-015, INT-INTL-001..005 |

## Bloqueios conhecidos

- **INT-INTL-002** (TechLab AI) — bloqueado pelo sync P3 (`openapi.json` vazio). Programar contra
  as portas; gerar DTOs no sync.
