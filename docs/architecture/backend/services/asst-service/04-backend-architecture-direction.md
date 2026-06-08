# 04 — Backend Architecture Direction — ASST (Asset Hub)

> Direção técnica do `asst-service`. Decisões com tradeoff → ADR.

## 1. Stack

- **Java 21** · **Spring Boot 3.5.x** · **Gradle 8.x (Kotlin DSL)**.
- **PostgreSQL 15+** (schema operacional `emp_<slug>`; `ddl-auto: validate`, DDL via MIG/Flyway).
- **Elasticsearch 9.x** (índice dimension `assets`, ingest `direct-java-client`).
- **Kafka / AWS MSK** (event bus `journey-os.*`).
- **TechLab AI** (HTTP — `document_composition` + classificação; consumido via cliente gerado de `openapi.json`).
- **Eureka (REG)** para discovery · **GWY** como edge · **WRKS** para identidade/AccessDecision.
- Resilience4j (circuit breaker/timeout nas chamadas TechLab AI), Lombok, SLF4J, MapStruct (opcional para mapeamento entity↔domain).

## 2. Service Boundary

**Single service** (`asst-service`) — default do monorepo (ver `ADR-002`). O domínio de assets
é coeso (asset + versão + aprovação + studio + busca) e não justifica decomposição no MVP. O
Asset Studio é um **caso de uso interno** (orquestra TechLab AI), não um serviço separado.

## 3. Package Organization

Base `com.journeyos.asst` (layout hexagonal canônico — `services-catalog.md` §3):

```
com.journeyos.asst
├── api/            controller/ (AssetController, AssetStudioController, AssetApprovalController)
│                   dto/ (records Request/Response) · exception/ (@RestControllerAdvice, ProblemDetail)
├── application/    service/ (CriarAssetService, ComporNoStudioService, SubmeterAssetService,
│                            AprovarAssetService, PublicarAssetService, BuscarAssetsService)
│                   port/in/ (use cases) · port/out/ (AssetRepositoryPort, AssetSearchPort,
│                            ComposicaoIaPort, AccessDecisionPort, EventoPublisherPort)
├── domain/         model/ (Asset, VersaoAsset, Aprovacao, EstadoAsset, TipoAsset) — zero Spring/JPA
│                   service/ (TransicaoEstadoService, PoliticaVersaoService)
└── infrastructure/ persistence/ (entity/repository/adapter — JPA emp_<slug>)
                    clients/ (AccessEvaluateClient @FeignClient → wrks-service; TechLabAiClient)
                    messaging/ (producer/ consumer/) · search/ (Elastic adapter `assets`)
                    config/ (DomainServiceConfig, Resilience4jConfig) · security/ (JWT, EmpresaContextHolder)
```

`@Transactional` apenas em `application/service` (RULE-03). `@FeignClient` apenas em
`infrastructure/clients` (RULE-06).

## 4. Hub Service Dependencies

| Dependência | Tipo | Uso |
|---|---|---|
| **WRKS** | sync (Feign `AccessEvaluateClient`) + JWKS | Autorização `asst.*` + validação de JWT. |
| **MIG** | precondição | Schema `emp_<slug>` provisionado antes do bootRun. |
| **REG (Eureka)** | discovery | Registro/descoberta de `asst-service`. |
| **GWY** | edge | Roteia `/api/v1/assets/**` para ASST. |

## 5. External Integrations

- **TechLab AI** (`document_composition`): Asset Studio compõe/edita conteúdo. Cliente gerado de `integrations/techlab-ai/openapi.json` (DTOs em `gen/techlabai/`, **não** hand-written). Timeout + circuit breaker; fallback graceful (Studio degrada, CRUD intacto). Endpoint declarado na tabela de consumo do `CLAUDE.md` via `/be-architect-vision`.
- **Elasticsearch** (`assets`): adapter de busca + projeção de Asset Intelligence (tags/classificação). Reindex idempotente na publicação. Contrato em `elastic-data-contract.md`.
- **Object storage (binários):** **fora do MVP** — binários referenciados por URL externa. S3/presigned-URL é assunção pós-MVP (ver `06`).

## 6. Async vs Sync Decisions

| Operação | Modo | Racional |
|---|---|---|
| CRUD asset / versão | **sync** | Resposta imediata; transacional. |
| Submeter / aprovar / publicar | **sync** | State machine transacional; consistência forte. |
| Asset Studio (composição IA) | **sync com timeout + CB** (async opcional pós-MVP) | UX espera o rascunho; chamada à TechLab AI protegida por Resilience4j. Composições longas podem migrar para async (`202 + callback`) pós-MVP. |
| Indexação Elastic | **sync best-effort** (não bloqueia publicação) | Busca é projeção; falha de index não reverte publicação (reconciliação posterior). |
| Eventos de domínio | **async** (Kafka, outbox) | Desacopla COMM/JRNY/SALE; idempotente. |

---

## Referências

- `adr/ADR-001..005` · `03-initial-domain-framing.md` · `05-persistence-model.md`
- `docs/architecture/backend/standards/platform-patterns.md` (Feign+Resilience4j, Kafka, outbox)
- `docs/architecture/integrations/techlab-ai-integration.md`
