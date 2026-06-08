# Issues Map — JRNY (Journey & Routing)

> 16 issues funcionais (`JRNY-001..016`) + 6 de integração (`INT-JRNY-001..006`).
> Módulo de orquestração de jornada (standard): cobre todas as camadas hexagonais + Routing Engine
> determinístico + decision log imutável + assist de IA opcional (TechLab AI orchestration) +
> projeção Elastic fact (journey-events / routing-decisions).

## Tabela mestra

| Issue | Título | P | Est. | Specs | Depende de |
|---|---|---|---|---|---|
| JRNY-001 | Bootstrap jrny-service | P1 | S | 01,07 | INT-JRNY-001 |
| JRNY-002 | Domínio + state machines + MotorRoteamento | P1 | L | 02,03,04 | JRNY-001 |
| JRNY-003 | API Journey Builder (CRUD + publish/archive/nova-versão) | P1 | L | 01,03 | JRNY-002 |
| JRNY-004 | RotearLeadService (avaliação determinística + inscrição) | P2 | L | 02,09 | JRNY-002,003 |
| JRNY-005 | Decision log imutável + resultados | P2 | M | 02,05 | JRNY-004 |
| JRNY-006 | Eventos de roteamento (outbox) + Routing Query API | P2 | L | 02,01,09 | JRNY-005 |
| JRNY-007 | Migrations Flyway (5 tabelas, empresa) | P3 | M | 04 | JRNY-002 |
| JRNY-008 | Persistência JPA + isolamento de schema | P3 | L | 04,06 | JRNY-007 |
| JRNY-009 | Assist de IA (orchestration) + fallback determinístico | P4 | M | 02,10 | JRNY-004, INT-JRNY-003 |
| JRNY-010 | AssetQueryClient + reação a asset.versao.publicada | P4 | M | 10,09 | JRNY-003, INT-JRNY-002 |
| JRNY-011 | Projeção Elastic (journey-events/routing-decisions) | P4 | M | 07,10 | JRNY-006, INT-JRNY-004 |
| JRNY-012 | Security (JWT + AccessDecision + tenant HTTP/Kafka + MDC) | P5 | M | 06 | JRNY-003, INT-JRNY-002 |
| JRNY-013 | Idempotência + concorrência de inscrição | P5 | M | 05 | JRNY-004,008 |
| JRNY-014 | Messaging (6 consumers + 4 producers outbox) | P6 | L | 09 | JRNY-006, INT-JRNY-005 |
| JRNY-015 | Observability + health | P7 | S | 07 | JRNY-001 |
| JRNY-016 | BDD end-to-end (3 features, gate D-218) | P8 | L | 08 | JRNY-006,009,012,014 |
| INT-JRNY-001 | Service discovery (Eureka/REG) | P1 | S | 10 | — |
| INT-JRNY-002 | AccessEvaluateClient (WRKS) + cache evict | P5 | M | 06,10 | INT-JRNY-001 |
| INT-JRNY-003 | Contrato TechLab AI orchestration (DTOs gerados) | P4 | M | 10 | JRNY-009 |
| INT-JRNY-004 | Integração Elasticsearch (índices fact) | P4 | M | 10 | INT-JRNY-001 |
| INT-JRNY-005 | Kafka config (outbox/DLQ/retries) | P6 | M | 09 | INT-JRNY-001 |
| INT-JRNY-006 | JourneyQueryClient (leitura provida a COMM/SALE) | P6 | S | 01,10 | JRNY-006 |

## Por prioridade

| P | Foco | Issues |
|---|---|---|
| P1 | Scaffold + domínio + Journey Builder | JRNY-001, JRNY-002, JRNY-003, INT-JRNY-001 |
| P2 | Orquestração do domínio (golden path: avaliar→rotear→decisão→evento) | JRNY-004, JRNY-005, JRNY-006 |
| P3 | Persistência + migrations | JRNY-007, JRNY-008 |
| P4 | Integrações externas (TechLab AI + ASST + Elastic) | JRNY-009, JRNY-010, JRNY-011, INT-JRNY-003, INT-JRNY-004 |
| P5 | Security + multi-tenancy + idempotência | JRNY-012, JRNY-013, INT-JRNY-002 |
| P6 | Messaging | JRNY-014, INT-JRNY-005, INT-JRNY-006 |
| P7 | Observability + health | JRNY-015 |
| P8 | BDD end-to-end | JRNY-016 |
| P9 | Hardening | (resiliência tratada em INT-JRNY-002/003/004/005 + JRNY-013; SLAs em SPEC-05/10) |

## Por SPEC

| SPEC | Issues |
|---|---|
| SPEC-01-api-surface | JRNY-001, JRNY-003, JRNY-006, INT-JRNY-006 |
| SPEC-02-routing-engine-orchestration | JRNY-002, JRNY-004, JRNY-005, JRNY-006, JRNY-009 |
| SPEC-03-journey-builder | JRNY-002, JRNY-003 |
| SPEC-04-data-model-migrations | JRNY-002, JRNY-007, JRNY-008 |
| SPEC-05-idempotency-concurrency | JRNY-005, JRNY-013 |
| SPEC-06-security | JRNY-008, JRNY-012, INT-JRNY-002 |
| SPEC-07-observability-health | JRNY-001, JRNY-011, JRNY-015 |
| SPEC-08-bdd-test-scenarios | JRNY-016 |
| SPEC-09-messaging-architecture | JRNY-004, JRNY-006, JRNY-010, JRNY-014, INT-JRNY-005 |
| SPEC-10-integrations | JRNY-009, JRNY-010, JRNY-011, INT-JRNY-001..005 |

## Por camada hexagonal

| Camada | Issues |
|---|---|
| domain (model + services) | JRNY-002 |
| api (controllers/dto/exception) | JRNY-003, JRNY-006, INT-JRNY-006 |
| application (use cases + ports) | JRNY-004, JRNY-005, JRNY-006, JRNY-009, JRNY-010, JRNY-011, JRNY-013 |
| infrastructure (persistence/clients/messaging/search/security) | JRNY-007, JRNY-008, JRNY-012, JRNY-014, JRNY-015, INT-JRNY-001..005 |

## Grafo de dependências (resumo)

```
INT-JRNY-001 → JRNY-001 → JRNY-002 → JRNY-003 → JRNY-004 → JRNY-005 → JRNY-006
JRNY-002 → JRNY-007 → JRNY-008 → JRNY-013
JRNY-004 → JRNY-009 (INT-JRNY-003)
JRNY-003 → JRNY-010 (INT-JRNY-002)
JRNY-006 → JRNY-011 (INT-JRNY-004)
JRNY-003 → JRNY-012 (INT-JRNY-002)
JRNY-006 → JRNY-014 (INT-JRNY-005) ; JRNY-006 → INT-JRNY-006
JRNY-001 → JRNY-015
{JRNY-006, JRNY-009, JRNY-012, JRNY-014} → JRNY-016 (BDD)
```

## Numeração

- Funcionais: `JRNY-001..016` (sem saltos).
- Integração: `INT-JRNY-001..006`.
- Total: **22 issues**.
