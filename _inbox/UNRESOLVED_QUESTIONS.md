# Unresolved questions — discovery ingestion (D-073)

> Source: `D:\01_Trabalho\Cybersoft\TechLab IA\techlab-ba\projects\journey-os`
> Generated at: 2026-06-04T17:30:46Z

The discovery ingestion populated `project-context.json` with the fields it could extract confidently. The items below need human input before running `/new-project P1`. Edit `project-context.json` directly, then proceed.

## Open items

_(no unresolved items — every required field was extracted)_
## Field provenance

Which input file each extracted field came from:

- `_extensions.compliance` ← `business/constraints.md`
- `_extensions.frontend_reference` ← `design/frontend-reference/`
- `_extensions.lbc_personas` ← `business/lean-business-case.md`
- `_extensions.wireframe` ← `design/wireframe.md`
- `ai.hasAi` ← `handoff-package.md`
- `modules.registry` ← `handoff-package.md`
- `multiTenancy.globalSchema` ← `handoff-package.md`
- `multiTenancy.isolationStrategy` ← `architecture/adr/ADR-003-multi-tenancy-schema-per-empresa.md`
- `multiTenancy.mode` ← `handoff-package.md (D-293 normalized: isolation/term decoupled, mode from LBC classification)`
- `multiTenancy.term` ← `architecture/adr/ADR-003-multi-tenancy-schema-per-empresa.md`
- `project.codeName` ← `handoff-package.md`
- `project.description` ← `business/lean-business-case.md`
- `project.displayName` ← `business/lean-business-case.md`
- `project.issuePrefix` ← `handoff-package.md`
- `project.name` ← `business/lean-business-case.md`
- `project.rigorLevel` ← `handoff-package.md`
- `project.segment` ← `handoff-package.md`
- `stack.backend.framework` ← `architecture/adr/ADR-001-backend-jvm-java.md`
- `stack.backend.language` ← `architecture/adr/ADR-001-backend-jvm-java.md`
- `stack.backend.packageBase` ← `handoff-package.md`
- `stack.backend.version` ← `architecture/adr/ADR-001-backend-jvm-java.md`
- `stack.database.engine` ← `handoff-package.md`
- `stack.elastic.indices` ← `handoff-package.md`
- `stack.frontend.framework` ← `architecture/adr/ADR-005-frontend-angular-nx.md`
- `stack.frontend.monorepoTool` ← `architecture/adr/ADR-005-frontend-angular-nx.md`
- `stack.frontend.npmScope` ← `handoff-package.md`
- `stack.messaging.enabled` ← `handoff-package.md`
- `stack.search.engine` ← `handoff-package.md`

## ADRs preserved

13 ADR file(s) copied verbatim to `_inbox/adr/` as discovery history. The framework's own ADR generation produces a parallel set under `docs/architecture/backend/adr/` in P2.

- `_inbox/adr/ADR-001-backend-jvm-java.md`
- `_inbox/adr/ADR-002-ia-techlab-orquestrada.md`
- `_inbox/adr/ADR-003-multi-tenancy-schema-per-empresa.md`
- `_inbox/adr/ADR-004-arquitetura-hexagonal.md`
- `_inbox/adr/ADR-005-frontend-angular-nx.md`
- `_inbox/adr/ADR-006-postgresql-system-of-record.md`
- `_inbox/adr/ADR-007-elasticsearch-search-observability.md`
- `_inbox/adr/ADR-008-event-first-outbox-kafka.md`
- `_inbox/adr/ADR-009-routing-engine-explicavel.md`
- `_inbox/adr/ADR-010-comunicacao-via-integracao.md`
- `_inbox/adr/ADR-011-maturity-score-deterministico.md`
- `_inbox/adr/ADR-012-cqrs-light.md`
- `_inbox/adr/ADR-013-realtime-streaming-ui.md`
