# ADRs — JRNY (Journey & Routing)

> Decisões arquiteturais do serviço `jrny-service`. Cada decisão com tradeoff visível é um ADR.

## Índice

| ADR | Título | Status |
|---|---|---|
| [ADR-001](ADR-001-hexagonal-architecture.md) | Arquitetura hexagonal (Ports & Adapters) | accepted |
| [ADR-002](ADR-002-single-service-boundary.md) | Fronteira: single service (builder + routing engine + decision log coesos) | accepted |
| [ADR-003](ADR-003-messaging-strategy.md) | Mensageria + IA: roteamento dirigido por evento (Kafka) + assist sync resiliente (TechLab AI) | accepted |
| [ADR-004](ADR-004-multitenant-strategy.md) | Multi-tenancy: schema-per-tenant (`emp_<slug>`), JRNY só lê/escreve no schema do tenant | accepted |
| [ADR-005](ADR-005-routing-engine-model.md) | Routing Engine determinístico + decision log imutável + assist de IA com fallback | accepted |

## Mapa de Relações

```
ADR-001 (hexagonal) ── base de todos
ADR-002 (single service) ── fronteira do serviço; depende de ADR-001
ADR-004 (multi-tenancy) ── alinhado ao global shared/multi-empresa.md (ADR-001 global)
ADR-005 (routing engine + decision log) ── núcleo do domínio; concretiza as invariantes de 03
   └── ADR-003 (mensageria/IA) ── roteamento reage a eventos; assist chama TechLab AI resiliente (opcional)
```

## Processo

- Status possíveis: `proposed` | `accepted` | `superseded by ADR-YYY`.
- ADRs locais do serviço **não** substituem os ADRs globais (`docs/architecture/backend/adr/` e `docs/architecture/shared/`); refinam decisões específicas de JRNY alinhadas a eles.
- Mudança de decisão = novo ADR com `superseded by`, nunca edição destrutiva do aceito.
