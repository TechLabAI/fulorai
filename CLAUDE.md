# Journey OS -- O Journey OS é um Sistema Operacional de Crescimento para empresas de educação digital, infoprodutos e vendas consultivas no Brasil e na América Latina.

> Monorepo: `/backend` (Java 21 microservices) + `/frontend` (Angular + Nx) + `/integrations/techlab-ai/` (TechLab AI docs snapshot — service runs as Docker image) + `/docs/architecture/` (specification).
>
> **Stack:** Java 21 . Spring Boot 3.5.0 . Gradle 8.x (Kotlin DSL) . None . PostgreSQL 15+ . Angular 18+ . Nx 19+ . TechLab AI (consumed via HTTP)

---

## Monorepo layout

```
/backend/                              # Java 21 microservices
  build.gradle.kts (root)
  settings.gradle.kts
  services/
    /
    /
    /
    /
    /
    /
    /
    /
    /
    /

    journey-os-migrations/         # Centralized Flyway (all schemas)

/frontend/                             # Nx workspace, npmScope: @journeyos
  apps/
    journey-os-web/                       # single Angular app (for now)
  libs/
    shared/{ui-tokens,ui-feedback,ui-components,error-model,access-http-base}/

/integrations/techlab-ai/              # TechLab AI docs snapshot (docs-only, auto-synced)
  README.md                            # upstream README at pinned SHA
  openapi.json                         # source for auto-generating Java DTOs
  docs/                                # SDD.md, ADRs, SPECs, contracts, RUNBOOK
  .source-sha                          # pinned commit SHA (matches project-context.json)

/docs/architecture/integrations/
  techlab-ai-integration.md            # how THIS project consumes TechLab AI

/docs/architecture/
  backend/{adr,services,standards,issues,plans}/
  frontend/{adr,libs,standards,issues,plans}/
  shared/{modelo-dados,contratos,rbac}/

```

---

## Business modules (= unit of work of the AI pipeline)

| Code | Name | Microservice | Nx Lib |
|---|---|---|---|
| WRKS | Workspace & Identity | `` | -- |
| LEAD | Lead Intelligence & Qualification | `` | -- |
| JRNY | Journey & Routing | `` | -- |
| ASST | Asset Hub | `` | -- |
| COMM | Communication Hub | `` | -- |
| SALE | Sales & Revenue | `` | -- |
| INTL | Intelligence & Platform | `` | -- |
| GWY | API Gateway | `` | -- |
| REG | Service Registry | `` | -- |
| MIG | Migrations | `` | -- |

Issue prefix: `<MODULE>-NNN` (e.g.: `WRKS-001`, `LEAD-001`, `JRNY-001`). Issues live in `docs/architecture/{backend,frontend}/issues/`; GitHub sync to be set up when repository is created.

---

## TechLab AI Integration

This project delegates **all AI capabilities** to TechLab AI — a separate Python service consumed via HTTP.

- **Upstream repository:** 
- **Pinned source SHA:** `PENDING_FIRST_COMMIT` (recorded in `project-context.json.ai.techlabAi.sourceSha`)
- **Docs snapshot location:** `integrations/techlab-ai/` (synced read-only)
- **Service runtime:** Docker image `ghcr.io/DaniloAmaral-Dev/techlab-ai:latest` (port 8090 locally)
- **Upstream issue prefix:** `TLAB-NNN`
- **Integration contract (this project):** `docs/architecture/integrations/techlab-ai-integration.md`

### Bounded contexts exposed by TechLab AI

### Endpoints consumed by each module

Updated by `/be-architect-vision <MODULE>` as modules declare their TechLab AI usage.

| Module | Endpoints |
|---|---|
| **LEAD** | Capability `qualification` (assist opcional ao Maturity Score 6D; degrada para cálculo determinístico em falha). Endpoints exatos pendentes do sync upstream (P3 — `integrations/techlab-ai/openapi.json` ainda vazio). |
| **ASST** | Capability `document_composition` (Asset Studio — compõe/edita conteúdo de asset a partir de brief + contexto da empresa) + classificação/tagging (Asset Intelligence). Síncrono com circuit breaker; degrada graciosamente (CRUD/aprovação intactos). Endpoints exatos pendentes do sync upstream (P3 — `integrations/techlab-ai/openapi.json` ainda vazio). |
| **JRNY** | Capability `orchestration` (Routing Engine — recomenda próximo-melhor-estágio/ação a partir do contexto do lead + jornada). Assist **opcional**: síncrono com circuit breaker; degrada para roteamento determinístico em falha (decisão segue só com regras versionadas). Endpoints exatos pendentes do sync upstream (P3 — `integrations/techlab-ai/openapi.json` ainda vazio). |
| **COMM** | Capability `document_composition` (Template Studio — compõe/edita copy de mensagem a partir de brief + contexto da empresa). Síncrono com circuit breaker; degrada graciosamente (CRUD de template/roteamento/disparo intactos). Endpoints exatos pendentes do sync upstream (P3 — `integrations/techlab-ai/openapi.json` ainda vazio). |
| **INTL** | Capabilities `knowledge` (embeddings + recuperação/composição RAG sobre evidência do Elasticsearch) + `orchestration` (composição da resposta do AI Copilot). Síncrono com circuit breaker; degrada para recuperação-apenas em falha (resposta marcada `nao_fundamentada`/degradada, nunca alucina fato fundamentado). `analytics` é pós-MVP. Endpoints exatos pendentes do sync upstream (P3 — `integrations/techlab-ai/openapi.json` ainda vazio). |

### How DTOs are generated

The Java DTOs for TechLab AI requests/responses are **not hand-written**. They are auto-generated from `integrations/techlab-ai/openapi.json` via `openapi-generator-cli` during the scaffold step. The output lives at `backend/services/<svc>/src/main/gen/techlabai/dtos/` and is regenerated whenever the source SHA is updated.

### CI contract validation

A CI job verifies that the locally pinned `openapi.json` is consistent with the version exposed by the running Docker image. Drift between the contract and the running service blocks the merge.

### Updating the pinned SHA

```bash
python scripts/sync-techlab-ai.py --target-sha <new-sha>
# 1. fetches techlab-ai at <new-sha>
# 2. updates integrations/techlab-ai/ snapshot (docs + openapi.json)
# 3. updates project-context.json.ai.techlabAi.sourceSha
# 4. re-runs openapi-generator-cli to refresh DTOs
# 5. appends entry to project-journal.md
```

---

## Hexagonal -- mandatory package structure (each BE microservice)

Base package: `com.journeyos.<module>` (e.g.: `com.journeyos.wrks`).

```
com.journeyos.<module>/
├── api/
│   ├── controller/          # @RestController
│   ├── dto/                 # Java records (request/response)
│   └── exception/           # @RestControllerAdvice + ProblemDetail (RFC 7807)
├── application/
│   ├── service/             # @Service -- use cases (@Transactional ONLY here)
│   └── port/
│       ├── in/              # Inbound (use cases)
│       └── out/             # Outbound (repos, clients)
├── domain/
│   ├── model/               # POJOs/records -- ZERO Spring/JPA
│   └── service/             # Domain services -- ZERO Spring
└── infrastructure/
    ├── clients/             # @FeignClient
    ├── config/              # @Configuration (includes DomainServiceConfig)
    ├── messaging/{producer,consumer}/
    ├── persistence/{entity,repository,adapter}/
    └── security/            # Spring Security filters, MDC
```

---

## Non-negotiable rules (ArchUnit enforced in `:<service>:architectureCheck`)

```
RULE-01  domain.* does not import org.springframework
RULE-02  domain.* does not import jakarta.persistence
RULE-03  @Transactional only in application.service
RULE-04  api.* does not depend on infrastructure.*
RULE-05  infrastructure.* does not depend on api.*
RULE-06  @FeignClient only in infrastructure.clients

RULE-08  spring.jpa.open-in-view=false mandatory
RULE-09  mandatory base package: com.journeyos.<module>
```

If `./gradlew :<service>:architectureCheck` fails → **do not commit**, fix first.

---

## Migrations (CENTRALIZED in `journey-os-migrations`)

- All migrations for ALL schemas live in `backend/journey-os-migrations/`.
- Naming: `V<N>__<module>_<description>.sql`. Schema-aware: each V indicates which schema it applies to (in path: `db/migration/global/V*.sql`).
- Individual microservices use `spring.jpa.hibernate.ddl-auto=validate` (schema prepared by `journey-os-migrations`).
- **Local dev:** run `./gradlew :journey-os-migrations:bootRun` FIRST; then the other services.

---

## Essential commands

```bash
# Build a service
./gradlew :<service>:build

# Unit tests (fast, no Docker)
./gradlew :<service>:test

# ArchUnit -- BLOCKING -- run before each commit
./gradlew :<service>:architectureCheck

# Integration tests (Testcontainers, requires Docker)
./gradlew :<service>:integrationTest

# Full BE monorepo
./gradlew build

# Local infra
docker compose -f docker/docker-compose.dev.yml up -d

# Frontend (in /frontend folder)
npx nx serve journey-os-web                 # dev server
npx nx build journey-os-web                 # prod build
npx nx affected:test                     # tests affected by diff
npx nx affected:lint

# TechLab AI (Docker image — pinned to source SHA in project-context.json)
docker run --rm -p 8090:8090 \
  -e TECHLAB_AI_JWT_ENABLED=false \
  -e TECHLAB_AI_ANTHROPIC_API_KEY=$ANTHROPIC_API_KEY \
  ghcr.io/DaniloAmaral-Dev/techlab-ai:latest                       # service entry: http://localhost:8090

```

---

## AI Pipeline -- per module

The pipeline operates per **MODULE** (WRKS/LEAD/JRNY/ASST/COMM/SALE/INTL/GWY/REG/MIG). There are **two complementary layers**:

```
┌─ LAYER 1 — ARCHITECT (creation of a NEW microservice, run once)
│   /be-architect-vision      → docs 01-06 + ADR skeleton
│   /be-architect-specs       → contracts (api / data-model / events / integration)
│   /be-architect-backlog     → atomic issues <MODULE>-NNN + plan-<MODULE>.md + generator-config.yml
│   /be-architect-scaffold    → calls scripts/be-module-generator.py (Spring Boot)
│   /be-architect-discovery   → reverse engineering of existing microservice
│   /be-architecture-autopilot <MODULE> → chains vision→specs→specs-validate→backlog→scaffold
│                                          (STOPS at scaffold; logs each step to
│                                          plans/architecture-master-plan.md; checkpoints + --resume)
│
├─ LAYER 2 — EXECUTION (iterative cycle to evolve the module)
│   VO → PLANNER → VO → IMPLEMENTER (1 priority) → VO → ...
│   /be-validator <MODULE>    → sole entry point; BASELINE or DECISION mode
│   /be-planner   <MODULE>    → triggered by VO when strategy is needed
│   /be-implement <MODULE> P  → triggered by VO; ONE priority at a time
│   /be-autopilot <MODULE>    → orchestrator chaining VO+Planner+Implement with checkpoints
│
└─ LAYER 3 — Python SCRIPTS (in scripts/, invoked by commands)
    be-module-generator.py     — document-driven microservice generator
    be-entity-generator.py     — domain + entity + repo + service + ctrl + DTO via data-model.md
    be-migration-generator.py  — Flyway SQL via data-model.md
    be-bdd-generator.py        — Cucumber step stubs via .feature
    be-infra-generator.py      — infra files
    be-scaffold.py             — files via plan-<ISSUE>.md
    be-file-guard.py           — protection of critical files
    apply_file_updates.py      — patcher utility
```

### Frontend commands (mirror of backend)

```bash
# Architect (NEW module — 5 steps)
/fe-architect-vision         <MODULE>
/fe-architect-specs          <MODULE>
/fe-architect-specs-validate <MODULE>    # EARS gate (C4): valida critérios EARS em SPEC-01..07 + cobertura→Gherkin
/fe-architect-backlog        <MODULE>
/fe-architect-scaffold       <MODULE>
# OR (steps 1-5 + e2e gate in one shot)
/fe-architecture-autopilot <MODULE>      # chains vision→specs→specs-validate→backlog→scaffold→e2e-validate,
                                         # STOPS at e2e-validate, logs to frontend architecture-master-plan.md

# Execution (same cycle as BE)
/fe-validator <MODULE>
/fe-planner   <MODULE>
/fe-implement <MODULE> <P>

# Pipeline per FEATURE (new feature in existing module)
/fe-feature-architect-discover      <MODULE> <feature-slug>
/fe-feature-architect-from-prototype <MODULE> <feature-slug> --source=prototipo/prototype/...
/fe-feature-architect-spec-delta    <MODULE> <feature-slug>
/fe-feature-architect-backlog       <MODULE> <feature-slug>
/fe-feature-architect-scaffold      <MODULE> <feature-slug>

# Meta-orchestrator (automates pipelines)
/fe-autopilot <MODULE> <feature-slug>    # Pipeline A (create feature)
/fe-autopilot <MODULE>-NNN               # Pipeline B (resolve issue)
```

### Recommended flow for a new module (from scratch)

```
1. /be-architect-vision  <MODULE>     → docs/architecture/backend/services/<svc>/01..06.md + adr/
2. /be-architect-specs   <MODULE>     → contracts/ (api, data-model, events, techlab-ai integration)
3. /be-architect-backlog <MODULE>     → issues/<MODULE>-NNN.md + plans/plan-<MODULE>.md + <svc>/generator-config.yml
4. /be-architect-scaffold <MODULE>    → backend/services/<svc>/ (Spring Boot skeleton)
   OR (steps 1-4 in one shot)
   /be-architecture-autopilot <MODULE>  → chains vision→specs→specs-validate→backlog→scaffold,
                                          STOPS at scaffold, logs to architecture-master-plan.md
5. /be-validator <MODULE>             → enters BASELINE; generates service README
6. /be-planner   <MODULE>             → creates initial plan (if not yet existing)
7. /be-implement <MODULE> P1, P2, ... → each priority, with VO between them
   OR
   /be-autopilot <MODULE>             → automatic orchestrator with checkpoints
```

### Canonical outputs

- Plans: `docs/architecture/backend/plans/plan-<MODULE>.md` (BE) and `docs/architecture/frontend/plans/plan-<MODULE>.md` (FE)
- Operational README: `backend/services/<service>/README.md`
- Per-service spec: `docs/architecture/backend/services/<service>/{contracts,diagrams,execution,tests}/`
- Issues: `docs/architecture/{backend,frontend}/issues/<MODULE>-NNN.md`
- Project ADRs: `docs/architecture/backend/adr/ADR-NNN-*.md`
- Transversal standards: `docs/architecture/backend/standards/*.md`

---

## Reference documents (read before implementing)

| Document | Contains |
|---|---|
| `docs/architecture/backend/standards/hexagonal-patterns.md` | Ports & Adapters, boundaries, ArchUnit rules |
| `docs/architecture/backend/standards/java-conventions.md` | Lombok, SLF4J, DI, JPA, naming, validation |
| `docs/architecture/backend/standards/snippets.md` | Snippets reference (ports, adapters, services, JMS, Feign, tests) |
| `docs/architecture/backend/standards/platform-patterns.md` | JMS Artemis, Feign+Resilience4j, centralized Flyway, MDC, Saga |
| `docs/architecture/backend/standards/testing-conventions.md` | Pyramid, Testcontainers, Cucumber, Pact |
| `docs/architecture/backend/standards/services-catalog.md` | Catalog of microservices + canonical packages + events + Feign clients |
| `docs/architecture/backend/standards/service-spec-authoring.md` | How to write per-service SPECs (Phase 1-3) |
| `docs/architecture/backend/standards/api-mock-convention.md` | Mock profile, /api/v0/, fixtures |

| `docs/architecture/frontend/standards/nx-boundaries.md` | Nx tags, allowed directions, ESLint config |
| `docs/architecture/frontend/standards/access-layer-contracts.md` | AuthSession, AccessDecision |
| `docs/architecture/shared/blueprint-core.md` | Mental model: app + modules + shared, golden rules |

| `docs/architecture/integrations/techlab-ai-integration.md` | Contract Java BE ↔ TechLab AI (endpoints, schemas, fallback, retry, DTO generation) |
| `integrations/techlab-ai/docs/SDD.md` | Upstream Software Design Document (read-only, synced from source SHA) |
| `integrations/techlab-ai/openapi.json` | OpenAPI spec (source for Java DTO generation via openapi-generator-cli) |

---

## Never do this

- **Never** use base package different from `com.journeyos.<module>`
- **Never** introduce "tool/PREFIX" concept -- here only MODULE exists
- **Never** put `@Transactional` in controller, repository or adapter
- **Never** return JPA `@Entity` directly from controller -- always DTO record
- **Never** use `@Autowired` in field -- always `@RequiredArgsConstructor`
- **Never** use `System.out` -- `@Slf4j` via Lombok
- **Never** hardcode secret -- use `${VAR_NAME}` in `application.yml`
- **Never** commit with `ddl-auto: create|update` -- always `validate`
- **Never** use `@Testcontainers` + `@Container` -- singleton container pattern (static initializer)
- **Never** forget `DomainServiceConfig.java` (domain services are POJOs and need `@Bean`)
- **Never** run a microservice before `journey-os-migrations`
- **Never** call an AI provider (Anthropic, OpenAI, Vertex AI, Ollama, NVIDIA NIM, etc.) directly from the Java BE -- always via TechLab AI HTTP
- **Never** modify content under `/integrations/techlab-ai/` -- it is a read-only snapshot synced from the upstream repo at the pinned SHA. Run `python scripts/sync-techlab-ai.py --target-sha <sha>` to update.
- **Never** edit generated DTOs under `backend/services/<svc>/.../gen/techlabai/` -- they are auto-generated from `integrations/techlab-ai/openapi.json` by `openapi-generator-cli`.

---

## Git conventions

Valid commit scopes:
`wrks, lead, jrny, asst, comm, sale, intl, gwy, reg, mig, web, libs, docs, infra, deps`.

Permanent branches: `dev`, `release`, `prod`. Never direct push -- always Pull Request.
