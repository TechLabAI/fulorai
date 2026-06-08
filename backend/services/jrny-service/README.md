# jrny-service -- Operational README
> Package: `com.journeyos.jrny` | Gradle: `:jrny-service` | Modulo: `JRNY` (Journey & Routing)

# 0. Service Overview

## Papel do servico
Motor de **jornada e roteamento** do Journey OS. Reúne três responsabilidades:
- **Journey Builder** — define jornadas multi-estágio versionadas (state machine de publicação RASCUNHO→PUBLICADA→ARQUIVADA).
- **Routing Engine** — a cada evento de domínio (lead qualificado/score/segmento) decide o próximo estágio do lead via regras determinísticas versionadas + assist de IA **opcional** (TechLab AI `orchestration`, com fallback determinístico).
- **Decision log imutável** — audita o "por quê" de cada decisão (insert-only).

JRNY **decide e sinaliza** (emite `lead.roteado`, `estagio.transicionado`, `jornada.*`); **não** executa ações de canal/venda (isso é de COMM/SALE).

## Responsabilidades principais
Journey Builder (CRUD jornada/estágios + publicar/arquivar/nova-versão); avaliação determinística de regras por prioridade; matrícula/avanço de inscrição; decision log; orchestration assist opcional; telemetria de jornada (Elastic); consumo de conteúdo publicado de ASST.

## Fora de escopo
Execução de canal (COMM), venda/receita (SALE), qualificação/score do lead (LEAD), identidade/RBAC (WRKS), chamada direta a provider de IA (sempre via TechLab AI HTTP).

## Schemas Postgres consumidos
`emp_<slug>` (schema-per-tenant). JRNY opera **somente** no schema da empresa; não toca `journeyos_global`. Migrations centralizadas em `journey-os-migrations`.

# 1. Arquitetura e Estrutura

## Stack
Java 21 · Spring Boot 3.5.x · Gradle 8.x (Kotlin DSL) · PostgreSQL 15+ (schema-per-tenant) · ActiveMQ Artemis (eventos) · Spring Cloud (Eureka + OpenFeign + Resilience4j) · porta local `8084`.

## Organizacao de pacotes
Estrutura hexagonal completa presente (`com.journeyos.jrny`):
- `api/` — controller (5: Jornada, Estagio, RegraRoteamento, RoteamentoQuery, RotearLead), dto (10 records), exception (GlobalExceptionHandler).
- `application/` — service (5), port/in (5 use cases), port/out (10 ports: repos + EventPublisher + RecomendacaoIa + AssetQuery + AccessDecision + JourneyEventIndex).
- `domain/` — model (5 records: Jornada, Estagio, RegraRoteamento, InscricaoJornada, DecisaoRoteamento), service (5 domain services).
- `infrastructure/` — clients (2 Feign), config (7), messaging/{consumer(6), producer(4)}, persistence/{entity(6), repository(6), adapter(5)}, security (multi-tenancy + JWT + correlation).
- `shared/` — audit (AuditAspect), error (ProblemDetail), messaging (EventEnvelope), security (AccessContextHolder, DataScope).

## Regras arquiteturais aplicadas (RULE-01..09)
ArchUnit presente: `architecture/ArchitectureTest.java` (72 linhas) + `CrossAspectArchTest.java`. Cobrem boundaries de camada, `@Transactional` só em `application.service`, base package `com.journeyos.jrny`. **Não executadas** neste baseline (toolchain Gradle ausente — gate diferido).

## Multi-empresa: como o servico propaga EmpresaContext
Infra de tenancy **real e presente** (não-stub): `TenantContextFilter` (lê claim JWT `tenant_id`, valida header `X-Tenant-Id`, 403 em mismatch), `TenantContextHolder`, `MultiTenantConnectionProvider`, `TenantIdentifierResolver`, `HibernateMultiTenancyConfig` (schema resolvido por tenant em runtime). `MdcContextRestorer` propaga contexto no consumo de eventos. **Lacuna:** como os `application.service` estão vazios, ainda **não há** chamadas `EmpresaContextHolder.require()` no caminho de caso de uso (RULE-07 ainda não exercida) — será introduzida em P5.

# 2. Funcionalidades e Fluxos Principais

## Fluxos criticos
Golden path-alvo: *evento de domínio (lead qualificado) → avaliar regras (+assist opcional) → decidir alvo → matricular/avançar inscrição → registrar decisão imutável → emitir `lead.roteado`*. **Estado atual:** wiring presente, lógica ausente (ver §3).

## Eventos emitidos (Artemis) — producers presentes (4)
`LeadRoteadoProducer`, `EstagioTransicionadoProducer`, `JornadaPublicadaProducer`, `JornadaConcluidaProducer`. (Esqueleto; emissão via outbox a implementar em P2/P6.)

## Eventos consumidos — consumers presentes (6)
`LeadQualificadoConsumer`, `LeadScoreAtualizadoConsumer`, `LeadSegmentoAlteradoConsumer`, `AssetVersaoPublicadaConsumer`, `EmpresaProvisionadaConsumer`, `ModeloAcessoAlteradoConsumer`. Idempotência prevista via `ProcessedEvent` (entity + repo presentes).

## Endpoints principais (REST)
Controllers mapeados (`/jrny-service/...`): jornada, estágios, regra-roteamento, rotear-lead, roteamento-query. **Sem métodos/handlers implementados ainda** — apenas injeção do use case.

## Dependencias inter-servicos (Feign clients usados)
`AccessEvaluateClient` (WRKS — AccessDecision `jrny.*`), `AssetQueryClient` (ASST — conteúdo publicado de estágio). Portas out para TechLab AI (`RecomendacaoIaPort`) e Elastic (`JourneyEventIndexPort`) presentes como interfaces vazias.

# 3. Estado Atual da Implementacao

## Implementado (DONE)
- Esqueleto hexagonal completo (todas as camadas, 5 controllers / 5 services / 5 domain services / 10 ports / 6 consumers / 4 producers / 5 adapters).
- Infra transversal real: multi-tenancy (filter + Hibernate providers), SecurityConfig (OAuth2 RS), `CorrelationIdInterceptor`, `AuditAspect`, `DataScopeFilterAspect`, `ArtemisConfig`, `FeignClientConfig`, `WebMvcConfig`, `DomainServiceConfig`.
- Migration `V1__create_initial_schema.sql` real e completa: **5 tabelas** (jornada, estagio, + 3) com `empresa_id` guard, CHECKs de state machine, índices.
- Testes estruturais reais: ArchUnit (2 classes) e 3 features Gherkin (journey-creation, routing-decision, stage-transition) com Background/Scenarios concretos.

## Parcial (PARTIAL / STUB)
- **JPA entities** — **alinhadas à DDL da migration** (2026-06-05): as 5 entities mapeiam exatamente as colunas de `V1` (`id`/`empresa_id`/`nome`/`estado_jornada`/`versao`/JSONB via `@JdbcTypeCode(SqlTypes.JSON)`/`TIMESTAMPTZ` via `OffsetDateTime`). `decisao_roteamento` marcada `updatable=false` (decisão imutável, ADR-005). `ddl-auto=validate` agora bate. **Falta** o mapeamento domínio↔entity nos adapters (ainda stub) — P3.
- **BDD step definitions** — classes presentes, todos os steps lançam `PendingException`.
- **Idempotência** — `ProcessedEvent` + repo presentes; lógica de dedupe não implementada.

## Nao implementado (MISSING)
- Toda a lógica de negócio: use cases (interfaces vazias), `application.service` (corpos vazios, ex.: `RotearLeadService`), `domain.service` (TODOs), `domain.model` (records mínimos com TODO), DTOs (records de 1 campo com TODO).
- Routing Engine (avaliação determinística por prioridade), decision log imutável, state machines de jornada/inscrição.
- Integrações efetivas: TechLab AI `orchestration` (port vazio; `openapi.json` upstream ainda placeholder), AssetQuery, projeção Elastic.
- Persistência funcional (adapters sem round-trip validado), emissão/consumo real de eventos, RULE-07 enforcement nos serviços.

# 4. Qualidade e Evidencias

## Testes (unit / integration)
- Unit: nenhum teste de unidade de negócio (lógica ausente).
- Architecture: `ArchitectureTest` + `CrossAspectArchTest` presentes — **não executados** (Gradle ausente).
- Integration: `BaseIntegrationTest` (singleton Testcontainers pattern) + `ApplicationContextLoadsIT` presentes — não executados.
- BDD: 3 features completas; steps em `PendingException`.

## Cobertura funcional observada
0/8 prioridades funcionalmente fechadas. Cobertura de negócio observada: nula (apenas esqueleto + infra transversal).

## Observabilidade (logs, metricas, MDC)
`@Slf4j` (Lombok) disponível; `CorrelationIdInterceptor` + `MdcContextRestorer` presentes (correlationId/tenant no MDC em HTTP e no consumo de eventos). Sem métricas de domínio customizadas ainda (ex.: taxa de fallback do assist de IA — prevista em P7). Actuator a confirmar em P7.

# 5. Gaps Atuais

- **~~[BLOQUEANTE — P3] Drift entity ↔ migration~~ — RESOLVIDO (2026-06-05):** as 5 JPA entities foram alinhadas à DDL de `V1` (colunas, tipos, nullability, JSONB, `TIMESTAMPTZ`→`OffsetDateTime`, PK `id`); os 5 `JpaRepository` tiveram a query derivada `findByTenantId(String)` trocada por `findByEmpresaId(UUID)`. `ddl-auto=validate` deixa de falhar. Pendente de confirmação formal pelo gate `:jrny-service:integrationTest` (toolchain Gradle ausente — diferido).
- **Lógica de negócio 100% ausente** — todos os use cases/services/domain/DTOs são stubs gerados (TODO).
- **RULE-07 ainda não exercida** — sem `EmpresaContextHolder.require()` nos serviços (serviços vazios).
- **TechLab AI `orchestration` placeholder** — `RecomendacaoIaPort` vazio; `integrations/techlab-ai/openapi.json` ainda vazio (P3 global), logo DTOs não geráveis. Caminho determinístico é o padrão obrigatório.
- **Gramática de `condicao`** (predicado jsonb das regras) a definir/validar no implement (ancorada nos campos de `lead.qualificado`).
- **Permissões `jrny.*`** a confirmar no RBAC global.
- **Gates B5 não executáveis** — toolchain Gradle ausente no ambiente (test/architectureCheck/integrationTest/CucumberIT diferidos).

# 6. Issues Relacionadas ao Servico

Funcionais (16): [JRNY-001](../../../docs/architecture/backend/issues/JRNY-001.md) bootstrap · [JRNY-002](../../../docs/architecture/backend/issues/JRNY-002.md) domínio/state machines/MotorRoteamento · [JRNY-003](../../../docs/architecture/backend/issues/JRNY-003.md) API Journey Builder · [JRNY-004](../../../docs/architecture/backend/issues/JRNY-004.md) RotearLeadService · [JRNY-005](../../../docs/architecture/backend/issues/JRNY-005.md) decision log imutável · [JRNY-006](../../../docs/architecture/backend/issues/JRNY-006.md) eventos roteamento + query API · [JRNY-007](../../../docs/architecture/backend/issues/JRNY-007.md) migrations Flyway · [JRNY-008](../../../docs/architecture/backend/issues/JRNY-008.md) persistência JPA · [JRNY-009](../../../docs/architecture/backend/issues/JRNY-009.md) assist IA + fallback · [JRNY-010](../../../docs/architecture/backend/issues/JRNY-010.md) AssetQueryClient · [JRNY-011](../../../docs/architecture/backend/issues/JRNY-011.md) projeção Elastic · [JRNY-012](../../../docs/architecture/backend/issues/JRNY-012.md) security/JWT/AccessDecision/MDC · [JRNY-013](../../../docs/architecture/backend/issues/JRNY-013.md) idempotência/concorrência · [JRNY-014](../../../docs/architecture/backend/issues/JRNY-014.md) messaging consumers/producers · [JRNY-015](../../../docs/architecture/backend/issues/JRNY-015.md) observability/health · [JRNY-016](../../../docs/architecture/backend/issues/JRNY-016.md) BDD end-to-end.

Integração (6): INT-JRNY-001..006 (bootstrap/AccessEvaluate/TechLab AI orchestration/Elastic/Kafka/JourneyQueryClient).

# 7. Maturidade do Servico

## Score atual (0-100)
**27 — Inicial.**

Dimensões (be-validator §9):
- STRUCTURAL: **OK** — esqueleto hexagonal completo, ArchUnit presente.
- FUNCTIONAL: **LOW** — golden path e CRUD do agregado ausentes (use cases/services vazios).
- INTEGRATION: **LOW** — Feign/IA/Elastic apenas como interfaces vazias.
- OBSERVABILITY: **PARTIAL** — MDC/correlation presentes; sem métricas de domínio.
- RESILIENCE: **LOW** — sem circuit breaker/idempotência efetiva.
- MULTI-EMPRESA: **PARTIAL** — infra de tenancy real e entities com `empresa_id` guard alinhado à DDL; RULE-07 (`EmpresaContextHolder.require()`) ainda não exercida nos serviços (vazios).

## Leitura executiva
Scaffold de alta qualidade: a arquitetura, a infraestrutura transversal (multi-tenancy, segurança, MDC, auditoria), a migration (5 tabelas) e os artefatos de teste (ArchUnit + 3 features Gherkin) já estão no lugar; o drift entity↔migration foi resolvido (entities batem com `V1`, `ddl-auto=validate` ok). Porém **toda a lógica de negócio das 8 prioridades segue como stub gerado** (use cases/services/domain/adapters vazios; máquinas de estado e decision log ainda ausentes). Posição: pós-scaffold, pré-P1. Próximo do baseline de ASST (32); a diferença é a ausência total das máquinas de estado de jornada/inscrição e do decision log.

# 8. Historico de Evolucao (append-only)

- 2026-06-05 — **Fix drift entity↔migration** (pós-baseline, a pedido). As 5 JPA entities (`Jornada/Estagio/RegraRoteamento/InscricaoJornada/DecisaoRoteamento`JpaEntity) foram reescritas para espelhar exatamente a DDL de `V1__create_initial_schema.sql`: PK `id` (era `<tabela>_id`), `empresa_id` UUID guard (era `tenant_id` String), todas as colunas de domínio, JSONB via `@JdbcTypeCode(SqlTypes.JSON)`, `TIMESTAMPTZ`→`OffsetDateTime`, `decisao_roteamento` `updatable=false` (imutável). Os 5 `JpaRepository` trocaram a query derivada `findByTenantId(String)`→`findByEmpresaId(UUID)` (evita falha de bootstrap do Spring Data). `processed_events`/`outbox_event` confirmados como providos pela migration compartilhada de idempotência/outbox (data-model.md §289) — `ProcessedEvent` intacto. `ddl-auto=validate` deixa de falhar; confirmação formal diferida ao gate `:jrny-service:integrationTest` (toolchain Gradle ausente).
- 2026-06-05 — **B1 BASELINE** (be-autopilot, escopo restrito a B1). README operacional gerado a partir do template do validator (substitui o stub de scaffold que usava paths inexistentes `docs/architecture/tools/...`). Estado real consolidado: scaffold hexagonal completo + infra transversal real + migration de 5 tabelas + ArchUnit/3 features; lógica de negócio 100% stub; drift entity↔migration detectado. Score 27 (Inicial). 0/8 prioridades. Gates B5 não executados (toolchain Gradle ausente — diferido).

# 9. Estado Atual Resumido (para agentes)

STRUCTURAL: OK
FUNCTIONAL: LOW
INTEGRATION: LOW
OBSERVABILITY: PARTIAL
RESILIENCE: LOW
MULTI-EMPRESA: PARTIAL   (entities com empresa_id alinhado à DDL; RULE-07 ainda não exercida nos serviços)

# 10. Proxima Atencao Recomendada

Decisão de fluxo (B2): **IMPLEMENTADOR → P1** (Scaffold + domínio + Journey Builder), via `/be-implement JRNY P1` — preencher domain models a partir de `domain-model-diagram.puml`, máquina de publicação e API Journey Builder. **Antes de P3**, resolver o drift entity↔migration (regenerar as JPA entities alinhadas à DDL de `V1`). Fechamento formal das prioridades fica **diferido** até o toolchain Gradle existir (replay em lote via `python scripts/be-gates-replay.py --run --update`). _(Ação não executada neste passo — usuário pediu apenas BASELINE.)_

END DOCUMENT
