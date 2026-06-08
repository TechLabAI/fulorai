# TechLab AI Integration — WRKS

> **WRKS consumes NO TechLab AI capabilities.**

WRKS is the foundation identity/RBAC/multi-tenancy service. It has no AI use case in the MVP
(no orchestration, document_composition, knowledge, or analytics). Therefore:

- No `@FeignClient` to TechLab AI.
- No DTOs generated from `integrations/techlab-ai/openapi.json` for this service.
- No TechLab AI events consumed/produced.

The CLAUDE.md "Endpoints consumed by each module" table requires **no row** for WRKS.

> If a future feature needs AI (e.g. anomaly detection on access patterns), it must be added
> via a new `/be-architect-vision` round and routed through TechLab AI over HTTP (never call an
> AI provider directly from Java — platform rule).
