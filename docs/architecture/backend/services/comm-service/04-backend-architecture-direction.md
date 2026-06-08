# 04 — Backend Architecture Direction — COMM (Communication Hub)

> Direção técnica do `comm-service`. Decisões com tradeoff → ADR.

## 1. Stack

- **Java 21** · **Spring Boot 3.5.x** · **Gradle 8.x (Kotlin DSL)**.
- **PostgreSQL 15+** (schema operacional `emp_<slug>`; `ddl-auto: validate`, DDL via MIG/Flyway).
- **Elasticsearch 9.x** (índice fact `communication-events`, ingest `direct-java-client`).
- **Kafka / AWS MSK** (event bus `journey-os.*`; outbox para disparo desacoplado).
- **TechLab AI** (HTTP — `document_composition`; consumido via cliente gerado de `openapi.json`).
- **Provedores de canal** (Meta WABA / SES / SendGrid / Telegram Bot / Twilio / SNS) via adapters HTTP.
- **Eureka (REG)** para discovery · **GWY** como edge · **WRKS** para identidade/AccessDecision · **ASST** (Feign `AssetQueryClient`).
- Resilience4j (circuit breaker/timeout/retry nas chamadas a provedores e à TechLab AI), Lombok, SLF4J, MapStruct (opcional para mapeamento entity↔domain).

## 2. Service Boundary

**Single service** (`comm-service`) — default do monorepo (ver `ADR-002`). O domínio de
comunicação é coeso (template + roteamento + disparo + entrega + config de canal) e não justifica
decomposição no MVP. O Template Studio é um **caso de uso interno** (orquestra TechLab AI) e os
adapters de canal são **detalhe de infraestrutura** sob um port único, não serviços separados.

## 3. Package Organization

Base `com.journeyos.comm` (layout hexagonal canônico — `services-catalog.md` §3):

```
com.journeyos.comm
├── api/            controller/ (TemplateController, TemplateStudioController, MensagemController,
│                              RoteamentoController, CanalController, WebhookController)
│                   dto/ (records Request/Response) · exception/ (@RestControllerAdvice, ProblemDetail)
├── application/    service/ (CriarTemplateService, ComporNoStudioService, RotearMensagemService,
│                            EnviarMensagemService, RegistrarEventoEntregaService,
│                            ConfigurarCanalService, BuscarStatusService)
│                   port/in/ (use cases) · port/out/ (TemplateRepositoryPort, MensagemRepositoryPort,
│                            RoteamentoRepositoryPort, CanalEnvioPort, ComposicaoIaPort,
│                            AssetQueryPort, AccessDecisionPort, EventoPublisherPort, CommSearchPort)
├── domain/         model/ (Template, Mensagem, EventoEntrega, RegraRoteamento, ConfigCanal,
│                          Canal, EstadoEntrega, TipoTemplate) — zero Spring/JPA
│                   service/ (ResolucaoRoteamentoService, TransicaoEntregaService, RenderTemplateService)
└── infrastructure/ persistence/ (entity/repository/adapter — JPA emp_<slug>)
                    clients/ (AccessEvaluateClient @FeignClient → wrks-service;
                             AssetQueryClient @FeignClient → asst-service; TechLabAiClient)
                    channels/ (WhatsAppEnvioAdapter, EmailEnvioAdapter, TelegramEnvioAdapter,
                             SmsEnvioAdapter — implementam CanalEnvioPort; CanalEnvioRouter)
                    messaging/ (producer/ consumer/ outbox/) · search/ (Elastic adapter `communication-events`)
                    config/ (DomainServiceConfig, Resilience4jConfig) · security/ (JWT, EmpresaContextHolder)
```

`@Transactional` apenas em `application/service` (RULE-03). `@FeignClient` apenas em
`infrastructure/clients` (RULE-06). Os adapters de canal em `infrastructure/channels` implementam
um port `out` único (`CanalEnvioPort`) — o domínio nunca importa um SDK de provedor.

## 4. Hub Service Dependencies

| Dependência | Tipo | Uso |
|---|---|---|
| **WRKS** | sync (Feign `AccessEvaluateClient`) + JWKS | Autorização `comm.*` + validação de JWT. |
| **ASST** | sync (Feign `AssetQueryClient`) | Lê assets publicados como fonte de conteúdo de template. |
| **MIG** | precondição | Schema `emp_<slug>` provisionado antes do bootRun. |
| **REG (Eureka)** | discovery | Registro/descoberta de `comm-service`. |
| **GWY** | edge | Roteia `/api/v1/templates|messages|routing-rules|channels/**` para COMM (webhooks expostos via edge dedicado). |

## 5. External Integrations

- **TechLab AI** (`document_composition`): Template Studio compõe/edita copy. Cliente gerado de `integrations/techlab-ai/openapi.json` (DTOs em `gen/techlabai/`, **não** hand-written). Timeout + circuit breaker; fallback graceful (Studio degrada, CRUD/disparo intactos). Endpoint declarado na tabela de consumo do `CLAUDE.md` via `/be-architect-vision`.
- **Provedores de canal** (Meta WABA, SES/SendGrid, Telegram Bot, Twilio/SNS): atrás do port `CanalEnvioPort` com um adapter por canal/provedor (ver `ADR-005`). Cada adapter: envia (HTTP) + normaliza callbacks (webhook → `EventoEntrega`). Resilience4j por adapter. Credenciais por `config_canal.credencial_ref` (secret manager), nunca hardcoded.
- **ASST** (`AssetQueryClient`): leitura de assets publicados (contrato Feign estável; nunca a entity).
- **Elasticsearch** (`communication-events`): adapter de projeção (fact append-only) do ciclo de vida. Best-effort (não bloqueia o disparo). Contrato em `elastic-data-contract.md`.
- **Object storage (anexos/mídia):** **fora do MVP** — referenciados por URL externa.

## 6. Async vs Sync Decisions

| Operação | Modo | Racional |
|---|---|---|
| CRUD template / regra / config canal | **sync** | Resposta imediata; transacional. |
| Template Studio (composição IA) | **sync com timeout + CB** (async opcional pós-MVP) | UX espera o rascunho; chamada à TechLab AI protegida por Resilience4j. |
| Roteamento (resolver canal/template) | **sync** | Decisão determinística no momento do pedido. |
| Aceite de disparo (`POST /messages`) | **sync → 202** | Valida, renderiza, persiste `PENDENTE`, grava outbox e retorna `202 ENFILEIRADA`. |
| Envio ao provedor | **async (worker + outbox)** com retry/backoff + CB | Desacopla do request; absorve latência/rate-limit do provedor; idempotente por chave. |
| Callbacks de entrega (webhooks) | **async (inbound)** | Provedor confirma entrega/leitura quando ocorre; atualiza estado + grava `EventoEntrega`. |
| Projeção Elastic (`communication-events`) | **sync best-effort** (não bloqueia) | Analytics é projeção; falha de index não reverte o envio (reconciliação posterior). |
| Eventos de domínio | **async** (Kafka, outbox) | Desacopla JRNY/SALE/INTL; idempotente. |

---

## Referências

- `adr/ADR-001..005` · `03-initial-domain-framing.md` · `05-persistence-model.md`
- `docs/architecture/backend/standards/platform-patterns.md` (Feign+Resilience4j, Kafka, outbox)
- `docs/architecture/integrations/techlab-ai-integration.md`
