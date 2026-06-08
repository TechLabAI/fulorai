# Plano -- WRKS (Workspace & Identity)

## Status das prioridades
- P1 -- pendente
- P2 -- pendente
- P3 -- pendente
- P4 -- pendente
- P5 -- pendente
- P6 -- pendente
- P7 -- pendente
- P8 -- pendente
- P9 -- pendente (absorvido em INT-WRKS-002/003/004 + SPEC-10)

## 0. Leitura executiva

### Papel do serviço (de 01-architectural-vision.md)
Fundação de identidade e isolamento do Journey OS: dono dos workspaces (`empresa`), org structure
(business units, teams), usuários, RBAC canônico (papéis/permissões) e identidade/sessão (login
Keycloak OIDC, emissão de JWT RS256, AccessDecision). Primeiro serviço a subir; precondição de
qualquer outra capacidade.

### MVP scope (de 01)
Workspace/empresa + provisionamento; org structure; usuários + associações; RBAC + versão de
acesso; identidade/sessão (login/troca/refresh/logout/restore); AccessDecision + cache; session
policy; auditoria consolidada. **Fora:** MFA, multi-SSO, papéis custom, IP-enforcement, billing.

### Diagnóstico inicial (gaps de 06)
- Org structure (business_unit/team) é novidade — formalizada no data-model (WRKS-008).
- Gatilho MIG a concretizar (WRKS-010/INT-WRKS-004).
- Bundles de permissão `all` (TODO em `papeis.md`) — refinar antes de produção.
- Mensageria: Kafka (project-context) vs JMS legado nos docs shared (adotado Kafka).
- **Ambiente sem toolchain Gradle:** gates compileJava/architectureCheck/BDD ficam pendentes até wrapper existir.

## 1. Estratégia geral

### Objetivo macro
Entregar o serviço fundação executável e seguro, na ordem: esqueleto → golden path de identidade
→ persistência → integrações → segurança/multi-tenancy → mensageria/auditoria → observabilidade → BDD.

### Ordem das prioridades

| P | Título | Motivo |
|---|---|---|
| P1 | Scaffold + contratos mínimos | Esqueleto, domínio puro, superfície REST |
| P2 | Orquestração de identidade | Golden path: login → JWT → empresa; provisionamento |
| P3 | Persistência + migrations | IAM em `journeyos_global`, seeds canônicos |
| P4 | Integrações externas | Keycloak + MIG (com resiliência) |
| P5 | Security + multi-tenancy | JWT/JWKS, AccessDecision, anti-escalonamento, cross-empresa |
| P6 | Messaging + auditoria | Eventos (outbox) + sink de auditoria + Elastic |
| P7 | Observability + health | MDC, métricas IAM, readiness |
| P8 | BDD end-to-end | Cucumber: 0 failed, cobertura SHALL (D-218) |

## 2. Plano por prioridade

### Prioridade 1 -- Scaffold + contratos mínimos
Status: pendente
- **Objetivo:** serviço sobe, registra no Eureka, domínio puro e superfície REST com ProblemDetail.
- **Issues:** WRKS-001, WRKS-002, WRKS-003, INT-WRKS-001.
- **Specs:** SPEC-01, SPEC-07, SPEC-02/03/04 (modelo).
- **Sequência:** WRKS-001 → WRKS-002 → WRKS-003 (INT-WRKS-001 em paralelo).
- **Aceite:** build + architectureCheck PASS; `/actuator/health` 200; erros em problem+json.
- **Riscos:** RULE-09 (pacote) — `bounded_context: wrks` no generator-config.
- **Instrução:** começar pelo generator-config.yml já emitido; não retornar `@Entity` em controller.

### Prioridade 2 -- Orquestração de identidade (golden path)
Status: pendente
- **Objetivo:** login OIDC → JWT escopado; troca/refresh/logout; provisionamento de empresa (saga).
- **Issues:** WRKS-004, WRKS-005, WRKS-006.
- **Specs:** SPEC-02, SPEC-05, SPEC-06.
- **Sequência:** WRKS-004 → WRKS-005; WRKS-006 em paralelo.
- **Aceite:** single/multi-empresa; refresh rotation; saga PROVISIONANDO→ATIVA idempotente.
- **Riscos:** dependência de TokenIssuer (WRKS-011) e Keycloak (WRKS-009) — antecipar stubs.

### Prioridade 3 -- Persistência + migrations
Status: pendente
- **Objetivo:** IAM persistido e validado; seeds canônicos aplicados.
- **Issues:** WRKS-007, WRKS-008.
- **Specs:** SPEC-04.
- **Sequência:** WRKS-008 (schema) → WRKS-007 (JPA/adapters).
- **Aceite:** migrations limpas; CHECK slug; uniques; CRUD Testcontainers.
- **Riscos:** Flyway centralizado (coordenar com MIG); ordem V0001 antes de V0002.

### Prioridade 4 -- Integrações externas
Status: pendente
- **Objetivo:** Keycloak (OIDC) e MIG (provisionamento) com resiliência.
- **Issues:** WRKS-009, WRKS-010, INT-WRKS-004.
- **Specs:** SPEC-10.
- **Aceite:** Keycloak down → 502 sem bypass; MIG timeout → retriable sem schema duplicado.
- **Riscos:** sem bypass de auth; circuit-breaker bem configurado.

### Prioridade 5 -- Security + multi-tenancy
Status: pendente
- **Objetivo:** JWT/JWKS, AccessDecision+cache, anti-escalonamento, cross-empresa, RBAC admin.
- **Issues:** WRKS-011, WRKS-012, WRKS-013, WRKS-014, INT-WRKS-002, INT-WRKS-003.
- **Specs:** SPEC-03, SPEC-06.
- **Sequência:** WRKS-011 → WRKS-012 → WRKS-013/014 (INT-002/003 em paralelo).
- **Aceite:** versão stale → 401; escalonamento → 403; isolamento cross-empresa; mudança RBAC < 5s.
- **Riscos:** RULE-07 (require()); guarda cross-empresa em queries nativas.

### Prioridade 6 -- Messaging + auditoria
Status: pendente
- **Objetivo:** eventos com outbox + sink de auditoria idempotente + Elastic.
- **Issues:** WRKS-015, WRKS-016, INT-WRKS-005, INT-WRKS-006.
- **Specs:** SPEC-09, SPEC-05.
- **Aceite:** outbox atômico; consume idempotente; index resiliente; contrato provider.
- **Riscos:** dedup por `correlationId`+`evento`; `clear()` em `finally`.

### Prioridade 7 -- Observability + health
Status: pendente
- **Objetivo:** MDC, métricas IAM, readiness por dependência.
- **Issues:** WRKS-017.
- **Specs:** SPEC-07.
- **Aceite:** métricas `journey-os_iam_session_*`; readiness; sem segredo em log.

### Prioridade 8 -- BDD end-to-end
Status: pendente
- **Objetivo:** step defs das 4 features; 0 failed; cobertura de toda cláusula SHALL.
- **Issues:** WRKS-018.
- **Specs:** SPEC-08 (+ todas via SHALL).
- **Aceite:** `*CucumberIT*` 0 failed; Testcontainers singleton.

## 3. Dependências externas
- Keycloak (OIDC), Redis/Valkey, PostgreSQL (`journeyos_global`), Kafka (AWS MSK), Elasticsearch
  (`audit-events`), MIG (provisionamento), REG (Eureka). TechLab AI: **nenhuma**.

## 4. Restrições arquiteturais
- ArchUnit RULE-01..09 (CLAUDE.md) — `architectureCheck` bloqueante.
- Camadas hexagonais (api/application/domain/infrastructure); domínio sem Spring/JPA.
- `@Transactional` somente em `application.service` (RULE-03).
- `EmpresaContextHolder.require()` em todo application service (RULE-07).
- Pacote base `com.journeyos.wrks` (RULE-09); `open-in-view=false` (RULE-08).
- Nunca chamar provider de IA direto (não aplicável — WRKS não usa IA).

## 5. Referências
- `docs/architecture/backend/services/wrks-service/` (vision 01-06, ADR-001..005, contracts, spec/backend, tests/cucumber, diagrams).
- `docs/architecture/backend/services/wrks-service/generator-config.yml`.
- `docs/architecture/backend/issues/WRKS-001..018.md`, `INT-WRKS-001..006.md`, `issues_map-WRKS.md`.
- `docs/architecture/shared/rbac/`, `shared/multi-empresa.md`, `shared/modelo-dados/{global-schema,empresa}.md`.
