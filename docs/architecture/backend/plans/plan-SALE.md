# Plano — SALE (sale-service)

## Status das prioridades
- P1 — pendente
- P2 — pendente
- P3 — pendente
- P4 — pendente
- P5 — pendente
- P6 — pendente
- P7 — pendente
- P8 — pendente
- P9 — pendente

## 0. Leitura executiva

### Papel do serviço (de 01-architectural-vision.md)
SALE é o **motor de receita** do Journey OS: dono do pipeline de CRM, das ofertas, das compras/receita,
da atribuição de receita e do LTV dentro de cada `empresa`. Transforma fechamentos dispersos em um
funil de receita rastreável, explicável e auditável.

### MVP scope (de 01)
Pipeline/CRM (oportunidade → estágios → ganho/perda), ofertas versionadas, ingestão idempotente de
compra com reconhecimento de receita, atribuição determinística (last/first/linear-touch), LTV por
contato e os eventos `oportunidade.*`/`compra.*`/`receita.*`/`ltv.*`. **Sem TechLab AI no MVP.**

### Diagnóstico inicial (gaps de 06)
- Conjunto final de estágios e modelos de atribuição a confirmar (default `last-touch`).
- Contrato exato da fonte de compra (checkout/INTL Event Platform) — MVP via API idempotente.
- Definição de `contato_ref` (chave de LTV) e relação com o `lead` de LEAD.
- Schemas dos índices Elastic `revenue-events`/`campaign-events`.

## 1. Estratégia geral

### Objetivo macro
Entregar o golden path da âncora `compra.confirmada` (oportunidade → compra → receita atribuída → LTV)
com idempotência forte e conservação de receita, sobre o esqueleto hexagonal.

### Ordem das prioridades

| P | Título | Motivo |
|---|---|---|
| P1 | Scaffold + API CRUD agregados | base executável + contratos mínimos |
| P2 | Orquestração do domínio | golden path da âncora `compra.confirmada` |
| P3 | Persistência + migrations | materializar os agregados no `emp_<slug>` |
| P4 | Integrações externas | WRKS Feign, Elastic, fonte de compra |
| P5 | Security + multi-tenancy + LGPD | isolamento e PII do comprador |
| P6 | Messaging | producers (outbox) + consumers idempotentes |
| P7 | Observability + health | actuator + métricas de receita |
| P8 | BDD end-to-end | Cucumber cobrindo SHALL (D-218) |
| P9 | Hardening | resiliência + re-atribuição + runbook |

## 2. Plano por prioridade

### Prioridade 1 — Scaffold + API CRUD
Status: pendente
#### Objetivo / Resultado esperado
Esqueleto compila + `architectureCheck` PASS; recursos `/oportunidades`, `/ofertas`, `/compras` (ingestão) expostos.
#### Issues vinculadas
- SALE-001, SALE-002, SALE-003, SALE-004
#### Specs cobertas
- SPEC-01, SPEC-04 (estrutura)
#### Sequência de execução
- Fase 1: SALE-001 (scaffold) → Fase 2: SALE-002/003/004 (controllers + DTOs + ports)
#### Critérios de aceite
- ArchUnit PASS; endpoints respondem com ProblemDetail; nenhuma `@Entity` exposta.
#### Riscos
- Conflito de nomes do entity-generator encadeado (ver master plan ACHADO WRKS) → usar só o layer base.
#### Instrução para implementador
Rodar scaffold via generator-config; não editar DTOs gerados sem necessidade.

### Prioridade 2 — Orquestração do domínio (âncora)
Status: pendente
#### Objetivo / Resultado esperado
Golden path completo: pipeline + reconhecimento de receita + atribuição + LTV + eventos.
#### Issues vinculadas
- SALE-005, SALE-006, SALE-007, SALE-008
#### Specs cobertas
- SPEC-02, SPEC-03
#### Sequência de execução
- Fase 1: SALE-005 (pipeline) → Fase 2: SALE-007 (atribuição) + SALE-008 (LTV) → Fase 3: SALE-006 (orquestra a compra)
#### Critérios de aceite
- Conservação de receita (Σ itens = total; Σ atribuição = receita); idempotência; eventos publicados.
#### Riscos
- Calibração de touchpoints incompleta (R1) → default LAST_TOUCH conservador.
#### Instrução para implementador
Domain services POJO (zero Spring) registrados em `DomainServiceConfig`.

### Prioridade 3 — Persistência + migrations
Status: pendente
#### Objetivo / Resultado esperado
9 tabelas em `emp_<slug>`, adapters de repositório, migrations Flyway centralizadas.
#### Issues vinculadas
- SALE-009, SALE-010
#### Specs cobertas
- SPEC-04
#### Critérios de aceite
- `validate` no boot; UNIQUE(`id_externo`,`origem`); partial unique do modelo ativo.

### Prioridade 4 — Integrações externas
Status: pendente
#### Issues vinculadas
- SALE-011, SALE-012, INT-SALE-003, INT-SALE-004
#### Specs cobertas
- SPEC-10
#### Critérios de aceite
- WRKS Feign deny-by-default; Elastic best-effort; ingestão de compra mediada e idempotente.

### Prioridade 5 — Security + multi-tenancy + LGPD
Status: pendente
#### Issues vinculadas
- SALE-013, SALE-014, INT-SALE-001
#### Specs cobertas
- SPEC-06
#### Critérios de aceite
- Sem leitura cross-empresa; PII do comprador protegida; service token na ingestão.

### Prioridade 6 — Messaging
Status: pendente
#### Issues vinculadas
- SALE-015, SALE-016, INT-SALE-002, INT-SALE-005
#### Specs cobertas
- SPEC-09
#### Critérios de aceite
- Outbox; consumers idempotentes; contrato de evento estável.

### Prioridade 7 — Observability + health
Status: pendente
#### Issues vinculadas
- SALE-017
#### Specs cobertas
- SPEC-07

### Prioridade 8 — BDD end-to-end
Status: pendente
#### Issues vinculadas
- SALE-018
#### Specs cobertas
- SPEC-08 (gate D-218)

### Prioridade 9 — Hardening
Status: pendente
#### Issues vinculadas
- SALE-019
#### Specs cobertas
- SPEC-03, SPEC-10

## 3. Dependências externas
- **WRKS** (AccessDecision/JWT + eventos) — bloqueante para autorização/seed.
- **MIG** (schema `emp_<slug>`) — bloqueante para boot.
- **LEAD** (eventos) — habilita golden path automático (não bloqueante).
- **Fonte de compra** (checkout/INTL Event Platform) — bloqueante para receita automática.
- **Kafka/AWS MSK** e **Elasticsearch** disponíveis.

## 4. Restrições arquiteturais
- ArchUnit RULE-01..09 (CLAUDE.md).
- Camadas hexagonais (api/application/domain/infrastructure).
- `@Transactional` somente em `application.service`.
- Domínio sem Spring/JPA; `@FeignClient` só em `infrastructure.clients`.
- **Sem chamada direta a provedor de IA nem a gateway de pagamento.**

## 5. Referências
- `docs/architecture/backend/services/sale-service/` (vision 01..06, specs, contracts, diagrams)
- `docs/architecture/backend/issues/SALE-*.md` + `INT-SALE-*.md` + `issues_map-SALE.md`
- `docs/architecture/backend/services/sale-service/generator-config.yml`
