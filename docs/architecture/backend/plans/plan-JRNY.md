# Plano -- JRNY (Journey & Routing)

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
JRNY é o **motor de jornada e roteamento** do Journey OS: o **Journey Builder** (define jornadas
multi-estágio versionadas), o **Routing Engine** (decide, a cada evento de domínio, o próximo
estágio do lead via regras determinísticas + assist de IA opcional) e o **decision log** imutável
(audita o "por quê" de cada decisão). JRNY **decide e sinaliza** — não executa ações de canal/venda
(isso é de COMM/SALE). Opera somente no schema `emp_<slug>` e nunca chama provider de IA direto.

### MVP scope (01)
Journey Builder (jornada/estágios + state machine de publicação); Routing Engine (regras
versionadas + avaliação determinística); decision log imutável; orchestration assist (TechLab AI,
opcional com fallback); telemetria de jornada (Elastic `journey-events`/`routing-decisions`);
consumo de conteúdo publicado de ASST; leitura cross-módulo (`JourneyQueryClient`).

### Diagnóstico inicial (gaps — 06)
- Contrato TechLab AI `orchestration` ainda placeholder (P3 bloqueado) → ponto de coupling marcado (INT-JRNY-003); caminho determinístico é o padrão.
- Gramática de `condicao` (predicado jsonb) ancorada nos campos de `lead.qualificado` (LEAD) — refinar operadores no implement.
- Permissões `jrny.*` a confirmar no RBAC global.
- Definição fina de estágio terminal/conclusão a refinar nas SPECs.
- Superfície do `JourneyQueryClient` evolui quando COMM/SALE forem arquitetados.

## 1. Estratégia geral

### Objetivo macro
Entregar o golden path *evento de domínio (lead qualificado) → avaliar regras (+assist opcional) →
decidir alvo → matricular/avançar → registrar decisão imutável → emitir `lead.roteado`*, com
roteamento determinístico e auditável; depois reforçar persistência, integrações (IA/ASST/Elastic),
segurança, mensageria, observabilidade e BDD.

### Ordem das prioridades

| P | Título | Motivo |
|---|---|---|
| P1 | Scaffold + domínio + Journey Builder | Base executável + state machines testáveis |
| P2 | Routing Engine (golden path) | Evento-âncora `lead.roteado` + decision log |
| P3 | Persistência + migrations | Fonte da verdade no `emp_<slug>` |
| P4 | Integrações (TechLab AI + ASST + Elastic) | Assist opcional + conteúdo de estágio + telemetria |
| P5 | Security + multi-tenancy + idempotência | Autorização `jrny.*`, tenant guard (HTTP/Kafka), replays |
| P6 | Messaging | Consumers idempotentes + producers (outbox) + JourneyQueryClient |
| P7 | Observability + health | Actuator, métricas (taxa de fallback IA), MDC |
| P8 | BDD end-to-end | Gate D-218 (toda SHALL → cenário) |

## 2. Plano por prioridade

### Prioridade 1 -- Scaffold + domínio + Journey Builder
Status: pendente
#### Objetivo / Resultado esperado
Serviço sobe (Eureka/Actuator), domínio puro com state machines + MotorRoteamento, API de
construção de jornada (CRUD + publicar/arquivar/nova-versão).
#### Issues vinculadas
- JRNY-001, JRNY-002, JRNY-003, INT-JRNY-001
#### Specs cobertas
- SPEC-01, SPEC-03, SPEC-07
#### Sequência de execução
- Fase 1: bootstrap (JRNY-001 + INT-JRNY-001) · Fase 2: domínio (JRNY-002) · Fase 3: API Journey Builder (JRNY-003)
#### Critérios de aceite
- build + architectureCheck PASS; `POST /journeys` cria RASCUNHO v1; publicar sem estágio → 422; transição inválida → 409.
#### Riscos
- Acoplamento acidental domínio↔Spring (mitigado por ArchUnit RULE-01/02).
#### Instrução para implementador
- `/be-implement JRNY P1`. Domínio sem Spring/JPA; controller retorna DTO record.

### Prioridade 2 -- Routing Engine (golden path)
Status: pendente
#### Objetivo / Resultado esperado
Avaliação determinística de regras (prioridade) + matrícula/avanço de inscrição + decisão imutável
+ emissão do evento-âncora `lead.roteado` + Routing Query API.
#### Issues vinculadas
- JRNY-004, JRNY-005, JRNY-006
#### Specs cobertas
- SPEC-02, SPEC-05, SPEC-01, SPEC-09
#### Sequência de execução
- Fase 1: RotearLeadService (JRNY-004) · Fase 2: decision log imutável (JRNY-005) · Fase 3: eventos outbox + query API (JRNY-006)
#### Critérios de aceite
- `ROTEADO` emite `lead.roteado`; `SEM_MUDANCA`/`NAO_ROTEADO` registrados sem emitir; terminal → `jornada.concluida`; decisões consultáveis por lead.
#### Riscos
- Estado corrompido por transição fora da máquina (mitigado: só pelo agregado raiz); regras ambíguas (mitigado: prioridade + decision log — R2).
#### Instrução para implementador
- `/be-implement JRNY P2`. Decisão imutável (ADR-005); evento via outbox; avaliação reprodutível.

### Prioridade 3 -- Persistência + migrations
Status: pendente
#### Objetivo / Resultado esperado
DDL das 5 tabelas no `emp_<slug>` (com `empresa_id` guard) + adapters JPA respeitando isolamento e imutabilidade da decisão.
#### Issues vinculadas
- JRNY-007, JRNY-008
#### Specs cobertas
- SPEC-04, SPEC-06
#### Sequência de execução
- Fase 1: migrations (JRNY-007) · Fase 2: JPA/adapters (JRNY-008)
#### Critérios de aceite
- `ddl-auto=validate` passa; round-trip via Testcontainers; índice parcial ATIVA aplicado; decisão insert-only; sem entity na API.
#### Riscos
- Vazamento cross-tenant (mitigado: search_path + `empresa_id` guard nos adapters).
#### Instrução para implementador
- `/be-implement JRNY P3`. Migrations em `journey-os-migrations` (`db/migration/empresa/`).

### Prioridade 4 -- Integrações (TechLab AI + ASST + Elastic)
Status: pendente
#### Objetivo / Resultado esperado
Assist de IA (`orchestration`) opcional com fallback determinístico; conteúdo de estágio via
ASST; projeção fact em Elastic — tudo resiliente.
#### Issues vinculadas
- JRNY-009, JRNY-010, JRNY-011, INT-JRNY-003, INT-JRNY-004
#### Specs cobertas
- SPEC-02, SPEC-10
#### Sequência de execução
- Fase 1: contrato/cliente TechLab AI (INT-JRNY-003) → assist (JRNY-009) · Fase 2: AssetQueryClient (JRNY-010) · Fase 3: Elastic (INT-JRNY-004 → JRNY-011)
#### Critérios de aceite
- IA down → `assist_ia=INDISPONIVEL` e roteamento determinístico decide; ASST down → jornada lê sem conteúdo resolvido; Elastic down → decisão não bloqueia.
#### Riscos
- `openapi.json` placeholder (P3) → DTOs gerados quando o SHA for pinado.
#### Instrução para implementador
- `/be-implement JRNY P4`. Nunca chamar provider de IA direto; DTOs gerados de `openapi.json`; index best-effort.

### Prioridade 5 -- Security + multi-tenancy + idempotência
Status: pendente
#### Objetivo / Resultado esperado
JWT + AccessDecision (`jrny.*`) + tenant guard em HTTP **e** Kafka; idempotência por `eventId`; concorrência segura de inscrição.
#### Issues vinculadas
- JRNY-012, JRNY-013, INT-JRNY-002
#### Specs cobertas
- SPEC-06, SPEC-05
#### Sequência de execução
- Fase 1: AccessEvaluateClient (INT-JRNY-002) → segurança (JRNY-012) · Fase 2: idempotência/concorrência (JRNY-013)
#### Critérios de aceite
- 401/403 corretos; tenant fixado antes de side effects (HTTP e consumer); reentrega → no-op; sem dupla inscrição ATIVA.
#### Riscos
- Cache de AccessDecision desatualizado (mitigado: invalidação por `modelo.acesso.alterado`); WRKS down → nega por omissão.
#### Instrução para implementador
- `/be-implement JRNY P5`. `@Transactional` só em application.service (RULE-03); `EmpresaContextHolder.clear()` no `finally`.

### Prioridade 6 -- Messaging
Status: pendente
#### Objetivo / Resultado esperado
6 consumers idempotentes + 4 producers (outbox) + contrato `JourneyQueryClient` para COMM/SALE.
#### Issues vinculadas
- JRNY-014, INT-JRNY-005, INT-JRNY-006
#### Specs cobertas
- SPEC-09, SPEC-01
#### Sequência de execução
- Fase 1: Kafka config (INT-JRNY-005) → consumers/producers (JRNY-014) · Fase 2: JourneyQueryClient (INT-JRNY-006)
#### Critérios de aceite
- Rollback não publica; reentrega → no-op; score/segmento dispara reroteamento ou grava `SEM_MUDANCA`; leitura de estado estável para COMM/SALE.
#### Riscos
- Ghost events (mitigado: outbox); consumer com Feign síncrono no caminho crítico (evitar).
#### Instrução para implementador
- `/be-implement JRNY P6`. Tenant do envelope; consumer crítico sem chamada Feign síncrona.

### Prioridade 7 -- Observability + health
Status: pendente
#### Objetivo / Resultado esperado
Actuator + métricas (latência de avaliação, **taxa de fallback do assist de IA**) + MDC; readiness UP mesmo com IA/Elastic degradados.
#### Issues vinculadas
- JRNY-015
#### Specs cobertas
- SPEC-07
#### Critérios de aceite
- `/actuator/health` liveness/readiness; métrica de fallback de IA; logs com `correlationId`/`empresaId`/`leadId`.
#### Instrução para implementador
- `/be-implement JRNY P7`. `@Slf4j`, nunca `System.out`.

### Prioridade 8 -- BDD end-to-end
Status: pendente
#### Objetivo / Resultado esperado
Cenários Cucumber executáveis cobrindo as ~158 cláusulas SHALL (gate D-218).
#### Issues vinculadas
- JRNY-016
#### Specs cobertas
- SPEC-08 (+ todas)
#### Critérios de aceite
- `*CucumberIT*` executa os 3 features; ≥1 cenário por SHALL; WRKS/ASST/TechLab AI stubados (inclui IA indisponível → fallback).
#### Instrução para implementador
- `/be-implement JRNY P8`. Testcontainers PostgreSQL com schema migrado.

## 3. Dependências externas
- **WRKS** (AccessDecision/JWKS) — runtime. **LEAD** (eventos de qualificação/score/segmento —
  gatilho + payload da `condicao`). **ASST** (`AssetQueryClient` + `asset.versao.publicada`).
  **MIG** (schema `emp_<slug>`). **TechLab AI** (`orchestration`, P3 placeholder — assist opcional).
  **Elasticsearch** (`journey-events`/`routing-decisions`). **Kafka/AWS MSK**. **REG/GWY**.

## 4. Restrições arquiteturais
- ArchUnit RULE-01..09 (CLAUDE.md) — bloqueante.
- Camadas hexagonais (api/application/domain/infrastructure).
- `@Transactional` somente em `application.service`.
- Domínio sem Spring/JPA; controller nunca retorna `@Entity`.
- Nunca chamar provider de IA direto (sempre via TechLab AI HTTP); assist é opcional (fallback determinístico).
- `empresa_id` como guarda em todas as tabelas (schema isola; validado nos adapters); tenant fixado em HTTP **e** no consumo de eventos.
- Decisão de roteamento imutável (insert-only); JRNY decide e sinaliza, não executa.

## 5. Referências
- `docs/architecture/backend/services/jrny-service/` (vision 01..06, ADRs, contracts, specs, diagrams)
- `docs/architecture/backend/issues/JRNY-001..016.md`, `INT-JRNY-001..006.md`, `issues_map-JRNY.md`
- `docs/architecture/backend/services/jrny-service/generator-config.yml`
