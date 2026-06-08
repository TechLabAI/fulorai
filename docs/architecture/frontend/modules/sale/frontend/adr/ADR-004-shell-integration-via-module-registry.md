# ADR-004 — Integração com o Shell via module registry — SALE

- **Status:** accepted
- **Transversal:** sim

## Contexto

O Shell precisa descobrir rotas, item de menu, permissões e flags do SALE sem conhecer seus detalhes
internos. Há dois caminhos: registro estático (descriptor) e registro em runtime
(`ModuleShellIntegrationService`). Em produção, o TCE/governança pode substituir/filtrar o registro.

## Decisão

SALE integra ao Shell por **duas vias complementares**:

1. **Estática (fallback):** `SALE_MODULE_DESCRIPTOR` (de `@journeyos/sale`) registrado em
   `apps/journey-os-web/src/app/config/module-descriptors.ts`. Fornece menu/route/permissões/flags.
2. **Runtime:** `SaleShellIntegrationService` (em `libs/sale/integration`) registra/atualiza o módulo
   no boot (`sale.bootstrap.ts`) e expõe breadcrumbs/navegação via `navigation`.

A visibilidade de menu/ações é filtrada por `NavigationService` + `AccessDecisionService` (permissões
`sale.*`). O **registro efetivo no Shell** é tarefa do **implement P1** (issue `FE-SALE-003`), como nos
módulos anteriores (WRKS/ASST/INTL/LEAD/COMM).

## Alternativas consideradas

- **Somente estático** — rejeitada: não cobre registro/governança em runtime (TCE).
- **Somente runtime** — rejeitada: perde fallback determinístico em build/SSR/test.

## Consequências

**Positivas:** Shell desacoplado; fallback + runtime; governança em prod. **Negativas:** dois pontos de
registro a manter consistentes (mitigado pelo descriptor único como fonte).

## Referências

- ADR-004 de WRKS/ASST/INTL/LEAD/COMM · `standards/access-layer-contracts.md` · SPEC-06 (shell-integration)
