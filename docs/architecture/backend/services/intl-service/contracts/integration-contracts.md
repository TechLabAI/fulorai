# Integration Contracts — intl-service (INTL)

> Sistemas externos consumidos por INTL e suas políticas de auth/SLA/fallback.
> EARS guide: `docs/architecture/backend/standards/ears-notation.md`.

## 1. TechLab AI (serviço externo HTTP)

| Item | Valor |
|---|---|
| Base URL | `TECHLAB_AI_BASE_URL` (local `http://localhost:8090`) |
| Auth | JWT (toggle `TECHLAB_AI_JWT_ENABLED`); local `false` |
| Capabilities | `knowledge`, `orchestration` (`analytics` pós-MVP) |
| Timeout | `TECHLAB_AI_TIMEOUT_MS` (default 20000) |
| Circuit breaker | failure-rate 50%, wait-in-open 30s |
| Fallback | copilot → recuperação-apenas (`DEGRADADA`); embedding → `503` p/ retry |
| Contrato | `contracts/techlab-ai-integration.md`; DTOs gerados de `openapi.json` |

## 2. Elasticsearch 9.x (infra adjacente)

| Item | Valor |
|---|---|
| Cliente | `backend/services/elastic-client-lib` (`SearchPort`/`IndexPort`) |
| URL | `ELASTICSEARCH_URL` (local `http://localhost:9200`) |
| Auth | local: nenhuma; prod: user/pass ou API key + TLS |
| Índices próprios | `journey-os_ai-copilot-events` (fact), `journey-os_knowledge-nodes` (dimension) |
| Índices lidos | `journey-os_*` (facts dos módulos) — read-only |
| DLQ | `journey-os_dlq` |
| Contrato de dado | `docs/architecture/integrations/elastic-data-contract.md` (bloco de 8 campos, D-269) |
| Fallback | leitura indisponível → `503`; bulk falho → DLQ + retry do caller |

EARS:
- IF o Elasticsearch está indisponível para recuperação, THEN THE SYSTEM SHALL responder ao copiloto com `NAO_FUNDAMENTADA` (sem evidência) ou `503` na analítica.
- THE SYSTEM SHALL usar doc-id determinístico em toda projeção para garantir idempotência.

## 3. Kafka / AWS MSK (event bus)

| Item | Valor |
|---|---|
| Bootstrap | `KAFKA_BOOTSTRAP_SERVERS` |
| Consumer group | `intl-service` |
| Tópicos consumidos | `journey-os.asset.versao.publicada`, `journey-os.empresa.provisionada`, `journey-os.modelo.acesso.alterado` |
| Tópico publicado | `journey-os.copilot.resposta.gerada` |
| Idempotência | por `eventId`; DLQ de mensageria após retries |

## 4. PostgreSQL + pgVector

| Item | Valor |
|---|---|
| URL | `INTL_DB_URL` (local `jdbc:postgresql://localhost:5432/journeyos`) |
| Schema | `emp_<slug>` (resolvido por `EmpresaContextHolder`) |
| Extensões | `pgcrypto`, `vector` (criadas pela V1 global do MIG) |
| ddl-auto | `validate` |

## 5. Matriz de degradação

| Dependência | Indisponível → | Impacto |
|---|---|---|
| TechLab AI | copilot `DEGRADADA` / embedding `503` | resposta sem síntese; nó fica `RASCUNHO`. |
| Elasticsearch (read) | copilot `NAO_FUNDAMENTADA` / analytics `503` | sem evidência/agregação. |
| Elasticsearch (write) | projeção → DLQ + retry | auditoria/analytics atrasadas. |
| WRKS (AccessDecision) | `403`/`503` conforme cache | operação bloqueada (fail-closed). |
| Kafka | consumo pausa, producer bufferiza/retry | ingestão/eventos atrasados (eventual). |
