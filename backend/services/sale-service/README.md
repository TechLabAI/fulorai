# sale-service -- Operational README
> Package: `com.journeyos.sale` | Gradle: `:sale-service` | Modulo: `SALE`

# 0. Service Overview
## Papel do servico
SALE e o **motor de receita** do Journey OS: dono do pipeline de CRM (oportunidade -> estagios ->
ganho/perda), das ofertas versionadas, da ingestao idempotente de compra com reconhecimento de
receita, da atribuicao deterministica (last/first/linear-touch) e do LTV por contato, dentro de
cada `empresa`. Transforma fechamentos dispersos em um funil de receita rastreavel e auditavel.

## Responsabilidades principais
- Pipeline/CRM: ciclo de vida da oportunidade com historico de estagios.
- Ofertas versionadas (modelo ativo unico por oferta).
- Compra: ingestao idempotente (`id_externo` + `origem`) e reconhecimento de receita.
- Atribuicao de receita (default `last-touch`) e calculo de LTV por `contato_ref`.
- Emissao dos eventos `oportunidade.*`, `compra.*`, `receita.*`, `ltv.*`.

## Fora de escopo
- Processamento de pagamento (gateway externo / checkout / INTL Event Platform e a fonte da compra).
- Qualquer chamada direta a provedor de IA (sem TechLab AI no MVP -- atribuicao/LTV deterministicos).

## Schemas Postgres consumidos: `journeyos_global` + `emp_*`
Dados transacionais de receita residem no schema por empresa (`emp_<slug>`); contexto de empresa
e propagado por tenant (ver secao 1).

# 1. Arquitetura e Estrutura
## Stack
Java 21 . Spring Boot 3.5.11 . Gradle 8.x (Kotlin DSL) . PostgreSQL 15+ . ActiveMQ Artemis .
Spring Cloud (Eureka + OpenFeign + Resilience4j) . Actuator + Micrometer/Prometheus . porta 8086.

## Organizacao de pacotes
Hexagonal completa (119 arquivos Java em `src/main/java`):
- `api/` -- 5 controllers (oportunidade/oferta/compra/atribuicao/ltv), 12 DTOs, GlobalExceptionHandler (RFC 7807).
- `application/` -- 5 use cases (port in), 13 ports out (9 repositorios + EventPublisher + Search + AccessDecisionCache), 5 services.
- `domain/` -- 9 models (Oportunidade/Oferta/Compra/ItemCompra/Atribuicao/ModeloAtribuicao/Campanha/HistoricoEstagio/Ltv) + 9 domain services.
- `infrastructure/` -- clients (Feign AccessEvaluateClient), config (Domain/Feign/Security/WebMvc/Artemis/HibernateMultiTenancy), messaging (7 producers + 4 consumers), persistence (9 entities + repos + adapters + ProcessedEvent), security (multi-tenant).
- `shared/` -- audit (AuditAspect), error (ProblemDetailFactory/CodedException), messaging (EventEnvelope/EventDestinations), security (AccessContextHolder/DataScope/DataScopeFilterAspect).

## Regras arquiteturais aplicadas (RULE-01..09)
ArchUnit presente (`ArchitectureTest` RULE-01..06 + `CrossAspectArchTest`). `application.yml` conforme:
`spring.jpa.open-in-view=false` (RULE-08) e `ddl-auto=validate`. Pacote base `com.journeyos.sale` (RULE-09).
Gate ArchUnit NAO executado nesta sessao (toolchain Gradle ausente -- diferido).

## Multi-empresa: como o servico propaga EmpresaContext
Infra de tenancy presente e schema-per-tenant: `TenantContextFilter` -> `TenantContextHolder.require()`
(lanca `IllegalStateException` sem contexto) -> `TenantIdentifierResolver` + `MultiTenantConnectionProvider`
(`HibernateMultiTenancyConfig`). `AccessContextHolder.requireDataScope()` + `DataScopeFilterAspect` para
escopo de dados. Enforcement ainda NAO exercido em `application.service` (servicos vazios -- ver secao 3).

# 2. Funcionalidades e Fluxos Principais
## Fluxos criticos
Golden path da ancora `compra.confirmada` (oportunidade -> compra -> receita atribuida -> LTV):
**NAO implementado** (stub) -- planejado para P2.

## Eventos emitidos (Artemis)
Producers presentes (esqueleto): OportunidadeCriada, OportunidadeEstagioAlterado, OportunidadeGanha,
OportunidadePerdida, CompraConfirmada, ReceitaAtribuida, LtvAtualizado.
Consumers presentes (esqueleto): EmpresaProvisionada, LeadQualificado, LeadScoreAtualizado, ModeloAcessoAlterado.
Idempotencia via `ProcessedEvent`. Sem logica de publicacao/consumo real ainda.

## Endpoints principais (REST)
`/sale-service/oportunidade`, `/oferta`, `/compra`, `/atribuicao`, `/ltv` -- controllers mapeados,
porem **sem metodos de endpoint** (use cases vazios). DTOs sao stubs (apenas `tenantId` / TODO).

## Dependencias inter-servicos (Feign clients usados)
- **WRKS** via `AccessEvaluateClient` (AccessDecision/autorizacao) -- esqueleto.

# 3. Estado Atual da Implementacao
## Implementado (DONE)
- Esqueleto hexagonal completo e conforme (api/application/domain/infrastructure/shared).
- Infra transversal REAL: multi-tenancy (filter/holder/resolver/connection-provider), `AccessContextHolder`/`DataScope`/`DataScopeFilterAspect`, `AuditAspect`, `GlobalExceptionHandler` (ProblemDetail RFC 7807), `DomainServiceConfig`, `CorrelationIdInterceptor`/MDC.
- `application.yml` conforme (open-in-view=false, ddl-auto=validate).
- Migration `V1__create_initial_schema.sql` REAL (176 linhas, 9 tabelas: oportunidade/oferta/compra/item_compra/atribuicao/modelo_atribuicao/campanha/historico_estagio/ltv) com CHECKs de estado, `NUMERIC(15,2)`+moeda e indices.
- ArchUnit (2 classes) + 3 features Gherkin concretas.

## Parcial (PARTIAL / STUB)
- Controllers mapeados mas sem endpoints; DTOs com TODO (so `tenantId`).
- Producers/consumers de mensageria presentes mas sem logica.
- Feign `AccessEvaluateClient` declarado sem uso efetivo.

## Nao implementado (MISSING)
- `application.service` -- todos os 5 services vazios (`{}`); use cases (port in) vazios.
- `domain.service` -- todos os 9 com TODO (motor de atribuicao/LTV ausente).
- `infrastructure.persistence.adapter` -- todos lancam `UnsupportedOperationException`.
- `domain.model` -- agregados sem invariantes.
- Golden path da ancora `compra.confirmada` e conservacao de receita.
- BDD steps em `PendingException`.

# 4. Qualidade e Evidencias
## Testes (unit / integration)
- Unit: nenhum teste de logica (logica ausente). `ArchitectureTest` + `CrossAspectArchTest` presentes.
- Integration: `ApplicationContextLoadsIT` + `BaseIntegrationTest` (Testcontainers Postgres).
- BDD: `CucumberIT` + 3 features (sales-pipeline / purchase-revenue / revenue-attribution); steps em `PendingException`.
- Nenhum gate executado nesta sessao (toolchain Gradle ausente -- diferido).

## Cobertura funcional observada
Nula em nivel de negocio (esqueleto pre-implementacao).

## Observabilidade (logs, metricas, MDC)
Actuator + Micrometer/Prometheus declarados; `CorrelationIdInterceptor` + `MdcContextRestorer` presentes.

# 5. Gaps Atuais
- Logica de negocio 100% stub (services/use cases/domain/adapters).
- DTOs e domain models sem campos/invariantes reais.
- Desvio de convencao: `V1` reside em `src/main/resources/db/migration/` (deveria ser centralizada em `journey-os-migrations`).
- `flyway` presente no `application.yml` do servico (migracao deve vir do `journey-os-migrations`).
- RULE-07 (EmpresaContext.require em application.service) ainda nao exercido.
- Contrato exato da fonte de compra (checkout/INTL) e definicao de `contato_ref` (chave LTV) pendentes.

# 6. Issues Relacionadas ao Servico
- SALE-001 .. SALE-019 -- `docs/architecture/backend/issues/SALE-001.md` .. `SALE-019.md`
- INT-SALE-001 .. INT-SALE-005 -- `docs/architecture/backend/issues/INT-SALE-001.md` .. `INT-SALE-005.md`
- Mapa: `docs/architecture/backend/issues/issues_map-SALE.md`
- Plano: `docs/architecture/backend/plans/plan-SALE.md`

# 7. Maturidade do Servico
## Score atual (0-100): 30 -- Inicial
## Leitura executiva
Esqueleto hexagonal completo, conforme as regras estruturais (RULE-08/09 OK), com infra transversal
real (multi-tenancy, audit, data-scope, RFC 7807) e migration DDL completa (9 tabelas). Toda a logica
de receita -- pipeline, ingestao de compra, atribuicao e LTV -- esta ausente (stub). Pronto para iniciar
P1 (API CRUD) e P2 (golden path da ancora). 0/9 prioridades; 0/24 issues DONE.

# 8. Historico de Evolucao (append-only)
- 2026-06-05 -- B1 BASELINE (be-autopilot, escopo restrito a B1). README operacional gerado pelo template do validator (substitui stub de scaffold que usava o termo proibido "tool" e paths `docs/architecture/tools/...`). Estado consolidado: esqueleto hexagonal completo (119 arquivos Java, 9 agregados, 5 superficies REST, 13 ports-out, Feign WRKS, 7 producers + 4 consumers, idempotencia ProcessedEvent) + infra transversal real (multi-tenancy/audit/data-scope/MDC) + migration V1 (9 tabelas) + ArchUnit/3 features; logica de negocio 100% stub (services/use cases vazios, domain services TODO, adapters em UnsupportedOperationException, DTOs TODO, BDD PendingException). Score 30 (Inicial). Gates B5 diferidos (toolchain Gradle ausente). Loop B2->B5 NAO executado (usuario pediu apenas BASELINE).

# 9. Estado Atual Resumido (para agentes)
STRUCTURAL: OK
FUNCTIONAL: LOW
INTEGRATION: LOW
OBSERVABILITY: PARTIAL
RESILIENCE: LOW
MULTI-EMPRESA: PARTIAL   (RULE-07 enforce ainda nao exercido -- infra presente, application.service vazio)

# 10. Proxima Atencao Recomendada
IMPLEMENTADOR -> P1 (Scaffold + API CRUD: definir DTOs/use cases e endpoints de oportunidade/oferta/compra),
seguido de P2 (orquestracao da ancora `compra.confirmada`). Antes de P3, resolver o desvio da migration
(centralizar em `journey-os-migrations`) e confirmar alinhamento entity<->DDL para `ddl-auto=validate`.

END DOCUMENT
