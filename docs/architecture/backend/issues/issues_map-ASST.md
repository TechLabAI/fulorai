# Issues Map — ASST (Asset Hub)

> 16 issues funcionais (`ASST-001..016`) + 6 de integração (`INT-ASST-001..006`).
> Módulo de núcleo de conteúdo (standard): cobre todas as camadas hexagonais + Asset Studio (IA)
> + versionamento imutável + aprovação + busca Elastic.

## Por prioridade

| P | Foco | Issues |
|---|---|---|
| P1 | Scaffold + contratos mínimos | ASST-001, ASST-002, ASST-003, INT-ASST-001 |
| P2 | Orquestração do domínio (golden path: versão→submit→aprovar→publicar) | ASST-004, ASST-005, ASST-006 |
| P3 | Persistência + migrations | ASST-007, ASST-008 |
| P4 | Integrações externas (TechLab AI + Elastic) | ASST-009, ASST-010, ASST-011, INT-ASST-003, INT-ASST-004 |
| P5 | Security + multi-tenancy + idempotência | ASST-012, ASST-013, INT-ASST-002 |
| P6 | Messaging | ASST-014, INT-ASST-005, INT-ASST-006 |
| P7 | Observability + health | ASST-015 |
| P8 | BDD end-to-end | ASST-016 |
| P9 | Hardening | (resiliência tratada em INT-ASST-002/003/004; SLAs em SPEC-10) |

## Por SPEC

| SPEC | Issues |
|---|---|
| SPEC-01-api-surface | ASST-001, ASST-003, ASST-006, INT-ASST-006 |
| SPEC-02-asset-lifecycle | ASST-002, ASST-004, ASST-005, ASST-006 |
| SPEC-03-asset-studio-composition | ASST-009, ASST-010, ASST-013, INT-ASST-003 |
| SPEC-04-data-model-migrations | ASST-002, ASST-007, ASST-008 |
| SPEC-05-idempotency-concurrency | ASST-013, ASST-014 |
| SPEC-06-security | ASST-003, ASST-012, INT-ASST-002 |
| SPEC-07-observability-health | ASST-001, ASST-015 |
| SPEC-08-bdd-test-scenarios | ASST-016 |
| SPEC-09-messaging-architecture | ASST-006, ASST-014, INT-ASST-005 |
| SPEC-10-integrations | ASST-009, ASST-010, ASST-011, INT-ASST-001..005 |

## Por camada hexagonal

| Camada | Issues |
|---|---|
| domain (model + services) | ASST-002 |
| api (controllers/dto/exception) | ASST-003, ASST-004, ASST-005, ASST-006, INT-ASST-006 |
| application (use cases + ports) | ASST-004, ASST-005, ASST-006, ASST-009, ASST-010, ASST-011, ASST-013 |
| infrastructure (persistence/clients/messaging/search/security) | ASST-007, ASST-008, ASST-012, ASST-014, ASST-015, INT-ASST-001..005 |

## Grafo de dependências (resumo)

```
ASST-001 → ASST-002 → ASST-003 → ASST-004 → ASST-005 → ASST-006
ASST-002 → ASST-007 → ASST-008 → {ASST-011, ASST-012}
ASST-004 → ASST-009 (INT-ASST-003) → ASST-010
ASST-008 → ASST-011 (INT-ASST-004)
ASST-003 → ASST-012 (INT-ASST-002)
ASST-006 → {ASST-013, ASST-014 (INT-ASST-005), INT-ASST-006}
{ASST-006, ASST-009, ASST-012, ASST-014} → ASST-016 (BDD)
ASST-001 → ASST-015
```

## Numeração

- Funcionais: `ASST-001..016` (sem saltos).
- Integração: `INT-ASST-001..006`.
- Total: **22 issues**.
