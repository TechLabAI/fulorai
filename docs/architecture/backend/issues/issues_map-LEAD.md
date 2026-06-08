# Issues Map — LEAD (Lead Intelligence & Qualification)

> 18 issues funcionais (`LEAD-001..018`) + 5 de integração (`INT-LEAD-001..005`).
> Módulo de domínio (standard): cobre todas as camadas hexagonais + Maturity Score 6D + LGPD + messaging.

## Por prioridade

| P | Foco | Issues |
|---|---|---|
| P1 | Scaffold + contratos mínimos | LEAD-001, LEAD-002, LEAD-003, INT-LEAD-001 |
| P2 | Orquestração do domínio (golden path) | LEAD-004, LEAD-005, LEAD-006, LEAD-007 |
| P3 | Persistência + migrations | LEAD-008, LEAD-009 |
| P4 | Integrações externas | LEAD-010, LEAD-011, INT-LEAD-002, INT-LEAD-003 |
| P5 | Security + multi-tenancy + LGPD | LEAD-012, LEAD-013, LEAD-014, INT-LEAD-004 |
| P6 | Messaging | LEAD-015, LEAD-016, INT-LEAD-005 |
| P7 | Observability + health | LEAD-017 |
| P8 | BDD end-to-end | LEAD-018 |
| P9 | Hardening | (resiliência em INT-LEAD-002/003/004/005; SLAs em SPEC-10/integration-contracts) |

## Por SPEC

| SPEC | Issues |
|---|---|
| SPEC-01-api-surface | LEAD-001, LEAD-003, LEAD-007, LEAD-011 |
| SPEC-02-lead-qualification-orchestration | LEAD-004, LEAD-005, LEAD-007, LEAD-018 |
| SPEC-03-maturity-score-6d | LEAD-005, LEAD-006, LEAD-010, LEAD-018 |
| SPEC-04-data-model-migrations | LEAD-002, LEAD-008, LEAD-009, LEAD-014 |
| SPEC-05-idempotency-concurrency | LEAD-004, LEAD-006, LEAD-015, LEAD-016, INT-LEAD-005 |
| SPEC-06-security | LEAD-003, LEAD-012, LEAD-013, LEAD-014, INT-LEAD-004 |
| SPEC-07-observability-health | LEAD-001, LEAD-017 |
| SPEC-08-bdd-test-scenarios | LEAD-018 |
| SPEC-09-messaging-architecture | LEAD-015, LEAD-016, INT-LEAD-004, INT-LEAD-005 |
| SPEC-10-integrations | LEAD-010, LEAD-011, INT-LEAD-001..004 |

## Por camada hexagonal

| Camada | Issues |
|---|---|
| domain (model + services) | LEAD-002, LEAD-006, LEAD-007 |
| api (controllers/dto/exception) | LEAD-003 |
| application (use cases + ports) | LEAD-002, LEAD-004, LEAD-005, LEAD-007, LEAD-014 |
| infrastructure (persistence/clients/messaging/security/cache/search) | LEAD-008, LEAD-009, LEAD-010, LEAD-011, LEAD-012, LEAD-013, LEAD-015, LEAD-016, LEAD-017, INT-LEAD-001..005 |

## Grafo de dependências (resumo)

```
LEAD-001 → LEAD-002 → LEAD-003 → LEAD-004 → LEAD-005
LEAD-002 → LEAD-006 → LEAD-005 → LEAD-007
LEAD-008 → LEAD-009 → {LEAD-011, LEAD-014, LEAD-015}
INT-LEAD-001 → INT-LEAD-002 → LEAD-012 → LEAD-013
LEAD-006 → LEAD-010 (INT-LEAD-003)
INT-LEAD-002 → INT-LEAD-004 → LEAD-012; LEAD-016 → INT-LEAD-004
LEAD-005 → LEAD-015 → INT-LEAD-005; LEAD-016 → INT-LEAD-005
{LEAD-004..016} → LEAD-018 (BDD)
```

## Numeração

- Funcionais: `LEAD-001..018` (sem saltos).
- Integração: `INT-LEAD-001..005`.
- Total: **23 issues**.
