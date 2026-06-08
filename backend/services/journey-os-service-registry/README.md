# journey-os-service-registry -- Operational README
> Package: `com.journeyos.reg` | Gradle: `:journey-os-service-registry` | Modulo: `REG`

# 0. Service Overview

## Papel do servico
Autoridade unica e bem-conhecida de service-discovery (Netflix Eureka Server) para que os
microservicos do backend e a API Gateway se localizem por **nome logico**, nunca por host/porta
hardcoded. Roda standalone single-node na porta `8761`.

## Responsabilidades principais
- Hospedar o registro Eureka (dashboard em `/`).
- Expor contrato de health para orquestracao (`/actuator/health`).
- Nao se registrar em si mesmo (`register-with-eureka: false`, `fetch-registry: false`).
- Configuracao env-driven; tuning de self-preservation por profile.

## Fora de escopo
- Dominio de negocio, persistencia, mensageria e multi-empresa (ADR-001/003/004 — modulo de infra).
- Autenticacao do dashboard (restricao via rede no deploy; auth fora do MVP — risco R2).
- Alta disponibilidade / cluster multi-node (deferido — ADR-005; mitigado por caches client-side, risco R1).

## Schemas Postgres consumidos
Nao aplicavel (modulo de infra — sem `journeyos_global`, sem `emp_*`, sem datasource).

# 1. Arquitetura e Estrutura

## Stack
- Java 21 (toolchain Gradle).
- Spring Boot 3.5.11 + Spring Cloud `2025.0.1` (Netflix Eureka Server starter).
- Spring Boot Actuator + Micrometer Prometheus registry.
- Gradle 8.x (Kotlin DSL); Spotless (google-java-format AOSP).

## Organizacao de pacotes
- Base: `com.journeyos.reg`.
- **Sem** camadas hexagonais (`api/application/domain/infrastructure`) — modulo de infra sem dominio (ADR-001).
- Entry point: `JourneyOsServiceRegistryApplication` (`@EnableEurekaServer` + `@SpringBootApplication`).

## Regras arquiteturais aplicadas (RULE-01..09)
- Apenas **RULE-09** (pacote base `com.journeyos.reg`) e aplicavel.
- RULE-01..06 e RULE-08 sao N/A (sem dominio, JPA, Feign, `@Transactional` ou datasource — ADR-001).
- **Gap:** o `ArchitectureTest` atual herda o template generico (assere RULE-01..06 sobre camadas
  inexistentes) e **nao** assere RULE-09 (base package). Ver Gaps §5 / REG-005.

## Multi-empresa: propagacao de EmpresaContext
Nao aplicavel (ADR-004 — servico de infra nao toca dado de empresa; sem `EmpresaContextHolder`).

# 2. Funcionalidades e Fluxos Principais

## Fluxos criticos
- **Service discovery:** servicos de negocio + gateway registram-se e resolvem peers por nome logico via Eureka.
- **Eviction/self-preservation:** base config com self-preservation desabilitado e eviction a cada 5000ms.

## Eventos emitidos (Artemis)
Nao aplicavel (sem mensageria — ADR-003).

## Endpoints principais (REST)
- `GET /` — dashboard Eureka.
- `GET /actuator/health` — health (UP), `show-details: always`.
- `GET /actuator/prometheus` — metricas Micrometer.
- Eureka REST API (`/eureka/*`) — registro/heartbeat dos clientes.

## Dependencias inter-servicos (Feign clients usados)
Nao aplicavel (REG nao consome outros servicos; os *clientes* e que se registram nele).

# 3. Estado Atual da Implementacao

## Implementado (DONE)
- **REG-001** — Eureka Server bootavel (`@EnableEurekaServer`, app class).
- **REG-002** — `application.yml` base: porta `8761`, self-registration off, fetch-registry off,
  self-preservation off, eviction 5000ms, actuator `health,prometheus` expostos.
- Overlay `application-default.yml` (CI/dev local: `eureka.client.enabled: false`).
- Teste de integracao `ApplicationContextLoadsIT` (context loads) com `BaseIntegrationTest` (profile `test`).

## Parcial (PARTIAL / STUB)
- **REG-003** (P2) — existe overlay `default`; **faltam** `application-local.yml` / `application-prod.yml`
  e hostname anunciado por profile.
- **REG-004** (P3) — actuator health/prometheus OK; **falta** logging estruturado service-tagged
  `[journey-os-service-registry]` (platform-patterns.md §4).

## Nao implementado (MISSING)
- **REG-005** (P4) — guard ArchUnit reduzido (somente RULE-09 base package). Test atual e o template
  generico e nao cobre o criterio do issue.
- Task Gradle `architectureCheck` nao definida no `build.gradle.kts` (ArchUnit roda via `:test`).

# 4. Qualidade e Evidencias

## Testes
- Unit: nenhum teste unitario de negocio (esperado — modulo de infra).
- Architecture: `ArchitectureTest` (ArchTest via `:test`) — conteudo generico, ver §3/§5.
- Integration: `ApplicationContextLoadsIT` (singleton-free, `@SpringBootTest` RANDOM_PORT, profile `test`).
- **Gates nao executados** nesta baseline: toolchain Gradle ausente no ambiente (build/test/archCheck
  diferidos — ver implementation-master-plan ledger).

## Cobertura funcional observada
Boot + context load + exposicao actuator confirmados por inspecao estatica; sem execucao de gate.

## Observabilidade (logs, metricas, MDC)
- Metricas: Micrometer + endpoint Prometheus.
- Health: `/actuator/health` (`show-details: always`).
- Logs estruturados service-tagged: **ausentes** (gap REG-004).
- MDC: nao aplicavel (sem fluxo de empresa/correlation).

# 5. Gaps Atuais
1. `ArchitectureTest` generico nao assere RULE-09 (base package) — viola o escopo reduzido do REG-005.
2. Ausencia de `application-local.yml` / `application-prod.yml` + hostname anunciado (REG-003 P2).
3. Logging estruturado service-tagged ausente (REG-004 P3).
4. Task Gradle `architectureCheck` inexistente (README/CLAUDE referenciam-na).
5. `group = ""` vazio no `build.gradle.kts` (cosmetico).
6. Gates de build/test nao validados (toolchain Gradle ausente — diferido).

# 6. Issues Relacionadas ao Servico
- [REG-001](../../../docs/architecture/backend/issues/REG-001.md) — Scaffold Eureka Server application — **DONE**
- [REG-002](../../../docs/architecture/backend/issues/REG-002.md) — Base application.yml (porta, self-register off, actuator) — **DONE**
- [REG-003](../../../docs/architecture/backend/issues/REG-003.md) — Profile overlays + self-preservation tuning — **PARTIAL**
- [REG-004](../../../docs/architecture/backend/issues/REG-004.md) — Health probe + structured logging — **PARTIAL**
- [REG-005](../../../docs/architecture/backend/issues/REG-005.md) — Reduced ArchUnit check (RULE-09 base package) — **MISSING**

# 7. Maturidade do Servico

## Score atual (0-100): **58 — Parcial**

## Leitura executiva
O nucleo de infra esta entregue e bootavel: Eureka Server na 8761, sem auto-registro, com health e
metricas expostos (P1 100% DONE — o maior valor de um modulo de discovery). Restam P2 (overlays
local/prod + hostname), P3 (logging estruturado) e P4 (guard ArchUnit RULE-09, atualmente
incorreto). Sem dominio/persistencia/mensageria/multi-empresa por design (ADR-001/003/004), logo o
teto de escopo e enxuto e o caminho ate Maduro e curto. Done/Total de issues: **2/5**.

# 8. Historico de Evolucao (append-only)
- 2026-06-05 — BASELINE (be-validator Modo 1, via be-autopilot REG): README operacional gerado a
  partir do estado real. Consolidado: P1 DONE (REG-001/002), P2/P3 PARTIAL (REG-003/004), P4 MISSING
  (REG-005). Score 58 (Parcial). Gates Gradle diferidos (toolchain ausente).

# 9. Estado Atual Resumido (para agentes)
```
STRUCTURAL:    OK       (Eureka Server bootavel; entry point + config base presentes)
FUNCTIONAL:    PARTIAL  (P1 DONE; P2/P3 parciais; P4 missing)
INTEGRATION:   OK       (N/A por design — sem inbound integration; ADR-001)
OBSERVABILITY: PARTIAL  (actuator health/prometheus OK; logging service-tagged ausente)
RESILIENCE:    PARTIAL  (self-preservation off global; falta tuning prod por profile)
MULTI-EMPRESA: OK       (N/A — modulo de infra nao toca dado de empresa; ADR-004, RULE-07 N/A)
```

# 10. Proxima Atencao Recomendada
PLANNER nao necessario (plan-REG.md ja existe e cobre P1-P4). Acao recomendada: **IMPLEMENTADOR**
nas prioridades pendentes, comecando por **P4/REG-005** (corrigir o guard ArchUnit para RULE-09 —
baixo custo, fecha a unica regra arquitetural aplicavel) e seguindo **P2/REG-003** e **P3/REG-004**.
Gates B5 permanecem diferidos ate haver toolchain Gradle (replay: `python scripts/be-gates-replay.py --run --update`).

END DOCUMENT
