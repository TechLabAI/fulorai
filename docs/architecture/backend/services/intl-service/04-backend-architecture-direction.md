# 04 — Backend Architecture Direction — INTL

> Serviço: `intl-service` · Pacote: `com.journeyos.intl` · Porta: `8087`

## 1. Stack

- **Java 21**, **Spring Boot 3.5.x**, **Gradle 8.x (Kotlin DSL)**.
- **PostgreSQL 15+** + **pgVector** (schema `emp_<slug>`; coluna de embedding opcional).
- **Elasticsearch 9.x** via `backend/services/elastic-client-lib` (`SearchPort`/`IndexPort`).
- **Kafka / AWS MSK** (consumer transversal + producer).
- **TechLab AI** (HTTP) — `knowledge` + `orchestration`; DTOs gerados de `openapi.json`.
- **Resilience4j** (circuit breaker/timeout/fallback), **Eureka** (REG), **Flyway** via MIG.

## 2. Service Boundary (single service vs decomposição)

**Decisão (ADR-002):** **single service** `intl-service`. Copilot/Conhecimento e a
governança-de-plataforma/leitura-analítica compartilham contexto de `empresa`, o mesmo
`elastic-client-lib` e o mesmo ciclo de autorização — separá-los no MVP traria overhead de rede e
de coordenação sem ganho. A fronteira interna entre os dois é marcada por **portas distintas**
(`KnowledgePort`/`OrchestrationPort` vs `SearchPort` analítico), o que permite extrair um
`intl-platform-service` no pós-MVP sem reescrever o domínio.

## 3. Package Organization

```
com.journeyos.intl
├── api/
│   ├── controller/   CopilotController, KnowledgeController, AnalyticsController
│   ├── dto/          *Request / *Response (Java records)
│   └── exception/    @RestControllerAdvice + ProblemDetail (RFC 7807)
├── application/
│   ├── service/      CopilotService, KnowledgeIngestService, AnalyticsService, EventPlatformService
│   └── port/
│       ├── in/       ResponderCopilotoUseCase, CurarConhecimentoUseCase, ConsultarAnaliticaUseCase
│       └── out/      SearchPort, IndexPort, KnowledgePort, OrchestrationPort,
│                     IntlEventPublisherPort, AccessDecisionCachePort, AssetQueryPort
├── domain/
│   ├── model/        ConversaCopiloto, MensagemCopiloto, NoConhecimento, BaseConhecimento,
│   │                 Citacao, EventoIndexado, RegistroIndice, enums
│   └── service/      RankingFundamentacaoService, TraceabilityValidator (POJOs puros)
└── infrastructure/
    ├── clients/      TechLabAiClient (HTTP), AssetQueryClient (@FeignClient asst-service),
    │                 AccessEvaluateClient (@FeignClient wrks-service)
    ├── config/       DomainServiceConfig, Resilience4jConfig, ElasticConfig
    ├── messaging/    consumer/ (asset.versao.publicada, empresa.provisionada, modelo.acesso.alterado)
    │                 producer/ (copilot.resposta.gerada)
    ├── persistence/  entity/ repository/ adapter/ (JPA emp_<slug>)
    ├── elastic/      IntlIndexAdapter / IntlSearchAdapter (sobre elastic-client-lib)
    └── security/     filtros JWT, MDC, EmpresaContextHolder
```

## 4. Hub Service Dependencies

- **WRKS** — `AccessEvaluateClient` (autorização `intl.*`) + JWKS; eventos
  `empresa.provisionada` / `modelo.acesso.alterado`.
- **ASST** — `AssetQueryClient` (conteúdo de asset publicado como fonte de conhecimento — opcional);
  evento `asset.versao.publicada`.
- **MIG** — schema `emp_<slug>` + registro de índices (pré-condição).
- **REG** — service discovery (Eureka).

## 5. External Integrations

- **TechLab AI** (`knowledge` + `orchestration`) — síncrono, circuit breaker, timeout curto,
  fallback recuperação-apenas. Custo/latência registrados por resposta. Sem chamada direta a
  provedor de IA.
- **Elasticsearch** — `SearchPort` (recuperação RAG + analítica cross-index), `IndexPort`
  (projeções próprias `ai-copilot-events`/`knowledge-nodes` + DLQ). Toda query filtra `empresa`.

## 6. Async vs Sync Decisions

| Fluxo | Modo | Racional |
|---|---|---|
| Pergunta ao Copilot | **Síncrono** (REST) | UX conversacional exige resposta imediata; circuit breaker protege a TechLab AI. |
| Ingestão de conhecimento via `asset.versao.publicada` | **Assíncrono** (Kafka consumer) | Desacopla ASST; embedding/index pode ser feito fora do caminho crítico. |
| Projeção `ai-copilot-events` | **Síncrono** ao gerar a resposta | Auditoria/custo no mesmo fluxo; idempotente por doc-id. |
| `copilot.resposta.gerada` | **Assíncrono** (producer) | Notifica consumidores de analítica/auditoria. |
| Seed por `empresa.provisionada` | **Assíncrono** (Kafka consumer) | Provisão por tenant fora do caminho de request. |
| Leitura analítica | **Síncrono** (REST, read-only) | Consulta sob demanda; sem escrita. |
