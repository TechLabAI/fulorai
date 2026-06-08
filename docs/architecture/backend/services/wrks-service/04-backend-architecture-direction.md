# 04 — Backend Architecture Direction — WRKS

## 1. Stack

| Camada | Tecnologia |
|---|---|
| Linguagem | Java 21 |
| Framework | Spring Boot 3.5.x (Web MVC; **não** reativo) |
| Build | Gradle 8.x (Kotlin DSL) |
| Persistência | PostgreSQL 15+ (`journeyos_global`), Spring Data JPA + Hibernate |
| Migrations | Centralizadas em `journey-os-migrations` (Flyway) — WRKS roda `ddl-auto: validate` |
| Cache | Redis/Valkey (Spring Data Redis) — sessão, AccessDecision, blacklist |
| Identidade | Keycloak (OIDC) como IdP; WRKS emite JWT RS256 (Nimbus/`spring-security-oauth2-jose`) |
| Mensageria | Kafka (AWS MSK) — Spring for Apache Kafka |
| Search/Index | Elasticsearch 9.x (cliente Java direto) — índice `audit-events` |
| Discovery | Eureka (REG) |
| Resilience | Resilience4j (retry/circuit-breaker em IdP/MIG) |

## 2. Service Boundary

**Single service** (`wrks-service`). Toda a fronteira IAM cabe num serviço coeso; não há razão
para decompor no MVP. Justificativa registrada em `ADR-002` (WRKS como autoridade de identidade).
A indexação de auditoria é um adapter de saída, não um serviço separado.

## 3. Package Organization

Base: `com.journeyos.wrks` (RULE-09). Layout hexagonal canônico (`services-catalog.md` §3):

```
com.journeyos.wrks
├── api/{controller,dto,exception}
├── application/{service, port/in, port/out}
├── domain/{model, service}
└── infrastructure/{clients, config, messaging/{producer,consumer}, persistence/{entity,repository,adapter}, security, cache}
```

ArchUnit bloqueante: RULE-01..09 (`architectureCheck`). Domínio sem Spring/JPA (RULE-01/02);
`@Transactional` só em `application.service` (RULE-03); `@FeignClient` só em `infrastructure.clients` (RULE-06).

## 4. Hub Service Dependencies

| Dependência | Direção | Mecanismo |
|---|---|---|
| **REG (Eureka)** | WRKS → REG | Registro/discovery |
| **MIG** | WRKS → MIG | Gatilho de provisionamento de schema (HTTP/Feign ou comando) |
| **GWY** | GWY → WRKS | GWY consome JWKS de WRKS para validar JWT |
| **Todos os serviços** | serviço → WRKS | `POST /access/evaluate` (sync) + consumo de `modelo.acesso.alterado` (async) |

WRKS **não depende** de nenhum serviço de negócio (é fundação). Dependências de WRKS são
apenas infra (Keycloak, Redis, Postgres, Kafka, Elastic) + MIG/REG.

## 5. External Integrations

- **Keycloak (OIDC)** — `IdpPort` (infrastructure.clients): troca de código OIDC, validação de token do IdP, dados do usuário. WRKS mapeia o usuário do IdP para `journeyos_global.usuario`.
- **Redis** — `SessionCachePort`/`AccessDecisionCachePort`/`BlacklistPort` (infrastructure.cache).
- **Elasticsearch** — `AuditIndexPort` (infrastructure.persistence/adapter) para `audit-events`.
- **MIG** — `MigrationTriggerPort` (infrastructure.clients).

## 6. Async vs Sync Decisions

| Interação | Modo | Racional |
|---|---|---|
| AccessDecision (evaluate) | **Sync** (HTTP) + cache Redis | Baixa latência no caminho crítico de toda request. |
| Login / refresh / logout | **Sync** (HTTP) | Interativo; resposta imediata ao usuário. |
| `modelo.acesso.alterado`, `usuario.criado`, `empresa.provisionada` | **Async** (Kafka) | Notificação/propagação; consumidores desacoplados. |
| Auditoria (`evento_auditoria`) | **Async** (Kafka consumer) | Não pode bloquear o produtor; tolera atraso. |
| Provisionar schema (MIG) | **Sync trigger + async confirmação** | Dispara e confirma via evento `empresa.provisionada`. |

Propagação de contexto em listeners async: header `empresaId` na mensagem; `EmpresaContextHolder`
populado no consumer e `clear()` no `finally` (ver `shared/multi-empresa.md`).

---

## Referências

- `docs/architecture/backend/standards/{hexagonal-patterns,java-conventions,platform-patterns}.md`
- `ADR-001` (hexagonal), `ADR-003` (messaging), `ADR-005` (token/sessão)
