# Architecture Master Plan — Journey OS Backend

> Rastreia a camada de arquitetura (Layer 1 — Architect) de cada módulo, do vision ao scaffold.
> Atualizado automaticamente pelo `/be-architecture-autopilot` a cada etapa concluída.
> **Não editar à mão durante uma corrida do autopilot** — é um espelho de progresso, nunca a
> fonte da verdade (a verdade são os arquivos em `docs/architecture/...` e `backend/services/...`).
>
> **Ordem de execução recomendada:** infra → fundação de domínio → núcleo → plataforma.
> **Pipeline por módulo:** Vision → Specs → Backlog → Scaffold → Implement (loop).

---

## Visão Geral — Status por Módulo

| # | Prefixo | Serviço | Tipo | Vision | Specs | Backlog | Scaffold | Implement |
|---|---------|---------|------|--------|-------|---------|----------|-----------|
| 1 | **MIG** | `journey-os-migrations` | infra | ✅ | ✅ | ✅ | ✅ | ⬜ |
| 2 | **REG** | `journey-os-service-registry` | infra | ✅ | ✅ | ✅ | ✅ | ⬜ |
| 3 | **GWY** | `journey-os-api-gateway` | infra | ✅ | ✅ | ✅ | ✅ | ⬜ |
| 4 | **WRKS** | `wrks-service` | standard | ✅ | ✅ | ✅ | ✅ | ⬜ |
| 5 | **LEAD** | `lead-service` | standard | ✅ | ✅ | ✅ | ✅ | ⬜ |
| 6 | **ASST** | `asst-service` | standard | ✅ | ✅ | ✅ | ✅ | ⬜ |
| 7 | **JRNY** | `jrny-service` | standard | ✅ | ✅ | ✅ | ✅ | ⬜ |
| 8 | **COMM** | `comm-service` | standard | ✅ | ✅ | ✅ | ✅ | ⬜ |
| 9 | **SALE** | `sale-service` | standard | ✅ | ✅ | ✅ | ✅ | ⬜ |
| 10 | **INTL** | `intl-service` | standard | ✅ | ✅ | ✅ | ✅ | ⬜ |

Legenda: ⬜ pendente · 🔄 em andamento · ✅ concluído · 🚫 bloqueado

---

## Ledger de gates diferidos

> Gates que **não puderam rodar** no ambiente de scaffold por **ausência de toolchain**
> (ver `[[gradle-toolchain-absent]]`). Cada linha traz o **comando de recuperação exato**.
> Quando o toolchain estiver disponível, rode `python scripts/be-gates-replay.py --run --update`
> (usa `scripts/preflight.py` para checar disponibilidade e só executa os gates runnable).
> O comando root do Gradle (`./gradlew compileJava`) cobre **todos** os subprojetos de uma vez.

| Data | Escopo | Gate | Comando de recuperação | Status |
|---|---|---|---|---|
| 2026-06-04 | backend (todos, 10) | compileJava | `./gradlew compileJava` | diferido |
| 2026-06-04 | backend (todos, 10) | architectureCheck | `./gradlew test --tests "*.architecture.*"` | diferido |
| 2026-06-04 | backend standard (7) | bddGate | `./gradlew test --tests "*CucumberIT*"` | diferido |

---

## Artefatos Globais (pré-condição para todos os módulos)

### Setup do projeto

- [ ] `project-context.json` — preenchido e válido
- [ ] `CLAUDE.md` — gerado e revisado
- [ ] `docs/architecture/` — skeleton criado
- [ ] `backend/` — Gradle root + `settings.gradle.kts`
- [ ] `frontend/` — Nx workspace inicializado
- [ ] **P3 — TechLab AI sync** 🚫 bloqueado (aguarda primeiro commit upstream)
  - [ ] `integrations/techlab-ai/` snapshot populado
  - [ ] `docs/architecture/integrations/techlab-ai-integration.md` preenchido

### ADRs globais (já existentes)

- [x] `docs/architecture/backend/adr/ADR-001-hexagonal-architecture.md`
- [x] `docs/architecture/backend/adr/ADR-002-modular-monolith.md`
- [x] `docs/architecture/backend/adr/ADR-003-multi-tenancy.md`

### Standards (já existentes)

- [x] `docs/architecture/backend/standards/hexagonal-patterns.md`
- [x] `docs/architecture/backend/standards/java-conventions.md`
- [x] `docs/architecture/backend/standards/snippets.md`
- [x] `docs/architecture/backend/standards/platform-patterns.md`
- [x] `docs/architecture/backend/standards/testing-conventions.md`
- [x] `docs/architecture/backend/standards/services-catalog.md`
- [x] `docs/architecture/backend/standards/service-spec-authoring.md`
- [x] `docs/architecture/backend/standards/api-mock-convention.md`
- [x] `docs/architecture/backend/standards/ears-notation.md`

### Catálogos transversais (populados por `/be-architect-vision` de cada módulo)

- [ ] `docs/architecture/backend/standards/services-catalog.md` — Event Catalog (seção 6)
- [ ] `docs/architecture/backend/standards/services-catalog.md` — Feign Client Registry (seção 7)
- [ ] `docs/architecture/shared/contratos/event-catalog.md` — catálogo completo de eventos

---

## Módulo 1 — MIG (Migrations)

> Serviço: `journey-os-migrations` · Tipo: infra · Pacote: `com.journeyos.mig`
> Comando: `/be-architect-vision MIG` → specs → backlog → scaffold

### Etapa A1 — Vision (`/be-architect-vision MIG`)

- [x] `docs/architecture/backend/services/journey-os-migrations/_brief.md`
- [x] `docs/architecture/backend/services/journey-os-migrations/01-architectural-vision.md`
- [x] `docs/architecture/backend/services/journey-os-migrations/02-architecture-blueprint.md`
- [x] `docs/architecture/backend/services/journey-os-migrations/03-initial-domain-framing.md`
- [x] `docs/architecture/backend/services/journey-os-migrations/04-backend-architecture-direction.md`
- [x] `docs/architecture/backend/services/journey-os-migrations/05-persistence-model.md`
- [x] `docs/architecture/backend/services/journey-os-migrations/06-risks-gaps-assumptions.md`
- [x] `docs/architecture/backend/services/journey-os-migrations/adr/README.md`
- [x] `docs/architecture/backend/services/journey-os-migrations/adr/ADR-001-hexagonal-architecture.md`
- [x] `docs/architecture/backend/services/journey-os-migrations/adr/ADR-002-migration-strategy.md`
- [x] `docs/architecture/backend/services/journey-os-migrations/adr/ADR-003-schema-partitioning.md`
- [x] `docs/architecture/backend/services/journey-os-migrations/adr/ADR-004-multitenant-strategy.md`
- [x] `docs/architecture/backend/services/journey-os-migrations/adr/ADR-005-flyway-baseline.md`

### Etapa A2 — Specs (`/be-architect-specs MIG`)

- [x] `docs/architecture/backend/services/journey-os-migrations/journey-os-migrations-spec.md`
- [x] `docs/architecture/backend/services/journey-os-migrations/setup-local.md`
- [x] `docs/architecture/backend/services/journey-os-migrations/contracts/api-contract.md` _(added: A4-backlog prereq; "no business API")_
- [x] `docs/architecture/backend/services/journey-os-migrations/contracts/data-model.md`
- [x] `docs/architecture/backend/services/journey-os-migrations/contracts/event-contracts.md`
- [x] `docs/architecture/backend/services/journey-os-migrations/contracts/hub-integration.md`
- [x] `docs/architecture/backend/services/journey-os-migrations/contracts/integration-contracts.md`
- [x] `docs/architecture/backend/services/journey-os-migrations/events/event-catalog.md`
- [x] `docs/architecture/backend/services/journey-os-migrations/spec/backend/SPEC-01-api-surface.md`
- [x] `docs/architecture/backend/services/journey-os-migrations/spec/backend/SPEC-04-data-model-migrations.md`
- [x] `docs/architecture/backend/services/journey-os-migrations/spec/backend/SPEC-05-idempotency-concurrency.md`
- [x] `docs/architecture/backend/services/journey-os-migrations/spec/backend/SPEC-06-security.md`
- [x] `docs/architecture/backend/services/journey-os-migrations/spec/backend/SPEC-07-observability-health.md`
- [x] `docs/architecture/backend/services/journey-os-migrations/diagrams/c4-context.puml`
- [x] `docs/architecture/backend/services/journey-os-migrations/diagrams/c4-container.puml`
- [x] `docs/architecture/backend/services/journey-os-migrations/diagrams/c4-component.puml`

### Etapa A3 — Backlog (`/be-architect-backlog MIG`)

- [x] `docs/architecture/backend/issues/MIG-001.md` .. `MIG-008.md` (8 issues funcionais)
- [x] `docs/architecture/backend/issues/INT-MIG-001.md` .. `INT-MIG-002.md` (2 issues integração)
- [x] `docs/architecture/backend/issues/issues_map-MIG.md`
- [x] `docs/architecture/backend/services/journey-os-migrations/generator-config.yml` _(type=standard, domínio vazio — ver header)_
- [x] `docs/architecture/backend/plans/plan-MIG.md`

### Etapa A4 — Scaffold (`/be-architect-scaffold MIG`)

- [x] `backend/services/journey-os-migrations/` — projeto Gradle gerado (34 base + V1 migration); registrado em `settings.gradle.kts`
- [x] `backend/services/journey-os-migrations/src/main/resources/db/migration/V1__create_initial_schema.sql` — 5 extensões (uuid-ossp, pgcrypto, pg_trgm, unaccent, vector)
- [ ] `db/migration/global/` + `db/migration/empresa/` — **partição schema-aware adiada ao implement (MIG-003)**: o gerador `standard` emite V1 em `db/migration/` plano; reorganizar em P2.
- [ ] **Gate pós-scaffold (compileJava + architectureCheck) NÃO executado** — sem toolchain Gradle no ambiente (sem wrapper, sem gradle no PATH). Rodar: `./gradlew :journey-os-migrations:spotlessApply compileJava` e `:test --tests "*.architecture.*"` quando o wrapper existir.

### Etapa B — Implement (`/be-autopilot MIG --implement`)

- [ ] Baseline (be-validator BASELINE)
- [ ] plan-MIG.md com prioridades definidas
- [ ] P1 implementado e validado
- [ ] Score maturidade ≥ 80

---

## Módulo 2 — REG (Service Registry)

> Serviço: `journey-os-service-registry` · Tipo: infra · Pacote: `com.journeyos.reg`

### Etapa A1 — Vision (`/be-architect-vision REG`)

- [x] `docs/architecture/backend/services/journey-os-service-registry/_brief.md`
- [x] `docs/architecture/backend/services/journey-os-service-registry/01-architectural-vision.md`
- [x] `docs/architecture/backend/services/journey-os-service-registry/02-architecture-blueprint.md`
- [x] `docs/architecture/backend/services/journey-os-service-registry/03-initial-domain-framing.md`
- [x] `docs/architecture/backend/services/journey-os-service-registry/04-backend-architecture-direction.md`
- [x] `docs/architecture/backend/services/journey-os-service-registry/05-persistence-model.md`
- [x] `docs/architecture/backend/services/journey-os-service-registry/06-risks-gaps-assumptions.md`
- [x] `docs/architecture/backend/services/journey-os-service-registry/adr/README.md`
- [x] `docs/architecture/backend/services/journey-os-service-registry/adr/ADR-001-hexagonal-architecture.md`
- [x] `docs/architecture/backend/services/journey-os-service-registry/adr/ADR-002-eureka-vs-consul.md`
- [x] `docs/architecture/backend/services/journey-os-service-registry/adr/ADR-003-messaging-strategy.md`
- [x] `docs/architecture/backend/services/journey-os-service-registry/adr/ADR-004-multitenant-strategy.md`
- [x] `docs/architecture/backend/services/journey-os-service-registry/adr/ADR-005-health-check-strategy.md`

### Etapa A2 — Specs (`/be-architect-specs REG`)

- [x] `docs/architecture/backend/services/journey-os-service-registry/journey-os-service-registry-spec.md`
- [x] `docs/architecture/backend/services/journey-os-service-registry/setup-local.md`
- [x] `docs/architecture/backend/services/journey-os-service-registry/contracts/api-contract.md`
- [x] `docs/architecture/backend/services/journey-os-service-registry/contracts/integration-contracts.md`
- [x] `docs/architecture/backend/services/journey-os-service-registry/events/event-catalog.md`
- [x] `docs/architecture/backend/services/journey-os-service-registry/spec/backend/SPEC-01-api-surface.md`
- [x] `docs/architecture/backend/services/journey-os-service-registry/spec/backend/SPEC-06-security.md`
- [x] `docs/architecture/backend/services/journey-os-service-registry/spec/backend/SPEC-07-observability-health.md`
- [x] `docs/architecture/backend/services/journey-os-service-registry/diagrams/c4-context.puml`
- [x] `docs/architecture/backend/services/journey-os-service-registry/diagrams/c4-container.puml`
- [x] `docs/architecture/backend/services/journey-os-service-registry/diagrams/c4-component.puml`

### Etapa A3 — Backlog (`/be-architect-backlog REG`)

- [x] `docs/architecture/backend/issues/REG-001.md` .. `REG-NNN.md`
- [x] `docs/architecture/backend/issues/issues_map-REG.md`
- [x] `docs/architecture/backend/services/journey-os-service-registry/generator-config.yml`
- [x] `docs/architecture/backend/plans/plan-REG.md`

### Etapa A4 — Scaffold (`/be-architect-scaffold REG`)

- [x] `backend/services/journey-os-service-registry/` — projeto Gradle gerado (type=registry)

### Etapa B — Implement (`/be-autopilot REG --implement`)

- [ ] Baseline · plan-REG.md · P1 implementado · Score ≥ 80

---

## Módulo 3 — GWY (API Gateway)

> Serviço: `journey-os-api-gateway` · Tipo: infra · Pacote: `com.journeyos.gwy`

### Etapa A1 — Vision (`/be-architect-vision GWY`)

- [x] `docs/architecture/backend/services/journey-os-api-gateway/_brief.md`
- [x] `docs/architecture/backend/services/journey-os-api-gateway/01-architectural-vision.md`
- [x] `docs/architecture/backend/services/journey-os-api-gateway/02-architecture-blueprint.md`
- [x] `docs/architecture/backend/services/journey-os-api-gateway/03-initial-domain-framing.md`
- [x] `docs/architecture/backend/services/journey-os-api-gateway/04-backend-architecture-direction.md`
- [x] `docs/architecture/backend/services/journey-os-api-gateway/05-persistence-model.md`
- [x] `docs/architecture/backend/services/journey-os-api-gateway/06-risks-gaps-assumptions.md`
- [x] `docs/architecture/backend/services/journey-os-api-gateway/adr/README.md`
- [x] `docs/architecture/backend/services/journey-os-api-gateway/adr/ADR-001-hexagonal-architecture.md`
- [x] `docs/architecture/backend/services/journey-os-api-gateway/adr/ADR-002-gateway-routing-strategy.md`
- [x] `docs/architecture/backend/services/journey-os-api-gateway/adr/ADR-003-auth-filter.md`
- [x] `docs/architecture/backend/services/journey-os-api-gateway/adr/ADR-004-multitenant-strategy.md`
- [x] `docs/architecture/backend/services/journey-os-api-gateway/adr/ADR-005-rate-limiting.md`

### Etapa A2 — Specs (`/be-architect-specs GWY`)

- [x] `docs/architecture/backend/services/journey-os-api-gateway/journey-os-api-gateway-spec.md`
- [x] `docs/architecture/backend/services/journey-os-api-gateway/setup-local.md`
- [x] `docs/architecture/backend/services/journey-os-api-gateway/contracts/api-contract.md`
- [x] `docs/architecture/backend/services/journey-os-api-gateway/contracts/integration-contracts.md`
- [x] `docs/architecture/backend/services/journey-os-api-gateway/events/event-catalog.md`
- [x] `docs/architecture/backend/services/journey-os-api-gateway/spec/backend/SPEC-01-api-surface.md`
- [x] `docs/architecture/backend/services/journey-os-api-gateway/spec/backend/SPEC-05-idempotency-concurrency.md`
- [x] `docs/architecture/backend/services/journey-os-api-gateway/spec/backend/SPEC-06-security.md`
- [x] `docs/architecture/backend/services/journey-os-api-gateway/spec/backend/SPEC-07-observability-health.md`
- [x] `docs/architecture/backend/services/journey-os-api-gateway/diagrams/c4-context.puml`
- [x] `docs/architecture/backend/services/journey-os-api-gateway/diagrams/c4-container.puml`
- [x] `docs/architecture/backend/services/journey-os-api-gateway/diagrams/c4-component.puml`

### Etapa A3 — Backlog (`/be-architect-backlog GWY`)

- [x] `docs/architecture/backend/issues/GWY-001.md` .. `GWY-012.md` (12 funcionais) + `INT-GWY-001..004.md` (4 integração)
- [x] `docs/architecture/backend/issues/issues_map-GWY.md`
- [x] `docs/architecture/backend/services/journey-os-api-gateway/generator-config.yml` (type=gateway, port=8080)
- [x] `docs/architecture/backend/plans/plan-GWY.md`

### Etapa A4 — Scaffold (`/be-architect-scaffold GWY`)

- [x] `backend/services/journey-os-api-gateway/` — projeto Gradle gerado (type=gateway, pacote `com.journeyos.gwy`, 13 arquivos); registrado em `backend/settings.gradle.kts`. Verificação compileJava/architectureCheck **diferida** (sem Gradle/wrapper no ambiente).

### Etapa B — Implement (`/be-autopilot GWY --implement`)

- [ ] Baseline · plan-GWY.md · P1 implementado · Score ≥ 80

---

## Módulo 4 — WRKS (Workspace & Identity)

> Serviço: `wrks-service` · Tipo: standard · Pacote: `com.journeyos.wrks`
> **Fundação de domínio** — todos os módulos de negócio dependem deste.

### Etapa A1 — Vision (`/be-architect-vision WRKS`)

- [ ] `docs/architecture/backend/services/wrks-service/_brief.md`
- [ ] `docs/architecture/backend/services/wrks-service/01-architectural-vision.md`
- [ ] `docs/architecture/backend/services/wrks-service/02-architecture-blueprint.md`
- [ ] `docs/architecture/backend/services/wrks-service/03-initial-domain-framing.md`
- [ ] `docs/architecture/backend/services/wrks-service/04-backend-architecture-direction.md`
- [ ] `docs/architecture/backend/services/wrks-service/05-persistence-model.md`
- [ ] `docs/architecture/backend/services/wrks-service/06-risks-gaps-assumptions.md`
- [ ] `docs/architecture/backend/services/wrks-service/adr/README.md`
- [ ] `docs/architecture/backend/services/wrks-service/adr/ADR-001-hexagonal-architecture.md`
- [ ] `docs/architecture/backend/services/wrks-service/adr/ADR-002-single-service-boundary.md`
- [ ] `docs/architecture/backend/services/wrks-service/adr/ADR-003-messaging-strategy.md`
- [ ] `docs/architecture/backend/services/wrks-service/adr/ADR-004-multitenant-strategy.md`
- [ ] `docs/architecture/backend/services/wrks-service/adr/ADR-005-rbac-model.md`

### Etapa A2 — Specs (`/be-architect-specs WRKS`)

- [ ] `docs/architecture/backend/services/wrks-service/wrks-service-spec.md`
- [ ] `docs/architecture/backend/services/wrks-service/setup-local.md`
- [ ] `docs/architecture/backend/services/wrks-service/contracts/api-contract.md`
- [ ] `docs/architecture/backend/services/wrks-service/contracts/data-model.md`
- [ ] `docs/architecture/backend/services/wrks-service/contracts/event-contracts.md`
- [ ] `docs/architecture/backend/services/wrks-service/contracts/hub-integration.md`
- [ ] `docs/architecture/backend/services/wrks-service/contracts/integration-contracts.md`
- [ ] `docs/architecture/backend/services/wrks-service/tests/cucumber/workspace-management.feature`
- [ ] `docs/architecture/backend/services/wrks-service/tests/cucumber/user-provisioning.feature`
- [ ] `docs/architecture/backend/services/wrks-service/tests/cucumber/rbac-enforcement.feature`
- [ ] `docs/architecture/backend/services/wrks-service/events/event-catalog.md`
- [ ] `docs/architecture/backend/services/wrks-service/spec/backend/SPEC-01-api-surface.md`
- [ ] `docs/architecture/backend/services/wrks-service/spec/backend/SPEC-02-workspace-lifecycle.md`
- [ ] `docs/architecture/backend/services/wrks-service/spec/backend/SPEC-03-user-identity.md`
- [ ] `docs/architecture/backend/services/wrks-service/spec/backend/SPEC-04-data-model-migrations.md`
- [ ] `docs/architecture/backend/services/wrks-service/spec/backend/SPEC-05-idempotency-concurrency.md`
- [ ] `docs/architecture/backend/services/wrks-service/spec/backend/SPEC-06-security.md`
- [ ] `docs/architecture/backend/services/wrks-service/spec/backend/SPEC-07-observability-health.md`
- [ ] `docs/architecture/backend/services/wrks-service/spec/backend/SPEC-08-bdd-test-scenarios.md`
- [ ] `docs/architecture/backend/services/wrks-service/spec/backend/SPEC-09-messaging-architecture.md`
- [ ] `docs/architecture/backend/services/wrks-service/spec/backend/SPEC-10-integrations.md`
- [ ] `docs/architecture/backend/services/wrks-service/diagrams/c4-context.puml`
- [ ] `docs/architecture/backend/services/wrks-service/diagrams/c4-container.puml`
- [ ] `docs/architecture/backend/services/wrks-service/diagrams/c4-component.puml`

### Etapa A3 — Backlog (`/be-architect-backlog WRKS`)

- [ ] `docs/architecture/backend/issues/WRKS-001.md` .. `WRKS-NNN.md` (15–25 issues funcionais)
- [ ] `docs/architecture/backend/issues/INT-WRKS-001.md` .. `INT-WRKS-MMM.md` (5–10 issues integração)
- [ ] `docs/architecture/backend/issues/issues_map-WRKS.md`
- [ ] `docs/architecture/backend/services/wrks-service/generator-config.yml`
- [ ] `docs/architecture/backend/plans/plan-WRKS.md`

### Etapa A4 — Scaffold (`/be-architect-scaffold WRKS`)

- [ ] `backend/services/wrks-service/` — skeleton hexagonal completo (16 subpacotes)
- [ ] `backend/services/wrks-service/build.gradle.kts`
- [ ] `backend/services/wrks-service/src/main/java/com/journeyos/wrks/` — estrutura hexagonal
- [ ] `backend/services/wrks-service/src/main/resources/application.yml` (+ perfis)
- [ ] `backend/services/wrks-service/src/test/` — BaseIntegrationTest singleton pattern
- [ ] `backend/services/wrks-service/src/test/java/.../ArchitectureTest.java` — ArchUnit RULE-01..08
- [ ] DDL executado por be-migration-generator.py e be-entity-generator.py
- [ ] Step stubs Cucumber gerados por be-bdd-generator.py

### Etapa B — Implement (`/be-autopilot WRKS --implement`)

- [ ] Baseline — score calculado
- [ ] plan-WRKS.md com P1..P9 definidas
- [ ] P1 — Scaffold + API CRUD agregado principal ✅/⬜
- [ ] P2 — Orquestração do domínio (golden path WorkspaceCreated)
- [ ] P3 — Persistência + migrations
- [ ] P4 — Integrações externas (Feign clients)
- [ ] P5 — Security + multi-tenancy (OAuth2, TenantContextHolder)
- [ ] P6 — Messaging (producers + consumers)
- [ ] P7 — Observability + health
- [ ] P8 — BDD end-to-end (Cucumber completo)
- [ ] P9 — Hardening (SLAs, retries, circuit breaker)
- [ ] `./gradlew :services:wrks-service:architectureCheck` — PASS
- [ ] Score maturidade ≥ 80

---

## Módulo 5 — LEAD (Lead Intelligence & Qualification)

> Serviço: `lead-service` · Tipo: standard · Pacote: `com.journeyos.lead`
> **Dependência:** WRKS (multi-tenancy, usuários)

### Etapa A1 — Vision (`/be-architect-vision LEAD`)

- [ ] `docs/architecture/backend/services/lead-service/_brief.md`
- [ ] `docs/architecture/backend/services/lead-service/01-architectural-vision.md`
- [ ] `docs/architecture/backend/services/lead-service/02-architecture-blueprint.md`
- [ ] `docs/architecture/backend/services/lead-service/03-initial-domain-framing.md`
- [ ] `docs/architecture/backend/services/lead-service/04-backend-architecture-direction.md`
- [ ] `docs/architecture/backend/services/lead-service/05-persistence-model.md`
- [ ] `docs/architecture/backend/services/lead-service/06-risks-gaps-assumptions.md`
- [ ] `docs/architecture/backend/services/lead-service/adr/README.md`
- [ ] `docs/architecture/backend/services/lead-service/adr/ADR-001-hexagonal-architecture.md`
- [ ] `docs/architecture/backend/services/lead-service/adr/ADR-002-single-service-boundary.md`
- [ ] `docs/architecture/backend/services/lead-service/adr/ADR-003-messaging-strategy.md`
- [ ] `docs/architecture/backend/services/lead-service/adr/ADR-004-multitenant-strategy.md`
- [ ] `docs/architecture/backend/services/lead-service/adr/ADR-005-maturity-score-model.md`

### Etapa A2 — Specs (`/be-architect-specs LEAD`)

- [ ] `docs/architecture/backend/services/lead-service/lead-service-spec.md`
- [ ] `docs/architecture/backend/services/lead-service/setup-local.md`
- [ ] `docs/architecture/backend/services/lead-service/contracts/api-contract.md`
- [ ] `docs/architecture/backend/services/lead-service/contracts/data-model.md`
- [ ] `docs/architecture/backend/services/lead-service/contracts/event-contracts.md`
- [ ] `docs/architecture/backend/services/lead-service/contracts/hub-integration.md`
- [ ] `docs/architecture/backend/services/lead-service/contracts/integration-contracts.md`
- [ ] `docs/architecture/backend/services/lead-service/contracts/techlab-ai-integration.md` _(TechLab AI: qualification)_
- [ ] `docs/architecture/backend/services/lead-service/tests/cucumber/lead-capture.feature`
- [ ] `docs/architecture/backend/services/lead-service/tests/cucumber/lead-qualification.feature`
- [ ] `docs/architecture/backend/services/lead-service/tests/cucumber/maturity-score.feature`
- [ ] `docs/architecture/backend/services/lead-service/events/event-catalog.md`
- [ ] `docs/architecture/backend/services/lead-service/spec/backend/SPEC-01-api-surface.md`
- [ ] `docs/architecture/backend/services/lead-service/spec/backend/SPEC-02-lead-qualification-orchestration.md`
- [ ] `docs/architecture/backend/services/lead-service/spec/backend/SPEC-03-maturity-score-6d.md`
- [ ] `docs/architecture/backend/services/lead-service/spec/backend/SPEC-04-data-model-migrations.md`
- [ ] `docs/architecture/backend/services/lead-service/spec/backend/SPEC-05-idempotency-concurrency.md`
- [ ] `docs/architecture/backend/services/lead-service/spec/backend/SPEC-06-security.md`
- [ ] `docs/architecture/backend/services/lead-service/spec/backend/SPEC-07-observability-health.md`
- [ ] `docs/architecture/backend/services/lead-service/spec/backend/SPEC-08-bdd-test-scenarios.md`
- [ ] `docs/architecture/backend/services/lead-service/spec/backend/SPEC-09-messaging-architecture.md`
- [ ] `docs/architecture/backend/services/lead-service/spec/backend/SPEC-10-integrations.md`
- [ ] `docs/architecture/backend/services/lead-service/diagrams/c4-context.puml`
- [ ] `docs/architecture/backend/services/lead-service/diagrams/c4-container.puml`
- [ ] `docs/architecture/backend/services/lead-service/diagrams/c4-component.puml`

### Etapa A3 — Backlog (`/be-architect-backlog LEAD`)

- [ ] `docs/architecture/backend/issues/LEAD-001.md` .. `LEAD-NNN.md`
- [ ] `docs/architecture/backend/issues/INT-LEAD-001.md` .. `INT-LEAD-MMM.md`
- [ ] `docs/architecture/backend/issues/issues_map-LEAD.md`
- [ ] `docs/architecture/backend/services/lead-service/generator-config.yml`
- [ ] `docs/architecture/backend/plans/plan-LEAD.md`

### Etapa A4 — Scaffold (`/be-architect-scaffold LEAD`)

- [ ] `backend/services/lead-service/` — skeleton hexagonal completo

### Etapa B — Implement (`/be-autopilot LEAD --implement`)

- [ ] Baseline · plan-LEAD.md · P1..P9 · ArchUnit PASS · Score ≥ 80

---

## Módulo 6 — ASST (Asset Hub)

> Serviço: `asst-service` · Tipo: standard · Pacote: `com.journeyos.asst`
> **Dependência:** WRKS

### Etapa A1 — Vision (`/be-architect-vision ASST`)

- [ ] `docs/architecture/backend/services/asst-service/_brief.md`
- [ ] `docs/architecture/backend/services/asst-service/01-architectural-vision.md`
- [ ] `docs/architecture/backend/services/asst-service/02-architecture-blueprint.md`
- [ ] `docs/architecture/backend/services/asst-service/03-initial-domain-framing.md`
- [ ] `docs/architecture/backend/services/asst-service/04-backend-architecture-direction.md`
- [ ] `docs/architecture/backend/services/asst-service/05-persistence-model.md`
- [ ] `docs/architecture/backend/services/asst-service/06-risks-gaps-assumptions.md`
- [ ] `docs/architecture/backend/services/asst-service/adr/README.md`
- [ ] `docs/architecture/backend/services/asst-service/adr/ADR-001-hexagonal-architecture.md`
- [ ] `docs/architecture/backend/services/asst-service/adr/ADR-002-single-service-boundary.md`
- [ ] `docs/architecture/backend/services/asst-service/adr/ADR-003-messaging-strategy.md`
- [ ] `docs/architecture/backend/services/asst-service/adr/ADR-004-multitenant-strategy.md`
- [ ] `docs/architecture/backend/services/asst-service/adr/ADR-005-asset-versioning.md`

### Etapa A2 — Specs (`/be-architect-specs ASST`)

- [ ] `docs/architecture/backend/services/asst-service/asst-service-spec.md`
- [ ] `docs/architecture/backend/services/asst-service/setup-local.md`
- [ ] `docs/architecture/backend/services/asst-service/contracts/api-contract.md`
- [ ] `docs/architecture/backend/services/asst-service/contracts/data-model.md`
- [ ] `docs/architecture/backend/services/asst-service/contracts/event-contracts.md`
- [ ] `docs/architecture/backend/services/asst-service/contracts/hub-integration.md`
- [ ] `docs/architecture/backend/services/asst-service/contracts/integration-contracts.md`
- [ ] `docs/architecture/backend/services/asst-service/contracts/techlab-ai-integration.md` _(TechLab AI: document_composition)_
- [ ] `docs/architecture/backend/services/asst-service/tests/cucumber/asset-creation.feature`
- [ ] `docs/architecture/backend/services/asst-service/tests/cucumber/asset-versioning.feature`
- [ ] `docs/architecture/backend/services/asst-service/tests/cucumber/approval-workflow.feature`
- [ ] `docs/architecture/backend/services/asst-service/events/event-catalog.md`
- [ ] `docs/architecture/backend/services/asst-service/spec/backend/SPEC-01..10-*.md` (10 SPECs)
- [ ] `docs/architecture/backend/services/asst-service/diagrams/c4-{context,container,component}.puml`

### Etapa A3 — Backlog (`/be-architect-backlog ASST`)

- [ ] Issues `ASST-001..NNN` + `INT-ASST-001..MMM` + `issues_map-ASST.md`
- [ ] `docs/architecture/backend/services/asst-service/generator-config.yml`
- [ ] `docs/architecture/backend/plans/plan-ASST.md`

### Etapa A4 — Scaffold (`/be-architect-scaffold ASST`)

- [ ] `backend/services/asst-service/` — skeleton hexagonal completo

### Etapa B — Implement (`/be-autopilot ASST --implement`)

- [ ] Baseline · plan-ASST.md · P1..P9 · ArchUnit PASS · Score ≥ 80

---

## Módulo 7 — JRNY (Journey & Routing)

> Serviço: `jrny-service` · Tipo: standard · Pacote: `com.journeyos.jrny`
> **Dependências:** WRKS, LEAD, ASST

### Etapa A1 — Vision (`/be-architect-vision JRNY`)

- [x] `docs/architecture/backend/services/jrny-service/_brief.md`
- [x] `docs/architecture/backend/services/jrny-service/01-architectural-vision.md`
- [x] `docs/architecture/backend/services/jrny-service/02-architecture-blueprint.md`
- [x] `docs/architecture/backend/services/jrny-service/03-initial-domain-framing.md`
- [x] `docs/architecture/backend/services/jrny-service/04-backend-architecture-direction.md`
- [x] `docs/architecture/backend/services/jrny-service/05-persistence-model.md`
- [x] `docs/architecture/backend/services/jrny-service/06-risks-gaps-assumptions.md`
- [x] `docs/architecture/backend/services/jrny-service/adr/README.md`
- [x] `docs/architecture/backend/services/jrny-service/adr/ADR-001-hexagonal-architecture.md`
- [x] `docs/architecture/backend/services/jrny-service/adr/ADR-002-single-service-boundary.md`
- [x] `docs/architecture/backend/services/jrny-service/adr/ADR-003-messaging-strategy.md`
- [x] `docs/architecture/backend/services/jrny-service/adr/ADR-004-multitenant-strategy.md`
- [x] `docs/architecture/backend/services/jrny-service/adr/ADR-005-routing-engine-model.md`

### Etapa A2 — Specs (`/be-architect-specs JRNY`)

- [x] `docs/architecture/backend/services/jrny-service/jrny-service-spec.md`
- [x] `docs/architecture/backend/services/jrny-service/setup-local.md` _(port 8084)_
- [x] `docs/architecture/backend/services/jrny-service/contracts/api-contract.md`
- [x] `docs/architecture/backend/services/jrny-service/contracts/data-model.md` _(5 sql blocks, schema=empresa)_
- [x] `docs/architecture/backend/services/jrny-service/contracts/event-contracts.md`
- [x] `docs/architecture/backend/services/jrny-service/contracts/hub-integration.md`
- [x] `docs/architecture/backend/services/jrny-service/contracts/integration-contracts.md`
- [x] `docs/architecture/backend/services/jrny-service/contracts/techlab-ai-integration.md` _(TechLab AI: orchestration)_
- [x] `docs/architecture/backend/services/jrny-service/tests/cucumber/journey-creation.feature` _(12 cenários)_
- [x] `docs/architecture/backend/services/jrny-service/tests/cucumber/routing-decision.feature` _(10 cenários)_
- [x] `docs/architecture/backend/services/jrny-service/tests/cucumber/stage-transition.feature` _(8 cenários)_
- [x] `docs/architecture/backend/services/jrny-service/events/event-catalog.md`
- [x] `docs/architecture/backend/services/jrny-service/spec/backend/SPEC-01..10-*.md` (10 SPECs; 02=routing-engine-orchestration, 03=journey-builder)
- [x] `docs/architecture/backend/services/jrny-service/diagrams/c4-{context,container,component}.puml`

### Etapa A3 — Backlog (`/be-architect-backlog JRNY`)

- [x] Issues `JRNY-001..016` + `INT-JRNY-001..006` + `issues_map-JRNY.md`
- [x] `docs/architecture/backend/services/jrny-service/generator-config.yml`
- [x] `docs/architecture/backend/plans/plan-JRNY.md`

### Etapa A4 — Scaffold (`/be-architect-scaffold JRNY`)

- [x] `backend/services/jrny-service/` — skeleton hexagonal completo (106 java + V1 5 tabelas + 3 BDD features); registrado em `backend/settings.gradle.kts`
- [x] Conflito @Entity do entity-generator encadeado resolvido (padrão WRKS): removidos 20 órfãos `*Entity/*Repository/*Port/*JpaAdapter`, mantido layer base `*JpaEntity/*JpaRepository/*RepositoryPort/*RepositoryAdapter`
- [ ] **Gate pós-scaffold (compileJava + architectureCheck + CucumberIT) DEFERIDO** — sem Gradle/wrapper no ambiente; rodar `:jrny-service:spotlessApply compileJava`, `:test --tests "*.architecture.*"` e `"*CucumberIT*"` quando o wrapper existir

### Etapa B — Implement (`/be-autopilot JRNY --implement`)

- [ ] Baseline · plan-JRNY.md · P1..P9 · ArchUnit PASS · Score ≥ 80

---

## Módulo 8 — COMM (Communication Hub)

> Serviço: `comm-service` · Tipo: standard · Pacote: `com.journeyos.comm`
> **Dependências:** WRKS, LEAD, JRNY

### Etapa A1 — Vision (`/be-architect-vision COMM`)

- [x] `docs/architecture/backend/services/comm-service/_brief.md`
- [x] `docs/architecture/backend/services/comm-service/01-architectural-vision.md`
- [x] `docs/architecture/backend/services/comm-service/02-architecture-blueprint.md`
- [x] `docs/architecture/backend/services/comm-service/03-initial-domain-framing.md`
- [x] `docs/architecture/backend/services/comm-service/04-backend-architecture-direction.md`
- [x] `docs/architecture/backend/services/comm-service/05-persistence-model.md`
- [x] `docs/architecture/backend/services/comm-service/06-risks-gaps-assumptions.md`
- [x] `docs/architecture/backend/services/comm-service/adr/README.md`
- [x] `docs/architecture/backend/services/comm-service/adr/ADR-001-hexagonal-architecture.md`
- [x] `docs/architecture/backend/services/comm-service/adr/ADR-002-single-service-boundary.md`
- [x] `docs/architecture/backend/services/comm-service/adr/ADR-003-messaging-strategy.md`
- [x] `docs/architecture/backend/services/comm-service/adr/ADR-004-multitenant-strategy.md`
- [x] `docs/architecture/backend/services/comm-service/adr/ADR-005-channel-adapter-pattern.md`

### Etapa A2 — Specs (`/be-architect-specs COMM`)

- [x] `docs/architecture/backend/services/comm-service/comm-service-spec.md` _(port 8085)_
- [x] `docs/architecture/backend/services/comm-service/setup-local.md`
- [x] Contracts: `api-contract`, `data-model` (5 tabelas, schema=empresa sem empresa_id), `event-contracts`, `hub-integration`, `integration-contracts`
- [x] `docs/architecture/backend/services/comm-service/contracts/techlab-ai-integration.md` _(TechLab AI: document_composition — Template Studio)_
- [x] Features Cucumber: `message-dispatch`, `template-rendering`, `channel-routing`
- [x] `docs/architecture/backend/services/comm-service/events/event-catalog.md`
- [x] `docs/architecture/backend/services/comm-service/spec/backend/SPEC-01..10-*.md` (10 SPECs; SPEC-02=dispatch lifecycle, SPEC-03=channel routing/adapter)
- [x] Diagramas C4: context, container, component

### Etapa A3 — Backlog (`/be-architect-backlog COMM`)

- [x] Issues `COMM-001..016` + `INT-COMM-001..006` + `issues_map-COMM.md` (22 issues)
- [x] `docs/architecture/backend/services/comm-service/generator-config.yml` _(standard, bounded_context=comm, port 8085, 4 aggregates/1 entity/6 services/6 outbound_ports)_
- [x] `docs/architecture/backend/plans/plan-COMM.md` _(P1..P8)_

### Etapa A4 — Scaffold (`/be-architect-scaffold COMM`)

- [x] `backend/services/comm-service/` — skeleton hexagonal completo (130 java, port 8085, pacote `com.journeyos.comm`); registrado em `backend/settings.gradle.kts`
- [x] `V1__create_initial_schema.sql` (5 tabelas: template_mensagem/mensagem/evento_entrega/regra_roteamento/config_canal)
- [x] BDD harness (3 features + step stubs + CucumberIT + CucumberSpringContext); `ArchitectureTest` @AnalyzeClasses `com.journeyos.comm` (RULE-09)
- [ ] **Gate pós-scaffold (compileJava + architectureCheck + A5.bdd-gate) DEFERIDO** — sem toolchain Gradle no ambiente (idem WRKS/ASST/LEAD). Rodar `./gradlew :services:comm-service:spotlessApply compileJava` + `:test --tests "*.architecture.*"`/`"*CucumberIT*"` quando o wrapper existir.
- [ ] **Artefato conhecido:** duplicate `@Entity` (`XEntity` + `XJpaEntity`) gerado pelo entity-gen encadeado — idêntico a ASST/LEAD; base é canônica (ver memória toolchain-entity-generator-conflict).

### Etapa B — Implement (`/be-autopilot COMM --implement`)

- [ ] Baseline · plan-COMM.md · P1..P9 · ArchUnit PASS · Score ≥ 80

---

## Módulo 9 — SALE (Sales & Revenue)

> Serviço: `sale-service` · Tipo: standard · Pacote: `com.journeyos.sale`
> **Dependências:** WRKS, LEAD, JRNY, COMM

### Etapa A1 — Vision (`/be-architect-vision SALE`)

- [x] `docs/architecture/backend/services/sale-service/_brief.md`
- [x] `docs/architecture/backend/services/sale-service/01-architectural-vision.md`
- [x] `docs/architecture/backend/services/sale-service/02-architecture-blueprint.md`
- [x] `docs/architecture/backend/services/sale-service/03-initial-domain-framing.md`
- [x] `docs/architecture/backend/services/sale-service/04-backend-architecture-direction.md`
- [x] `docs/architecture/backend/services/sale-service/05-persistence-model.md`
- [x] `docs/architecture/backend/services/sale-service/06-risks-gaps-assumptions.md`
- [x] `docs/architecture/backend/services/sale-service/adr/README.md`
- [x] `docs/architecture/backend/services/sale-service/adr/ADR-001-hexagonal-architecture.md`
- [x] `docs/architecture/backend/services/sale-service/adr/ADR-002-single-service-boundary.md`
- [x] `docs/architecture/backend/services/sale-service/adr/ADR-003-messaging-strategy.md`
- [x] `docs/architecture/backend/services/sale-service/adr/ADR-004-multitenant-strategy.md`
- [x] `docs/architecture/backend/services/sale-service/adr/ADR-005-revenue-attribution-model.md`

### Etapa A2 — Specs (`/be-architect-specs SALE`)

- [x] `docs/architecture/backend/services/sale-service/sale-service-spec.md`
- [x] `docs/architecture/backend/services/sale-service/setup-local.md`
- [x] Contracts: `api-contract`, `data-model` (9 tabelas), `event-contracts`, `hub-integration`, `integration-contracts` _(sem `techlab-ai-integration` — sem IA no MVP)_
- [x] Features Cucumber: `sales-pipeline`, `purchase-revenue`, `revenue-attribution`
- [x] `docs/architecture/backend/services/sale-service/events/event-catalog.md`
- [x] `docs/architecture/backend/services/sale-service/spec/backend/SPEC-01..10-*.md` (10 SPECs; 02=pipeline-orchestration, 03=revenue-attribution-ltv)
- [x] Diagramas C4: context, container, component

### Etapa A3 — Backlog (`/be-architect-backlog SALE`)

- [x] Issues `SALE-001..019` (19) + `INT-SALE-001..005` (5) + `issues_map-SALE.md`
- [x] `docs/architecture/backend/services/sale-service/generator-config.yml` (standard, bounded_context=sale, port 8086, 6 aggregates/3 entities/5 services/3 outbound_ports/7 eventos)
- [x] `docs/architecture/backend/plans/plan-SALE.md` (P1..P9)

### Etapa A4 — Scaffold (`/be-architect-scaffold SALE`)

- [x] `backend/services/sale-service/` — skeleton hexagonal completo (164 java, pacote `com.journeyos.sale`, port 8086); V1__create_initial_schema.sql (9 tabelas, schema empresa); BDD harness (3 features + step stubs + CucumberIT); registrado em `backend/settings.gradle.kts`; ArchUnit @AnalyzeClasses `com.journeyos.sale`
- [ ] **Gate pós-scaffold (compileJava + architectureCheck + BDD) NÃO executado** — sem toolchain Gradle no ambiente (sem wrapper/CLI). Rodar `./gradlew :services:sale-service:spotlessApply compileJava` e `:test --tests "*.architecture.*"`/`"*CucumberIT*"` quando o wrapper existir.

### Etapa B — Implement (`/be-autopilot SALE --implement`)

- [ ] Baseline · plan-SALE.md · P1..P9 · ArchUnit PASS · Score ≥ 80

---

## Módulo 10 — INTL (Intelligence & Platform)

> Serviço: `intl-service` · Tipo: standard · Pacote: `com.journeyos.intl`
> **Dependências:** todos os módulos (consumidor de eventos transversal)

### Etapa A1 — Vision (`/be-architect-vision INTL`)

- [x] `docs/architecture/backend/services/intl-service/_brief.md`
- [x] `docs/architecture/backend/services/intl-service/01-architectural-vision.md`
- [x] `docs/architecture/backend/services/intl-service/02-architecture-blueprint.md`
- [x] `docs/architecture/backend/services/intl-service/03-initial-domain-framing.md`
- [x] `docs/architecture/backend/services/intl-service/04-backend-architecture-direction.md`
- [x] `docs/architecture/backend/services/intl-service/05-persistence-model.md`
- [x] `docs/architecture/backend/services/intl-service/06-risks-gaps-assumptions.md`
- [x] `docs/architecture/backend/services/intl-service/adr/README.md`
- [x] `docs/architecture/backend/services/intl-service/adr/ADR-001-hexagonal-architecture.md`
- [x] `docs/architecture/backend/services/intl-service/adr/ADR-002-single-service-boundary.md`
- [x] `docs/architecture/backend/services/intl-service/adr/ADR-003-event-platform-indexing-strategy.md` _(indexação descentralizada + contrato governado)_
- [x] `docs/architecture/backend/services/intl-service/adr/ADR-004-multitenant-strategy.md`
- [x] `docs/architecture/backend/services/intl-service/adr/ADR-005-ai-copilot-integration.md` _(RAG fundamentado + TechLab AI)_

### Etapa A2 — Specs (`/be-architect-specs INTL`)

- [x] `docs/architecture/backend/services/intl-service/intl-service-spec.md` _(port 8087)_
- [x] `docs/architecture/backend/services/intl-service/setup-local.md`
- [x] Contracts: `api-contract`, `data-model` (7 tabelas, schema empresa), `event-contracts`, `hub-integration`, `integration-contracts`
- [x] `docs/architecture/backend/services/intl-service/contracts/techlab-ai-integration.md` _(TechLab AI: knowledge + orchestration; analytics pós-MVP)_
- [x] Features Cucumber: `ai-copilot`, `knowledge-base`, `event-platform-analytics`
- [x] `docs/architecture/backend/services/intl-service/events/event-catalog.md`
- [x] `docs/architecture/backend/services/intl-service/spec/backend/SPEC-01..10-*.md` (10 SPECs; 02=copilot-orchestration RAG, 03=knowledge-event-platform)
- [x] Diagramas C4: context, container, component
- [x] Matrizes Elastic (`elastic-data-contract.md` §3 + `elastic-stack-integration.md` §2): `ai-copilot-events` (fact) + `knowledge-nodes` (dimension)

### Etapa A3 — Backlog (`/be-architect-backlog INTL`)

- [x] Issues `INTL-001..017` (17 funcionais) + `INT-INTL-001..006` (6 integração) + `issues_map-INTL.md`
- [x] `docs/architecture/backend/services/intl-service/generator-config.yml` _(standard, bounded_context=intl, port 8087, 4 aggregates/3 entities/3 services/6 outbound_ports)_
- [x] `docs/architecture/backend/plans/plan-INTL.md` _(P1..P9)_

### Etapa A4 — Scaffold (`/be-architect-scaffold INTL`)

- [x] `backend/services/intl-service/` — skeleton hexagonal completo (131 java, pacote `com.journeyos.intl`, port 8087, 4 aggregates/3 entities) + V1__create_initial_schema.sql (7 tabelas, schema empresa) + BDD harness (3 features + 3 step stubs + CucumberIT + CucumberSpringContext); ArchitectureTest `@AnalyzeClasses com.journeyos.intl` (RULE-09 OK); registrado (descomentado) em `backend/settings.gradle.kts`
- [ ] **Gate pós-scaffold (compileJava + architectureCheck + BDD) NÃO executado** — sem toolchain Gradle no ambiente (sem wrapper/CLI). Artefato conhecido: duplicate `@Entity`/port/adapter (base `*JpaEntity` + entity-gen `*Entity`; base canônica). Rodar `./gradlew :services:intl-service:spotlessApply compileJava` e `:test --tests "*.architecture.*"`/`"*CucumberIT*"` quando o wrapper existir.

### Etapa B — Implement (`/be-autopilot INTL --implement`)

- [ ] Baseline · plan-INTL.md · P1..P9 · ArchUnit PASS · Score ≥ 80

---

## Resumo de contagem de artefatos

| Módulo | Docs Vision | Docs Specs | Issues (aprox.) | Plans |
|--------|------------|------------|-----------------|-------|
| MIG | 13 | ~12 | 10–15 | 1 |
| REG | 13 | ~10 | 10–15 | 1 |
| GWY | 13 | ~12 | 10–15 | 1 |
| WRKS | 13 | 24 | 25–35 | 1 |
| LEAD | 13 | 25 | 25–35 | 1 |
| ASST | 13 | 24 | 25–35 | 1 |
| JRNY | 13 | 25 | 25–35 | 1 |
| COMM | 13 | 24 | 25–35 | 1 |
| SALE | 13 | 23 | 25–35 | 1 |
| INTL | 13 | 25 | 25–35 | 1 |
| **Total** | **130** | **~204** | **~250–330** | **10** |

> Artefatos de código (Java skeleton) gerados pelo `be-module-generator.py` não estão
> contabilizados acima — são produzidos automaticamente pelo scaffold.

---

## Referências de pipeline

| Comando | Etapa | Pré-requisito |
|---------|-------|---------------|
| `/be-architect-vision <M>` | A1 | Brief do módulo |
| `/be-architect-specs <M>` | A2 | Vision completa (01..06 + ADRs) |
| `/be-architect-backlog <M>` | A3 | Specs + contracts completos |
| `/be-architect-scaffold <M>` | A4 | `generator-config.yml` + issues + plan |
| `/be-validator <M>` | B1 BASELINE | Scaffold executável |
| `/be-planner <M>` | B3 | Baseline calculado |
| `/be-implement <M> P<N>` | B4 | Plano com prioridade definida |
| `/be-autopilot <M>` | A→B | Detecta estado e encadeia tudo |

---

## Log cronológico do autopilot

> Append-only. Uma linha por transição de etapa do `/be-architecture-autopilot`.

- 2026-06-04T18:07:50Z -- MIG -- vision -- início -- fresh start, infra (centralized Flyway)
- 2026-06-04T18:07:50Z -- MIG -- vision -- OK -- 13 arquivos (brief, docs 01..06, adr README + ADR-001..005)
- 2026-06-04T18:11:29Z -- REG -- vision -- OK -- _brief + docs 01..06 + adr README + ADR-001..005 (infra/registry, no domain)
- 2026-06-04T18:07:47Z -- GWY -- vision -- início -- fresh start, infra (gateway), reativo/WebFlux
- 2026-06-04T18:13:00Z -- GWY -- vision -- OK -- 13 arquivos (brief, docs 01..06, adr README + ADR-001..005); sem eventos/Feign; A3 será N/A
- 2026-06-04T18:14:00Z -- GWY -- specs -- início -- conjunto reduzido (gateway): sem data-model/event-contracts/cucumber/techlab-ai
- 2026-06-04T18:16:00Z -- GWY -- specs -- OK -- 12 arquivos (spec entry, setup-local, api-contract, integration-contracts, event-catalog vazio, SPEC-01/05/06/07, c4 x3); EARS aplicado
- 2026-06-04T18:16:00Z -- GWY -- specs-validate -- N/A -- módulo de infraestrutura (gateway) sem specs EARS de domínio
- 2026-06-04T18:18:00Z -- GWY -- backlog -- início -- gateway: sem P3 (persistência) nem P8 (BDD-domínio)
- 2026-06-04T18:22:00Z -- GWY -- backlog -- OK -- 12 issues GWY-001..012 + 4 INT-GWY-001..004; issues_map; generator-config.yml (gateway, 8080); plan-GWY (P1,P2,P4,P5,P6,P7)
- 2026-06-04T18:25:00Z -- GWY -- scaffold -- correção-fonte -- generator-config.yml sem bounded_context/issue_prefix gerava pacote com.journeyos.journeyosapigateway (viola RULE-09); adicionado bounded_context=gwy, issue_prefix=GWY (convenção REG)
- 2026-06-04T18:26:00Z -- GWY -- scaffold -- OK -- be-module-generator gerou 13 arquivos (pacote com.journeyos.gwy); registrado em backend/settings.gradle.kts
- 2026-06-04T18:26:00Z -- GWY -- scaffold -- gate-diferido -- compileJava/architectureCheck não executados (sem Gradle/wrapper no ambiente); A5.bdd-gate N/A (gateway)
- 2026-06-04T18:15:32Z -- REG -- specs -- OK -- reduced set: spec, setup-local, api+integration contracts, event-catalog(empty), SPEC-01/06/07, 3x C4
- 2026-06-04T18:15:32Z -- REG -- specs-validate -- N/A -- infra/registry: no EARS domain specs to convert to BDD
- 2026-06-04T18:07:50Z -- MIG -- specs -- OK -- 16 arquivos: spec, setup-local, 5 contracts (api/data-model/event/hub/integration), event-catalog(empty), SPEC-01/04/05/06/07, 3x C4
- 2026-06-04T18:07:50Z -- MIG -- specs-validate -- N/A -- infra/migrations: no EARS business-domain specs to convert to BDD (A3 skipped)
- 2026-06-04T18:07:50Z -- MIG -- backlog -- OK -- 8 issues (MIG-001..008) + 2 INT + issues_map + generator-config(type=standard,domínio vazio) + plan-MIG (P1/P2/P3/P5/P7)
- 2026-06-04T18:07:50Z -- MIG -- scaffold -- fix-fonte -- generator-config sem bounded_context/issue_prefix → pacote com.journeyos.journeyosmigrations + prefix GWY; corrigido p/ bounded_context=mig, issue_prefix=MIG (convenção REG)
- 2026-06-04T18:07:50Z -- MIG -- scaffold -- OK -- 34 base files + V1(5 extensões) em com.journeyos.mig; módulo registrado em settings.gradle.kts; gate compile/ArchUnit NÃO executado (sem toolchain Gradle); BDD gate N/A
- 2026-06-04T18:17:48Z -- REG -- backlog -- OK -- 5 issues (REG-001..005, P1..P4), 0 INT, issues_map, plan-REG, generator-config.yml (type=registry)
- 2026-06-04T18:22:03Z -- REG -- scaffold -- OK -- 12 files (pkg com.journeyos.reg, type=registry, port 8761); registered in root settings; fixed generator-config (bounded_context=reg, issue_prefix=REG)
- 2026-06-04T18:22:03Z -- REG -- scaffold -- WARN -- BDD gate N/A (registry); compileJava/architectureCheck NOT run (no Gradle in env) -- verification pending
- 2026-06-04T19:06:30Z -- WRKS -- vision -- início -- fresh start, standard (fundação identidade/RBAC/multi-tenancy)
- 2026-06-04T19:06:30Z -- WRKS -- vision -- OK -- 13 arquivos (brief, docs 01..06, adr README + ADR-001..005); services-catalog populado (wrks-service, eventos, Feign AccessDecision); roles canônicos INFOPRODUTOR/HEAD_GROWTH/SDR
- 2026-06-04T19:06:30Z -- WRKS -- specs -- início -- full spec set (standard); IAM em journeyos_global
- 2026-06-04T19:06:30Z -- WRKS -- specs -- OK -- 25 arquivos: spec entry, setup-local, 6 contracts (api/data-model/event/hub/integration/techlab-ai=none), 4 .feature, event-catalog, SPEC-01..10, 3x C4; EARS aplicado; data-model com sql blocks (schema global, identificadores pt-BR canônicos)
- 2026-06-04T19:06:30Z -- WRKS -- specs-validate -- gate-deferido -- 104 SHALL clauses / 26 cenários BDD já autorais nos .feature; geração be-spec-to-bdd.py DEFERIDA p/ A5 (skeleton do serviço só existe pós-scaffold); gate compile/BDD não executável (sem wrapper/CLI Gradle no ambiente, idem MIG/REG/GWY)
- 2026-06-04T19:06:30Z -- WRKS -- backlog -- OK -- 18 issues WRKS-001..018 + 6 INT-WRKS-001..006 + issues_map + plan-WRKS (P1..P8) + generator-config.yml (standard, bounded_context=wrks, port 8081, 6 aggregates/5 entities/8 services/8 ports/6 eventos)
- 2026-06-04T19:06:30Z -- WRKS -- scaffold -- fix-toolchain -- corrigido bug em scripts/be-entity-generator.py (smart_query_methods sem param `overrides`, L325) que bloqueava TODO módulo standard; corrigido generator-config.yml (removidos `# comments` inline em outbound_ports/aggregates que corrompiam nomes de classe)
- 2026-06-04T19:06:30Z -- WRKS -- scaffold -- OK -- be-module-generator: 152 java + V1 (11 tabelas IAM journeyos_global) + BDD harness (4 features+4 steps+CucumberIT+CucumberSpringContext); registrado em settings.gradle.kts; removido 1 órfão (EmpresaEntity.java) do crash; NÃO rodado o entity-gen encadeado (convenção conflitante <X>Entity vs base <X>JpaEntity → duplicate @Entity)
- 2026-06-04T19:06:30Z -- WRKS -- scaffold -- gate-deferido -- compileJava/architectureCheck/CucumberIT NÃO executados (sem wrapper/CLI Gradle, idem MIG/REG/GWY)
- 2026-06-04T19:06:30Z -- WRKS -- ACHADO-toolchain -- be-module-generator encadeia be-entity-generator com convenção de nomes incompatível com o layer base (`<X>Entity/Repository/Port/JpaAdapter` vs base `<X>JpaEntity/JpaRepository/RepositoryPort/RepositoryAdapter`) → @Entity duplicada. WRKS é o 1º módulo standard a exercitar esse caminho (MIG tinha domínio vazio). Requer atenção do mantenedor; p/ WRKS o layer base é canônico e suficiente.
- 2026-06-04T19:18:35Z -- ASST -- vision -- início -- fresh start, standard (Asset Hub); depende de WRKS; scripts/ populado
- 2026-06-04T19:18:35Z -- ASST -- vision -- OK -- 13 arquivos (brief, docs 01..06, adr README + ADR-001..005); services-catalog populado (asst-service: resp + 4 eventos + Feign AssetQueryClient + TechLabAiClient document_composition); CLAUDE.md TechLab table (ASST=document_composition); âncora asset.versao.publicada; versionamento imutável + state machine de aprovação (ADR-005)
- 2026-06-04T19:18:35Z -- ASST -- specs -- início -- full spec set (standard); TechLab AI document_composition; índice Elastic assets (dimension)
- 2026-06-04T19:18:35Z -- ASST -- specs -- OK -- 25 arquivos: spec entry (port 8083), setup-local, 6 contracts (api/data-model/event/hub/integration/techlab-ai=document_composition), 3 .feature (asset-creation/versioning/approval-workflow), event-catalog, SPEC-01..10, 3x C4; EARS aplicado; data-model schema=empresa SEM empresa_id (schema isola), tabelas asset/versao_asset(imutável)/aprovacao/tag_asset
- 2026-06-04T19:18:35Z -- ASST -- specs-validate -- início -- gerar BDD a partir das specs EARS (be-spec-to-bdd.py); gate compile deferido p/ A5 (sem skeleton/Gradle)
- 2026-06-04T19:18:35Z -- ASST -- specs-validate -- gate-deferido -- 125 SHALL clauses / 18 cenários BDD autorais em 3 .feature; be-spec-to-bdd.py NÃO executável (be_spec_drift_lib ausente em scripts/ + skeleton asst-service inexistente + sem Gradle); geração BDD + gate compile/comportamento DEFERIDOS p/ A5 (idem WRKS)
- 2026-06-04T19:18:35Z -- ASST -- backlog -- OK -- 16 issues ASST-001..016 + 6 INT-ASST-001..006 + issues_map + plan-ASST (P1..P8) + generator-config.yml (standard, bounded_context=asst, port 8083, 1 aggregate Asset / 3 entities / 5 services / 4 ports / 4 eventos)
- 2026-06-04T19:18:35Z -- ASST -- scaffold -- início -- be-module-generator.py (skeleton hexagonal); pós-scaffold: spotlessApply→compileJava→architectureCheck (deferido se sem Gradle)
- 2026-06-04T19:18:35Z -- ASST -- scaffold -- OK -- be-module-generator gerou 125 arquivos (pacote com.journeyos.asst, port 8083, 1 aggregate/3 entities/5 services) + V1__create_initial_schema.sql (4 tabelas, schema empresa, sem empresa_id) + BDD harness (3 features + step stubs + CucumberIT); registrado em backend/settings.gradle.kts; ArchitectureTest @AnalyzeClasses com.journeyos.asst (RULE-09 OK)
- 2026-06-04T19:18:35Z -- ASST -- scaffold -- gate-deferido -- compileJava/architectureCheck + A5.bdd-gate NÃO executados (sem Gradle/wrapper no ambiente, idem MIG/REG/GWY/WRKS); rodar ./gradlew :services:asst-service:spotlessApply compileJava e :test --tests "*.architecture.*" + "*CucumberIT*" quando o wrapper existir
- 2026-06-04T19:18:35Z -- ASST -- PIPELINE ARQUITETURA COMPLETO (vision→specs→specs-validate→backlog→scaffold); próximo: Layer 2 manual (/be-autopilot ASST --implement ou /be-validator ASST)
- 2026-06-04T19:18:04Z -- LEAD -- vision -- início -- fresh start, standard (Lead Intelligence & Qualification); depende de WRKS
- 2026-06-04T19:20:00Z -- LEAD -- vision -- OK -- 13 arquivos (_brief, docs 01..06, adr README + ADR-001..005); services-catalog + CLAUDE.md populados; TechLab AI=qualification (assist+fallback); event bus Kafka/AWS MSK; âncora lead.qualificado; Maturity Score 6D (ADR-005 proposed)
- 2026-06-04T19:30:00Z -- LEAD -- specs -- OK -- 25 arquivos: spec entry (port 8082), setup-local, 6 contracts (api/data-model[12 tabelas schema=empresa]/event/hub/integration/techlab-ai=qualification), 3 .feature, event-catalog, SPEC-01..10 (02=orchestration, 03=Maturity Score 6D), 3x C4; EARS aplicado
- 2026-06-04T19:33:00Z -- LEAD -- specs-validate -- gate-deferido -- ~100 SHALL clauses / 17 cenários BDD autorais em 3 .feature; geração be-spec-to-bdd.py DEFERIDA p/ A5 (skeleton do serviço só existe pós-scaffold); gate compile/BDD não executável (sem Gradle/wrapper no ambiente, idem WRKS)
- 2026-06-04T19:42:00Z -- LEAD -- backlog -- OK -- 18 issues LEAD-001..018 + 5 INT-LEAD-001..005 + issues_map + plan-LEAD (P1..P9) + generator-config.yml (standard, bounded_context=lead, port 8082, 4 aggregates/8 entities/4 services/4 outbound_ports/4 eventos); INT-LEAD-003 bloqueado por P3 (TechLab AI sync)
- 2026-06-04T19:50:00Z -- LEAD -- scaffold -- OK -- be-module-generator gerou ~200 arquivos (pacote com.journeyos.lead, port 8082); 12 tabelas em V1__create_initial_schema.sql; ArchUnit @AnalyzeClasses com.journeyos.lead; 3 .feature + step stubs + CucumberIT; registrado em backend/settings.gradle.kts
- 2026-06-04T19:50:00Z -- LEAD -- scaffold -- gate-diferido -- spotlessApply/compileJava/architectureCheck + A5.bdd-gate NÃO executados (sem Gradle/wrapper no ambiente, idem WRKS/MIG/REG/GWY); rodar ./gradlew :services:lead-service:spotlessApply compileJava e :test --tests "*.architecture.*"/"*CucumberIT*" quando o wrapper existir
- 2026-06-04T19:49:27Z -- JRNY -- vision -- início -- fresh start, standard (Journey & Routing — Journey Builder + Routing Engine + decision log); depende de WRKS/LEAD/ASST
- 2026-06-04T19:49:27Z -- JRNY -- vision -- OK -- 13 arquivos (_brief, docs 01..06, adr README + ADR-001..005); services-catalog populado (jrny-service: owns jornada/estagio/regra_roteamento/inscricao/decisao_roteamento; produz jornada.publicada/lead.roteado[âncora]/estagio.transicionado/jornada.concluida; consome lead.qualificado/score/segmento+asset.versao.publicada; Feign JourneyQueryClient[provê]+AssetQueryClient[consome]+AccessEvaluate; TechLab orchestration) + Event Catalog(4 eventos JRNY) + Feign Registry; CLAUDE.md TechLab table (JRNY=orchestration, assist opcional/fallback determinístico); âncora lead.roteado; ADR-005 Routing Engine determinístico + decision log imutável + assist IA com fallback; índices Elastic fact journey-events/routing-decisions
- 2026-06-04T19:49:27Z -- JRNY -- specs -- OK -- 24 arquivos: spec entry, setup-local (port 8084), 6 contracts (api/data-model/event/hub/integration/techlab-ai=orchestration), 3 .feature (30 cenários: journey-creation 12 / routing-decision 10 / stage-transition 8), event-catalog, SPEC-01..10 (02=routing-engine-orchestration, 03=journey-builder), 3x C4; EARS aplicado (~158 SHALL); data-model com 5 sql blocks (jornada/estagio/regra_roteamento/inscricao_jornada/decisao_roteamento), schema=empresa, gen_random_uuid (pgcrypto via MIG), CHECKs + unique parcial (lead_id,jornada_id) WHERE estado=ATIVA + unique (jornada_id,ordem) + CHECK resultado=ROTEADO=>estagio_alvo_id NOT NULL; gramática de condicao ancorada nos campos de lead.qualificado (LEAD)
- 2026-06-04T19:49:27Z -- JRNY -- specs-validate -- gate-deferido -- ~158 SHALL clauses / 30 cenários BDD autorais em 3 .feature; geração be-spec-to-bdd.py DEFERIDA p/ A5 (skeleton do serviço só existe pós-scaffold); gate compile/BDD não executável (sem Gradle/wrapper no ambiente, idem WRKS/LEAD/ASST)
- 2026-06-04T19:49:27Z -- JRNY -- backlog -- OK -- 16 issues JRNY-001..016 + 6 INT-JRNY-001..006 + issues_map-JRNY + plan-JRNY (P1..P8) + generator-config.yml (standard, bounded_context=jrny, port 8084, 2 aggregates [Jornada,InscricaoJornada]/3 entities [Estagio,RegraRoteamento,DecisaoRoteamento]/5 application_services/5 enums/2 feign [AccessEvaluate+AssetQuery]/6 consumed/4 published/5 outbound_ports incl RecomendacaoIaPort+JourneyEventIndexPort); generator-config SEM inline comments em list items (lição WRKS)
- 2026-06-04T19:49:27Z -- JRNY -- scaffold -- OK -- be-module-generator gerou jrny-service (pacote com.journeyos.jrny, port 8084); 106 java files (após limpeza) + V1__create_initial_schema.sql (5 tabelas: jornada/estagio/regra_roteamento/inscricao_jornada/decisao_roteamento + unique parcial ATIVA + unique (jornada_id,ordem) + CHECK resultado<>ROTEADO) + BDD harness (3 features + step stubs + CucumberIT + CucumberSpringContext); ArchitectureTest @AnalyzeClasses com.journeyos.jrny; registrado em backend/settings.gradle.kts
- 2026-06-04T19:49:27Z -- JRNY -- scaffold -- CONFLITO-RESOLVIDO -- entity-generator encadeado gerou @Entity duplicada (<X>Entity + <X>JpaEntity na mesma tabela, ×5). Decisão do usuário: padrão WRKS (limpar agora). Removidos 20 órfãos (*Entity/*Repository/*Port/*JpaAdapter), mantido layer base canônico (*JpaEntity/*JpaRepository/*RepositoryPort/*RepositoryAdapter); sem refs penduradas (verificado). NOTA: ASST/COMM/SALE ainda têm os 2 conjuntos (conflito pendente neles)
- 2026-06-04T19:49:27Z -- JRNY -- scaffold -- gate-deferido -- compileJava/architectureCheck + A5.bdd-gate (CucumberIT) NÃO executados (sem Gradle/wrapper, idem WRKS/LEAD/ASST/COMM/SALE); rodar ./gradlew :services:jrny-service:spotlessApply compileJava e :test --tests "*.architecture.*"/"*CucumberIT*" quando o wrapper existir
- 2026-06-04T19:49:27Z -- JRNY -- PIPELINE ARQUITETURA COMPLETO (vision→specs→specs-validate→backlog→scaffold); próximo: Layer 2 manual (/be-autopilot JRNY --implement ou /be-validator JRNY)
- 2026-06-04T19:49:27Z -- LEAD/ASST/COMM/SALE -- scaffold -- CONFLITO-RESOLVIDO -- aplicada limpeza padrão WRKS (a pedido do usuário) ao conflito @Entity duplicada do entity-generator encadeado: removidos órfãos *Entity/*Repository/*Port/*JpaAdapter (LEAD 48, ASST 16, COMM 20, SALE 36 = 120 arquivos), mantido layer base canônico (*JpaEntity/*JpaRepository/*RepositoryPort/*RepositoryAdapter) + ProcessedEvent + named infra ports (TechLabQualificationPort/LeadSearchPort/AssetSearchPort/ComposicaoIaPort/CanalEnvioPort/CommSearchPort/SaleSearchPort/etc.); sem refs penduradas (verificado). TODOS os módulos standard (WRKS/LEAD/ASST/JRNY/COMM/SALE) agora limpos; INTL (ainda não scaffoldado) precisará da mesma limpeza
- 2026-06-04T19:54:00Z -- SALE -- vision -- início -- fresh start, standard (Sales & Revenue — CRM/pipeline + ofertas + compras + atribuição + LTV); depende de WRKS/LEAD/JRNY/COMM
- 2026-06-04T19:54:00Z -- SALE -- vision -- OK -- 13 arquivos (_brief, docs 01..06, adr README + ADR-001..005); services-catalog populado (sale-service: owns oportunidade/historico_estagio/oferta/compra/item_compra/modelo_atribuicao/atribuicao/campanha/ltv; produz oportunidade.criada/estagio.alterado/ganha/perdida + compra.confirmada[âncora] + receita.atribuida + ltv.atualizado; consome lead.qualificado/score + empresa.provisionada/modelo.acesso.alterado) + Event Catalog (7 eventos SALE) + Service Map (sale-service:8086); SEM TechLab AI no MVP (atribuição/LTV determinísticos; analytics pós-MVP); âncora compra.confirmada; ADR-005 atribuição de receita determinística (last/first/linear-touch) + idempotência de compra (id_externo+origem) + conservação de receita; índices Elastic fact revenue-events/campaign-events; SALE não processa pagamento (gateway externo)
- 2026-06-04T20:05:11Z -- COMM -- vision -- início -- fresh start, standard (Communication Hub); depende de WRKS/LEAD/JRNY
- 2026-06-04T20:05:11Z -- COMM -- vision -- OK -- 13 arquivos (_brief, docs 01..06, adr README + ADR-001..005); ADR-005=channel-adapter-pattern (CanalEnvioPort, provedor-agnóstico); services-catalog + CLAUDE.md TechLab table populados; TechLab AI=document_composition (Template Studio); âncora journey-os.mensagem.enviada; índice Elastic communication-events (fact)
- 2026-06-04T20:02:00Z -- SALE -- specs -- OK -- 24 arquivos: spec entry (port 8086), setup-local, 5 contracts (api/data-model[9 tabelas schema=empresa]/event/hub/integration; SEM techlab-ai — sem IA no MVP), 3 .feature (sales-pipeline/purchase-revenue/revenue-attribution), event-catalog, SPEC-01..10 (02=pipeline-orchestration, 03=revenue-attribution-ltv), 3x C4; EARS aplicado; data-model com SQL blocks (oportunidade/historico_estagio/oferta/compra[UNIQUE id_externo+origem]/item_compra/modelo_atribuicao[partial unique ativo]/atribuicao[conservação de receita]/campanha/ltv[materializado por contato_ref]); valores monetários NUMERIC(15,2)+moeda
- 2026-06-04T20:05:00Z -- SALE -- specs-validate -- gate-deferido -- 119 SHALL clauses / 19 cenários BDD autorais em 3 .feature (sales-pipeline 7 + purchase-revenue 6 + revenue-attribution 6); be-spec-to-bdd.py NÃO executável (be_spec_drift_lib ausente em scripts/ + skeleton sale-service inexistente + sem Gradle); geração BDD + gate compile/comportamento DEFERIDOS p/ A5 (idem WRKS/LEAD/ASST)
- 2026-06-04T20:25:00Z -- COMM -- specs -- OK -- 25 arquivos: spec entry (port 8085), setup-local, 6 contracts (api/data-model[5 tabelas schema=empresa sem empresa_id]/event/hub/integration/techlab-ai=document_composition), 3 .feature (message-dispatch/template-rendering/channel-routing), event-catalog, SPEC-01..10 (02=dispatch-lifecycle, 03=channel-routing/adapter), 3x C4; EARS aplicado; webhooks autenticados por assinatura de provedor; tenant resolvido da mensagem
- 2026-06-04T20:30:00Z -- COMM -- specs-validate -- gate-deferido -- ~142 SHALL (61 em SPEC-01..10) / 23 cenários BDD autorais em 3 .feature; be-spec-to-bdd.py NÃO executável (be_spec_drift_lib ausente em scripts/ + skeleton comm-service inexistente + sem Gradle); geração BDD + gate compile/comportamento DEFERIDOS p/ A5 (idem WRKS/ASST/LEAD)
- 2026-06-04T20:12:00Z -- SALE -- backlog -- OK -- 19 issues SALE-001..019 + 5 INT-SALE-001..005 + issues_map + plan-SALE (P1..P9) + generator-config.yml (standard, bounded_context=sale, port 8086, 6 aggregates Oportunidade/Oferta/Compra/ModeloAtribuicao/Campanha/Ltv / 3 entities HistoricoEstagio/ItemCompra/Atribuicao / 5 services / 3 outbound_ports SaleSearch/SaleEventPublisher/AccessDecisionCache / 7 eventos publicados / 4 consumed); SEM TechLab port (sem IA no MVP)
- 2026-06-04T20:18:00Z -- SALE -- scaffold -- OK -- be-module-generator gerou 164 java (pacote com.journeyos.sale, port 8086, 6 aggregates/3 entities; base layer canonico *JpaEntity/JpaRepository/RepositoryAdapter; NÃO encadeou be-entity-generator → sem duplicate @Entity) + V1__create_initial_schema.sql (9 tabelas schema empresa) + BDD harness (3 features + 3 step stubs + CucumberIT + CucumberSpringContext); registrado (descomentado) em backend/settings.gradle.kts; ArchitectureTest @AnalyzeClasses com.journeyos.sale (RULE-09 OK)
- 2026-06-04T20:18:00Z -- SALE -- scaffold -- gate-deferido -- compileJava/architectureCheck + A5.bdd-gate NÃO executados (sem gradlew/gradle no ambiente, idem WRKS/LEAD/ASST/MIG/REG/GWY); rodar ./gradlew :services:sale-service:spotlessApply compileJava e :test --tests "*.architecture.*"/"*CucumberIT*" quando o wrapper existir
- 2026-06-04T20:18:00Z -- SALE -- PIPELINE ARQUITETURA COMPLETO (vision→specs→specs-validate→backlog→scaffold); próximo: Layer 2 manual (/be-autopilot SALE --implement ou /be-validator SALE)
- 2026-06-04T20:45:00Z -- COMM -- backlog -- OK -- 16 issues COMM-001..016 + 6 INT-COMM-001..006 + issues_map + plan-COMM (P1..P8) + generator-config.yml (standard, bounded_context=comm, port 8085, 4 aggregates/1 entity/6 services/6 outbound_ports incl. CanalEnvioPort/ComposicaoIaPort/AssetQueryPort, 4 eventos pub, 4 consumidos); INT-COMM-003 relacionado a P3 bloqueado (TechLab AI sync)
- 2026-06-04T20:55:00Z -- COMM -- scaffold -- OK -- be-module-generator gerou 130 java (pacote com.journeyos.comm, port 8085, 4 aggregates/1 entity/6 controllers/10 DTOs) + V1__create_initial_schema.sql (5 tabelas, schema empresa sem empresa_id) + BDD harness (3 features + step stubs + CucumberIT + CucumberSpringContext); ArchitectureTest @AnalyzeClasses com.journeyos.comm (RULE-09 OK); registrado em backend/settings.gradle.kts
- 2026-06-04T20:55:00Z -- COMM -- scaffold -- gate-deferido -- compileJava/architectureCheck + A5.bdd-gate NÃO executados (sem Gradle/wrapper no ambiente, idem WRKS/ASST/LEAD); duplicate @Entity (XEntity+XJpaEntity) = artefato conhecido do entity-gen encadeado (idêntico a ASST/LEAD; base canônica)
- 2026-06-04T20:55:00Z -- COMM -- PIPELINE ARQUITETURA COMPLETO (vision→specs→specs-validate→backlog→scaffold); próximo: Layer 2 manual (/be-autopilot COMM --implement ou /be-validator COMM)
- 2026-06-05T00:31:56Z -- INTL -- vision -- início -- fresh start, standard (Intelligence & Platform — AI Copilot + Knowledge + governança Elastic + leitura analítica); depende de WRKS/ASST/TechLab AI/Elastic
- 2026-06-05T00:31:56Z -- INTL -- vision -- OK -- 13 arquivos (_brief, docs 01..06, adr README + ADR-001..005); port 8087; âncora journey-os.copilot.resposta.gerada; TechLab AI=knowledge+orchestration (RAG fundamentado, circuit breaker + fallback recuperação-apenas); ADR-003=plataforma de dados DESCENTRALIZADA (cada produtor JRNY/COMM/SALE escreve seus facts; INTL governa contrato 8-campos D-269/DLQ/ILM + escreve só ai-copilot-events[fact]/knowledge-nodes[dimension] + leitura analítica cross-index), ADR-004=multi-tenancy híbrida (PG schema-per-tenant + Elastic compartilhado c/ discriminador empresa), ADR-005=AI Copilot RAG (read-only, citações, INV fundamentação, sem IA direta); services-catalog + Event Catalog + Feign Registry + CLAUDE.md TechLab table populados (INTL=knowledge+orchestration); obs indices app-logs/traces/metrics/integration-logs DECLARADOS mas ingestão infra/APM (fora MVP); Integration Hub pós-MVP
- 2026-06-05T00:31:56Z -- INTL -- specs -- OK -- 25 arquivos: spec entry (port 8087), setup-local, 6 contracts (api/data-model[7 tabelas schema=empresa sem empresa_id: base_conhecimento/fonte_conhecimento/no_conhecimento[vector(1536) nullable]/conversa_copiloto/mensagem_copiloto/citacao/evento_indexado ledger]/event-contracts/techlab-ai=knowledge+orchestration/hub/integration), 3 .feature (ai-copilot 6 / knowledge-base 7 / event-platform-analytics 6), event-catalog, SPEC-01..10 (02=copilot-orchestration RAG fundamentado, 03=knowledge+event-platform descentralizado), 3x C4; EARS aplicado; matrizes Elastic (data-contract §3 + stack-integration §2) populadas (ai-copilot-events[fact]+knowledge-nodes[dimension]; obs app-logs/traces/metrics/integration-logs declarados, ingestão infra/APM fora MVP); âncora copilot.resposta.gerada; degradação graciosa (TechLab AI off → DEGRADADA, sem 5xx); registro_indice global ADIADO (governança via config no MVP)
- 2026-06-05T00:31:56Z -- INTL -- specs-validate -- gate-deferido -- 91 SHALL clauses (specs+contracts) / 19 cenários BDD autorais em 3 .feature (ai-copilot 6 + knowledge-base 7 + event-platform-analytics 6); be-spec-to-bdd.py NÃO executável (ModuleNotFoundError be_spec_drift_lib ausente em scripts/ + skeleton intl-service inexistente + sem Gradle); geração StepDefs/CucumberSpringContext + gate compile/comportamento DEFERIDOS p/ A5 (idem WRKS/LEAD/ASST/SALE/COMM)
- 2026-06-05T00:31:56Z -- INTL -- backlog -- OK -- 17 issues INTL-001..017 + 6 INT-INTL-001..006 + issues_map-INTL + plan-INTL (P1..P9) + generator-config.yml (standard, bounded_context=intl, issue_prefix=INTL, port 8087, 4 aggregates BaseConhecimento/FonteConhecimento/ConversaCopiloto/EventoIndexado / 3 entities NoConhecimento/MensagemCopiloto/Citacao / 3 application_services Copilot/Knowledge/Analytics / 6 enums / 2 feign AccessEvaluate+AssetQuery / 3 consumed / 1 published CopilotRespostaGerada / 6 outbound_ports IntlSearch/IntlIndex/Knowledge/Orchestration/IntlEventPublisher/AccessDecisionCache); INT-INTL-002 bloqueado por P3 (TechLab AI sync); generator-config SEM inline comments em list items (lição WRKS)
- 2026-06-05T00:31:56Z -- INTL -- scaffold -- OK -- be-module-generator gerou 131 java (pacote com.journeyos.intl, port 8087, 4 aggregates/3 entities) + V1__create_initial_schema.sql (7 tabelas schema empresa: base_conhecimento/fonte_conhecimento/no_conhecimento/conversa_copiloto/mensagem_copiloto/citacao/evento_indexado) + BDD harness (3 features ai-copilot/knowledge-base/event-platform-analytics + 3 step stubs + CucumberIT + CucumberSpringContext); ArchitectureTest @AnalyzeClasses com.journeyos.intl (RULE-09 OK); registrado (descomentado) em backend/settings.gradle.kts
- 2026-06-05T00:31:56Z -- INTL -- scaffold -- gate-deferido -- compileJava/architectureCheck + A5.bdd-gate NÃO executados (sem gradlew/gradle no ambiente, idem WRKS/LEAD/ASST/SALE/COMM/MIG/REG/GWY); ARTEFATO CONHECIDO: duplicate @Entity/port/adapter (base *JpaEntity/*RepositoryPort/*RepositoryAdapter + chained be-entity-generator *Entity/*Port/*JpaAdapter, idêntico WRKS/ASST/LEAD/COMM; base canônica); rodar ./gradlew :services:intl-service:spotlessApply compileJava e :test --tests "*.architecture.*"/"*CucumberIT*" quando o wrapper existir
- 2026-06-05T00:31:56Z -- INTL -- PIPELINE ARQUITETURA COMPLETO (vision->specs->specs-validate->backlog->scaffold); próximo: Layer 2 manual (/be-autopilot INTL --implement ou /be-validator INTL)
