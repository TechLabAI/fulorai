# Issues Map — COMM (Communication Hub)

> 16 issues funcionais (`COMM-001..016`) + 6 de integração (`INT-COMM-001..006`).
> Módulo de plataforma de comunicação (standard): cobre todas as camadas hexagonais + templates
> (Studio IA) + roteamento + disparo multicanal (adapters provedor-agnósticos) + ciclo de vida de entrega.

## Por prioridade

| P | Foco | Issues |
|---|---|---|
| P1 | Scaffold + domínio + API de template | COMM-001, COMM-002, COMM-003, INT-COMM-001 |
| P2 | Orquestração do domínio (golden path: rotear→enfileirar→enviar) | COMM-004, COMM-005, COMM-006 |
| P3 | Persistência + migrations | COMM-007, COMM-008 |
| P4 | Integrações externas (TechLab AI + canais + ASST/Elastic) | COMM-009, COMM-010, COMM-011, INT-COMM-003, INT-COMM-004, INT-COMM-006 |
| P5 | Security + multi-tenancy + idempotência | COMM-012, COMM-013, INT-COMM-002 |
| P6 | Messaging | COMM-014, INT-COMM-005 |
| P7 | Observability + health | COMM-015 |
| P8 | BDD end-to-end | COMM-016 |
| P9 | Hardening | (resiliência em INT-COMM-002/003/004; SLAs em SPEC-10) |

## Por SPEC

| SPEC | Issues |
|---|---|
| SPEC-01-api-surface | COMM-003, COMM-004, COMM-005, COMM-009, COMM-011 |
| SPEC-02-message-dispatch-lifecycle | COMM-002, COMM-005, COMM-006, COMM-007, COMM-013 |
| SPEC-03-channel-routing | COMM-002, COMM-004, COMM-010, INT-COMM-004 |
| SPEC-04-data-model-migrations | COMM-002, COMM-007, COMM-008 |
| SPEC-05-idempotency-concurrency | COMM-013, COMM-014 |
| SPEC-06-security | COMM-012, INT-COMM-002 |
| SPEC-07-observability-health | COMM-001, COMM-015, INT-COMM-001 |
| SPEC-08-bdd-test-scenarios | COMM-016 |
| SPEC-09-messaging-architecture | COMM-006, COMM-014, INT-COMM-005 |
| SPEC-10-integrations | COMM-009, COMM-010, INT-COMM-003, INT-COMM-004, INT-COMM-006 |

## Por camada hexagonal

| Camada | Issues |
|---|---|
| domain (model + services) | COMM-002 |
| api (controllers/dto/exception) | COMM-003, COMM-004, COMM-005, COMM-009, COMM-011, COMM-012 |
| application (use cases + ports) | COMM-004, COMM-005, COMM-006, COMM-009, COMM-013 |
| infrastructure (persistence/clients/channels/messaging/search/security) | COMM-007, COMM-008, COMM-010, COMM-012, COMM-014, COMM-015, INT-COMM-001..006 |

## Grafo de dependências (resumo)

```
COMM-001 → COMM-002 → COMM-003 → COMM-004 → COMM-005 → COMM-006
COMM-002 → COMM-007 → COMM-008 → COMM-011
COMM-002 → COMM-010 (INT-COMM-004) → COMM-006
COMM-003 → COMM-009 (INT-COMM-003)
COMM-003 → COMM-012 (INT-COMM-002)
COMM-006 → {COMM-013, COMM-014 (INT-COMM-005)}
{COMM-009, COMM-014} → INT-COMM-006
COMM-001 → COMM-015 ; INT-COMM-001 → COMM-001
{COMM-006, COMM-009, COMM-010, COMM-012, COMM-013, COMM-014} → COMM-016 (BDD)
```

## Numeração

- Funcionais: `COMM-001..016` (sem saltos).
- Integração: `INT-COMM-001..006`.
- Total: **22 issues**.
