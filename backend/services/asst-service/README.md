# asst-service -- Operational README
> Package: `com.journeyos.asst` | Gradle: `:asst-service` | Modulo: `ASST`

# 0. Service Overview

## Papel do servico
Asset Hub: repositorio unico de ativos de conteudo do workspace. Responsavel por catalogacao,
**versionamento imutavel**, **workflow de aprovacao** (rascunho->revisao->aprovado->publicado),
**Asset Studio** (composicao assistida por IA via TechLab AI `document_composition`) e **Asset
Intelligence** (tagging + indice Elastic `assets`). Assets publicados sao consumidos por COMM/JRNY/SALE.

## Responsabilidades principais
- CRUD e catalogo de `Asset`; maquina de estados do ciclo de vida.
- Versionamento imutavel (`VersaoAsset`) + workflow de `Aprovacao` (submit/approve/reject/publish).
- Asset Studio: composicao/edicao de conteudo via TechLab AI (`document_composition`).
- Asset Intelligence: tagging (`TagAsset`) + indexacao/busca via Elasticsearch (`assets`).
- Emissao de eventos de dominio (outbox) e exposicao de assets publicados (Feign/evento).

## Fora de escopo
- Chamada direta a provider de IA (sempre via TechLab AI HTTP).
- Processamento/armazenamento de binarios (object storage S3 e pos-MVP; assets por URL).
- Logica de jornada/comunicacao/venda (consumidores externos).

## Schemas Postgres consumidos
`emp_<slug>` (schema-per-tenant; tabelas operacionais **sem** `empresa_id` -- o schema isola).
Nao consome `journeyos_global` para dados operacionais. DDL provisionado por `journey-os-migrations`
(`db/migration/empresa/`, V7+); o servico roda `ddl-auto=validate`.

# 1. Arquitetura e Estrutura

## Stack
- Java 21 (toolchain) · Spring Boot 3.5.11 · Gradle 8.x (Kotlin DSL).
- Spring Web (MVC) · Spring Data JPA · PostgreSQL (schema-per-tenant via Hibernate multi-tenancy).
- Spring Security OAuth2 Resource Server (JWT) · OpenFeign (AccessDecision/WRKS) · Resilience4j.
- Kafka (eventos) · Actuator + Micrometer · Lombok · ArchUnit.

## Organizacao de pacotes
Esqueleto hexagonal **completo** gerado:
- `api.controller` (Asset, VersaoAsset, Aprovacao, AssetStudio, BuscaAsset) + `api.dto` (records) + `api.exception` (GlobalExceptionHandler/ProblemDetail).
- `application.service` (Asset, VersaoAsset, Aprovacao, AssetStudio, BuscaAsset) + `application.port.in` (UseCases) + `application.port.out` (4 RepositoryPort + ComposicaoIaPort + AccessDecisionPort + AssetSearchPort + EventPublisherPort).
- `domain.model` (Asset, VersaoAsset, Aprovacao, TagAsset) + `domain.service` (AssetDomainService).
- `infrastructure`: `persistence.{entity,repository,adapter}`, `messaging.{producer,consumer}`, `clients` (AccessEvaluateClient), `config`, `security`.
- `shared`: `audit` (AuditAspect/AuditAction), `security` (DataScope/AccessContextHolder/DataScopeFilterAspect), `error`, `messaging` (EventEnvelope/EventDestinations).

## Regras arquiteturais aplicadas (RULE-01..09)
- ArchUnit (`ArchitectureTest` + `CrossAspectArchTest`) cobre RULE-01..06 + aspectos transversais.
- RULE-08 OK: `spring.jpa.open-in-view: false`. RULE-03: `@Transactional` so em `application.service`.
- RULE-09 OK: pacote base `com.journeyos.asst`. `ddl-auto=validate` (RULE de migrations).
- Gates ArchUnit/test/integration **nao executados nesta baseline** (toolchain Gradle ausente — diferido).

## Multi-empresa: como o servico propaga EmpresaContext
Infra de multi-tenancy presente e wired: `TenantContextFilter` -> `TenantContextHolder` ->
`TenantIdentifierResolver` + `MultiTenantConnectionProvider` (`HibernateMultiTenancyConfig`) trocam
o schema por tenant. `DataScopeFilterAspect`/`AccessContextHolder` + `AuditAspect` presentes.
**Pendencia:** RULE-07 (`TenantContextHolder.require()`) ainda nao aplicado nos `application.service`
(servicos sao stubs vazios) — sera fechado em P5.

# 2. Funcionalidades e Fluxos Principais

## Fluxos criticos (golden path alvo, ainda nao implementado)
criar -> compor (Studio/IA) -> submeter -> aprovar -> publicar (versao vigente + evento-ancora
`asset.versao.publicada`). Atualmente apenas o esqueleto: controllers/services sem corpo.

## Eventos emitidos (Kafka, via producers — esqueleto)
`AssetCriadoProducer`, `AssetAprovadoProducer`, `AssetRejeitadoProducer`, `AssetVersaoPublicadaProducer`.
Consumidos: `EmpresaProvisionadaConsumer`, `ModeloAcessoAlteradoConsumer`. Idempotencia: entidade
`ProcessedEvent` + repository presentes (ainda nao integrados aos consumers). `EventEnvelope` definido.

## Endpoints principais (REST — mapeados, sem corpo)
`/asst-service/asset` (AssetController) + controllers de versao, aprovacao, studio e busca. Metodos
ainda nao declarados (UseCases sao interfaces vazias). `/actuator/health` + `/actuator/prometheus`.

## Dependencias inter-servicos (Feign clients usados)
- `AccessEvaluateClient` (Feign) -> WRKS (AccessDecision/`asst.*`).
- `ComposicaoIaPort` -> TechLab AI (`document_composition`) — contrato placeholder (sync upstream pendente).
- `AssetSearchPort` -> Elasticsearch (`assets`). `EventPublisherPort` -> Kafka.

# 3. Estado Atual da Implementacao

## Implementado (DONE)
- Esqueleto hexagonal completo (api/application/domain/infrastructure/shared) executavel.
- Infra de multi-tenancy (filter + holder + resolver + connection provider + Hibernate config).
- Infra de seguranca/auditoria (DataScope aspect, AuditAspect, GlobalExceptionHandler/ProblemDetail).
- Esqueleto de mensageria (4 producers + 2 consumers) + idempotencia (`ProcessedEvent` + repo).
- 4 entidades JPA (`Asset/VersaoAsset/Aprovacao/TagAsset` + `ProcessedEvent`), 4 repos, 4 adapters.
- `application.yml`: `open-in-view:false`, `ddl-auto:validate`, flyway off (migrations externas),
  Actuator (health/prometheus), MDC logging (`correlationId`/`tenantId`/`userId`).
- ArchUnit (`ArchitectureTest` + `CrossAspectArchTest`) + smoke `ApplicationContextLoadsIT`.

## Parcial (STUB)
- `domain.model.*` — records com campos minimos (`id/tenantId/createdAt/status`) + `// TODO` (faltam campos do data-model).
- `domain.service.AssetDomainService` — vazio (`// TODO` invariantes).
- `application.port.in.*UseCase` — interfaces vazias (sem assinaturas).
- `application.service.*Service` — `@Service @Transactional` sem metodos.
- `application.port.out.*` (ComposicaoIaPort/AccessDecisionPort/AssetSearchPort/EventPublisherPort) — interfaces vazias (`// TODO`).
- `persistence.adapter.*RepositoryAdapter` — metodos lancam `UnsupportedOperationException("not implemented")`.
- `JpaEntity` — campos parciais (`// TODO: complete fields from data-model.md`).

## Nao implementado (MISSING)
- **P1** logica CRUD + state machine · **P2** versionamento/aprovacao/publicacao + evento-ancora.
- **P3** migrations `emp_<slug>` + mapeamento JPA real · **P4** TechLab AI Studio + Asset Intelligence + Elastic.
- **P5** seguranca efetiva (`asst.*` AccessDecision, tenant guard, RULE-07) + idempotencia/concorrencia.
- **P6** mensageria efetiva (outbox + consumo idempotente + AssetQueryClient) · **P7** observabilidade custom.
- **P8** BDD end-to-end (3 features ja presentes em `src/test/resources/features/`, sem steps executaveis).

# 4. Qualidade e Evidencias

## Testes (unit / integration)
- Unit: `ArchitectureTest` + `CrossAspectArchTest` (ArchUnit). Sem testes unitarios de logica (sem logica).
- Integration: `ApplicationContextLoadsIT extends BaseIntegrationTest` (smoke de contexto).
- BDD: 3 `.feature` presentes (asset-creation, asset-versioning, approval-workflow) — **sem step defs** (P8).
- **Nenhum gate executado nesta baseline** (Gradle indisponivel). Status dos testes: NAO VERIFICADO.

## Cobertura funcional observada
Apenas boot/contexto + enforcement arquitetural. Nenhum caso de uso coberto (services/adapters stub).

## Observabilidade (logs, metricas, MDC)
- MDC configurado no pattern de log (`correlationId`/`tenantId`/`userId`) via `CorrelationIdInterceptor`/`MdcContextRestorer`.
- Actuator health + Prometheus expostos; micrometer com tag `application`. Metricas custom (Studio/index) pendentes (P7).

# 5. Gaps Atuais
- README anterior era stub generico ("Journey OS tool", Artemis, `t_<tenantId>`, Spring Cloud "ASST") — corrigido nesta baseline.
- Toda a logica de dominio/aplicacao/persistencia e stub (UseCases vazios, adapters lancam excecao, domain TODO).
- Contrato TechLab AI `document_composition` placeholder (`openapi.json` vazio) → DTOs ainda nao geraveis (P4 bloqueado parcialmente).
- `issuer-uri` aponta Keycloak; validacao/identidade deve alinhar com WRKS (JWKS/AccessDecision) — confirmar em P5.
- RULE-07 (`require()`) ainda nao presente nos services — risco de isolamento cross-tenant ate P5.
- Gates de build/ArchUnit/test/integration nao executaveis no ambiente (toolchain Gradle ausente) — diferidos.

# 6. Issues Relacionadas ao Servico
16 funcionais (`ASST-001..016`) + 6 de integracao (`INT-ASST-001..006`). Ver
`docs/architecture/backend/issues/issues_map-ASST.md`. Mapa por prioridade:
- P1: ASST-001/002/003 + INT-ASST-001 · P2: ASST-004/005/006 · P3: ASST-007/008
- P4: ASST-009/010/011 + INT-ASST-003/004 · P5: ASST-012/013 + INT-ASST-002
- P6: ASST-014 + INT-ASST-005/006 · P7: ASST-015 · P8: ASST-016
- Plano: [plan-ASST.md](../../../docs/architecture/backend/plans/plan-ASST.md)

# 7. Maturidade do Servico

## Score atual (0-100): 32 -- Inicial

## Leitura executiva
Scaffold estruturalmente forte: esqueleto hexagonal completo, infra de multi-tenancy/seguranca/
auditoria e esqueleto de mensageria + idempotencia ja presentes e conformes (ArchUnit por inspecao).
Porem **zero funcionalidade**: dominio, casos de uso, adapters e integracoes sao stubs (TODO /
`UnsupportedOperationException`). Pronto para iniciar P1 (dominio + CRUD); valor de negocio ainda
nao entregue. Score acima do tipico inicial puro pela densidade de infra transversal ja gerada.

# 8. Historico de Evolucao (append-only)
- 2026-06-05 -- BASELINE (Validator Modo 1): consolidado estado do scaffold (esqueleto hexagonal
  completo + infra multi-tenancy/messaging/idempotencia; logica 100% stub). README regenerado do
  template canonico (substitui stub generico). Score inicial 32. Gates Gradle nao executados (diferidos).

# 9. Estado Atual Resumido (para agentes)
STRUCTURAL: OK
FUNCTIONAL: LOW
INTEGRATION: LOW
OBSERVABILITY: PARTIAL
RESILIENCE: LOW
MULTI-EMPRESA: PARTIAL   (infra presente; RULE-07 require() ausente nos application.service — pendente P5)

# 10. Proxima Atencao Recomendada
Iniciar **P1 (Scaffold + dominio + API CRUD)**: ASST-001 (bootstrap) -> INT-ASST-001 -> ASST-002
(dominio `Asset` + state machine, completar campos do data-model e invariantes em `AssetDomainService`)
-> ASST-003 (API CRUD com DTO/ProblemDetail). Definir as assinaturas dos `*UseCase` e implementar os
`*RepositoryAdapter` (hoje lancam `UnsupportedOperationException`). Acionar Planner apenas se a ordem
do plano precisar ajuste; caso contrario seguir para o Implementador em P1.

END DOCUMENT
