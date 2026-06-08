# Plano -- COMM (Communication Hub)

## Status das prioridades
- P1 -- pendente
- P2 -- pendente
- P3 -- pendente
- P4 -- pendente
- P5 -- pendente
- P6 -- pendente
- P7 -- pendente
- P8 -- pendente

## 0. Leitura executiva

### Papel do serviço (01-architectural-vision.md)
COMM é o hub de comunicação multicanal do workspace: templates versionados (com composição
assistida via TechLab AI `document_composition`), regras de roteamento, disparo padronizado e
idempotente por WhatsApp/Email/Telegram/SMS através de **adapters de canal provedor-agnósticos**
(ADR-005), e rastreio do ciclo de vida de entrega. Opera só no schema `emp_<slug>` e nunca chama
provider de IA direto. JRNY/SALE/LEAD acionam disparos; ASST fornece assets publicados.

### MVP scope (01)
Template CRUD + Studio; roteamento (preferido+fallback); disparo multicanal idempotente; máquina
de entrega `PENDENTE→ENFILEIRADA→ENVIADA→ENTREGUE→LIDA`/`FALHADA`; projeção Elastic
`communication-events`; config de canal por empresa (segredo via `credencial_ref`).

### Diagnóstico inicial (gaps — 06)
- Contrato TechLab AI `document_composition` ainda placeholder (P3 bloqueado) → coupling point marcado (INT-COMM-003).
- Contratos finos dos provedores de canal a detalhar nos adapters (INT-COMM-004).
- Schema de `condicoes` de roteamento a detalhar no implement.
- Permissões `comm.*` a confirmar no RBAC global.
- Acionamento por JRNY/SALE (eventos de gatilho) a fixar quando esses módulos pinarem nomes — COMM expõe `POST /messages` estável.

## 1. Estratégia geral

### Objetivo macro
Entregar o golden path *rotear → renderizar template → enfileirar → enviar (ao provedor) →
confirmar entrega* com idempotência e proveniência, abstraindo provedores atrás de `CanalEnvioPort`;
depois reforçar integrações (IA/canais/ASST/Elastic), segurança, mensageria e BDD.

### Ordem das prioridades

| P | Título | Motivo |
|---|---|---|
| P1 | Scaffold + domínio + API de template | Base executável + state machine de entrega testável |
| P2 | Golden path (rotear→enfileirar→enviar) | Evento-âncora `mensagem.enviada` |
| P3 | Persistência + migrations | Fonte da verdade no `emp_<slug>` |
| P4 | Integrações (TechLab AI + canais + ASST/Elastic) | Template Studio + envio real + assets + analytics |
| P5 | Security + multi-tenancy + idempotência | Autorização `comm.*`, tenant guard, webhook signature, replays |
| P6 | Messaging | Eventos (outbox) + consumo idempotente + callbacks |
| P7 | Observability + health | Actuator, métricas por canal/provedor, MDC |
| P8 | BDD end-to-end | Gate D-218 (toda SHALL → cenário) |

## 2. Plano por prioridade

### Prioridade 1 -- Scaffold + domínio + API de template
Status: pendente
#### Objetivo / Resultado esperado
Serviço sobe (Eureka/Actuator), domínio puro com state machine de entrega + roteamento + render, CRUD de template com DTO/ProblemDetail.
#### Issues vinculadas
- COMM-001, COMM-002, COMM-003, INT-COMM-001
#### Specs cobertas
- SPEC-01, SPEC-02, SPEC-03, SPEC-07
#### Sequência de execução
- Fase 1: bootstrap (COMM-001 + INT-COMM-001) · Fase 2: domínio (COMM-002) · Fase 3: API template (COMM-003)
#### Critérios de aceite
- build + architectureCheck PASS; `POST /templates` cria RASCUNHO; transição de entrega inválida lança erro de domínio.
#### Riscos
- Acoplamento acidental domínio↔Spring/SDK de provedor (mitigado por ArchUnit).
#### Instrução para implementador
- `/be-implement COMM P1`. Domínio sem Spring/JPA (RULE-01/02); controller retorna DTO.

### Prioridade 2 -- Golden path (rotear → enfileirar → enviar)
Status: pendente
#### Objetivo / Resultado esperado
Roteamento (preferido+fallback) + aceite de disparo (202 ENFILEIRADA) + worker de envio + máquina de entrega + evento-âncora `mensagem.enviada`.
#### Issues vinculadas
- COMM-004, COMM-005, COMM-006
#### Specs cobertas
- SPEC-01, SPEC-02, SPEC-03, SPEC-09
#### Sequência de execução
- Fase 1: roteamento (COMM-004) · Fase 2: aceite + render (COMM-005) · Fase 3: worker + entrega + âncora (COMM-006)
#### Critérios de aceite
- Disparo válido → 202 ENFILEIRADA; envio OK → ENVIADA + `journey-os.mensagem.enviada`; sem canal → 422.
#### Riscos
- Dependência do adapter de canal (COMM-010/INT-COMM-004) — usar stub até P4; worker desacopla.
#### Instrução para implementador
- `/be-implement COMM P2`. Snapshot imutável no envio; transições monotônicas.

### Prioridade 3 -- Persistência + migrations
Status: pendente
#### Objetivo / Resultado esperado
Entidades JPA + adapters + Flyway (5 tabelas) no `emp_<slug>`; `ddl-auto=validate` passa.
#### Issues vinculadas
- COMM-007, COMM-008
#### Specs cobertas
- SPEC-04
#### Sequência de execução
- Fase 1: JPA + adapters (COMM-007) · Fase 2: migrations (COMM-008)
#### Critérios de aceite
- CRUD persiste no tenant; UNIQUE `chave_idempotencia` e `(canal, provedor)`; sem `empresa_id` nas tabelas.
#### Riscos
- Mapeamento JSONB; isolamento por schema (testes Testcontainers).
#### Instrução para implementador
- `/be-implement COMM P3`. DDL via `be-migration-generator.py` a partir de `data-model.md`.

### Prioridade 4 -- Integrações (TechLab AI + canais + ASST/Elastic)
Status: pendente
#### Objetivo / Resultado esperado
Template Studio (IA) + adapters de canal (envio real + webhooks) + AssetQueryClient + projeção `communication-events`.
#### Issues vinculadas
- COMM-009, COMM-010, COMM-011, INT-COMM-003, INT-COMM-004, INT-COMM-006
#### Specs cobertas
- SPEC-03, SPEC-10
#### Sequência de execução
- Fase 1: channel adapters (COMM-010 + INT-COMM-004) + config (COMM-011) · Fase 2: Studio (COMM-009 + INT-COMM-003) · Fase 3: ASST + Elastic (INT-COMM-006)
#### Critérios de aceite
- Envio por adapter sob Resilience4j; Studio degrada gracioso; AssetQuery só publicados; Elastic best-effort.
#### Riscos
- TechLab AI `openapi.json` placeholder (P3 bloqueado) — marcar coupling; contratos de provedor variam por canal.
#### Instrução para implementador
- `/be-implement COMM P4`. NUNCA chamar IA/provedor fora dos adapters/clients; segredos via `credencial_ref`.

### Prioridade 5 -- Security + multi-tenancy + idempotência
Status: pendente
#### Objetivo / Resultado esperado
JWT/JWKS + `comm.*` AccessDecision + EmpresaContextHolder + webhook signature + idempotência (disparo/Studio/consumers) + concorrência otimista.
#### Issues vinculadas
- COMM-012, COMM-013, INT-COMM-002
#### Specs cobertas
- SPEC-05, SPEC-06
#### Sequência de execução
- Fase 1: WRKS client + security (COMM-012 + INT-COMM-002) · Fase 2: idempotência/concorrência (COMM-013)
#### Critérios de aceite
- Cross-empresa bloqueado; webhook autenticado; replays sem duplicação; transições concorrentes seguras.
#### Riscos
- Resolução de tenant em webhook (da mensagem, não do payload).
#### Instrução para implementador
- `/be-implement COMM P5`. `@Transactional` só em application.service.

### Prioridade 6 -- Messaging
Status: pendente
#### Objetivo / Resultado esperado
Producers (outbox) + consumers idempotentes + ingestão de webhook + DLQ; gatilhos JRNY/SALE quando pinados.
#### Issues vinculadas
- COMM-014, INT-COMM-005
#### Specs cobertas
- SPEC-09, SPEC-05
#### Sequência de execução
- Fase 1: Kafka wiring + DLQ (INT-COMM-005) · Fase 2: producers/consumers + callbacks (COMM-014)
#### Critérios de aceite
- Outbox sem evento fantasma; consumer reentregue → no-op; webhook → transição + evento.
#### Riscos
- Nomes de eventos JRNY/SALE não finalizados (adicionar no implement).
#### Instrução para implementador
- `/be-implement COMM P6`. Idempotência por `eventId` antes de efeito.

### Prioridade 7 -- Observability + health
Status: pendente
#### Objetivo / Resultado esperado
MDC + métricas por canal/provedor + actuator (readiness no DB; provedores/Elastic degradados).
#### Issues vinculadas
- COMM-015
#### Specs cobertas
- SPEC-07
#### Critérios de aceite
- `correlationId`/`empresaId` no MDC; métricas de entregabilidade; CB aberto = health degradado, readiness UP.
#### Instrução para implementador
- `/be-implement COMM P7`. Nunca logar segredo/PII renderizada.

### Prioridade 8 -- BDD end-to-end
Status: pendente
#### Objetivo / Resultado esperado
Suite Cucumber verde (3 features) cobrindo toda cláusula SHALL (gate D-218).
#### Issues vinculadas
- COMM-016
#### Specs cobertas
- SPEC-08 (+ cobertura cruzada SPEC-01..10)
#### Critérios de aceite
- `:comm-service:test --tests "*CucumberIT*"` 0 failed; ≥ 1 cenário por SHALL.
#### Instrução para implementador
- `/be-implement COMM P8`. Provedores e TechLab AI stubbados; Testcontainers PostgreSQL.

## 3. Dependências externas
- WRKS (AccessDecision/JWKS) · ASST (AssetQueryClient) · MIG (schema) · REG/GWY (discovery/edge).
- TechLab AI (`document_composition`, P3 placeholder) · Provedores de canal (Meta/SES/Telegram/Twilio) · Elasticsearch (`communication-events`) · Kafka (AWS MSK).
- JRNY/SALE (acionamento por evento — pós-pin dos nomes).

## 4. Restrições arquiteturais
- ArchUnit RULE-01..09 (CLAUDE.md); SDK de provedor só em `infrastructure.channels`.
- Camadas hexagonais (api/application/domain/infrastructure).
- `@Transactional` somente em application.service; `@FeignClient` só em infrastructure.clients.
- Nunca chamar provider de IA direto (sempre TechLab AI HTTP); segredos via `${VAR}`/`credencial_ref`.

## 5. Referências
- `docs/architecture/backend/services/comm-service/01..06-*.md` + `adr/ADR-001..005`
- `docs/architecture/backend/services/comm-service/spec/backend/SPEC-01..10`
- `docs/architecture/backend/services/comm-service/contracts/*` + `generator-config.yml`
- `docs/architecture/backend/issues/COMM-001..016.md` + `INT-COMM-001..006.md` + `issues_map-COMM.md`
