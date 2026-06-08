# comm-service -- Operational README
> Package: `com.journeyos.comm` | Gradle: `:comm-service` | Modulo: `COMM`

# 0. Service Overview

## Papel do servico
Communication Hub do Journey OS. Responsavel por compor, rotear e despachar mensagens
multi-canal (WhatsApp / Email / Telegram / SMS) para leads, a partir de templates
versionados e regras de roteamento, com ciclo de vida de entrega rastreado por eventos.

## Responsabilidades principais
- CRUD de `TemplateMensagem` (rascunho -> ativo -> arquivado) com variaveis e versionamento.
- Template Studio: composicao/edicao de copy via TechLab AI (`document_composition`) com fallback gracioso.
- CRUD de `RegraRoteamento` + resolucao de canal/template para um lead.
- Disparo assincrono de `Mensagem` (aceite -> render -> enfileiramento) com idempotencia.
- Maquina de estado de entrega (PENDENTE -> ENFILEIRADA -> ENVIADA -> ENTREGUE -> LIDA / FALHADA).
- Configuracao de canal (`ConfigCanal`) com segredo via `credencial_ref`.
- Ingestao de webhooks de provedor (registro de entrega) e emissao de eventos-ancora.

## Fora de escopo
- Provedores de IA diretos (toda IA via TechLab AI HTTP -- nunca chamar Anthropic/OpenAI direto).
- Qualificacao de lead (LEAD), jornada/roteamento de estagio (JRNY), gestao de assets (ASST).
- Migracao de schema (centralizada em `journey-os-migrations`).

## Schemas Postgres consumidos
`journeyos_global` + `emp_*` (schema-per-tenant; resolvido em runtime via `TenantContextHolder`).

# 1. Arquitetura e Estrutura

## Stack
- Java 21 + Spring Boot 3.5.11 (Gradle Kotlin DSL).
- Spring Data JPA (`ddl-auto: validate`, `open-in-view: false`), PostgreSQL.
- ActiveMQ Artemis (messaging), Spring Cloud Eureka + OpenFeign + Resilience4j.
- Actuator + Micrometer/Prometheus. Spotless (google-java-format AOSP).
- Porta local: `8085`.

## Organizacao de pacotes
Estrutura hexagonal canonica completa e presente:
`api/{controller,dto,exception}` . `application/{service,port/in,port/out}` .
`domain/{model,service}` . `infrastructure/{clients,config,messaging,persistence,security}` .
`shared/{audit,error,messaging,security}`.

## Regras arquiteturais aplicadas (RULE-01..09)
- RULE-01/02/03/04/05/06: cobertas por `ArchitectureTest` (ArchUnit, 6 regras ativas + 1 extra WebClient).
- RULE-07 (tenant `.require()`): documentada no teste como verificacao por code-review + IT -- **ainda nao exercida** (services vazios).
- RULE-08 (`open-in-view=false`): presente em `application.yml`.
- RULE-09 (pacote base `com.journeyos.comm`): OK.

## Multi-empresa: propagacao de EmpresaContext
Infra de multi-tenancy schema-per-tenant cabeada: `TenantContextFilter` (le claim JWT `tenant_id`),
`TenantContextHolder`, `MultiTenantConnectionProvider` + `TenantIdentifierResolver` (Hibernate),
`HibernateMultiTenancyConfig`, `MdcContextRestorer` (restaura tenant no consumer), propagacao via
`FeignClientConfig`. Falta: chamadas `.require()` no nivel de `application.service` (nenhuma logica ainda).

# 2. Funcionalidades e Fluxos Principais

## Fluxos criticos
Todos **scaffoldados, nenhum implementado** (corpos de servico vazios, controllers sem endpoints):
- Template CRUD / Template Studio (IA) . Roteamento (regra + resolucao) .
  Disparo assincrono + dispatch worker . Config de canal . Registro de entrega (webhook).

## Eventos emitidos (Artemis)
Producers presentes (classes), `EventDestinations` **sem destinos pinados** (sem `events.arch.json` na geracao):
`MensagemEnfileiradaProducer`, `MensagemEnviadaProducer`, `MensagemEntregueProducer`, `MensagemFalhadaProducer`.
Consumers presentes: `EmpresaProvisionadaConsumer`, `AssetVersaoPublicadaConsumer`,
`LeadSegmentoAlteradoConsumer`, `ModeloAcessoAlteradoConsumer` (+ `ProcessedEvent` para idempotencia).

## Endpoints principais (REST)
Controllers presentes sob `/comm-service/*` (template, roteamento, mensagem, registro-entrega,
config-canal, template-studio) -- **sem metodos/handlers** ainda.

## Dependencias inter-servicos (Feign clients usados)
- `AccessEvaluateClient` (WRKS -- AccessDecision `comm.*`) -- `@FeignClient` com `name/url` vazios.
- `AssetQueryClient` (ASST -- origem de asset para template) -- `@FeignClient` com `name/url` vazios.
- TechLab AI: `ComposicaoIaPort` (`document_composition`) -- porta declarada, sem operacoes.

# 3. Estado Atual da Implementacao

## Implementado (DONE)
- Esqueleto hexagonal completo (api/application/domain/infrastructure/shared).
- Infra de multi-tenancy (filtro JWT, Hibernate multi-tenant, MDC restorer).
- Config base: Artemis, Feign, Security (OAuth2 resource server), WebMvc, DomainServiceConfig.
- ArchUnit (`ArchitectureTest` + `CrossAspectArchTest`).
- Migration DDL gerada localmente (`V1__create_initial_schema.sql`: template_mensagem, mensagem, +3 tabelas).

## Parcial (PARTIAL / STUB)
- Ports out (repos/clients/IA/eventos): interfaces presentes, **todas com `// TODO`** sem operacoes.
- Feign clients: classes presentes, `@FeignClient(name="", url="${}")` nao configurados.
- Producers/consumers: classes presentes, logica de publicacao/consumo nao implementada.
- Observabilidade: padrao MDC + actuator OK; metricas por canal/provedor ausentes.

## Nao implementado (MISSING)
- Toda a logica de negocio: `application.service` com corpos vazios; `domain.model` so com `id/tenantId/createdAt`;
  `domain.service` so com `// TODO`; controllers sem endpoints; DTOs sem campos efetivos.
- `EmpresaContext.require()` no nivel de service (RULE-07 nao exercida).
- Migration nao centralizada em `journey-os-migrations` (`flyway.enabled=false`, comentario "V7+").
- ~101 marcadores `TODO/FIXME` em `src/main/java`.

# 4. Qualidade e Evidencias

## Testes (unit / integration)
- Unit: apenas testes de arquitetura (ArchUnit). Sem testes de logica (nao ha logica).
- Integration: `ApplicationContextLoadsIT` (apenas `contextLoads`) sobre `BaseIntegrationTest` (Testcontainers).
- BDD: 3 features (message-dispatch, channel-routing, template-rendering); **todos os steps lancam `PendingException`**.

## Cobertura funcional observada
Nula em termos de comportamento de negocio. Cobertura estrutural/arquitetural presente.

## Observabilidade (logs, metricas, MDC)
Padrao de log com `correlationId/tenantId/userId` (MDC); `CorrelationIdInterceptor`; actuator expoe `health,prometheus`.

# 5. Gaps Atuais
- G1: Nenhuma logica de negocio (services/domain/ports vazios) -- 0/16 issues funcionais implementadas.
- G2: Migration local nao migrada para `journey-os-migrations` (centralizacao pendente).
- G3: Feign clients sem `name/url`; `EventDestinations` sem destinos pinados.
- G4: RULE-07 (`.require()`) nao exercida em nenhum service.
- G5: BDD steps e DTOs sao stubs; sem testes de comportamento.

# 6. Issues Relacionadas ao Servico
- [COMM-001](../../../docs/architecture/backend/issues/COMM-001.md) -- Bootstrap comm-service (Spring Boot + Eureka + Actuator + ArchUnit)
- [COMM-002](../../../docs/architecture/backend/issues/COMM-002.md) -- Dominio puro (modelos + state machine de entrega + domain services)
- [COMM-003](../../../docs/architecture/backend/issues/COMM-003.md) -- Template CRUD API
- [COMM-004](../../../docs/architecture/backend/issues/COMM-004.md) -- Roteamento: RegraRoteamento CRUD + resolucao de canal/template
- [COMM-005](../../../docs/architecture/backend/issues/COMM-005.md) -- Disparo (aceite assincrono): POST /messages
- [COMM-006](../../../docs/architecture/backend/issues/COMM-006.md) -- Dispatch worker + maquina de entrega + evento-ancora
- [COMM-007](../../../docs/architecture/backend/issues/COMM-007.md) -- Persistencia JPA + adapters (emp_<slug>)
- [COMM-008](../../../docs/architecture/backend/issues/COMM-008.md) -- Migrations Flyway (5 tabelas) via data-model
- [COMM-009](../../../docs/architecture/backend/issues/COMM-009.md) -- Template Studio (TechLab AI document_composition) + fallback
- [COMM-010](../../../docs/architecture/backend/issues/COMM-010.md) -- Channel adapters (CanalEnvioPort) + CanalEnvioRouter
- [COMM-011](../../../docs/architecture/backend/issues/COMM-011.md) -- Config de canal API + segredo via credencial_ref
- [COMM-012](../../../docs/architecture/backend/issues/COMM-012.md) -- Security: JWT + comm.* AccessDecision + tenant guard + webhook signature
- [COMM-013](../../../docs/architecture/backend/issues/COMM-013.md) -- Idempotencia (disparo + Studio + consumers) + concorrencia otimista
- [COMM-014](../../../docs/architecture/backend/issues/COMM-014.md) -- Messaging: producers (outbox) + consumers + ingestao de webhook
- [COMM-015](../../../docs/architecture/backend/issues/COMM-015.md) -- Observability + health (MDC, metricas por canal/provedor)
- [COMM-016](../../../docs/architecture/backend/issues/COMM-016.md) -- BDD end-to-end (Cucumber: 3 features)

Status declarado nas issues: nao identificado (sem campo `status` preenchido nos arquivos).

# 7. Maturidade do Servico

## Score atual: 25 / 100 -- Inicial

## Leitura executiva
Scaffold de altissima qualidade estrutural: arquitetura hexagonal completa, infra de multi-tenancy
real, ArchUnit ativo, contratos/SPECs/ADRs/issues completos (16 issues + 10 SPECs + 5 ADRs). Porem
a camada funcional e inteiramente um esqueleto -- 0/16 issues de negocio implementadas, ~101 TODOs,
services e dominio vazios. Pronto para iniciar o ciclo de implementacao priorizado; nenhum
comportamento de negocio ainda existe ou e testavel.

# 8. Historico de Evolucao (append-only)
- 2026-06-05 -- BASELINE (be-validator Modo 1 via be-autopilot): estado real consolidado; README
  regenerado a partir do stub de scaffold. Score 25/100 (Inicial). Estrutura completa, logica ausente
  (0/16 issues funcionais; ~101 TODOs). Gates de build/teste nao executados (toolchain Gradle ausente no ambiente).

# 9. Estado Atual Resumido (para agentes)
STRUCTURAL: OK
FUNCTIONAL: LOW
INTEGRATION: PARTIAL
OBSERVABILITY: PARTIAL
RESILIENCE: LOW
MULTI-EMPRESA: PARTIAL   (RULE-07 enforce nao exercido -- services vazios; infra de tenant presente)

# 10. Proxima Atencao Recomendada
Entrar no ciclo de implementacao priorizado (Planner -> Implement) comecando pelo nucleo de dominio
e persistencia (COMM-002 dominio + state machine, COMM-007 JPA/adapters, COMM-008 centralizar
migration em journey-os-migrations), antes das camadas de API/disparo/IA. Esta execucao foi
**escopada apenas para BASELINE** -- nenhuma decisao de fluxo, plano ou implementacao foi produzida.

END DOCUMENT
