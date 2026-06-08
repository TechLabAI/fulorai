# Integration Contracts — JRNY (external systems)

> External (non-Journey-OS) systems JRNY integrates with. TechLab AI has its own contract
> (`techlab-ai-integration.md`). EARS for behavior.

## 1. Elasticsearch — indices `journey-events` + `routing-decisions` (fact)

- **Purpose:** append-only telemetry/audit projections. `journey-events` = one document per stage
  transition; `routing-decisions` = one document per routing decision (the decision log).
  `domainContext=JRNY`.
- **Access:** `direct-java-client` (per `project-context.json.stack.elastic.ingestMode`); no Logstash.
- **Auth:** `ELASTIC_URIS` (+ API key/credentials in non-local envs).
- **Tenant isolation:** documents carry `empresaId`; all queries filter by the current tenant (no cross-empresa leakage).
- `WHEN a routing decision is persisted, THE SYSTEM SHALL index it into routing-decisions (best-effort, non-blocking).`
- `WHEN a stage transition is persisted, THE SYSTEM SHALL index it into journey-events (best-effort, non-blocking).`
- `IF Elasticsearch is unavailable, THEN THE SYSTEM SHALL NOT fail or revert the routing decision AND SHALL reconcile the index afterwards (PostgreSQL is the source of truth).`
- **Contract:** `docs/architecture/integrations/elastic-data-contract.md`.

## 2. SLA / rate limits / fallback (summary)

| System | Timeout | Breaker | Fallback |
|---|---|---|---|
| TechLab AI (`orchestration`) | 2s (short — golden path) | 50% failure rate | deterministic routing (`assist_ia=INDISPONIVEL`); never blocks (`techlab-ai-integration.md`) |
| Elasticsearch (`journey-events`/`routing-decisions`) | short | yes | decision unaffected; async reindex from PostgreSQL |
| WRKS (Feign) | platform default | yes | cached AccessDecision (`hub-integration.md`) |
| ASST (Feign `AssetQueryClient`) | platform default | yes | last-known stage content ref; non-blocking to routing |

## Referências

- `docs/architecture/integrations/elastic-data-contract.md` · `elastic-stack-integration.md`
- `docs/architecture/backend/standards/platform-patterns.md` (Feign + Resilience4j)
