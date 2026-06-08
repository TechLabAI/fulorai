# ADRs — WRKS (Workspace & Identity)

> Decisões arquiteturais do serviço `wrks-service`. Cada decisão com tradeoff visível é um ADR.

## Índice

| ADR | Título | Status |
|---|---|---|
| [ADR-001](ADR-001-hexagonal-architecture.md) | Arquitetura hexagonal (Ports & Adapters) | accepted |
| [ADR-002](ADR-002-identity-authority.md) | WRKS como autoridade de identidade (Keycloak = IdP, RBAC do Journey OS) | accepted |
| [ADR-003](ADR-003-messaging-strategy.md) | Estratégia de mensageria (sync evaluate + async eventos via Kafka) | accepted |
| [ADR-004](ADR-004-multitenant-strategy.md) | Multi-tenancy: schema-per-tenant + WRKS como orquestrador de provisionamento | accepted |
| [ADR-005](ADR-005-token-session-model.md) | Modelo de token/sessão: JWT RS256 + refresh rotation + invalidação por versão | accepted |

## Mapa de Relações

```
ADR-001 (hexagonal) ── base de todos
ADR-002 (identity authority) ── decide a fronteira; depende de ADR-001
   └── ADR-005 (token/sessão) ── concretiza como a credencial é emitida/invalidada
ADR-004 (multi-tenancy) ── alinhado ao global shared/multi-empresa.md (ADR-001 global)
ADR-003 (messaging) ── habilita propagação de ADR-005 (modelo.acesso.alterado) + auditoria
```

## Processo

- Status possíveis: `proposed` | `accepted` | `superseded by ADR-YYY`.
- ADRs locais do serviço **não** substituem os ADRs globais (`docs/architecture/backend/adr/` e `docs/architecture/shared/`); refinam decisões específicas de WRKS alinhadas a eles.
- Mudança de decisão = novo ADR com `superseded by`, nunca edição destrutiva do aceito.
