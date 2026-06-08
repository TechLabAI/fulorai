# lead-service -- Operational README
> Package: `com.journeyos.lead` | Gradle: `:lead-service` | Modulo: `LEAD`

# 0. Service Overview

## Papel do servico
Inteligencia de leads do Journey OS: dono do agregado **lead** em cada `empresa`
(schema-per-tenant), consolida perfil, aplica regras de qualificacao versionadas e calcula
o **Maturity Score (6D)** explicavel, com segmentacao dinamica. Transforma a base bruta em
fila priorizada/roteavel publicada via eventos `lead.*`.

## Responsabilidades principais
- Captura/dedup de leads (chave natural normalizada).
- Perfil + surveys (atributos, perguntas, respostas).
- Regras de qualificacao versionadas (exatamente uma ativa por empresa).
- Maturity Score 6D deterministico e explicavel (assist TechLab AI **opcional**, fail-open).
- Segmentacao dinamica (predicado JSON sobre perfil + score).
- Publicacao do evento-ancora `lead.qualificado` (+ `capturado`/`score.atualizado`/`segmento.alterado`).

## Fora de escopo
- Roteamento/jornada (JRNY), comunicacao (COMM), receita (SALE).
- Chamada direta a provedor de IA -- somente via TechLab AI (capability `qualification`).
- Provisionamento de schema -- responsabilidade de `journey-os-migrations` (MIG).

## Schemas Postgres consumidos: `journeyos_global` + `emp_*`

# 1. Arquitetura e Estrutura

## Stack
- Java 21 + Spring Boot 3.5.x, Gradle 8.x (Kotlin DSL).
- PostgreSQL 15+ (schema-per-tenant), ActiveMQ Artemis (JMS), Spring Cloud (Eureka + OpenFeign + Resilience4j).
- Elasticsearch (indice `leads`), Redis/Valkey (cache AccessDecision), TechLab AI via HTTP.
- Porta local: **8082**.

## Organizacao de pacotes
Estrutura hexagonal completa e presente (`api`, `application/{port.in,port.out,service}`,
`domain/{model,service}`, `infrastructure/{clients,config,messaging,persistence,security}`, `shared`):
- **api**: `LeadController`, `QualificationController`, `SegmentController`, `SurveyController` (+ DTOs records, `GlobalExceptionHandler`).
- **application**: 4 use cases in (`Lead/Qualification/Segment/Survey`), 16 ports out, 4 services.
- **domain**: 12 models + 12 domain services (POJOs puros).
- **infrastructure**: 12 adapters + 12 JPA entities + 12 JPA repos, multi-tenancy (filter/connection-provider/resolver/hibernate-config), 4 producers + 2 consumers, Feign `AccessEvaluateClient`.

## Regras arquiteturais aplicadas (RULE-01..09)
- Pacote base `com.journeyos.lead` (RULE-09): OK.
- `spring.jpa.open-in-view=false` (RULE-08): OK em `application.yml`.
- `@Transactional` somente em `application.service` (RULE-03): OK (services anotados; ainda sem corpo).
- ArchUnit presente: `architecture/ArchitectureTest.java` + `CrossAspectArchTest.java`.
- **Gate ArchUnit nao executado** (toolchain Gradle ausente -- ver §4).

## Multi-empresa: como o servico propaga EmpresaContext
Infra de schema-per-tenant scaffoldada: `TenantContextFilter` -> `TenantContextHolder` ->
`TenantIdentifierResolver` + `MultiTenantConnectionProvider` (Hibernate). `AccessContextHolder` +
`DataScopeFilterAspect` para escopo de dados. **RULE-07 (`require()` do contexto de empresa) ainda
nao exercido** nos use cases -- os `application.service` estao vazios (ver §3/§5).

# 2. Funcionalidades e Fluxos Principais

## Fluxos criticos
Golden path alvo `capturar -> perfilar -> qualificar -> segmentar -> publicar` **nao implementado**
(use cases e domain services sem corpo). Apenas a superficie (controllers/ports/adapters) existe como stub.

## Eventos emitidos (Artemis)
Producers scaffoldados (boilerplate `JmsTemplate.convertAndSend`, sem outbox):
`LeadCapturadoProducer`, `LeadQualificadoProducer`, `LeadScoreAtualizadoProducer`, `LeadSegmentoAlteradoProducer`.

## Endpoints principais (REST)
Base paths declarados (`/lead-service/lead`, `/qualification`, `/segment`, `/survey`) com
`@PreAuthorize` derivado de `rbac.arch.json`. **Sem metodos/endpoints implementados.**

## Dependencias inter-servicos (Feign clients usados)
- `AccessEvaluateClient` (WRKS -- AccessDecision) scaffoldado.
- `TechLabQualificationPort` (TechLab AI `qualification`) -- **stub vazio**, bloqueado pelo sync upstream (P3 global; `openapi.json` vazio).
- Consumers: `EmpresaProvisionadaConsumer`, `ModeloAcessoAlteradoConsumer` (stubs).

# 3. Estado Atual da Implementacao

## Implementado (DONE)
- Esqueleto hexagonal completo (todas as camadas/pacotes gerados).
- `application.yml` com `open-in-view=false`, `ddl-auto=validate`, porta 8082, pacote base correto.
- Migration `V1__create_initial_schema.sql` **completa** (12 tabelas do data-model: lead, perfil_lead,
  atributo_perfil, survey, pergunta, resposta_survey, regra_qualificacao, condicao_regra,
  maturity_score, score_dimensao, segmento, lead_segmento) com CHECKs/uniques/indices.
- Infra de multi-tenancy (filter + connection-provider + resolver + hibernate-config).
- ArchUnit + BDD scaffold (3 features: lead-capture/qualification/maturity-score; steps presentes).

## Parcial (PARTIAL / STUB)
- DTOs/entities presentes mas mapeamento minimo.
- Producers/consumers com boilerplate, sem outbox/idempotencia.
- Observabilidade: MDC/`CorrelationIdInterceptor` presentes; metricas de score ausentes.

## Nao implementado (MISSING)
- Corpo dos `application.service` (Lead/Qualification/Segment/Survey) -- vazios.
- Corpo dos `domain.service` (incl. `MaturityScoreDomainService`) -- motor de score 6D ausente.
- Ports out vazios (TODO), adapters de persistencia lancam `UnsupportedOperationException`.
- Endpoints REST (controllers sem metodos).
- Integracao TechLab AI/Elastic (DTOs nao geraveis -- sync bloqueado).
- LGPD (anonimizacao/expurgo), enforcement RULE-07 nos use cases.

# 4. Qualidade e Evidencias

## Testes (unit / integration)
- Unit: nenhum teste de negocio (services vazios).
- ArchUnit: `ArchitectureTest` (72 LOC) + `CrossAspectArchTest` presentes -- **nao executados**.
- BDD: `LeadCaptureSteps` (155 LOC) + `LeadQualificationSteps` + `MaturityScoreSteps`; `CucumberIT`.
- Integration: `ApplicationContextLoadsIT` + `BaseIntegrationTest` (singleton Testcontainer).

## Cobertura funcional observada
Nula (scaffold). Cenarios BDD nao passam ate o golden path existir.

## Observabilidade (logs, metricas, MDC)
`@Slf4j` (Lombok) em todo o codigo; MDC via `CorrelationIdInterceptor`; sem metricas custom.

> **Gates B5 nao executados:** ambiente sem toolchain Gradle (`gradlew`/wrapper ausente). Os gates
> `:lead-service:test`, `:lead-service:architectureCheck`, `:lead-service:integrationTest`,
> `*CucumberIT*` estao **diferidos** (ver implementation-master-plan, ledger de gates).

# 5. Gaps Atuais
1. Logica de negocio inteira ausente (services in/domain + ports out + adapters como stub/excecao).
2. Motor de Maturity Score 6D nao implementado (`MaturityScoreDomainService` vazio).
3. Endpoints REST nao expostos (controllers sem metodos).
4. TechLab AI `qualification` bloqueado (sync upstream -- `openapi.json` vazio; DTOs nao geraveis).
5. Indexacao Elastic `leads`, Feign WRKS e cache AccessDecision nao funcionais.
6. RULE-07 (contexto de empresa) nao exercido; LGPD (anonimizacao/expurgo) ausente.
7. **Desvio de migration:** `V1` reside em `lead-service/src/main/resources/db/migration` -- a
   convencao do projeto e migrations **centralizadas** em `journey-os-migrations` (coordenar com MIG).
8. Gates de validacao (build/test/ArchUnit/BDD) diferidos por ausencia de toolchain Gradle.

# 6. Issues Relacionadas ao Servico
23 issues (18 funcionais + 5 integracao). Detalhe em `docs/architecture/backend/issues/`:
- Funcionais: [`LEAD-001`..`LEAD-018`](../../../docs/architecture/backend/issues/) (`LEAD-NNN.md`).
- Integracao: [`INT-LEAD-001`..`INT-LEAD-005`](../../../docs/architecture/backend/issues/) (`INT-LEAD-NNN.md`).
- Mapa: `docs/architecture/backend/issues/issues_map-LEAD.md`.
- Plano por prioridade (P1..P9): `docs/architecture/backend/plans/plan-LEAD.md`.

Distribuicao por prioridade: P1 (LEAD-001/002/003 + INT-LEAD-001) · P2 (004/005/006/007) ·
P3 (008/009) · P4 (010/011 + INT-002/003) · P5 (012/013/014 + INT-004) · P6 (015/016 + INT-005) ·
P7 (017) · P8 (018) · P9 (resiliencia transversal). Estado: **0/23 DONE** (scaffold).

# 7. Maturidade do Servico

## Score atual (0-100): **22 -- Inicial**
| Dimensao | Estado | Nota |
|---|---|---|
| STRUCTURAL | OK | esqueleto hexagonal completo, RULE-08/09, ArchUnit presente |
| FUNCTIONAL | LOW | services/domain/ports vazios; adapters lancam excecao; sem endpoints |
| INTEGRATION | LOW | Feign/TechLab/Elastic scaffold; TechLab bloqueado (sync) |
| OBSERVABILITY | PARTIAL | MDC/correlacao ok; sem metricas |
| RESILIENCE | LOW | Resilience4j configuravel; nada funcional |
| MULTI-EMPRESA | PARTIAL | infra schema-per-tenant presente; RULE-07 nao exercido |

## Leitura executiva
Servico **scaffold-completo** com migration de dados real (12 tabelas) e infra de multi-tenancy,
porem **sem nenhuma logica de negocio**. Pronto para iniciar o ciclo de implementacao a partir de
P1 (contratos minimos) -> P2 (golden path). Gates formais aguardam toolchain Gradle.

# 8. Historico de Evolucao (append-only)
- 2026-06-05 -- B1 BASELINE (be-autopilot, escopo restrito a B1). README operacional gerado
  substituindo o stub de scaffold (que usava o termo proibido "tool"). Estado consolidado:
  scaffold hexagonal completo + V1 migration (12 tabelas) + multi-tenancy; logica de negocio
  ausente (services/domain/ports vazios, adapters em `UnsupportedOperationException`). Score 22
  (Inicial). 0/23 issues DONE. Gates B5 diferidos (toolchain Gradle ausente).

# 9. Estado Atual Resumido (para agentes)
STRUCTURAL: OK
FUNCTIONAL: LOW
INTEGRATION: LOW
OBSERVABILITY: PARTIAL
RESILIENCE: LOW
MULTI-EMPRESA: PARTIAL   (RULE-07 nao exercido -- use cases vazios)

# 10. Proxima Atencao Recomendada
PLANNER/IMPLEMENTADOR -> P1 (Scaffold + contratos minimos: superficie REST funcional + ports +
ProblemDetail RFC 7807), depois P2 (golden path do evento-ancora `lead.qualificado` com o motor
de Maturity Score 6D em `domain.service`). Manter assist TechLab AI atras de flag (sync bloqueado)
e degradar para calculo deterministico. Validacao formal (gates) so apos toolchain Gradle disponivel.

END DOCUMENT
