# WRKS-SERVICE -- Operational README
> Package: `com.journeyos.wrks` | Gradle: `:wrks-service` | Modulo: `WRKS`

# 0. Service Overview
## Papel do servico
Fundacao de identidade e isolamento do Journey OS: dono dos workspaces (`empresa`), org structure
(business units, teams), usuarios, RBAC canonico (papeis/permissoes) e identidade/sessao (login
Keycloak OIDC, emissao de JWT RS256, AccessDecision). Primeiro servico de dominio a subir;
precondicao de qualquer outra capacidade.
## Responsabilidades principais
Workspace/empresa + provisionamento (saga PROVISIONANDO->ATIVA); org structure; usuarios +
associacoes `usuario_empresa`; RBAC + versao de acesso (`modelo_acesso_versao`); identidade/sessao
(login/troca-empresa/refresh/logout); AccessDecision (permissoes + data-scope) + cache; auditoria
consolidada (`evento_auditoria` + sink Elastic).
## Fora de escopo
MFA, multi-SSO, papeis custom, IP-enforcement, billing (MVP scope de `01-architectural-vision.md`).
## Schemas Postgres consumidos: `journeyos_global` + `emp_*`
IAM canonico (empresa, business_unit, team, usuario, papel, permissao, papel_permissao,
usuario_empresa, usuario_team, modelo_acesso_versao, evento_auditoria) reside em `journeyos_global`.
Acesso a dados por empresa via schema-per-tenant `emp_*` resolvido em runtime por
`TenantContextHolder` + multi-tenancy Hibernate.

# 1. Arquitetura e Estrutura
## Stack
Java 21 . Spring Boot 3.5.x . Gradle (Kotlin DSL) . PostgreSQL 15+ . Keycloak (OIDC, resource
server JWT) . Kafka (AWS MSK) / Artemis (config presente) . Elasticsearch (`audit-events`) .
Eureka client (REG, port 8081). TechLab AI: **nao aplicavel** (WRKS nao usa IA).
## Organizacao de pacotes
Estrutura hexagonal completa e materializada (168 arquivos):
`com.journeyos.wrks.{api.{controller,dto,exception}, application.{service,port.in,port.out},
domain.{model,service}, infrastructure.{clients,config,messaging.{producer,consumer},
persistence.{entity,repository,adapter},security}, shared.{audit,error,messaging,security}}`.
Entrypoint `WrksApplication`.
## Regras arquiteturais aplicadas (RULE-01..09)
- RULE-01/02/04/05/06/03: cobertas por `ArchitectureTest` (ArchUnit) -- DONE.
- RULE-07 (TenantContext.require): mecanismo presente (`TenantContextHolder.require()`), porem
  **nao exercido** nas application services (vazias) -- PARTIAL.
- RULE-08 (`open-in-view=false`): presente em `application.yml` -- DONE.
- RULE-09 (pacote base `com.journeyos.wrks`): respeitado -- DONE.
- Gates `architectureCheck`/`test` NAO executados (toolchain Gradle ausente -- diferido).
## Multi-empresa: como o servico propaga EmpresaContext
`TenantContextFilter` (Order HIGHEST+50) extrai claim `tenant_id` do JWT, valida contra header
`X-Tenant-Id` (403 em mismatch), seta `TenantContextHolder` (ThreadLocal + MDC) e limpa em
`finally`. `AccessContextHolder` carrega permissoes + `DataScope` por request. Falta o uso efetivo
de `require()` dentro das services (ainda nao implementadas).

# 2. Funcionalidades e Fluxos Principais
## Fluxos criticos
Especificados (SPEC-01..10) e com esqueleto presente, porem **nao implementados**: login OIDC ->
JWT escopado por empresa; troca-empresa; refresh rotation; logout (blacklist jti); provisionamento
de empresa (saga + gatilho MIG); AccessDecision + cache; administracao RBAC.
## Eventos emitidos (Artemis/Kafka)
Producers presentes como classes (EmpresaProvisionada, ModeloAcessoAlterado, SessaoEstabelecida,
SessaoEncerrada, UsuarioCriado, UsuarioEmpresaAssociado) + consumer de auditoria. Envelope/destinos
em `shared.messaging`. Logica de publicacao/outbox **nao implementada** (P6).
## Endpoints principais (REST)
Controllers presentes (Empresa, BusinessUnit, Team, Usuario, Papel, Access, Sessao, Auditoria) com
`@RequestMapping` e injecao do use case, **sem metodos/endpoints** ainda. `GlobalExceptionHandler`
(@RestControllerAdvice) emite `ProblemDetail` RFC-7807 via `ProblemDetailFactory` -- DONE.
## Dependencias inter-servicos (Feign clients usados)
`MigrationTriggerClient` (@FeignClient para MIG -- provisionamento de schema) presente porem
**placeholder quebrado** (`name=""`, `url="${}"`, sem metodos) -- STUB. REG (Eureka) para discovery
configurado em `application.yml`.

# 3. Estado Atual da Implementacao
## Implementado (DONE)
- Estrutura hexagonal completa (todas as camadas + `shared`), `WrksApplication`, build (build.gradle.kts,
  settings.gradle.kts, Dockerfile, docker-compose, scripts/init-db.sql).
- `application.yml` conforme: `open-in-view=false`, `ddl-auto=validate`, Flyway off (centralizado),
  Eureka, OAuth2 resource server (issuer Keycloak), Hikari, actuator health/prometheus, log MDC
  (correlationId/tenantId/userId).
- Cross-cutting: `TenantContextHolder`/`TenantContextFilter`, `AccessContextHolder`/`DataScope`,
  `CorrelationIdInterceptor`, `GlobalExceptionHandler` + `ProblemDetailFactory`/`CodedException`,
  `DomainServiceConfig` (6 domain @Bean), `SecurityConfig`/`FeignClientConfig`/`ArtemisConfig`/
  `HibernateMultiTenancyConfig`/`WebMvcConfig`, `AuditAspect`/`DataScopeFilterAspect`.
- ArchUnit `ArchitectureTest` (RULE-01..06 + extra WebClient) + `CrossAspectArchTest`.
- Migration V1 (`db/migration/V1__create_initial_schema.sql`): 11 tabelas IAM completas em
  `journeyos_global` (empresa com CHECK status/slug, business_unit, team, usuario, usuario_team,
  papel, permissao, papel_permissao, usuario_empresa, modelo_acesso_versao com seed, evento_auditoria).
- BDD: 4 features (login-and-session, workspace-provisioning, user-administration, access-decision)
  + wiring Cucumber (`CucumberIT`, `CucumberSpringContext`) + 2 ITs (`ApplicationContextLoadsIT`,
  `BaseIntegrationTest`).
## Parcial (PARTIAL / STUB)
- Domain models (records) e JPA entities: campos esqueleto + `// TODO: complete fields`.
- Repository adapters: implementam as portas mas lancam `UnsupportedOperationException("not implemented")`.
- `MigrationTriggerClient`: @FeignClient placeholder invalido (`name=""`, `url="${}"`).
- Messaging producers/consumer + aspects de auditoria: classes presentes, logica nao implementada.
- BDD step defs: todos `throw new PendingException()`.
## Nao implementado (MISSING)
- Ports `application.port.in` (use cases): interfaces **vazias**, sem assinaturas de metodo.
- Application services: corpos **vazios** (nenhum caso de uso).
- Domain services: POJOs `// TODO` sem invariantes/regras.
- Controllers: nenhum endpoint REST exposto.
- Toda a logica de negocio: identidade/sessao, provisionamento, RBAC/AccessDecision, persistencia
  efetiva, integracoes (Keycloak/MIG), outbox/auditoria, metricas IAM. (P2..P8 nao iniciadas.)

# 4. Qualidade e Evidencias
## Testes (unit / integration)
Sem testes unitarios de dominio/servico (logica ausente). ArchUnit e ITs presentes mas **nao
executados** (toolchain Gradle ausente). BDD em PendingException. Nenhuma evidencia de execucao.
## Cobertura funcional observada
0% funcional -- nenhum caso de uso implementado; endpoints inexistentes; adapters lancam excecao.
## Observabilidade (logs, metricas, MDC)
PARTIAL: padrao de log com MDC (correlationId/tenantId/userId) e `CorrelationIdInterceptor`
presentes; actuator `health`+`prometheus` expostos. Metricas IAM (`journey-os_iam_session_*`) e
readiness por dependencia (P7) MISSING.

# 5. Gaps Atuais
- Funcionalidade zero: use cases (port.in) vazios, services vazias, controllers sem endpoints,
  adapters lancando `UnsupportedOperationException`, domain services TODO.
- `MigrationTriggerClient` invalido (`url="${}"`) -- provavel falha de carga do contexto Feign ate corrigir.
- Migration V1 reside **dentro do servico** (`src/main/resources/db/migration/`) com `flyway.enabled=false`;
  o padrao do projeto e migrations CENTRALIZADAS em `journey-os-migrations` (CLAUDE.md). Reconciliar
  com MIG (coordenar ordem/versionamento e schema-aware layout) -- ver P3.
- RULE-07 (`require()`) nao exercido (services vazias) -- enforcement multi-empresa nao validavel ainda.
- Domain models/entities com campos incompletos vs DDL (ex.: `Empresa` record tem 3 campos vs ~9 no schema).
- Toolchain Gradle ausente -> gates `:wrks-service:test`/`architectureCheck`/`integrationTest`/`*CucumberIT*`
  diferidos ([[gradle-toolchain-absent]] / [[toolchain-preflight-ledger]]).
- Precedencia operacional: MIG (schemas) + REG (Eureka) precisam estar de pe antes do WRKS.

# 6. Issues Relacionadas ao Servico
Funcionais (`docs/architecture/backend/issues/WRKS-NNN.md`):
- P1: WRKS-001, WRKS-002, WRKS-003 | P2: WRKS-004, WRKS-005, WRKS-006 | P3: WRKS-007, WRKS-008
- P4: WRKS-009, WRKS-010 | P5: WRKS-011, WRKS-012, WRKS-013, WRKS-014 | P6: WRKS-015, WRKS-016
- P7: WRKS-017 | P8: WRKS-018
Integracao (`docs/architecture/backend/issues/INT-WRKS-NNN.md`):
- P1: INT-WRKS-001 | P4: INT-WRKS-004 | P5: INT-WRKS-002, INT-WRKS-003 | P6: INT-WRKS-005, INT-WRKS-006
Mapa: `docs/architecture/backend/issues/issues_map-WRKS.md`. Plano: `plans/plan-WRKS.md`. Total: **24 issues**.

# 7. Maturidade do Servico
## Score atual (0-100): 24 -- Inicial
## Leitura executiva
Modulo fundacao totalmente arquitetado (vision 01-06, ADR-001..005, contratos, SPEC-01..10, 24
issues, plano) e com **esqueleto estrutural solido e conforme**: hexagonal completo, ArchUnit
RULE-01..06, `application.yml` conforme (RULE-08), DDL IAM completa, infraestrutura transversal
(tenant/access context, ProblemDetail, MDC) real. Porem a **funcionalidade e nula**: nenhum caso de
uso, endpoint ou regra de dominio implementados; adapters lancam excecao e o Feign client esta
quebrado. 0/8 prioridades funcionalmente fechadas. Proximo passo objetivo: P1 (contratos minimos /
superficie REST) seguido do golden path de identidade (P2). Score reflete estrutura forte + funcao
ausente.

# 8. Historico de Evolucao (append-only)
- 2026-06-05 -- BASELINE (Validator Modo 1) via be-autopilot (escopo restrito a B1 por pedido do
  usuario). README operacional regenerado (substitui stub generico que citava "Journey OS tool",
  "Spring Cloud WRKS" e paths `docs/architecture/tools/`). Estado consolidado: scaffold de 168
  arquivos com estrutura/cross-cutting/DDL/ArchUnit reais, mas business logic ausente (use cases
  vazios, services vazias, controllers sem endpoints, adapters lancando UnsupportedOperationException,
  Feign placeholder invalido, BDD PendingException). Score inicial 24 (Inicial). Gates B5 nao
  executados (toolchain Gradle ausente -- diferido).

# 9. Estado Atual Resumido (para agentes)
STRUCTURAL: PARTIAL   (hexagonal completo + ArchUnit RULE-01..06 + RULE-08/09; controllers sem endpoints, ports.in vazios)
FUNCTIONAL: LOW        (0 casos de uso; adapters lancam excecao)
INTEGRATION: LOW       (Feign placeholder invalido; Keycloak/MIG nao implementados)
OBSERVABILITY: PARTIAL (MDC + actuator health/prometheus; sem metricas IAM/readiness)
RESILIENCE: LOW        (sem circuit breaker/retry/idempotencia implementados)
MULTI-EMPRESA: PARTIAL (RULE-07 mecanismo presente -- TenantContextHolder.require()/TenantContextFilter -- nao exercido nas services)

# 10. Proxima Atencao Recomendada
B2 (DECISAO) sugere **IMPLEMENTADOR -> P1** (Scaffold + contratos minimos): declarar assinaturas
nos `application.port.in`, expor endpoints REST minimos com `ProblemDetail`, e corrigir o
`MigrationTriggerClient` (name/url validos) para o contexto carregar. Sequencia P1:
WRKS-001 -> WRKS-002 -> WRKS-003 (INT-WRKS-001 em paralelo). Pre-requisitos operacionais: MIG
(schemas `journeyos_global`/`emp_*`) e REG (Eureka) de pe. Gates de build/ArchUnit/BDD permanecem
diferidos ate o toolchain Gradle existir (replay via `python scripts/be-gates-replay.py --run --update`).
NAO executado nesta invocacao: o usuario pediu **apenas BASELINE**.

END DOCUMENT
