# 04 — Backend Architecture Direction — SALE (Sales & Revenue)

> Direção técnica do serviço. Stack canônica, fronteira, organização, integrações.

## 1. Stack

- **Java 21** · **Spring Boot 3.5.x** · **Gradle 8.x (Kotlin DSL)**.
- **PostgreSQL 15+** (schema operacional `emp_<slug>`); Flyway centralizado em `journey-os-migrations` (MIG); serviço com `ddl-auto=validate`.
- **Kafka / AWS MSK** — event bus (produz `oportunidade.*`/`compra.*`/`receita.*`/`ltv.*`, consome eventos LEAD/WRKS). *(Decisão de plataforma: o Journey OS usa Kafka/MSK; ver `ADR-003`.)*
- **Elasticsearch 9.x** — índices `revenue-events` e `campaign-events` (classe *fact*), ingestão `direct-java-client`.
- **Sem TechLab AI no MVP** — atribuição e LTV são determinísticos. Assist de insights de receita (capacidade `analytics`) é pós-MVP, e entraria via `infrastructure.clients` atrás de uma porta, com Resilience4j — nunca provider de IA direto.
- **Spring Security** (Resource Server JWT, chave pública de WRKS) · **Redis/Valkey** (cache de `AccessDecision`).
- Lombok (`@RequiredArgsConstructor`, `@Slf4j`), SpringDoc (OpenAPI), Testcontainers + Cucumber (testes).

## 2. Service Boundary

**Single service** (`type: standard`). SALE não se decompõe no MVP: pipeline (CRM), ofertas,
compras, atribuição e LTV compartilham o mesmo contexto transacional curto no `emp_<slug>` e o
mesmo gatilho de receita (`compra.confirmada`). Decomposição futura (ex.: motor de atribuição
dedicado, ou separar CRM de billing) é registrada como possibilidade em `ADR-002`, não antecipada.
SALE **não** assume qualificação (LEAD), roteamento (JRNY), comunicação (COMM) nem processamento
de pagamento (gateway externo).

## 3. Package Organization

Pacote base `com.journeyos.sale` (RULE-09), layout hexagonal canônico:

```
api/            controller · dto (records) · exception (@RestControllerAdvice + ProblemDetail)
application/    service (@Service, @Transactional) · port/in · port/out
domain/         model (POJO) · service (PipelineService, AttributionEngine, LtvCalculator)
infrastructure/ config (DomainServiceConfig, Resilience4j, Feign)
                messaging/{producer,consumer} · persistence/{entity,repository,adapter}
                search (Elastic adapter) · security (JWT filter, EmpresaContextHolder, MDC)
```

Portas de saída principais (`application.port.out`):
`OportunidadeRepositoryPort`, `OfertaRepositoryPort`, `CompraRepositoryPort`,
`ModeloAtribuicaoRepositoryPort`, `LtvRepositoryPort`, `SaleSearchPort` (Elastic),
`SaleEventPublisherPort` (Kafka). *(Pós-MVP: `TechLabAnalyticsPort`.)*

## 4. Hub Service Dependencies

| Serviço | Tipo | Uso |
|---|---|---|
| **WRKS** | sync (Feign) + eventos | `AccessEvaluateClient` (`@FeignClient(name="wrks-service")`) para autorização `sale.*`; consumo de `empresa.provisionada` / `modelo.acesso.alterado`. |
| **LEAD** | eventos | Consome `lead.qualificado` / `lead.score.atualizado` para criar/priorizar oportunidades. **Não** chama LEAD por Feign no fluxo de venda. |
| **REG (Eureka)** | discovery | Registro/descoberta para o Feign client. |
| **GWY** | entrada | Roteamento das chamadas autenticadas. |
| **MIG** | pré-condição | Prepara o schema `emp_<slug>` (migrations centralizadas). |

SALE **não** chama JRNY/COMM/INTL por Feign — a integração é por **eventos**.

## 5. External Integrations

- **Checkout / gateway externo** (Hotmart, link de pagamento): a compra confirmada chega via `POST /api/v1/compras` (idempotente por `id_externo`) no MVP; via **Event Platform do INTL** (pós-MVP). SALE **não** integra gateway de pagamento diretamente nem processa cobrança.
- **Elasticsearch** (`revenue-events`, `campaign-events`): adapter de busca para funil/receita; indexação em `compra.confirmada` e `receita.atribuida`.
- **PostgreSQL**: persistência operacional do tenant (pipeline, ofertas, compras, atribuição, LTV materializado).

## 6. Async vs Sync Decisions (alto nível)

| Interação | Modo | Razão |
|---|---|---|
| CRUD de oportunidade / mover estágio / ganhar-perder | **Sync** (request→response) | Caso de uso interativo do closer; transação curta no `emp_<slug>`. |
| Ingestão de compra / reconhecimento de receita | **Sync** (idempotente) | Confirmação precisa retornar status determinístico; idempotência por `id_externo`. |
| Atribuição de receita / recálculo de LTV | **Sync** (no fluxo da compra) | Deriva diretamente da compra confirmada; transação curta. |
| `AccessDecision` (WRKS) | **Sync** (Feign) + cache Redis | Autorização por requisição. |
| Notificação a jusante (`compra.*`/`receita.*`/`oportunidade.*`/`ltv.*`) | **Async** (Kafka) | Desacopla SALE de INTL/COMM/JRNY (ver `ADR-003`). |
| Consumo de `lead.*` / eventos WRKS | **Async** (consumer) | Criação reativa de oportunidade; seed e invalidação de cache. |
| Re-atribuição por mudança de modelo | **Sync** em lote pequeno (MVP) | Pipeline assíncrono dedicado é pós-MVP. |

---

## Referências

- `ADR-001` (hexagonal) · `ADR-002` (single-service) · `ADR-003` (messaging Kafka) · `ADR-005` (atribuição de receita)
- `docs/architecture/backend/standards/{hexagonal-patterns,platform-patterns,java-conventions}.md`
- `docs/architecture/backend/services/lead-service/contracts/` (eventos consumidos)
