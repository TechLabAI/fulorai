# intl-service -- Operational README
> Package: `com.journeyos.intl` | Gradle: `:intl-service` | Modulo: `INTL`

# 0. Service Overview

## Papel do servico
Camada de **inteligencia e plataforma** do Journey OS: AI Copilot conversacional com respostas
**fundamentadas e citadas** (RAG: Elasticsearch -> TechLab AI), Base de Conhecimento curada,
governanca da plataforma de dados Elastic (rastreabilidade/DLQ/registro de indices) e leitura
analitica cross-index. Consumidor **transversal** de eventos (ultimo da cadeia). Nunca chama IA direto;
nunca reindexa *facts* de outros modulos (ADR-003).

## Responsabilidades principais
- AI Copilot read-only com status `RESPONDIDA` / `NAO_FUNDAMENTADA` / `DEGRADADA` (RAG fundamentado).
- Base de Conhecimento (CRUD + ingestao por asset) com nos/fontes/citacoes.
- Governanca da plataforma Elastic + projecoes proprias (`ai-copilot-events`, `knowledge-nodes`).
- Leitura analitica cross-index (`analytics` e **pos-MVP**).
- Evento-ancora: `journey-os.copilot.resposta.gerada` (outbox).

## Fora de escopo
- Chamada direta a provider de IA (sempre via TechLab AI HTTP).
- Reindexacao/escrita de *facts* de outros modulos.
- Analitica avancada no MVP (read-only basico apenas).

## Schemas Postgres consumidos
`emp_<slug>` (schema-per-tenant; tabelas operacionais sem `empresa_id`). Conhecimento usa vetores
(`vector(1536)`, pgVector) — nullable. DDL por `journey-os-migrations` (`db/migration/empresa/`, V7+);
servico em `ddl-auto=validate`. Isolamento Elastic por discriminador `empresa` (multi-tenancy hibrida).

# 1. Arquitetura e Estrutura

## Stack
- Java 21 · Spring Boot 3.5.11 · Gradle 8.x (Kotlin DSL).
- Spring Web + Validation · Spring Data JPA · PostgreSQL + pgVector (schema-per-tenant).
- Spring Security OAuth2 Resource Server (JWT) · OpenFeign + Resilience4j (CB/fallback).
- Mensageria: starters Kafka **e** Artemis presentes (ver gap em §5) · Redis (cache AccessDecision).
- Actuator + Micrometer Prometheus · Lombok · ArchUnit · Testcontainers + Cucumber (deps presentes).

## Organizacao de pacotes
Esqueleto hexagonal **completo** gerado:
- `api.controller` (Copilot, Knowledge, Analytics) + `api.dto` (records) + `api.exception` (GlobalExceptionHandler/ProblemDetail).
- `application.service` (Copilot, Knowledge, Analytics) + `application.port.in` (UseCases) + `application.port.out` (7 RepositoryPort + IntlIndexPort + IntlSearchPort + KnowledgePort + OrchestrationPort + AccessDecisionCachePort + IntlEventPublisherPort).
- `domain.model` (BaseConhecimento, ConversaCopiloto, FonteConhecimento, EventoIndexado, NoConhecimento, Citacao, MensagemCopiloto) + `domain.service` (4 domain services).
- `infrastructure`: `persistence.{entity,repository,adapter}`, `messaging.{producer,consumer}`, `clients` (AccessEvaluateClient/WRKS, AssetQueryClient/ASST), `config`, `security`.
- `shared`: `audit`, `security` (DataScope/AccessContextHolder/DataScopeFilterAspect), `error`, `messaging` (EventEnvelope/EventDestinations).

## Regras arquiteturais aplicadas (RULE-01..09)
- ArchUnit (`ArchitectureTest` + `CrossAspectArchTest`) cobre RULE-01..06 + aspectos transversais.
- RULE-08 OK: `open-in-view: false`. RULE-03: `@Transactional` so em `application.service`.
- RULE-09 OK: pacote base `com.journeyos.intl`. `ddl-auto=validate`.
- Gates ArchUnit/test/integration/Cucumber **nao executados nesta baseline** (toolchain Gradle ausente — diferido).

## Multi-empresa: como o servico propaga EmpresaContext
Infra de multi-tenancy presente: `TenantContextFilter` -> `TenantContextHolder` ->
`TenantIdentifierResolver` + `MultiTenantConnectionProvider` (`HibernateMultiTenancyConfig`).
`DataScopeFilterAspect`/`AccessContextHolder` + `AuditAspect` presentes. Em Elastic, o filtro
`empresa` deve ser obrigatorio em toda query (P5). **Pendencia:** RULE-07 (`require()`) ainda nao
aplicado nos `application.service` (stubs) — fechamento em P5 (isolamento inviolavel / fail-closed).

# 2. Funcionalidades e Fluxos Principais

## Fluxos criticos (golden path alvo, ainda nao implementado)
Copilot RAG: recuperacao (Elastic) -> composicao (TechLab AI) -> fundamentacao/status -> persistencia
da conversa -> projecao (`ai-copilot-events`) -> evento `copilot.resposta.gerada`. Degradacao graciosa:
CB aberto -> resposta `DEGRADADA`/`NAO_FUNDAMENTADA`, nunca `5xx`, nunca alucina fato fundamentado.

## Eventos (Kafka/Artemis — esqueleto)
Produz: `CopilotRespostaGeradaProducer`. Consome: `AssetVersaoPublicadaConsumer`,
`EmpresaProvisionadaConsumer`, `ModeloAcessoAlteradoConsumer`. Idempotencia por `eventId`:
entidade `ProcessedEvent` + repo presentes (nao integrados). `EventEnvelope` definido.

## Endpoints principais (REST — mapeados, sem corpo)
`/intl-service/copilot`, `/intl-service/knowledge`, `/intl-service/analytics` (controllers sem
metodos; UseCases vazios). `/actuator/health` + `/actuator/prometheus`.

## Dependencias inter-servicos (Feign clients usados)
- `AccessEvaluateClient` -> WRKS (AccessDecision/JWKS, cache via `AccessDecisionCachePort`/Redis).
- `AssetQueryClient` -> ASST (consulta de asset publicado para ingestao de conhecimento).
- `KnowledgePort`/`OrchestrationPort` -> TechLab AI (`knowledge`/`orchestration`) — contrato placeholder.
- `IntlIndexPort`/`IntlSearchPort` -> Elasticsearch (governanca/projecoes) — `elastic-client-lib` ainda nao wired (ver §5).

# 3. Estado Atual da Implementacao

## Implementado (DONE)
- Esqueleto hexagonal completo (3 superficies REST, 7 agregados, 13 ports-out, 7 entidades/repos/adapters).
- Infra de multi-tenancy (filter + holder + resolver + connection provider + Hibernate config).
- Infra de seguranca/auditoria (DataScope aspect, AuditAspect, GlobalExceptionHandler/ProblemDetail).
- Esqueleto de mensageria (1 producer + 3 consumers) + idempotencia (`ProcessedEvent` + repo).
- 2 Feign clients (WRKS, ASST). `application.yml`: `open-in-view:false`, `ddl-auto:validate`,
  flyway off, Actuator (health/prometheus), MDC logging (`correlationId`/`tenantId`/`userId`).
- ArchUnit (`ArchitectureTest` + `CrossAspectArchTest`) + smoke `ApplicationContextLoadsIT`.

## Parcial (STUB)
- `domain.model.*` — records com campos minimos + `// TODO` (faltam campos do data-model; `NoConhecimento` so `id`).
- `domain.service.*` (4) — vazios. `application.port.in.*UseCase` — interfaces vazias.
- `application.service.*Service` (Copilot/Knowledge/Analytics) — `@Service @Transactional` sem metodos.
- `application.port.out.*` (KnowledgePort/OrchestrationPort/IntlIndex/IntlSearch/AccessDecisionCache/IntlEventPublisher + 7 repo) — interfaces vazias (`// TODO`).
- `persistence.adapter.*` — esqueleto (mapeamento dominio<->JPA pendente).

## Nao implementado (MISSING)
- **P1** superficie REST efetiva · **P2** Copilot orchestration (RAG, evento-ancora).
- **P3** migrations `emp_<slug>` + pgVector + mapeamento JPA · **P4** TechLab AI + Elastic + ingestao ASST.
- **P5** seguranca fail-closed + filtro `empresa` em toda query Elastic + RULE-07.
- **P6** mensageria efetiva (outbox exactly-once + consumo idempotente) · **P7** observabilidade (custo/latencia/DLQ).
- **P8** BDD (19 cenarios; 3 `.feature` presentes sem steps) · **P9** hardening (SLA/custo/runbook DLQ).

# 4. Qualidade e Evidencias

## Testes (unit / integration)
- Unit: `ArchitectureTest` + `CrossAspectArchTest` (ArchUnit). Sem testes de logica.
- Integration: `ApplicationContextLoadsIT extends BaseIntegrationTest` (smoke de contexto; Testcontainers/Cucumber configurados).
- BDD: 3 `.feature` (ai-copilot, knowledge-base, event-platform-analytics) — **sem step defs** (P8).
- **Nenhum gate executado nesta baseline** (Gradle indisponivel). Status dos testes: NAO VERIFICADO.

## Cobertura funcional observada
Apenas boot/contexto + enforcement arquitetural. Nenhum caso de uso coberto (services/adapters stub).

## Observabilidade (logs, metricas, MDC)
- MDC no pattern de log (`correlationId`/`tenantId`/`userId`). Actuator health + Prometheus expostos.
- Metricas de custo/latencia/DLQ e readiness degradada (CB aberto) pendentes (P7).

# 5. Gaps Atuais
- README anterior era stub generico ("Journey OS tool"/Artemis/`t_<tenantId>`/Spring Cloud "INTL") — corrigido nesta baseline.
- Toda a logica e stub (UseCases/ports vazios, services sem metodos, dominio TODO).
- `build.gradle.kts` com **dependencias duplicadas** (`oauth2-resource-server` 2x, `resilience4j-spring-boot3` 2x,
  `spring-security-test` em implementation+test) e glitch de formatacao (`...spring-security-test")// Test`) — limpar.
- **Mensageria ambigua:** starters Kafka **e** Artemis declarados; o alvo da plataforma e Kafka (AWS MSK) — consolidar.
- **`elastic-client-lib` nao declarado** como dependencia, embora `IntlIndexPort`/`IntlSearchPort`/`EventoIndexado` existam; pgVector (`vector(1536)`) ainda nao no build — wiring em P3/P4.
- Contrato TechLab AI `knowledge`/`orchestration` placeholder (`openapi.json` vazio) → INT-INTL-002 bloqueado; DTOs nao geraveis.
- `issuer-uri` Keycloak diverge do contrato (JWKS/AccessDecision via WRKS) — alinhar em P5.
- RULE-07 (`require()`) ausente + filtro `empresa` Elastic pendente — risco de vazamento cross-tenant ate P5.
- Gates de build/ArchUnit/test/integration/Cucumber nao executaveis (toolchain Gradle ausente) — diferidos.

# 6. Issues Relacionadas ao Servico
17 funcionais (`INTL-001..017`) + 6 de integracao (`INT-INTL-001..006`). Ver
`docs/architecture/backend/issues/issues_map-INTL.md`. Mapa por prioridade:
- P1: INTL-001/002/003/004 · P2: INTL-005/006 · P3: INTL-007/008
- P4: INTL-009/010/011 + INT-INTL-002/003/004 · P5: INTL-012 + INT-INTL-001
- P6: INTL-013/014 + INT-INTL-005/006 · P7: INTL-015 · P8: INTL-016 · P9: INTL-017
- Plano: [plan-INTL.md](../../../docs/architecture/backend/plans/plan-INTL.md)

# 7. Maturidade do Servico

## Score atual (0-100): 31 -- Inicial

## Leitura executiva
Scaffold o mais denso da plataforma: esqueleto hexagonal completo (RAG/Copilot/Knowledge/Analytics),
infra de multi-tenancy/seguranca/auditoria, mensageria + idempotencia e 2 Feign clients ja presentes.
Porem **zero funcionalidade** (tudo stub) e pendencias de wiring relevantes no build (deps duplicadas,
Kafka/Artemis ambiguo, `elastic-client-lib`/pgVector ausentes). Pronto para iniciar P1; valor ainda
nao entregue. Score ligeiramente abaixo do tipico do scaffold rico pela divida do build a sanear.

# 8. Historico de Evolucao (append-only)
- 2026-06-05 -- BASELINE (Validator Modo 1): consolidado estado do scaffold (esqueleto hexagonal
  completo + infra multi-tenancy/messaging/idempotencia + 2 Feign; logica 100% stub). README
  regenerado do template canonico. Detectados gaps de build (deps duplicadas, Kafka/Artemis ambiguo,
  elastic-client-lib/pgVector nao wired). Score inicial 31. Gates Gradle nao executados (diferidos).

# 9. Estado Atual Resumido (para agentes)
STRUCTURAL: OK
FUNCTIONAL: LOW
INTEGRATION: LOW
OBSERVABILITY: PARTIAL
RESILIENCE: LOW
MULTI-EMPRESA: PARTIAL   (infra presente; RULE-07 require() + filtro empresa Elastic ausentes — pendente P5)

# 10. Proxima Atencao Recomendada
Iniciar **P1 (Scaffold + API surface)**: INTL-001..004 — definir assinaturas dos `*UseCase`
(Copilot/Knowledge/Analytics), corpo dos controllers e DTOs, e completar campos do `domain.model`.
Em paralelo (divida tecnica de scaffold, baixo custo): sanear `build.gradle.kts` (remover deps
duplicadas, consolidar mensageria em Kafka, declarar `elastic-client-lib` + pgVector) e registrar a
divergencia `issuer-uri` (Keycloak vs JWKS WRKS) para P5. Acionar Planner so se a ordem do plano
precisar ajuste; caso contrario seguir para o Implementador em P1.

END DOCUMENT
