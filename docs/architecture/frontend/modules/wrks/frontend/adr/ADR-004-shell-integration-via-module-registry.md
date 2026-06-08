# ADR-004 — Integração com Shell via module registry

- **Status:** accepted

## Contexto

O `journey-os-web` (Shell) precisa descobrir o WRKS (rótulo de menu, rota, ícone, deep links,
permissões) e registrá-lo na navegação. Há duas vias possíveis: descoberta estática em build-time
e registro dinâmico em runtime.

## Decisão

WRKS se integra ao Shell por **duas camadas complementares**:

1. **Estático (fallback):** um descriptor em `module-descriptors.ts` do Shell + entrada em
   `shell-routes.ts` (gerados pelo scaffold) garantem que a module é conhecida em build-time.
2. **Runtime:** `WrksShellIntegrationService` (`libs/wrks/integration`) registra a module no
   `bootstrap` (`wrks.bootstrap.ts`) usando `wrks.contract.ts` (`ModuleMenuMetadata` + permissões +
   flags). A navegação efetiva é derivada por `NavigationService` a partir das permissões.

A visibilidade final de menu/ações é **sempre** decidida pela Access Layer
(`AccessDecisionService`/`NavigationService`), nunca hardcoded no descriptor.

## Alternativas consideradas

1. **Só estático** — rejeitada: não reflete permissões em runtime nem troca de empresa.
2. **Só runtime** — rejeitada: sem fallback em build-time, dificulta SSR/preload e testes.

## Consequências

- **Positivas:** module descoberta em build-time e ajustada em runtime por RBAC/empresa; desacopla
  Shell do conteúdo do menu.
- **Negativas:** duas fontes (descriptor estático + contrato runtime) a manter em sincronia — o
  scaffold gera ambas a partir de `wrks.contract.ts` para evitar drift.

## Referências

- `wrks.contract.ts`, `wrks.bootstrap.ts`, `wrks.nav.config.ts`
- `docs/architecture/frontend/standards/access-layer-contracts.md` (`NavigationService`)
- ADR-003 (lazy module)
