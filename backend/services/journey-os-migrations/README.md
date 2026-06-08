# journey-os-migrations -- Operational README
> Package: `com.journeyos.mig` | Gradle: `:journey-os-migrations` | Modulo: `MIG`

# 0. Service Overview
## Papel do servico
Fonte unica e versionada de **todo** o schema do Journey OS: schema `journeyos_global`
(com extensoes) + um schema por tenant `empresa`. Runner Flyway **centralizado** — nenhum
microservico de negocio possui DDL; todos sobem com `ddl-auto=validate` contra um schema
que o MIG ja preparou.
## Responsabilidades principais
- Aplicar migracoes versionadas schema-aware (global + fan-out por tenant), em ordem, fail-fast.
- Provisionar extensoes no global (`uuid-ossp`, `pgcrypto`, `pg_trgm`, `unaccent`, `vector`/pgvector).
- Garantir re-execucao idempotente (schema-history + lock do Flyway), forward-only (ADR-005).
- Expor readiness (`UP` apenas pos-sucesso) para orquestradores.
## Fora de escopo
- DDL de modulos de negocio (eles apenas validam).
- Gatilho de provisionamento de novo tenant (Gap G2, fora do MVP).
- Rollback destrutivo / `flyway:clean` (forward-only).
## Schemas Postgres consumidos: `journeyos_global` + `emp_*` (um por tenant)

# 1. Arquitetura e Estrutura
## Stack
Java 21 . Spring Boot 3.5.11 . Gradle 8.x (Kotlin DSL) . PostgreSQL 15+ . Flyway (alvo — **ainda nao incluido**).
## Organizacao de pacotes
`com.journeyos.mig` com camadas hexagonais presentes no scaffold:
- `api/exception` (GlobalExceptionHandler)
- `infrastructure/config` (DomainServiceConfig, FeignClientConfig, HibernateMultiTenancyConfig, SecurityConfig, WebMvcConfig)
- `infrastructure/security` (TenantContext*, MultiTenantConnectionProvider, CorrelationIdInterceptor)
- `shared/{audit,error,security}`
- `application` e `domain`: **vazios** (sem use cases / runner ainda).
## Regras arquiteturais aplicadas (RULE-01..09)
ArchUnit presente em `src/test/.../architecture/` (ArchitectureTest, CrossAspectArchTest).
Conformidade real **nao verificada nesta sessao** — toolchain Gradle ausente no ambiente
(gate diferido; ver secao 4).
## Multi-empresa: como o servico propaga EmpresaContext
Scaffold traz `TenantContextHolder` + `TenantContextFilter` + `TenantIdentifierResolver` +
`MultiTenantConnectionProvider` (Hibernate multi-tenancy schema-per-tenant). Para o MIG, a
fonte autoritativa de tenants ainda nao existe (Gap G1) — MVP usara `MIG_TENANT_SCHEMAS`
(config), tratado em MIG-005 (pendente).

# 2. Funcionalidades e Fluxos Principais
## Fluxos criticos
- Migrar global -> fan-out por tenant: **MISSING** (MIG-003/004/005, P2).
- Bootstrap de extensoes: V1 existe como SQL, porem Flyway **desabilitado** (nao executa).
## Eventos emitidos (Artemis): Nao aplicavel (MIG nao emite eventos — P6 fora de escopo).
## Endpoints principais (REST): Nao aplicavel (servico runner; apenas actuator).
## Dependencias inter-servicos (Feign clients usados): Nao aplicavel (sem Feign — P4 fora de escopo).

# 3. Estado Atual da Implementacao
## Implementado (DONE)
- Esqueleto Spring Boot + estrutura hexagonal de pacotes.
- Config multi-tenancy / security / correlation-id (scaffold).
- `V1__create_initial_schema.sql` com as 5 extensoes do global (arquivo presente).
- Testes de arquitetura e IT de carga de contexto (presentes, nao executados aqui).
## Parcial (PARTIAL / STUB)
- Layout de migracao: V1 em path **flat** (`db/migration/`), nao no layout schema-aware
  alvo (`db/migration/global/` + `empresa/`) — P2.
## Nao implementado (MISSING)
- **Dependencia Flyway ausente** no `build.gradle.kts` e `spring.flyway.enabled: false`.
- `FlywayConfig` / `MigrationRunner` (application.service) — P1/P2.
- Enumerator de tenants (`MIG_TENANT_SCHEMAS`) — P2 (MIG-005).
- Idempotencia/concorrencia + validacao de extensoes — P3 (MIG-006, INT-MIG-002).
- Security hardening (papel de migracao, clean off explicito, fail-fast credencial) — P5 (MIG-007).
- Observability (logs runId, actuator `flyway`, readiness pos-sucesso) — P7 (MIG-008).

# 4. Qualidade e Evidencias
## Testes (unit / integration)
Arquivos presentes: ArchitectureTest, CrossAspectArchTest (unit/arch); ApplicationContextLoadsIT,
BaseIntegrationTest (integration, Testcontainers). **Nao executados nesta sessao** — toolchain
Gradle ausente no ambiente (gate diferido; replay via `python scripts/be-gates-replay.py`).
## Cobertura funcional observada
Nenhuma logica de runner a cobrir ainda (application/domain vazios).
## Observabilidade (logs, metricas, MDC)
Pattern de log com MDC `correlationId`/`tenantId`/`userId` configurado; actuator expoe
`health,prometheus` (falta `info,flyway` — P7).

# 5. Gaps Atuais
- G1 — fonte autoritativa de tenants (registry WRKS) inexistente -> MVP via config (MIG-005).
- Flyway nao integrado (dependencia + `enabled:false`) — bloqueia toda a funcao central.
- Scaffold traz dependencias nao usadas pelo MIG (Artemis, Feign/Eureka) — ruido a podar.
- Gates de build/ArchUnit/test nao validados (toolchain Gradle ausente) — diferido.

# 6. Issues Relacionadas ao Servico
- [MIG-001](../../../docs/architecture/backend/issues/MIG-001.md) — scaffold + FlywayConfig (P1)
- [MIG-002](../../../docs/architecture/backend/issues/MIG-002.md) — V1 extensoes (P1)
- [MIG-003](../../../docs/architecture/backend/issues/MIG-003.md) — locations global/empresa (P2)
- [MIG-004](../../../docs/architecture/backend/issues/MIG-004.md) — MigrationRunner (P2)
- [MIG-005](../../../docs/architecture/backend/issues/MIG-005.md) — enumerator de tenants (P2)
- [MIG-006](../../../docs/architecture/backend/issues/MIG-006.md) — idempotencia/concorrencia (P3)
- [MIG-007](../../../docs/architecture/backend/issues/MIG-007.md) — security hardening (P5)
- [MIG-008](../../../docs/architecture/backend/issues/MIG-008.md) — observability (P7)
- [INT-MIG-001](../../../docs/architecture/backend/issues/INT-MIG-001.md) — DataSource + retry (P1)
- [INT-MIG-002](../../../docs/architecture/backend/issues/INT-MIG-002.md) — validacao de extensoes (P3)

# 7. Maturidade do Servico
## Score atual (0-100): 28 — Inicial
## Leitura executiva
O esqueleto e a infraestrutura transversal existem, mas a **razao de ser** do servico — o
runner Flyway centralizado, schema-aware, com fan-out por tenant — ainda nao foi implementada,
e o Flyway sequer esta no classpath/habilitado. Nenhuma das 5 prioridades aplicaveis
(P1/P2/P3/P5/P7) esta concluida. Estado consistente com "recem-scaffoldado".

# 8. Historico de Evolucao (append-only)
- 2026-06-05 — BASELINE (be-autopilot MIG, Validator Modo 1): README operacional regenerado a
  partir do estado real (substitui stub generico). Consolidado: scaffold presente; runner Flyway
  e layout schema-aware MISSING; Flyway ausente do build e desabilitado. Score 28 (Inicial).
  Gates Gradle nao executados (toolchain ausente — diferido).

# 9. Estado Atual Resumido (para agentes)
STRUCTURAL: PARTIAL  (scaffold hexagonal ok; application/domain vazios)
FUNCTIONAL: LOW      (runner Flyway / fan-out MISSING; Flyway nao no classpath)
INTEGRATION: LOW     (DataSource sem retry/fail-fast dedicado; sem validacao de extensoes)
OBSERVABILITY: PARTIAL  (MDC ok; falta actuator flyway + readiness pos-sucesso)
RESILIENCE: LOW      (sem idempotencia/lock explicito alem do default Flyway — que esta off)
MULTI-EMPRESA: PARTIAL  (config multi-tenant presente; enumerator de tenants MISSING; RULE-07 nao validado)

# 10. Proxima Atencao Recomendada
P1 — incluir dependencia Flyway, habilitar `spring.flyway.enabled`, criar `FlywayConfig`
(non-destructive, `clean` off) e DataSource com retry/fail-fast (MIG-001, MIG-002, INT-MIG-001).
Acionar via `/be-planner MIG` seguido de `/be-implement MIG P1` (fora do escopo desta invocacao,
que cobriu apenas o BASELINE).

END DOCUMENT
