# ADRs — INTL (Intelligence & Platform)

> Decisões arquiteturais do `intl-service`. Status: `proposed` | `accepted` | `superseded`.

## Índice

| ADR | Título | Status |
|---|---|---|
| [ADR-001](ADR-001-hexagonal-architecture.md) | Arquitetura hexagonal (Ports & Adapters) | accepted |
| [ADR-002](ADR-002-single-service-boundary.md) | Fronteira de serviço único (Copilot + Plataforma) | accepted |
| [ADR-003](ADR-003-event-platform-indexing-strategy.md) | Plataforma de dados: indexação descentralizada + contrato governado | accepted |
| [ADR-004](ADR-004-multitenant-strategy.md) | Multi-tenancy híbrida (PG schema-per-tenant + Elastic compartilhado) | accepted |
| [ADR-005](ADR-005-ai-copilot-integration.md) | AI Copilot via RAG fundamentado + TechLab AI | accepted |

## Mapa de Relações

```
ADR-001 (hexagonal) ──base── ADR-002, ADR-003, ADR-004, ADR-005
ADR-003 (plataforma de dados) ──restringe── ADR-005 (RAG lê o que ADR-003 governa)
ADR-004 (multi-tenancy) ──restringe── ADR-003 (discriminador empresa) + ADR-005 (filtro de recuperação)
ADR-005 (copilot) ──depende── TechLab AI (knowledge/orchestration) + Elasticsearch (recuperação)
```

## Processo

- Toda decisão com tradeoff visível vira ADR (não texto solto).
- ADRs nascem `proposed`; passam a `accepted` quando ratificadas; `superseded by ADR-YYY` quando
  substituídas.
- Decisões críticas do domínio extraídas do `_brief.md`: **plataforma de dados** (ADR-003) e
  **AI Copilot/RAG** (ADR-005).
