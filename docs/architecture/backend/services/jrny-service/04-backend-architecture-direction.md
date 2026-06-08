# 04 — Backend Architecture Direction — JRNY (Journey & Routing)

> Direção técnica do `jrny-service`. Decisões com tradeoff → ADR.

## 1. Stack

- **Java 21** · **Spring Boot 3.5.x** · **Gradle 8.x (Kotlin DSL)** · porta local `8084`.
- **PostgreSQL 15+** (schema operacional `emp_<slug>`; `ddl-auto: validate`, DDL via MIG/Flyway).
- **Elasticsearch 9.x** (índices fact `journey-events` + `routing-decisions`, ingest `direct-java-client`).
- **Kafka / AWS MSK** (event bus `journey-os.*` — consome LEAD/ASST/WRKS, produz roteamento).
- **TechLab AI** (HTTP — capability `orchestration`; consumido via cliente gerado de `openapi.json`).
- **Eureka (REG)** para discovery · **GWY** como edge · **WRKS** para identidade/AccessDecision · **ASST** para conteúdo publicado.
- Resilience4j (circuit breaker/timeout na chamada TechLab AI), Lombok, SLF4J, MapStruct (opcional para mapeamento entity↔domain).

## 2. Service Boundary

**Single service** (`jrny-service`) — default do monorepo (ver `ADR-002`). Journey Builder
(definição), Routing Engine (decisão) e decision log são facetas coesas do mesmo domínio de
jornada e compartilham os mesmos agregados. O Routing Engine é um **componente de domínio
interno** (avalia regras + orquestra o assist de IA via port `out`), não um serviço separado.

## 3. Package Organization

Base `com.journeyos.jrny` (layout hexagonal canônico — `services-catalog.md` §3):

```
com.journeyos.jrny
├── api/            controller/ (JourneyController, RoutingRuleController, RoutingQueryController)
│                   dto/ (records Request/Response) · exception/ (@RestControllerAdvice, ProblemDetail)
├── application/    service/ (CriarJornadaService, PublicarJornadaService, DefinirRegraService,
│                            RotearLeadService, AvancarEstagioService, ConsultarJornadaDoLeadService)
│                   port/in/ (use cases) · port/out/ (JornadaRepositoryPort, InscricaoRepositoryPort,
│                            DecisaoRepositoryPort, RecomendacaoIaPort, AssetQueryPort,
│                            AccessDecisionPort, EventoPublisherPort, JourneyEventIndexPort)
├── domain/         model/ (Jornada, Estagio, RegraRoteamento, InscricaoJornada, DecisaoRoteamento,
│                          EstadoJornada, TipoEstagio) — zero Spring/JPA
│                   service/ (MotorRoteamento, TransicaoEstagioService, AvaliadorCondicao)
└── infrastructure/ persistence/ (entity/repository/adapter — JPA emp_<slug>)
                    clients/ (AccessEvaluateClient @FeignClient → wrks-service;
                             AssetQueryClient @FeignClient → asst-service; TechLabAiClient orchestration)
                    messaging/ (producer/ consumer/) · search/ (Elastic adapters journey-events/routing-decisions)
                    config/ (DomainServiceConfig, Resilience4jConfig) · security/ (JWT, EmpresaContextHolder)
```

`@Transactional` apenas em `application/service` (RULE-03). `@FeignClient` apenas em
`infrastructure/clients` (RULE-06).

## 4. Hub Service Dependencies

| Dependência | Tipo | Uso |
|---|---|---|
| **WRKS** | sync (Feign `AccessEvaluateClient`) + JWKS | Autorização `jrny.*` + validação de JWT. |
| **LEAD** | async (Kafka consumer) | Eventos `lead.qualificado`/`score.atualizado`/`segmento.alterado` → gatilho de roteamento. |
| **ASST** | sync (Feign `AssetQueryClient`) + async (evento) | Conteúdo publicado referenciado nos estágios. |
| **MIG** | precondição | Schema `emp_<slug>` provisionado antes do bootRun. |
| **REG (Eureka)** | discovery | Registro/descoberta de `jrny-service`. |
| **GWY** | edge | Roteia `/api/v1/journeys/**` e `/api/v1/routing/**` para JRNY. |

## 5. External Integrations

- **TechLab AI** (`orchestration`): Routing Engine consulta recomendação de próximo-melhor-estágio. Cliente gerado de `integrations/techlab-ai/openapi.json` (DTOs em `gen/techlabai/`, **não** hand-written). Timeout + circuit breaker; **fallback determinístico** (regras decidem sem IA). Endpoint declarado na tabela de consumo do `CLAUDE.md` via `/be-architect-vision`.
- **ASST** (`AssetQueryClient`): leitura de assets publicados referenciados em estágios; atualização reativa por `asset.versao.publicada`.
- **Elasticsearch** (`journey-events`, `routing-decisions`): adapters de projeção fact (append-only). Index best-effort não bloqueia a decisão. Contrato em `elastic-data-contract.md`.

## 6. Async vs Sync Decisions

| Operação | Modo | Racional |
|---|---|---|
| CRUD jornada / estágio / regra | **sync** | Resposta imediata; transacional. |
| Publicar / arquivar jornada | **sync** | State machine transacional; consistência forte. |
| Gatilho de roteamento (lead.qualificado etc.) | **async** (Kafka consumer) | Reage a sinais de LEAD; desacoplado; idempotente. |
| Assist de IA (`orchestration`) | **sync com timeout + CB** | A decisão espera a recomendação por uma janela curta; falha → fallback determinístico imediato (nunca bloqueia). |
| Avaliação de regras (Routing Engine) | **sync (em domínio)** | Determinística e local; sem I/O além do assist opcional. |
| Indexação Elastic (`journey-events`/`routing-decisions`) | **sync best-effort** (não bloqueia decisão) | Telemetria/auditoria é projeção; falha de index não reverte a decisão (reconciliação posterior). |
| Eventos de domínio (`lead.roteado` etc.) | **async** (Kafka, outbox) | Desacopla COMM/SALE; idempotente. |

---

## Referências

- `adr/ADR-001..005` · `03-initial-domain-framing.md` · `05-persistence-model.md`
- `docs/architecture/backend/standards/platform-patterns.md` (Feign+Resilience4j, Kafka, outbox)
- `docs/architecture/integrations/techlab-ai-integration.md`
