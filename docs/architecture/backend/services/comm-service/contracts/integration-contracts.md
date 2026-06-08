# Integration Contracts — COMM (external systems)

> External (non-Journey-OS) systems COMM integrates with. TechLab AI has its own contract
> (`techlab-ai-integration.md`). EARS for behavior.

## 1. Channel providers (via `CanalEnvioPort` adapters — ADR-005)

COMM sends through provider-agnostic adapters under a single outbound port. The domain knows only
`canal`; each adapter wraps one provider and normalizes both send and webhook callbacks.

| Canal | Providers (MVP) | Send | Delivery callback |
|---|---|---|---|
| `WHATSAPP` | `META_WABA` | HTTP (Graph API) | webhook (delivery/read receipts) |
| `EMAIL` | `SES`, `SENDGRID` | HTTP/SMTP API | webhook/event (bounce/delivery/open) |
| `TELEGRAM` | `TELEGRAM_BOT` | HTTP (Bot API) | webhook (delivery) |
| `SMS` | `TWILIO`, `SNS` | HTTP | webhook (status callback) |

- **Auth:** per provider, resolved from `config_canal.credencial_ref` (secret manager) at the adapter; **never** hardcoded or logged.
- `WHEN the dispatch worker sends a message, THE SYSTEM SHALL select the adapter by (canal, config_canal.provedor) and call the provider under Resilience4j (timeout + circuit breaker + retry).`
- `IF the provider call fails after COMM_DISPATCH_MAX_RETRIES, THEN THE SYSTEM SHALL set estado_entrega=FALHADA, record the reason, emit journey-os.mensagem.falhada, and route the dispatch job to the DLQ.`
- `IF the provider is rate-limited (429), THEN THE SYSTEM SHALL back off and retry within the worker without failing the request path.`
- `WHEN a provider delivery/read webhook is received with a valid signature, THE SYSTEM SHALL normalize it into an EventoEntrega and advance the delivery state idempotently.`
- `IF a webhook signature is invalid, THEN THE SYSTEM SHALL reject it (401 'comm.webhook.assinatura-invalida') without mutating any message.`
- **Adding a channel/provider:** a new adapter under `infrastructure/channels` + a `config_canal` entry — no domain change.

## 2. Elasticsearch — index `communication-events` (fact)

- **Purpose:** append-only analytics projection of the message delivery lifecycle (one document per `evento_entrega`).
- **Access:** `direct-java-client` (per `project-context.json.stack.elastic.ingestMode`); no Logstash.
- **Auth:** `ELASTIC_URIS` (+ API key/credentials in non-local envs).
- **Tenant isolation:** documents carry `empresaId`; all queries filter by the current tenant (no cross-empresa leakage).
- `WHEN a delivery event is recorded, THE SYSTEM SHALL index it into communication-events (best-effort, non-blocking).`
- `IF Elasticsearch is unavailable, THEN THE SYSTEM SHALL NOT fail the dispatch/callback path; the fact index is reconciled afterwards from evento_entrega.`
- **Contract:** `docs/architecture/integrations/elastic-data-contract.md`.

## 3. Object storage (attachments/media) — out of MVP

- MVP: attachments/media are **referenced by external URL** in the rendered content; COMM does not upload/host them.
- `THE SYSTEM SHALL store media references as URLs and SHALL NOT proxy or transcode binary content in the MVP.`

## 4. SLA / rate limits / fallback (summary)

| System | Timeout | Breaker | Fallback |
|---|---|---|---|
| Channel providers | per-adapter (short) | yes | retry/backoff in worker → FALHADA + DLQ; channel fallback by routing |
| TechLab AI | 20s | 50% failure rate | 503 on Studio; CRUD/dispatch unaffected (`techlab-ai-integration.md`) |
| Elasticsearch | short | yes | skip index; async reconcile from evento_entrega |
| WRKS / ASST (Feign) | platform default | yes | cached AccessDecision / degraded asset source (`hub-integration.md`) |

## Referências

- `docs/architecture/integrations/elastic-data-contract.md` · `elastic-stack-integration.md`
- `docs/architecture/backend/standards/platform-patterns.md` (Feign + Resilience4j, outbox, DLQ)
- `adr/ADR-005-channel-adapter-pattern.md`
