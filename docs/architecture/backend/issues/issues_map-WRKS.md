# Issues Map — WRKS (Workspace & Identity)

> 18 issues funcionais (`WRKS-001..018`) + 6 de integração (`INT-WRKS-001..006`).
> Módulo fundação (standard): cobre todas as camadas hexagonais + RBAC/multi-tenancy/auditoria.

## Por prioridade

| P | Foco | Issues |
|---|---|---|
| P1 | Scaffold + contratos mínimos | WRKS-001, WRKS-002, WRKS-003, INT-WRKS-001 |
| P2 | Orquestração do domínio (golden path) | WRKS-004, WRKS-005, WRKS-006 |
| P3 | Persistência + migrations | WRKS-007, WRKS-008 |
| P4 | Integrações externas | WRKS-009, WRKS-010, INT-WRKS-004 |
| P5 | Security + multi-tenancy | WRKS-011, WRKS-012, WRKS-013, WRKS-014, INT-WRKS-002, INT-WRKS-003 |
| P6 | Messaging + auditoria | WRKS-015, WRKS-016, INT-WRKS-005, INT-WRKS-006 |
| P7 | Observability + health | WRKS-017 |
| P8 | BDD end-to-end | WRKS-018 |
| P9 | Hardening | (resiliência tratada em INT-WRKS-002/003/004; SLAs em SPEC-10) |

## Por SPEC

| SPEC | Issues |
|---|---|
| SPEC-01-api-surface | WRKS-001, WRKS-003, WRKS-014 |
| SPEC-02-identity-session | WRKS-004, WRKS-005, WRKS-006, WRKS-013 |
| SPEC-03-rbac-access-decision | WRKS-002, WRKS-011, WRKS-012, WRKS-014, INT-WRKS-006 |
| SPEC-04-data-model-migrations | WRKS-002, WRKS-007, WRKS-008 |
| SPEC-05-idempotency-concurrency | WRKS-005, WRKS-006, WRKS-012, WRKS-016 |
| SPEC-06-security | WRKS-003, WRKS-009, WRKS-011, WRKS-013, INT-WRKS-002 |
| SPEC-07-observability-health | WRKS-001, WRKS-017 |
| SPEC-08-bdd-test-scenarios | WRKS-018 |
| SPEC-09-messaging-architecture | WRKS-015, WRKS-016, INT-WRKS-005, INT-WRKS-006 |
| SPEC-10-integrations | WRKS-009, WRKS-010, INT-WRKS-001..005 |

## Por camada hexagonal

| Camada | Issues |
|---|---|
| domain (model + services) | WRKS-002, WRKS-013 |
| api (controllers/dto/exception) | WRKS-003, WRKS-014 |
| application (use cases + ports) | WRKS-004, WRKS-005, WRKS-006, WRKS-012, WRKS-013, WRKS-014 |
| infrastructure (persistence/clients/messaging/security/cache) | WRKS-007, WRKS-008, WRKS-009, WRKS-010, WRKS-011, WRKS-015, WRKS-016, WRKS-017, INT-WRKS-001..006 |

## Grafo de dependências (resumo)

```
WRKS-001 → WRKS-002 → WRKS-003 → {WRKS-004, WRKS-006}
WRKS-002 → WRKS-011 → {WRKS-004, WRKS-012, WRKS-013}
WRKS-008 → WRKS-007 → {WRKS-012, WRKS-014, WRKS-015, WRKS-016}
WRKS-004 → WRKS-005
WRKS-004 → WRKS-009 (INT-WRKS-002)
WRKS-006 → WRKS-010 (INT-WRKS-004)
WRKS-012 → WRKS-014; WRKS-015 → INT-WRKS-006; WRKS-016 → INT-WRKS-005
{WRKS-004..016} → WRKS-018 (BDD)
```

## Numeração

- Funcionais: `WRKS-001..018` (sem saltos).
- Integração: `INT-WRKS-001..006`.
- Total: **24 issues**.
