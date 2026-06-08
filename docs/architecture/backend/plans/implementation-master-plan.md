# Implementation Master Plan — Journey OS Backend

> Rastreia a camada de **execução (Layer 2 — Implement)** de cada módulo, do **baseline** à
> **maturidade ≥ 80** com checklist 100% DONE. É o documento-irmão do
> [`architecture-master-plan.md`](./architecture-master-plan.md): aquele cobre o Architect
> (vision→specs→backlog→scaffold); **este cobre o ciclo validator-driven** que evolui o serviço.
>
> Atualizado a cada transição de etapa pelo `/be-autopilot <MODULO> --implement` (e pelos
> sub-commands `/be-validator`, `/be-planner`, `/be-implement` quando rodados isoladamente).
> **Não é fonte da verdade** — é um espelho de progresso. A verdade são:
> os `README.md` operacionais de cada serviço (`backend/services/<svc>/README.md`),
> os `plan-<MODULO>.md` (estratégia por prioridade) e o código em `backend/services/`.
>
> **Pré-condição:** Layer 1 (Architect) 100% concluído para os 10 módulos — ver
> `architecture-master-plan.md`. ✅ Todos scaffoldados em 2026-06-04/05.

---

## Ciclo de execução (Layer 2) — recordatório

```
B1 BASELINE  (be-validator Modo 1)  → consolida estado real, gera README, calcula score
B2 DECISÃO   (be-validator Modo 2)  → PLANNER | IMPLEMENTADOR | VALIDAR | ENCERRAR
B3 PLANNER   (be-planner)           → plan-<MODULO>.md (prioridades P1..Pn) — já existem
B4 IMPLEMENT (be-implement <M> P)   → UMA prioridade por vez, na ordem do plano (escreve código)
B5 VALIDAÇÃO (be-validator Modo 3)  → gates build/test/ArchUnit/BDD + delta README
        └── loop B2→B5 até checklist 100% DONE e score ≥ 80 (safety cap = 5 iter/invocação)
```

Orquestrador: `/be-autopilot <MODULO> --implement` encadeia B1→B5 com checkpoints em
`tmp/be-autopilot/<MODULO>/state.json` (retomável via `--resume`).

---

## ⚠️ Bloqueador transversal — gates de validação diferidos (toolchain Gradle ausente)

O ambiente **não tem toolchain Gradle** (sem `gradlew`/wrapper, sem `gradle` no PATH —
ver `[[gradle-toolchain-absent]]`). Consequências para a Layer 2:

- **B4 (be-implement) NÃO roda Gradle** — escreve código e faz verificação local (leitura/diff).
  Logo, a **escrita de código de todas as prioridades não está bloqueada**.
- **B5 (be-validator Modo 3) DEPENDE dos gates** `:<svc>:test`, `:<svc>:architectureCheck`,
  `:<svc>:integrationTest`, `*CucumberIT*`. Sem toolchain, **nenhuma prioridade pode ser
  formalmente fechada (score-validada)** — o fechamento fica **diferido**.

**Estratégia adotada (code-first + gate-replay em lote):**
1. Rodar B1 (baseline) e B4 (implement) de todas as prioridades — produzem código + README.
2. Marcar cada prioridade como `CODE-DONE (gate diferido)` até o toolchain existir.
3. Quando o Gradle estiver disponível, rodar **um único replay em lote**:
   ```bash
   python scripts/preflight.py            # confirma toolchain runnable
   python scripts/be-gates-replay.py --run --update   # executa gates diferidos do ledger
   # cobertura total de uma vez (todos os subprojetos):
   ./gradlew spotlessApply compileJava
   ./gradlew test --tests "*.architecture.*"
   ./gradlew test --tests "*CucumberIT*"
   ./gradlew integrationTest
   ```
4. Só então promover `CODE-DONE → DONE` e recalcular os scores (ver
   `[[toolchain-preflight-ledger]]`).

### Ledger de gates de implementação diferidos

> Append-only. Cada prioridade implementada sem gate executado entra aqui com o comando exato.

| Data | Módulo | Prioridade | Gate diferido | Comando de recuperação | Status |
|---|---|---|---|---|---|
| — | — | — | — | _(preenchido ao implementar cada P)_ | — |

---

## Ordem de execução por ondas (respeita dependências)

> Dependências extraídas dos `plan-<MODULO>.md` (seção «Dependências externas») e do
> `architecture-master-plan.md`. A persistência de qualquer módulo standard (P3) **exige
> que MIG já tenha provisionado os schemas** (`journeyos_global` + `emp_*`).

| Onda | Módulos | Pré-requisito de início | Paralelizável? |
|------|---------|--------------------------|----------------|
| **0 — Infra** | **MIG** → **REG** → **GWY** | nenhum (fundação) | MIG primeiro; REG/GWY após MIG P1-P2 |
| **1 — Fundação** | **WRKS** | MIG (schemas) + REG (Eureka) | não (todos dependem dele) |
| **2 — Núcleo de domínio** | **LEAD** ∥ **ASST** | WRKS (multi-tenancy, AccessDecision) | sim (sem dep mútua) |
| **3 — Roteamento** | **JRNY** | WRKS + LEAD + ASST | não |
| **4 — Comunicação** | **COMM** | WRKS + LEAD + JRNY | não |
| **5 — Receita** | **SALE** | WRKS + LEAD + JRNY + COMM | não |
| **6 — Inteligência** | **INTL** | todos (consumidor transversal de eventos) | não (último) |

```
        ┌─────────── Onda 0 (infra) ───────────┐
        MIG ──► REG ──► GWY
          │
          ▼
        WRKS  ── Onda 1 (fundação de identidade)
          │
     ┌────┴────┐
     ▼         ▼
   LEAD      ASST     ── Onda 2 (núcleo, paralelo)
     │         │
     └────┬────┘
          ▼
        JRNY            ── Onda 3
          ▼
        COMM            ── Onda 4
          ▼
        SALE            ── Onda 5
          ▼
        INTL            ── Onda 6 (transversal)
```

---

## Visão Geral — Status de Execução por Módulo

Legenda: ⬜ pendente · 🔄 em andamento · 🟡 CODE-DONE (gate diferido) · ✅ DONE (gate verde) · 🚫 bloqueado · **N/A** não se aplica (prioridade inexistente no plano do módulo)

| Onda | Módulo | B1 | P1 | P2 | P3 | P4 | P5 | P6 | P7 | P8 | P9 | Gates B5 | Score | Estado |
|---|---|----|----|----|----|----|----|----|----|----|----|----|----|----|
| 0 | **MIG**  | ✅ | ⬜ | ⬜ | ⬜ | N/A | ⬜ | N/A | ⬜ | N/A | N/A | 🚫 diferido | 28 | 🔄 |
| 0 | **REG**  | ✅ | 🟡 | 🔄 | 🔄 | ⬜ | N/A | N/A | N/A | N/A | N/A | 🚫 diferido | 58 | 🔄 |
| 0 | **GWY**  | ✅ | ⬜ | ⬜ | N/A | ⬜ | ⬜ | ⬜ | ⬜ | N/A | N/A | 🚫 diferido | 25 | 🔄 |
| 1 | **WRKS** | ✅ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | N/A | 🚫 diferido | 24 | 🔄 |
| 2 | **LEAD** | ✅ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | 🚫 diferido | 22 | 🔄 |
| 2 | **ASST** | ✅ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | N/A | 🚫 diferido | 32 | 🔄 |
| 3 | **JRNY** | ✅ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | N/A | 🚫 diferido | 27 | 🔄 |
| 4 | **COMM** | ✅ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | N/A | 🚫 diferido | 25 | 🔄 |
| 5 | **SALE** | ✅ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | 🚫 diferido | 30 | 🔄 |
| 6 | **INTL** | ✅ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | 🚫 diferido | 31 | 🔄 |
| | **Total** | 10/10 | 0/10 | 0/10 | 0/9 | 0/9 | 0/9 | 0/8 | 0/9 | 0/7 | 0/3 | — | — | **0/74** |

> `B1` = baseline (be-validator Modo 1) executado. Células `N/A` = a prioridade não existe no
> `plan-<MODULO>.md` daquele módulo (infra/gateway têm conjuntos reduzidos). `Gates B5 🚫 diferido`
> enquanto não houver toolchain Gradle (ver bloqueador acima). Mapa serviço/pacote: ver cada seção
> de módulo. Todos os `plan-<MODULO>.md` já existem (gerados no Architect A3).
>
> **Total por coluna** = nº de módulos em que a prioridade existe (denominador) → 74 prioridades no total.

---

## Pré-condições globais de execução

- [ ] **MIG operacional primeiro** — `./gradlew :journey-os-migrations:bootRun` provisiona
      `journeyos_global` + extensões antes de qualquer outro serviço subir (CLAUDE.md).
- [ ] **Infra local de pé** — `docker compose -f docker/docker-compose.dev.yml up -d`
      (PostgreSQL 15+, Kafka/Artemis, Redis/Valkey, Elasticsearch, Keycloak).
- [ ] **REG (Eureka) de pé** — pré-condição de registro para WRKS+ (port 8761).
- [ ] **Toolchain Gradle disponível** 🚫 — pré-condição dos gates B5 (ver bloqueador acima).
- [ ] **TechLab AI sync (P3 global)** 🚫 bloqueado — aguarda primeiro commit upstream.
      Afeta integrações com IA de LEAD/ASST/JRNY/COMM/INTL (degradação graciosa já especificada;
      `openapi.json` vazio → DTOs não geráveis ainda). Não bloqueia P1/P2/P3 desses módulos.

### Modelo de score de maturidade (be-validator §9)

Dimensões consolidadas no README §9 de cada serviço, score 0–100:

| Dimensão | Significado | Fechada por (tipicamente) |
|---|---|---|
| STRUCTURAL | esqueleto hexagonal, RULE-01..09 verdes | P1 |
| FUNCTIONAL | golden path + CRUD do agregado âncora | P2, P3 |
| INTEGRATION | Feign clients, TechLab AI, eventos | P4, P6 |
| OBSERVABILITY | MDC, métricas, health/readiness | P7 |
| RESILIENCE | circuit breaker, retries, idempotência | P5, P9 |
| MULTI-EMPRESA | `EmpresaContextHolder.require()` (RULE-07) | P5 |

Faixas: `0–39 Inicial` · `40–59 Parcial` · `60–79 Consistente` · `80–100 Maduro`.
**Definition of Done de um módulo:** checklist 100% DONE **e** score ≥ 80 **e** ArchUnit verde.

---

## Onda 0 — Infraestrutura

### Módulo MIG — `journey-os-migrations`

> Pacote `com.journeyos.mig` · infra · **nenhuma dependência** · fonte: `plan-MIG.md`
> Bloqueia a persistência (P3) de **todos** os módulos standard.

- [x] **B1 Baseline** — README operacional + score inicial · **2026-06-05** · score **28 (Inicial)** · runner Flyway/layout schema-aware MISSING; Flyway ausente do build + `enabled:false`
- [ ] **P1 — Base, Flyway config e bootstrap** · MIG-001/002 · aceite: serviço sobe, Flyway aplica V1
- [ ] **P2 — Layout schema-aware, runner e tenants** · MIG-003/004 · reorganizar `db/migration/{global,empresa}/` (adiado do scaffold)
- [ ] **P3 — Idempotência/concorrência + validação de extensões** · MIG-005/006 · 5 extensões (uuid-ossp/pgcrypto/pg_trgm/unaccent/vector)
- [ ] **P5 — Security** · MIG-007 · credenciais via `${VAR}`, sem segredo hardcoded
- [ ] **P7 — Observability** · MIG-008 · health/readiness, log de migração
- [ ] **Integração** · INT-MIG-001/002
- [ ] **B5 gates** 🚫 diferido · `./gradlew :journey-os-migrations:test --tests "*.architecture.*"`
- [ ] **DoD** · checklist 100% + score ≥ 80

### Módulo REG — `journey-os-service-registry`

> Pacote `com.journeyos.reg` · infra (registry/Eureka, port 8761) · fonte: `plan-REG.md`

- [x] **B1 Baseline** · 2026-06-05 · README operacional gerado · score 58 (Parcial) · 2/5 issues DONE
- [🟡] **P1 — Scaffold + base config** · REG-001/002 · Eureka server sobe (8761, self-register off, actuator) · CODE-DONE, gate diferido
- [🔄] **P2 — Profiles + self-preservation** · REG-003 · PARTIAL: overlay `default` ok; faltam `local`/`prod` + hostname
- [🔄] **P3 — Observability + health** · REG-004 · PARTIAL: actuator health/prometheus ok; falta logging service-tagged
- [ ] **P4 — Architecture guard** · REG-005 · MISSING: ArchitectureTest genérico não assere RULE-09 (base package)
- [ ] **B5 gates** 🚫 diferido · BDD N/A (registry)
- [ ] **DoD** · checklist 100% + score ≥ 80

### Módulo GWY — `journey-os-api-gateway`

> Pacote `com.journeyos.gwy` · infra (gateway reativo/WebFlux, port 8080) · fonte: `plan-GWY.md`
> Sem P3 (persistência) nem P8 (BDD-domínio).

- [x] **B1 Baseline** — README operacional + score inicial · **2026-06-05** · score **25 (Inicial)** · scaffold reativo (boot+OAuth2 RS+Eureka+Actuator/Prometheus+ArchUnit) presente; rotas `lb://` vazias, sem filtros de borda/tenant/CORS/rate-limit; `issuer-uri` Keycloak diverge do contrato (JWKS WRKS)
- [ ] **P1 — Bootstrap + roteamento** · GWY-001..003 · rotas para serviços downstream
- [ ] **P2 — Pipeline de borda** · GWY-004..006 · filtros globais, correlação, ProblemDetail
- [ ] **P4 — Roteamento downstream + resiliência** · GWY-007/008 · circuit breaker, fallback
- [ ] **P5 — Segurança** · GWY-009/010 · auth filter (JWT/JWKS), sem bypass · INT-GWY-001..004
- [ ] **P6 — Rate-limiting distribuído** · GWY-011 · Redis/Valkey
- [ ] **P7 — Observabilidade + health** · GWY-012 · métricas de borda, readiness
- [ ] **B5 gates** 🚫 diferido · `./gradlew :journey-os-api-gateway:test --tests "*.architecture.*"`
- [ ] **DoD** · checklist 100% + score ≥ 80

---

## Onda 1 — Fundação de identidade

### Módulo WRKS — `wrks-service`

> Pacote `com.journeyos.wrks` · standard · **dep:** MIG, REG · **dependentes:** TODOS · fonte: `plan-WRKS.md`
> 18 issues + 6 INT. IAM em `journeyos_global`. TechLab AI: **nenhuma**.

- [x] **B1 Baseline** — README operacional regenerado · **2026-06-05** · score **24 (Inicial)** · scaffold de 168 arquivos: estrutura hexagonal completa + cross-cutting REAL (TenantContextHolder.require()/Filter, AccessContextHolder/DataScope, GlobalExceptionHandler RFC-7807, DomainServiceConfig 6 beans, ArchUnit RULE-01..06) + `application.yml` conforme (open-in-view=false RULE-08, ddl-auto=validate, Flyway off) + DDL IAM completa (11 tabelas, V1); **business logic nula** (ports.in vazios, services vazias, domain services TODO, controllers sem endpoints, adapters lançam UnsupportedOperationException, MigrationTriggerClient placeholder inválido, BDD PendingException). 0/8 prioridades; 0/24 issues DONE.
- [ ] **P1 — Scaffold + contratos mínimos** · WRKS-001/002/003 + INT-WRKS-001 · aceite: health 200, ProblemDetail, RULE-09
- [ ] **P2 — Orquestração de identidade (golden path)** · WRKS-004/005/006 · login OIDC→JWT escopado, refresh rotation, saga provisionamento empresa
- [ ] **P3 — Persistência + migrations** · WRKS-007/008 · IAM em `journeyos_global`, seeds canônicos (coordenar V0001 com MIG)
- [ ] **P4 — Integrações externas** · WRKS-009/010 + INT-WRKS-004 · Keycloak + MIG com resiliência (Keycloak down → 502 sem bypass)
- [ ] **P5 — Security + multi-tenancy** · WRKS-011..014 + INT-WRKS-002/003 · JWT/JWKS, AccessDecision+cache, anti-escalonamento, RULE-07
- [ ] **P6 — Messaging + auditoria** · WRKS-015/016 + INT-WRKS-005/006 · outbox + sink auditoria idempotente + Elastic
- [ ] **P7 — Observability + health** · WRKS-017 · MDC, métricas `journey-os_iam_session_*`, readiness
- [ ] **P8 — BDD end-to-end** · WRKS-018 · 4 features, `*CucumberIT*` 0 failed, cobertura SHALL (D-218)
- [ ] **B5 gates** 🚫 diferido · `:wrks-service:test`/`architectureCheck`/`*CucumberIT*`
- [ ] **DoD** · checklist 100% + score ≥ 80 + RULE-07 enforce

---

## Onda 2 — Núcleo de domínio (LEAD ∥ ASST — paralelo)

### Módulo LEAD — `lead-service`

> Pacote `com.journeyos.lead` · standard · **dep:** WRKS · fonte: `plan-LEAD.md`
> 18 issues + 5 INT. TechLab AI: `qualification` (assist + fallback determinístico).

- [x] **B1 Baseline** · 2026-06-05 · README operacional gerado (substitui stub "tool") · score **22 (Inicial)** · scaffold hexagonal completo + V1 migration (12 tabelas) + multi-tenancy; lógica de negócio ausente (services/domain/ports vazios, adapters em `UnsupportedOperationException`) · 0/23 issues DONE
- [ ] **P1 — Scaffold + contratos mínimos** · superfície REST, domínio puro, ProblemDetail
- [ ] **P2 — Orquestração do domínio (golden path)** · âncora `lead.qualificado`
- [ ] **P3 — Persistência + migrations** · 12 tabelas, schema `empresa`
- [ ] **P4 — Integrações externas** · TechLab AI `qualification` (degrada p/ cálculo determinístico) · INT-LEAD-003 🚫 (TechLab sync)
- [ ] **P5 — Security + multi-tenancy + LGPD** · RULE-07, isolamento cross-empresa
- [ ] **P6 — Messaging** · produtores/consumidores, Maturity Score 6D
- [ ] **P7 — Observability + health**
- [ ] **P8 — BDD end-to-end** · 3 features (lead-capture/qualification/maturity-score)
- [ ] **P9 — Hardening** · SLAs, retries, circuit breaker
- [ ] **B5 gates** 🚫 diferido · **DoD** · checklist 100% + score ≥ 80

### Módulo ASST — `asst-service`

> Pacote `com.journeyos.asst` · standard · **dep:** WRKS · fonte: `plan-ASST.md`
> 16 issues + 6 INT. TechLab AI: `document_composition` (Asset Studio).

- [x] **B1 Baseline** — README operacional + score inicial · **2026-06-05** · score **32 (Inicial)** · esqueleto hexagonal completo + infra multi-tenancy/messaging/idempotência presentes; lógica 100% stub (UseCases vazios, adapters lançam `UnsupportedOperationException`, domínio TODO)
- [ ] **P1 — Scaffold + domínio + API CRUD** · agregado `Asset`
- [ ] **P2 — Golden path (versão → aprovação → publicação)** · âncora `asset.versao.publicada`, versionamento imutável + state machine
- [ ] **P3 — Persistência + migrations** · 4 tabelas, schema `empresa` (sem `empresa_id`)
- [ ] **P4 — Integrações (TechLab AI + Elastic)** · `document_composition` + Asset Intelligence (tagging) · INT-ASST 🚫 parcial (TechLab sync)
- [ ] **P5 — Security + multi-tenancy + idempotência** · RULE-07
- [ ] **P6 — Messaging**
- [ ] **P7 — Observability + health**
- [ ] **P8 — BDD end-to-end** · 3 features (creation/versioning/approval-workflow)
- [ ] **B5 gates** 🚫 diferido · **DoD** · checklist 100% + score ≥ 80

---

## Onda 3 — Roteamento

### Módulo JRNY — `jrny-service`

> Pacote `com.journeyos.jrny` · standard · **dep:** WRKS, LEAD, ASST · fonte: `plan-JRNY.md`
> 16 issues + 6 INT. TechLab AI: `orchestration` (assist opcional + fallback determinístico).

- [x] **B1 Baseline** — README operacional + score inicial · **2026-06-05** · score **27 (Inicial)** · esqueleto hexagonal completo + infra transversal real (multi-tenancy/security/MDC/audit) + migration 5 tabelas + ArchUnit/3 features; lógica de negócio 100% stub; ~~drift entity↔migration~~ **RESOLVIDO 2026-06-05** (5 entities alinhadas à DDL de `V1` + repos `findByEmpresaId(UUID)`; `ddl-auto=validate` ok — confirmação formal diferida ao gate Gradle)
- [ ] **P1 — Scaffold + domínio + Journey Builder** · jornada/estágio/regra
- [ ] **P2 — Routing Engine (golden path)** · âncora `lead.roteado`, decisão determinística + decision log imutável
- [ ] **P3 — Persistência + migrations** · 5 tabelas (uniques parciais ATIVA, ordem)
- [ ] **P4 — Integrações (TechLab AI + ASST + Elastic)** · `orchestration` (degrada p/ regras versionadas) · INT-JRNY 🚫 parcial
- [ ] **P5 — Security + multi-tenancy + idempotência** · RULE-07
- [ ] **P6 — Messaging** · consome `lead.qualificado`/`asset.versao.publicada`; produz `jornada.*`/`estagio.transicionado`
- [ ] **P7 — Observability + health**
- [ ] **P8 — BDD end-to-end** · 3 features (30 cenários)
- [ ] **B5 gates** 🚫 diferido · **DoD** · checklist 100% + score ≥ 80

---

## Onda 4 — Comunicação

### Módulo COMM — `comm-service`

> Pacote `com.journeyos.comm` · standard · **dep:** WRKS, LEAD, JRNY · fonte: `plan-COMM.md`
> 16 issues + 6 INT. TechLab AI: `document_composition` (Template Studio).

- [ ] **B1 Baseline**
- [ ] **P1 — Scaffold + domínio + API de template**
- [ ] **P2 — Golden path (rotear → enfileirar → enviar)** · âncora `journey-os.mensagem.enviada`, CanalEnvioPort provedor-agnóstico
- [ ] **P3 — Persistência + migrations** · 5 tabelas, schema `empresa` (sem `empresa_id`)
- [ ] **P4 — Integrações (TechLab AI + canais + ASST/Elastic)** · `document_composition` · webhooks por assinatura de provedor · INT-COMM-003 🚫 parcial
- [ ] **P5 — Security + multi-tenancy + idempotência** · tenant resolvido da mensagem, RULE-07
- [ ] **P6 — Messaging**
- [ ] **P7 — Observability + health**
- [ ] **P8 — BDD end-to-end** · 3 features (message-dispatch/template-rendering/channel-routing)
- [ ] **B5 gates** 🚫 diferido · **DoD** · checklist 100% + score ≥ 80

---

## Onda 5 — Receita

### Módulo SALE — `sale-service`

> Pacote `com.journeyos.sale` · standard · **dep:** WRKS, LEAD, JRNY, COMM · fonte: `plan-SALE.md`
> 19 issues + 5 INT. **Sem TechLab AI no MVP** (atribuição/LTV determinísticos).

- [x] **B1 Baseline** — README operacional + score inicial · **2026-06-05** · score **30 (Inicial)** · esqueleto hexagonal completo (119 arquivos Java, 9 agregados, 5 superfícies REST, 13 ports-out, Feign WRKS, 7 producers + 4 consumers, idempotência `ProcessedEvent`) + infra transversal real (multi-tenancy/audit/data-scope/MDC/RFC-7807) + migration V1 (9 tabelas, NUMERIC(15,2)+moeda, CHECKs) + ArchUnit/3 features; **lógica de negócio 100% stub** (services/use cases vazios, domain services TODO, adapters em `UnsupportedOperationException`, DTOs TODO, BDD PendingException). Desvio: V1 local ao serviço (convenção = centralizada em journey-os-migrations). 0/9 prioridades · 0/24 issues DONE
- [ ] **P1 — Scaffold + API CRUD** · 6 agregados (Oportunidade/Oferta/Compra/ModeloAtribuicao/Campanha/Ltv)
- [ ] **P2 — Orquestração do domínio (âncora)** · âncora `compra.confirmada`, idempotência (id_externo+origem)
- [ ] **P3 — Persistência + migrations** · 9 tabelas, NUMERIC(15,2)+moeda, conservação de receita
- [ ] **P4 — Integrações externas** · SALE não processa pagamento (gateway externo)
- [ ] **P5 — Security + multi-tenancy + LGPD** · RULE-07
- [ ] **P6 — Messaging** · 7 eventos publicados (oportunidade.*/receita.atribuida/ltv.atualizado)
- [ ] **P7 — Observability + health**
- [ ] **P8 — BDD end-to-end** · 3 features (sales-pipeline/purchase-revenue/revenue-attribution)
- [ ] **P9 — Hardening**
- [ ] **B5 gates** 🚫 diferido · **DoD** · checklist 100% + score ≥ 80

---

## Onda 6 — Inteligência (transversal)

### Módulo INTL — `intl-service`

> Pacote `com.journeyos.intl` · standard · **dep:** todos (consumidor de eventos transversal) · fonte: `plan-INTL.md`
> 17 issues + 6 INT. TechLab AI: `knowledge` + `orchestration` (RAG fundamentado; `analytics` pós-MVP).

- [x] **B1 Baseline** — README operacional + score inicial · **2026-06-05** · score **31 (Inicial)** · esqueleto hexagonal completo (7 agregados, 3 superfícies REST, 13 ports-out, 2 Feign) + infra multi-tenancy/messaging/idempotência; lógica 100% stub; gaps de build (deps duplicadas, Kafka/Artemis ambíguo, `elastic-client-lib`/pgVector não wired)
- [ ] **P1 — Scaffold + API surface**
- [ ] **P2 — Copilot orchestration (RAG)** · âncora `journey-os.copilot.resposta.gerada`, RAG fundamentado (degrada p/ recuperação-apenas, nunca alucina)
- [ ] **P3 — Persistência + migrations** · 7 tabelas (no_conhecimento vector(1536) nullable; evento_indexado ledger)
- [ ] **P4 — Integrações externas** · TechLab AI `knowledge`+`orchestration` + Elastic (plataforma descentralizada) · INT-INTL-002 🚫 (TechLab sync)
- [ ] **P5 — Security + multi-tenancy** · multi-tenancy híbrida (PG schema-per-tenant + Elastic com discriminador empresa), RULE-07
- [ ] **P6 — Messaging** · consome eventos de JRNY/COMM/SALE; produz `copilot.resposta.gerada`
- [ ] **P7 — Observability + health**
- [ ] **P8 — BDD end-to-end** · 3 features (ai-copilot/knowledge-base/event-platform-analytics)
- [ ] **P9 — Hardening**
- [ ] **B5 gates** 🚫 diferido · **DoD** · checklist 100% + score ≥ 80

---

## Sequenciamento de integrações cross-módulo (golden-path de eventos)

> A ordem das ondas garante que, quando um módulo implementa seus consumidores (P6),
> o produtor do evento já existe. Cadeia canônica:

```
WRKS  empresa.provisionada / modelo.acesso.alterado
  └─► LEAD   lead.qualificado (+ score, segmento)
        ├─► JRNY   lead.roteado / jornada.publicada / estagio.transicionado
        │     └─► COMM   journey-os.mensagem.enviada
        │           └─► SALE   compra.confirmada / receita.atribuida / ltv.atualizado
        └─► ASST   asset.versao.publicada ──► JRNY (consome) / COMM (consome)
                                           └─► INTL (indexa tudo → copilot.resposta.gerada)
```

| Consumidor | Eventos consumidos | Produtor (onda) | INT issues |
|---|---|---|---|
| LEAD | empresa.provisionada, modelo.acesso.alterado | WRKS (1) | INT-LEAD-* |
| ASST | empresa.provisionada | WRKS (1) | INT-ASST-* |
| JRNY | lead.qualificado/score/segmento, asset.versao.publicada | LEAD, ASST (2) | INT-JRNY-* |
| COMM | jornada/estagio events, asset.versao.publicada | JRNY, ASST (3) | INT-COMM-* |
| SALE | lead.qualificado/score, compra/mensagem context | LEAD, COMM (4) | INT-SALE-* |
| INTL | todos os facts (journey/communication/revenue) | todas | INT-INTL-* |

---

## Resumo de contagem (prioridades + issues por módulo)

| Módulo | Prioridades | Issues func. | Issues INT | Total issues | Plan |
|--------|-------------|--------------|------------|--------------|------|
| MIG | 5 (P1,2,3,5,7) | 8 | 2 | 10 | ✅ |
| REG | 4 (P1–4) | 5 | 0 | 5 | ✅ |
| GWY | 6 (P1,2,4,5,6,7) | 12 | 4 | 16 | ✅ |
| WRKS | 8 (P1–8) | 18 | 6 | 24 | ✅ |
| LEAD | 9 (P1–9) | 18 | 5 | 23 | ✅ |
| ASST | 8 (P1–8) | 16 | 6 | 22 | ✅ |
| JRNY | 8 (P1–8) | 16 | 6 | 22 | ✅ |
| COMM | 8 (P1–8) | 16 | 6 | 22 | ✅ |
| SALE | 9 (P1–9) | 19 | 5 | 24 | ✅ |
| INTL | 9 (P1–9) | 17 | 6 | 23 | ✅ |
| **Total** | **74** | **145** | **46** | **191** | **10/10** |

---

## Referências de pipeline (Layer 2)

| Comando | Etapa | Pré-requisito |
|---------|-------|---------------|
| `/be-validator <M>` | B1 BASELINE | Scaffold executável (Layer 1 done) |
| `/be-validator <M>` | B2 DECISÃO | README consistente |
| `/be-planner <M>` | B3 | Baseline calculado (plan já existe) |
| `/be-implement <M> P<N>` | B4 | Plano com prioridade definida — UMA por vez |
| `/be-validator <M>` | B5 VALIDAÇÃO | Implementação concluída + **toolchain Gradle** 🚫 |
| `/be-autopilot <M> --implement` | B1→B5 | Encadeia tudo com checkpoints |
| `python scripts/be-gates-replay.py --run --update` | gate-replay | Toolchain disponível |

### Documentos de referência (ler antes de implementar)

- `plan-<MODULO>.md` — estratégia detalhada por prioridade (objetivo/issues/specs/sequência/aceite/riscos)
- `backend/services/<svc>/README.md` — fonte da verdade operacional (mantida pelo validator)
- `docs/architecture/backend/standards/{hexagonal-patterns,java-conventions,platform-patterns,testing-conventions}.md`
- `docs/architecture/backend/issues/<MODULO>-NNN.md` — critério de aceite atômico por issue

---

## Log cronológico da execução

> Append-only. Uma linha por transição de etapa do ciclo B1→B5 (por módulo/prioridade).
> Formato: `<ISO-8601> -- <MODULO> -- <etapa> -- <resultado> -- <notas>`

- 2026-06-05 -- (todos) -- plano-criado -- Implementation Master Plan gerado a partir do architecture-master-plan (Layer 1 100% concluído; Layer 2 não iniciada; gates B5 diferidos por ausência de toolchain Gradle)
- 2026-06-05 -- MIG -- B1 -- OK -- BASELINE (be-autopilot, escopo restrito a B1). README operacional regenerado (substitui stub genérico "tool"). Estado real: scaffold hexagonal presente; runner Flyway + layout schema-aware + fan-out por tenant MISSING; Flyway ausente do build.gradle.kts e `spring.flyway.enabled:false`. 0/5 prioridades (P1/P2/P3/P5/P7 pendentes). Score 28 (Inicial). Gates B5 não executados (toolchain Gradle ausente — diferido). Próxima ação sugerida: PLANNER→P1 (não executada — usuário pediu apenas BASELINE).
- 2026-06-05 -- GWY -- B1 -- OK -- BASELINE (be-autopilot, escopo restrito a B1). README operacional regenerado (substitui stub genérico que citava Artemis/Postgres/Keycloak/"tool"). Estado real: scaffold reativo executável (SecurityConfig OAuth2 RS + Eureka client + Actuator/Prometheus + ArchUnit RULE-01..06); rotas `lb://` VAZIAS, sem filtros de borda/correlação/anti-spoofing, sem tenant resolver/CORS/rate-limit, sem observabilidade por rota; `issuer-uri` aponta Keycloak (diverge do contrato JWKS via WRKS). 0/6 prioridades (P1/P2/P4/P5/P6/P7 pendentes). Score 25 (Inicial). Gates B5 não executados (toolchain Gradle ausente — diferido). Próxima ação sugerida: IMPLEMENTADOR→P1 (não executada — usuário pediu apenas BASELINE).
- 2026-06-05 -- REG -- B1 -- OK -- BASELINE (be-autopilot, escopo restrito a B1). README operacional regenerado (substitui stub genérico "tool"/Postgres+Artemis incorretos). Estado real: Eureka Server bootável na 8761, self-register off, actuator health/prometheus expostos — P1 (REG-001/002) CODE-DONE. P2/REG-003 PARTIAL (só overlay `default`; faltam local/prod + hostname); P3/REG-004 PARTIAL (falta logging service-tagged); P4/REG-005 MISSING (ArchitectureTest genérico não assere RULE-09; sem task `architectureCheck`). 2/5 issues DONE. Score 58 (Parcial). Gates B5 não executados (toolchain Gradle ausente — diferido). Próxima ação sugerida: IMPLEMENTADOR→P4/REG-005 (não executada — usuário pediu apenas BASELINE).
- 2026-06-05 -- ASST -- B1 -- OK -- BASELINE (be-autopilot, escopo restrito a B1). README operacional regenerado (substitui stub genérico "Journey OS tool"/Artemis/`t_<tenantId>`). Estado real: esqueleto hexagonal COMPLETO (api/application/domain/infrastructure/shared) + infra multi-tenancy (filter/holder/resolver/connection-provider/Hibernate config) + esqueleto de mensageria (4 producers + 2 consumers) + idempotência (`ProcessedEvent`) + 4 entidades/repos/adapters + ArchUnit (ArchitectureTest+CrossAspectArchTest); porém lógica 100% STUB — `*UseCase` interfaces vazias, `*Service` sem métodos, `*RepositoryAdapter` lançam `UnsupportedOperationException`, `domain.model`/`AssetDomainService`/ports-out TODO. `open-in-view:false` + `ddl-auto:validate` OK. 0/8 prioridades. Score 32 (Inicial). Gates B5 não executados (toolchain Gradle ausente — diferido). Próxima ação sugerida: IMPLEMENTADOR→P1 (não executada — usuário pediu apenas BASELINE).
- 2026-06-05 -- LEAD -- B1 -- OK -- BASELINE (be-autopilot, escopo restrito a B1). README operacional regenerado (substitui stub de scaffold que usava o termo proibido "tool"). Estado real: scaffold hexagonal COMPLETO (api/application/domain/infrastructure, 12 models + 12 domain services + 16 ports + 12 adapters + 4 producers + 2 consumers + multi-tenancy schema-per-tenant + Feign WRKS) + migration V1 com 12 tabelas (data-model completo); porém lógica de negócio AUSENTE: `application.service` e `domain.service` vazios (motor Maturity Score 6D ausente), ports out com TODO, adapters lançam `UnsupportedOperationException`, controllers sem endpoints. TechLab AI `qualification` bloqueado (sync upstream, `openapi.json` vazio). Desvio: V1 migration local ao serviço (convenção = centralizada em journey-os-migrations). 0/23 issues DONE. Score 22 (Inicial). Gates B5 não executados (toolchain Gradle ausente — diferido). Loop B2->B5 NÃO executado. Próxima ação sugerida: PLANNER/IMPLEMENTADOR->P1 (não executada — usuário pediu apenas BASELINE).
- 2026-06-05 -- JRNY -- B1 -- OK -- BASELINE (be-autopilot, escopo restrito a B1). README operacional gerado pelo template do validator (substitui stub de scaffold com paths inexistentes `docs/architecture/tools/...`). Estado real: esqueleto hexagonal COMPLETO (5 controllers/5 services/5 domain services/10 ports/6 consumers/4 producers/5 adapters/6 entities) + infra transversal REAL (TenantContextFilter+Hibernate multi-tenancy, SecurityConfig OAuth2 RS, CorrelationId/MDC, AuditAspect, ArtemisConfig) + migration V1 com 5 tabelas (empresa_id guard, CHECKs de state machine, índices) + ArchUnit (2 classes) + 3 features Gherkin concretas; porém lógica de negócio 100% STUB — `*UseCase` interfaces vazias, `*Service` sem corpo (ex.: RotearLeadService vazio), `domain.service`/`domain.model`/DTOs TODO, BDD steps em PendingException. **DRIFT BLOQUEANTE entity↔migration**: JPA entities com colunas genéricas de scaffold (`tenant_id/status/created_at`) divergem da DDL (`empresa_id/nome/estado_jornada/versao/ordem/tipo_estagio`) → `ddl-auto=validate` falharia (resolver antes de P3). RULE-07 ainda não exercida (serviços vazios). TechLab AI `orchestration` placeholder (openapi.json vazio). 0/8 prioridades · 0/22 issues. Score 27 (Inicial). Gates B5 não executados (toolchain Gradle ausente — diferido). Loop B2->B5 NÃO executado. Próxima ação sugerida: IMPLEMENTADOR→P1 (não executada — usuário pediu apenas BASELINE).
- 2026-06-05 -- WRKS -- B1 -- OK -- BASELINE (be-autopilot, escopo restrito a B1). README operacional regenerado (substitui stub genérico "Journey OS tool"/"Spring Cloud WRKS"/paths `docs/architecture/tools/`). Estado real: scaffold de 168 arquivos com estrutura hexagonal completa e conforme — cross-cutting REAL (TenantContextHolder.require()/TenantContextFilter, AccessContextHolder/DataScope, GlobalExceptionHandler RFC-7807 via ProblemDetailFactory, DomainServiceConfig 6 beans, CorrelationIdInterceptor), `application.yml` conforme (open-in-view=false RULE-08, ddl-auto=validate, Flyway off, Eureka, OAuth2 RS, MDC), ArchUnit RULE-01..06, DDL IAM completa (11 tabelas em journeyos_global, V1). **Business logic nula**: ports.in vazios, application services vazias, domain services TODO, controllers sem endpoints, repository adapters lançam UnsupportedOperationException, MigrationTriggerClient placeholder inválido (name=""/url="${}"), BDD steps PendingException. Caveat: migration V1 reside dentro do serviço (deveria ser centralizada em journey-os-migrations). 0/8 prioridades; 0/24 issues DONE. Score 24 (Inicial). Gates B5 não executados (toolchain Gradle ausente — diferido). Próxima ação sugerida: IMPLEMENTADOR→P1 (não executada — usuário pediu apenas BASELINE).
- 2026-06-05 -- INTL -- B1 -- OK -- BASELINE (be-autopilot, escopo restrito a B1). README operacional regenerado (substitui stub genérico "Journey OS tool"/Artemis/`t_<tenantId>`). Estado real: esqueleto hexagonal o mais denso da plataforma — 7 agregados (BaseConhecimento/ConversaCopiloto/FonteConhecimento/EventoIndexado/NoConhecimento/Citacao/MensagemCopiloto), 3 superfícies REST (Copilot/Knowledge/Analytics), 13 ports-out (7 repo + IntlIndex/IntlSearch/Knowledge/Orchestration/AccessDecisionCache/IntlEventPublisher), 2 Feign (WRKS/ASST), 1 producer + 3 consumers, infra multi-tenancy + idempotência (`ProcessedEvent`) + ArchUnit (2 classes); porém lógica 100% STUB — `*UseCase`/ports vazios, `*Service` sem métodos, `domain.model` TODO (NoConhecimento só `id`). `open-in-view:false` + `ddl-auto:validate` OK. **Gaps de build**: deps duplicadas (oauth2-resource-server 2x, resilience4j 2x, spring-security-test mal posicionado), mensageria ambígua (Kafka + Artemis), `elastic-client-lib`/pgVector não declarados apesar de IntlIndex/Search + EventoIndexado. TechLab AI `knowledge`/`orchestration` placeholder (openapi vazio → INT-INTL-002 bloqueado). RULE-07 + filtro empresa Elastic ausentes. 0/9 prioridades · 0/23 issues. Score 31 (Inicial). Gates B5 não executados (toolchain Gradle ausente — diferido). Loop B2->B5 NÃO executado. Próxima ação sugerida: IMPLEMENTADOR→P1 (não executada — usuário pediu apenas BASELINE).
- 2026-06-05 -- COMM -- B1 -- OK -- BASELINE (be-autopilot, escopo restrito a B1). README operacional regenerado (substitui stub de scaffold "Journey OS tool"/"Spring Cloud COMM"/paths `docs/architecture/tools/`). Estado real: esqueleto hexagonal COMPLETO (6 controllers/6 services/6 ports.in/12 ports.out/5 domain models/5 domain services/5 entities+repos+adapters) + infra multi-tenancy schema-per-tenant REAL (TenantContextFilter le claim JWT, Hibernate MultiTenantConnectionProvider/IdentifierResolver, MdcContextRestorer p/ consumers) + mensageria (4 producers + 4 consumers + ProcessedEvent idempotencia) + 2 Feign (WRKS AccessEvaluate/ASST AssetQuery) + porta TechLab AI ComposicaoIaPort (document_composition) + ArchUnit (ArchitectureTest 6 regras + CrossAspectArchTest) + migration V1 com 5 tabelas (template_mensagem/mensagem + CHECKs de state machine ENFILEIRADA->...->ENTREGUE/FALHADA, UNIQUE chave_idempotencia). `open-in-view:false` + `ddl-auto:validate` OK. Logica de negocio 100% STUB: ~101 TODOs; `*Service` com corpo vazio, `domain.model` so id/tenantId/createdAt, `domain.service`/ports-out com `// TODO`, controllers sem endpoints, DTOs sem campos, Feign `name=""/url="${}"`, EventDestinations sem destinos pinados, BDD steps em PendingException. RULE-07 (.require()) nao exercida (services vazios). Caveat: migration V1 local ao servico (convencao = centralizada em journey-os-migrations; `flyway.enabled=false`). TechLab AI `document_composition` placeholder (openapi.json upstream vazio). 0/9 prioridades; 0/16 issues DONE. Score 25 (Inicial). Gates B5 nao executados (toolchain Gradle ausente — diferido). Loop B2->B5 NAO executado. Proxima acao sugerida: IMPLEMENTADOR/PLANNER->P1 (nao executada — usuario pediu apenas BASELINE).
- 2026-06-05 -- SALE -- B1 -- OK -- BASELINE (be-autopilot, escopo restrito a B1). README operacional gerado pelo template do validator (substitui stub de scaffold que usava o termo proibido "tool" e paths `docs/architecture/tools/...`; corrige `schema-per-tenant t_<tenantId>` -> `emp_<slug>`). Estado real: esqueleto hexagonal COMPLETO (119 arquivos Java; 9 agregados Oportunidade/Oferta/Compra/ItemCompra/Atribuicao/ModeloAtribuicao/Campanha/HistoricoEstagio/Ltv; 5 superficies REST oportunidade/oferta/compra/atribuicao/ltv; 5 use cases + 13 ports-out; Feign WRKS AccessEvaluate; 7 producers + 4 consumers; idempotencia ProcessedEvent) + infra transversal REAL (multi-tenancy schema-per-tenant TenantContextFilter/Holder.require()/Resolver/ConnectionProvider/HibernateMultiTenancyConfig, AccessContextHolder/DataScope/DataScopeFilterAspect, AuditAspect, GlobalExceptionHandler RFC-7807, DomainServiceConfig, CorrelationIdInterceptor/MDC) + `application.yml` conforme (open-in-view=false RULE-08, ddl-auto=validate) + migration V1 (176 linhas, 9 tabelas, NUMERIC(15,2)+moeda, CHECKs de estado, indices) + ArchUnit (ArchitectureTest RULE-01..06 + CrossAspectArchTest) + 3 features Gherkin. **Logica de negocio 100% STUB**: 5 `*Service` vazios (`{}`), `*UseCase` ports vazios, 9 domain services TODO (motor de atribuicao/LTV ausente), controllers sem endpoints, DTOs com TODO (so `tenantId`), 9 adapters lancam `UnsupportedOperationException`, BDD steps PendingException. Golden path da ancora `compra.confirmada` NAO implementado. RULE-07 (.require em application.service) nao exercida (services vazios). Desvio: migration V1 local ao servico (convencao = centralizada em journey-os-migrations; `flyway` presente no yml). Sem TechLab AI no MVP (atribuicao/LTV deterministicos). 0/9 prioridades; 0/24 issues DONE. Score 30 (Inicial). Gates B5 nao executados (toolchain Gradle ausente — diferido). Loop B2->B5 NAO executado. Proxima acao sugerida: IMPLEMENTADOR->P1 (nao executada — usuario pediu apenas BASELINE).
- 2026-06-05 -- JRNY -- fix -- OK -- Correcao do drift entity↔migration (pos-baseline, a pedido). As 5 JPA entities (Jornada/Estagio/RegraRoteamento/InscricaoJornada/DecisaoRoteamento) reescritas para espelhar exatamente a DDL de V1: PK `id` (era `<tabela>_id`), `empresa_id` UUID guard (era `tenant_id` String), todas as colunas de dominio, JSONB via `@JdbcTypeCode(SqlTypes.JSON)` (config/condicao/snapshot_entrada), TIMESTAMPTZ->OffsetDateTime, decisao_roteamento `updatable=false` (imutavel ADR-005). 5 JpaRepository: query derivada `findByTenantId(String)`->`findByEmpresaId(UUID)` (evita falha de bootstrap Spring Data). `processed_events`/`outbox_event` confirmados como providos pela migration compartilhada de idempotencia/outbox (data-model.md §289) — `ProcessedEvent` intacto. Ports/adapters de dominio (`findByTenantId(String)`, stubs que lancam UnsupportedOperationException) mantidos — decisao de design de P1/P3, fora do escopo do drift. `ddl-auto=validate` deixa de falhar; confirmacao formal diferida ao gate `:jrny-service:integrationTest` (toolchain Gradle ausente). README §3/§5/§7/§8 atualizados.
