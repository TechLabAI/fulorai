# Plano -- LEAD (Lead Intelligence & Qualification)

## Status das prioridades
- P1 -- pendente
- P2 -- pendente
- P3 -- pendente
- P4 -- pendente
- P5 -- pendente
- P6 -- pendente
- P7 -- pendente
- P8 -- pendente
- P9 -- pendente

## 0. Leitura executiva

### Papel do serviço (de 01-architectural-vision.md)
Inteligência de leads do Journey OS: dono do **lead** em cada `empresa` (schema `emp_<slug>`),
consolida perfil, aplica regras de qualificação versionadas e calcula o **Maturity Score (6D)**
explicável, com segmentação dinâmica. Transforma a base bruta em fila priorizada/roteável.

### MVP scope (de 01)
Capture/dedup; perfil + surveys; qualification rules versionadas; Maturity Score 6D (determinístico
+ assist TechLab AI opcional); segmentação; fila/consulta (Elastic); eventos `lead.*`.

### Diagnóstico inicial (gaps de 06)
- Calibração das 6 dimensões a validar com growth (R1/A1).
- Contrato `qualification` da TechLab AI **bloqueado** (P3 sync, snapshot vazio).
- Limiares de transição e schema do índice `leads` a especificar.

## 1. Estratégia geral

### Objetivo macro
Entregar o golden path **capturar → perfilar → qualificar → segmentar → publicar** com score
determinístico e explicável, isolado por tenant, resiliente a falha da TechLab AI, e desacoplado
dos módulos a jusante via eventos.

### Ordem das prioridades

| P | Título | Motivo |
|---|---|---|
| P1 | Scaffold + contratos mínimos | base executável + superfície REST + ports |
| P2 | Orquestração do domínio | golden path do evento-âncora `lead.qualificado` |
| P3 | Persistência + migrations | materializar o modelo no `emp_<slug>` |
| P4 | Integrações externas | TechLab AI (assist), Elastic (fila), WRKS (Feign) |
| P5 | Security + multi-tenancy + LGPD | JWT/`lead.*`, cross-empresa guard, anonimização/expurgo |
| P6 | Messaging | producers (outbox) + consumers (seed/cache) idempotentes |
| P7 | Observability + health | actuator, métricas de score, MDC |
| P8 | BDD end-to-end | Cucumber cobrindo as SHALL (D-218) |
| P9 | Hardening | SLAs, circuit breakers, retries |

## 2. Plano por prioridade

### Prioridade 1 -- Scaffold + contratos mínimos
Status: pendente
#### Objetivo / Resultado esperado
Serviço sobe, registra no Eureka, expõe a superfície REST (stubs) com contrato de erro RFC 7807.
#### Issues vinculadas
- LEAD-001, LEAD-002, LEAD-003, INT-LEAD-001
#### Specs cobertas
- SPEC-01, SPEC-07
#### Sequência de execução
- Fase 1: INT-LEAD-001 + LEAD-001 (bootstrap+discovery). Fase 2: LEAD-002 (domínio/ports). Fase 3: LEAD-003 (API).
#### Critérios de aceite
- `build` + `architectureCheck` PASS; `/actuator/health` 200; erros em `problem+json`.
#### Riscos
- ArchUnit RULE-01/02 no domínio recém-criado.
#### Instrução para implementador
Não introduzir JPA/Spring no `domain`; portas out como interfaces puras.

### Prioridade 2 -- Orquestração do domínio (golden path)
Status: pendente
#### Objetivo / Resultado esperado
Capturar→qualificar→segmentar funcionando, emitindo `lead.capturado`/`qualificado`/`score.atualizado`/`segmento.alterado`.
#### Issues vinculadas
- LEAD-004, LEAD-005, LEAD-006, LEAD-007
#### Specs cobertas
- SPEC-02, SPEC-03, SPEC-05
#### Sequência de execução
- Fase 1: LEAD-006 (motor de score, domínio puro). Fase 2: LEAD-004 (capture/dedup). Fase 3: LEAD-005 (qualify + estado). Fase 4: LEAD-007 (segmentos).
#### Critérios de aceite
- Score determinístico/explicável; dedup idempotente; evento-âncora publicado; segmentos reavaliados.
#### Riscos
- Calibração das dimensões (config-driven mitiga); recálculo em massa (lote pequeno no MVP).
#### Instrução para implementador
Assist IA é opcional e nunca causa única de transição de estado.

### Prioridade 3 -- Persistência + migrations
Status: pendente
#### Objetivo / Resultado esperado
12 tabelas no `emp_<slug>`; adapters de repositório mapeando entity↔model.
#### Issues vinculadas
- LEAD-008, LEAD-009
#### Specs cobertas
- SPEC-04, SPEC-05
#### Sequência de execução
- Fase 1: LEAD-008 (migrations). Fase 2: LEAD-009 (entities/repos/adapters).
#### Critérios de aceite
- `ddl-auto=validate` sem erro; CRUD do lead (Testcontainers) PASS.
#### Riscos
- Ranges `V<N>` colidindo cross-módulo (coordenar com MIG).
#### Instrução para implementador
DDL sem schema hardcoded (aplicável a qualquer `emp_<slug>`).

### Prioridade 4 -- Integrações externas
Status: pendente
#### Objetivo / Resultado esperado
Assist TechLab AI (fail-open), índice Elastic `leads`, Feign WRKS.
#### Issues vinculadas
- LEAD-010, LEAD-011, INT-LEAD-002, INT-LEAD-003
#### Specs cobertas
- SPEC-03, SPEC-10
#### Sequência de execução
- Fase 1: INT-LEAD-002 (WRKS Feign). Fase 2: LEAD-011 (Elastic). Fase 3: LEAD-010 + INT-LEAD-003 (TechLab AI).
#### Critérios de aceite
- Falha da TechLab AI degrada para determinístico; Elastic indexa; WRKS fail-closed.
#### Riscos
- **Bloqueio P3**: snapshot TechLab AI vazio → assist atrás de flag desabilitada.
#### Instrução para implementador
Nunca chamar provedor de IA direto; DTOs gerados do `openapi.json`.

### Prioridade 5 -- Security + multi-tenancy + LGPD
Status: pendente
#### Objetivo / Resultado esperado
JWT resource server + `lead.*`, cross-empresa guard, anonimização/expurgo.
#### Issues vinculadas
- LEAD-012, LEAD-013, LEAD-014, INT-LEAD-004
#### Specs cobertas
- SPEC-06, SPEC-09
#### Sequência de execução
- Fase 1: LEAD-012 (JWT/authz) + INT-LEAD-004 (cache). Fase 2: LEAD-013 (contexto/guard). Fase 3: LEAD-014 (LGPD).
#### Critérios de aceite
- Cross-empresa guard; cache invalidado por `modelo.acesso.alterado`; LGPD anonimização/expurgo.
#### Riscos
- Vazamento de PII (logs/eventos/índice) — controlado por design.
#### Instrução para implementador
Autorização fail-closed; sem PII em logs/eventos.

### Prioridade 6 -- Messaging
Status: pendente
#### Objetivo / Resultado esperado
Producers (`lead.*` via outbox) + consumers (seed/cache) idempotentes.
#### Issues vinculadas
- LEAD-015, LEAD-016, INT-LEAD-005
#### Specs cobertas
- SPEC-09, SPEC-05
#### Sequência de execução
- Fase 1: INT-LEAD-005 (outbox/dedup). Fase 2: LEAD-015 (producers). Fase 3: LEAD-016 (consumers).
#### Critérios de aceite
- Publish atômico com commit; consumo idempotente; contexto de empresa limpo por mensagem.
#### Riscos
- Replays/lag — mitigado por dedup `(correlationId, evento)`.
#### Instrução para implementador
`EmpresaContextHolder.clear()` em `finally` no consumo.

### Prioridade 7 -- Observability + health
Status: pendente
#### Objetivo / Resultado esperado
Health/readiness + métricas de score + MDC.
#### Issues vinculadas
- LEAD-017
#### Specs cobertas
- SPEC-07
#### Critérios de aceite
- Readiness reflete dependências; métricas de score/fallback; logs sem PII.

### Prioridade 8 -- BDD end-to-end
Status: pendente
#### Objetivo / Resultado esperado
Cucumber cobrindo todas as SHALL (D-218).
#### Issues vinculadas
- LEAD-018
#### Specs cobertas
- SPEC-08 (+ SPEC-02/03)
#### Critérios de aceite
- ≥1 cenário por SHALL; `integrationTest` PASS; padrão singleton Testcontainer.

### Prioridade 9 -- Hardening
Status: pendente
#### Objetivo / Resultado esperado
SLAs, circuit breakers, retries, runbook.
#### Issues vinculadas
- (resiliência distribuída em INT-LEAD-002/003/004/005)
#### Specs cobertas
- SPEC-10
#### Critérios de aceite
- SLAs de `integration-contracts.md` atendidos; degradação graciosa validada.

## 3. Dependências externas
- **WRKS** (AccessDecision/JWKS + eventos `empresa.provisionada`/`modelo.acesso.alterado`).
- **MIG** (provisiona `emp_<slug>`).
- **TechLab AI** (`qualification`) — **bloqueado** por P3 (sync upstream).
- **Kafka/AWS MSK**, **Elasticsearch (`leads`)**, **Redis/Valkey**, **Eureka (REG)**.

## 4. Restrições arquiteturais
- ArchUnit RULE-01..09 (CLAUDE.md).
- Camadas hexagonais (api/application/domain/infrastructure).
- `@Transactional` somente em `application.service`.
- `open-in-view=false`; pacote base `com.journeyos.lead`.
- IA **somente** via TechLab AI (nunca provider direto).

## 5. Referências
- `docs/architecture/backend/services/lead-service/` (vision 01..06, contracts, spec/backend/SPEC-01..10, diagrams)
- `docs/architecture/backend/services/lead-service/generator-config.yml`
- `docs/architecture/backend/issues/LEAD-001..018.md`, `INT-LEAD-001..005.md`, `issues_map-LEAD.md`
- `docs/architecture/integrations/techlab-ai-integration.md`
