# 04 — Backend Architecture Direction — LEAD (Lead Intelligence & Qualification)

> Direção técnica do serviço. Stack canônica, fronteira, organização, integrações.

## 1. Stack

- **Java 21** · **Spring Boot 3.5.x** · **Gradle 8.x (Kotlin DSL)**.
- **PostgreSQL 15+** com **pgvector** (schema operacional `emp_<slug>`); Flyway centralizado em `journey-os-migrations` (MIG); serviço com `ddl-auto=validate`.
- **Kafka / AWS MSK** — event bus (produz `lead.*`, consome eventos WRKS). *(Decisão de plataforma: o Journey OS usa Kafka/MSK; ver `ADR-003`.)*
- **Elasticsearch 9.x** — índice `leads` (classe *dimension*), ingestão `direct-java-client`.
- **TechLab AI** (HTTP, capacidade `qualification`) com **Resilience4j** (circuit breaker, timeout, retry) — nunca provider de IA direto.
- **Spring Security** (Resource Server JWT, chave pública de WRKS) · **Redis/Valkey** (cache de `AccessDecision`).
- Lombok (`@RequiredArgsConstructor`, `@Slf4j`), SpringDoc (OpenAPI), Testcontainers + Cucumber (testes).

## 2. Service Boundary

**Single service** (`type: standard`). LEAD não se decompõe no MVP: capture, perfil, surveys,
qualificação, scoring e segmentação compartilham o mesmo agregado raiz (Lead) e o mesmo ciclo
transacional curto. Decomposição futura (ex.: motor de scoring dedicado) é registrada como
possibilidade em `ADR-002`, não antecipada. LEAD **não** assume roteamento (JRNY), venda (SALE)
nem comunicação (COMM).

## 3. Package Organization

Pacote base `com.journeyos.lead` (RULE-09), layout hexagonal canônico:

```
api/            controller · dto (records) · exception (@RestControllerAdvice + ProblemDetail)
application/    service (@Service, @Transactional) · port/in · port/out
domain/         model (POJO) · service (MaturityScoreCalculator, QualificationRuleEngine, SegmentEvaluator)
infrastructure/ clients (TechLabAiClient) · config (DomainServiceConfig, Resilience4j, Feign)
                messaging/{producer,consumer} · persistence/{entity,repository,adapter}
                search (Elastic adapter) · security (JWT filter, EmpresaContextHolder, MDC)
```

Portas de saída principais (`application.port.out`):
`LeadRepositoryPort`, `RegraQualificacaoRepositoryPort`, `SurveyRepositoryPort`,
`TechLabQualificationPort` (assist IA), `LeadSearchPort` (Elastic), `LeadEventPublisherPort` (Kafka).

## 4. Hub Service Dependencies

| Serviço | Tipo | Uso |
|---|---|---|
| **WRKS** | sync (Feign) + eventos | `AccessEvaluateClient` (`@FeignClient(name="wrks-service")`) para autorização `lead.*`; consumo de `empresa.provisionada` / `modelo.acesso.alterado`. |
| **REG (Eureka)** | discovery | Registro/descoberta para o Feign client. |
| **GWY** | entrada | Roteamento das chamadas autenticadas. |
| **MIG** | pré-condição | Prepara o schema `emp_<slug>` (migrations centralizadas). |

LEAD **não** chama JRNY/SALE/COMM por Feign — a integração a jusante é por **eventos**.

## 5. External Integrations

- **TechLab AI** (`qualification`): `TechLabAiClient` em `infrastructure.clients`, atrás de `TechLabQualificationPort`. DTOs **gerados** de `integrations/techlab-ai/openapi.json` (não escritos à mão). Circuit breaker + fallback determinístico obrigatórios.
- **Elasticsearch** (`leads`): adapter de busca para fila priorizada/segmentação; reindexação em `lead.score.atualizado`.
- **PostgreSQL/pgvector**: persistência operacional; embeddings de perfil para similaridade são **pós-MVP**.

## 6. Async vs Sync Decisions (alto nível)

| Interação | Modo | Razão |
|---|---|---|
| Ingestão de lead / qualificação / scoring | **Sync** (request→response) | Caso de uso interativo; transação curta no `emp_<slug>`. |
| Assist TechLab AI | **Sync** com timeout curto + fallback | Resposta precisa entrar no cálculo; não pode bloquear (circuit breaker). |
| `AccessDecision` (WRKS) | **Sync** (Feign) + cache Redis | Autorização por requisição. |
| Notificação a jusante (`lead.*`) | **Async** (Kafka) | Desacopla LEAD de JRNY/SALE/COMM/INTL (ver `ADR-003`). |
| Recálculo por mudança de regra | **Sync** em lote pequeno (MVP) | Pipeline assíncrono dedicado é pós-MVP. |
| Consumo de eventos WRKS | **Async** (consumer) | Seed e invalidação de cache reativos. |

---

## Referências

- `ADR-001` (hexagonal) · `ADR-002` (single-service) · `ADR-003` (messaging Kafka) · `ADR-005` (Maturity Score)
- `docs/architecture/backend/standards/{hexagonal-patterns,platform-patterns,java-conventions}.md`
- `docs/architecture/integrations/techlab-ai-integration.md`
