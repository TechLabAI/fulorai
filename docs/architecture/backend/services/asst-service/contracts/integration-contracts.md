# Integration Contracts — ASST (external systems)

> External (non-Journey-OS) systems ASST integrates with. TechLab AI has its own contract
> (`techlab-ai-integration.md`). EARS for behavior.

## 1. Elasticsearch — index `assets` (dimension)

- **Purpose:** full-text search + Asset Intelligence projection (one document per asset reflecting current state + tags).
- **Access:** `direct-java-client` (per `project-context.json.stack.elastic.ingestMode`); no Logstash.
- **Auth:** `ELASTIC_URIS` (+ API key/credentials in non-local envs).
- **Tenant isolation:** documents carry `empresaId`; all queries filter by the current tenant (no cross-empresa leakage in search).
- `WHEN an asset is created, a version is published, or tags change, THE SYSTEM SHALL upsert the asset document into the assets index (best-effort, non-blocking).`
- `IF Elasticsearch is unavailable, THEN THE SYSTEM SHALL NOT fail the write path AND SHALL fall back to PostgreSQL filtering for listing; the index is reconciled afterwards.`
- **Contract:** `docs/architecture/integrations/elastic-data-contract.md`.

## 2. Object storage (binaries) — out of MVP

- MVP: binaries (images/video) are **referenced by external URL** in `versao_asset.binarios`; ASST does not upload/host them.
- `THE SYSTEM SHALL store binary references as URLs with mime/size metadata and SHALL NOT proxy or transcode binary content in the MVP.`
- S3 / presigned-upload is a post-MVP assumption (see `06-risks-gaps-assumptions.md`).

## 3. SLA / rate limits / fallback (summary)

| System | Timeout | Breaker | Fallback |
|---|---|---|---|
| Elasticsearch | short (search path) | yes | PostgreSQL filtering; async reindex |
| TechLab AI | 20s | 50% failure rate | 503 on Studio; CRUD unaffected (`techlab-ai-integration.md`) |
| WRKS (Feign) | platform default | yes | cached AccessDecision (`hub-integration.md`) |

## Referências

- `docs/architecture/integrations/elastic-data-contract.md` · `elastic-stack-integration.md`
- `docs/architecture/backend/standards/platform-patterns.md` (Feign + Resilience4j)
