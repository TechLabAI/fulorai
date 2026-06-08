# journey-os-api-gateway -- Operational README
> Package: `com.journeyos.gwy` | Gradle: `:journey-os-api-gateway` | Modulo: `GWY`

# 0. Service Overview

## Papel do servico
Edge unico do Journey OS: a unica porta de entrada HTTP publica. Concentra roteamento dinamico
(`lb://` via Eureka), autenticacao de borda (validacao de JWT), resolucao/propagacao de tenant
(`empresa`), rate-limiting distribuido e CORS, mantendo os servicos de negocio focados no dominio.
Servico de **infraestrutura** (gateway reativo, Spring Cloud Gateway / WebFlux).

## Responsabilidades principais
- Roteamento dinamico para os microservicos de negocio via service discovery (`lb://`).
- Validacao de JWT na borda e propagacao de identidade/tenant (`X-Empresa-Id`, `X-Principal-Id`,
  `X-Correlation-Id`) -- anti-spoofing dos headers do cliente.
- Rate-limiting agregado entre replicas (Redis) e CORS centralizado.
- Observabilidade de borda (metricas por rota, health/readiness, tracing W3C).

## Fora de escopo
- Qualquer logica de negocio (nao ha dominio funcional proprio).
- Persistencia/JPA (servico stateless; nao depende de `journey-os-migrations`).
- Emissao de eventos de negocio (Artemis/Kafka) -- nao aplicavel.

## Schemas Postgres consumidos
Nao aplicavel -- o gateway e stateless e nao acessa Postgres (`journeyos_global` / `emp_*` nao
sao consumidos por este servico).

# 1. Arquitetura e Estrutura

## Stack
- Java 21 (toolchain) · Spring Boot 3.5.11 · Gradle 8.x (Kotlin DSL).
- Spring Cloud Gateway (reativo / WebFlux) · Spring Cloud BOM `2025.0.1`.
- Spring Security OAuth2 Resource Server (validacao JWT na borda).
- Netflix Eureka Client (service discovery).
- Actuator + Micrometer Prometheus (observabilidade).
- ArchUnit 1.3.0 (enforcement arquitetural) · Spotless (google-java-format AOSP).

## Organizacao de pacotes
- `com.journeyos.gwy` -- `JourneyOsApiGatewayApplication` (`@SpringBootApplication`).
- `com.journeyos.gwy.infrastructure.config` -- `SecurityConfig` (unica classe de producao alem do main).
- Camadas `api.*`, `application.*`, `domain.*` ainda **nao criadas** (esperadas pelas prioridades P2/P5).

## Regras arquiteturais aplicadas (RULE-01..09)
- ArchUnit cobre RULE-01..06 + extras (WebClient so em `infrastructure`). RULE-03 verificada.
- RULE-02/08 triviais/N-A (servico sem JPA; sem `open-in-view`).
- RULE-09 (pacote base `com.journeyos.gwy`) OK.
- Gates ArchUnit/test **nao executados nesta baseline** -- toolchain Gradle ausente no ambiente
  (gate diferido; ver ledger no implementation-master-plan).

## Multi-empresa: como o servico propaga EmpresaContext
Por design, o gateway deve extrair `empresa` do claim do JWT e propaga-la via `X-Empresa-Id`,
removendo qualquer header de identidade vindo do cliente (anti-spoofing). **Ainda nao implementado**
(filtros de borda e tenant resolver sao P2/P5). RULE-07 (`require()`) nao se aplica diretamente:
nao ha `application.service` que toque dado de empresa -- o gateway apenas propaga contexto.

# 2. Funcionalidades e Fluxos Principais

## Fluxos criticos
- Boot reativo + registro no Eureka (`eureka.client.enabled=false` no profile `default`/CI).
- Cadeia de seguranca reativa: `/actuator/health` e `/actuator/prometheus` publicos; demais
  exchanges exigem JWT (OAuth2 Resource Server). Roteamento downstream e filtros de borda pendentes.

## Eventos emitidos (Artemis)
Nao aplicavel.

## Endpoints principais (REST)
- `GET /actuator/health` (publico) · `GET /actuator/prometheus` (publico).
- `GET /actuator/gateway/routes` -- exposto pelo starter; lista vazia (rotas pendentes, GWY-002).
- Rotas `lb://` para servicos de negocio: **MISSING** (`spring.cloud.gateway.routes: []`).

## Dependencias inter-servicos (Feign clients usados)
Nenhum Feign client (gateway usa roteamento `lb://`, nao Feign). Dependencias externas:
REG/Eureka (discovery), WRKS (JWKS para validacao JWT), Redis/ElastiCache (rate-limit), ALB/Ingress (TLS).

# 3. Estado Atual da Implementacao

## Implementado (DONE)
- Scaffold executavel: `JourneyOsApiGatewayApplication` + build.gradle.kts (Gateway, OAuth2 RS,
  Eureka client, Actuator, Prometheus).
- `SecurityConfig` reativo: allowlist do Actuator (health/prometheus) + `anyExchange().authenticated()`
  + `oauth2ResourceServer.jwt`.
- `application.yml`: porta 8080, nome do app, Eureka, exposicao Actuator (health, prometheus).
- Teste de arquitetura (`ArchitectureTest`, RULE-01..06) + smoke de contexto (`ApplicationContextLoadsIT`).

## Parcial (PARTIAL / STUB)
- **P1 Bootstrap + roteamento** -- app sobe e registra no Eureka; `spring.cloud.gateway.routes` VAZIO
  (GWY-002 e INT-GWY-001 pendentes).
- **P5 Seguranca** -- esqueleto OAuth2 Resource Server presente, porem `issuer-uri` aponta para
  placeholder Keycloak (`KEYCLOAK_ISSUER_URI`), divergente do contrato (JWKS via WRKS). Sem tenant
  resolver, sem allowlist de rotas publicas alem do Actuator, sem CORS.
- **P7 Observabilidade** -- Actuator health + Prometheus expostos; faltam metricas por `routeId`,
  readiness sensivel a Eureka/Redis e tracing W3C (GWY-012).

## Nao implementado (MISSING)
- **P2 Pipeline de borda** -- filtros de correlacao/anti-spoofing, dominio+ports, handler RFC 7807
  (GWY-003, GWY-004, GWY-005, GWY-006).
- **P4 Roteamento downstream + resiliencia** -- timeouts por rota, no-retry em mutantes, 503/504
  (INT-GWY-004).
- **P5** restante -- JWKS via WRKS, auth JWT efetivo, propagacao de tenant, allowlist, CORS
  (GWY-007..010, INT-GWY-002).
- **P6 Rate-limiting distribuido** -- filtro + KeyResolver + adapter Redis (GWY-011, INT-GWY-003).
- Camadas `api`, `application`, `domain` -- ainda inexistentes.

# 4. Qualidade e Evidencias

## Testes (unit / integration)
- Unit: `ArchitectureTest` (ArchUnit RULE-01..06 + extras). Sem testes unitarios de logica (sem logica ainda).
- Integration: `ApplicationContextLoadsIT extends BaseIntegrationTest` (`@SpringBootTest` RANDOM_PORT,
  profile `test`) -- smoke de carga de contexto.
- **Nenhum gate executado nesta baseline** (Gradle indisponivel no ambiente). Status dos testes: NAO VERIFICADO.

## Cobertura funcional observada
Apenas boot/contexto e enforcement arquitetural. Roteamento, seguranca efetiva, rate-limit e
observabilidade de borda ainda sem cobertura.

## Observabilidade (logs, metricas, MDC)
- Micrometer Prometheus presente; tag `application` configurada. Metricas por rota/auth/rate-limit
  ainda nao instrumentadas. `correlationId`/MDC de borda pendente (P2).

# 5. Gaps Atuais
- README anterior era generico/inconsistente (mencionava Artemis/Postgres/Keycloak e "tool") -- corrigido nesta baseline.
- `issuer-uri` Keycloak diverge do contrato (validacao deve usar JWKS do WRKS) -- alinhar em P5/INT-GWY-002.
- Rotas `lb://` vazias: gateway nao encaminha trafego ainda (P1/GWY-002).
- Sem filtros de borda (correlacao, anti-spoofing) -- risco de spoofing de `X-Empresa-Id` ate P2/P5.
- Sem rate-limiting nem CORS centralizado (P6/P5).
- Gates de build/ArchUnit/test nao executaveis no ambiente atual (toolchain Gradle ausente) -- diferidos.

# 6. Issues Relacionadas ao Servico
12 funcionais + 4 de integracao (ver `docs/architecture/backend/issues/issues_map-GWY.md`):
- P1: [GWY-001](../../../docs/architecture/backend/issues/GWY-001.md), [GWY-002](../../../docs/architecture/backend/issues/GWY-002.md), [INT-GWY-001](../../../docs/architecture/backend/issues/INT-GWY-001.md)
- P2: [GWY-003](../../../docs/architecture/backend/issues/GWY-003.md), [GWY-004](../../../docs/architecture/backend/issues/GWY-004.md), [GWY-005](../../../docs/architecture/backend/issues/GWY-005.md), [GWY-006](../../../docs/architecture/backend/issues/GWY-006.md)
- P4: [INT-GWY-004](../../../docs/architecture/backend/issues/INT-GWY-004.md)
- P5: [GWY-007](../../../docs/architecture/backend/issues/GWY-007.md), [GWY-008](../../../docs/architecture/backend/issues/GWY-008.md), [GWY-009](../../../docs/architecture/backend/issues/GWY-009.md), [GWY-010](../../../docs/architecture/backend/issues/GWY-010.md), [INT-GWY-002](../../../docs/architecture/backend/issues/INT-GWY-002.md)
- P6: [GWY-011](../../../docs/architecture/backend/issues/GWY-011.md), [INT-GWY-003](../../../docs/architecture/backend/issues/INT-GWY-003.md)
- P7: [GWY-012](../../../docs/architecture/backend/issues/GWY-012.md)
- Plano: [plan-GWY.md](../../../docs/architecture/backend/plans/plan-GWY.md)

# 7. Maturidade do Servico

## Score atual (0-100): 25 -- Inicial

## Leitura executiva
Scaffold executavel e conforme arquitetura (boot reativo, OAuth2 RS skeleton, Eureka client,
Actuator/Prometheus, ArchUnit verde por inspecao). Porem nenhuma das funcoes-nucleo do gateway
esta operacional: rotas vazias, sem filtros de borda, sem tenant/CORS/rate-limit, sem
observabilidade por rota. Estrutura pronta para iniciar P1; valor de borda ainda nao entregue.

# 8. Historico de Evolucao (append-only)
- 2026-06-05 -- BASELINE (Validator Modo 1): consolidado estado do scaffold; README regenerado a
  partir do template canonico (substituindo README generico inconsistente). Score inicial 25.
  Gates Gradle nao executados (toolchain ausente) -- diferidos.

# 9. Estado Atual Resumido (para agentes)
STRUCTURAL: OK
FUNCTIONAL: LOW
INTEGRATION: LOW
OBSERVABILITY: PARTIAL
RESILIENCE: LOW
MULTI-EMPRESA: LOW   (RULE-07 N/A -- sem application.service; propagacao de tenant pendente em P2/P5)

# 10. Proxima Atencao Recomendada
Iniciar **P1 (Bootstrap + roteamento)**: GWY-001 (consolidar app+Eureka+Actuator) -> INT-GWY-001
(discovery locator) -> GWY-002 (rotas `lb://`), validando `/actuator/gateway/routes`. Em paralelo,
registrar a divergencia do `issuer-uri` (Keycloak vs JWKS WRKS) para corrigir em P5/INT-GWY-002.
Acionar o Planner apenas se a ordem do plano precisar de ajuste; caso contrario seguir para o
Implementador em P1.

END DOCUMENT
