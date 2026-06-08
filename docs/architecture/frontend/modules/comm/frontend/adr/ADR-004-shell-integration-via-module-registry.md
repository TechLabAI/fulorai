# ADR-004 — Integração com Shell via module registry

- **Status:** accepted

## Contexto

O Shell (`journey-os-web`) precisa descobrir o COMM (rota, label, ícone, deep links, permissões)
para montar navegação e carregar o módulo lazy, sem acoplar-se ao código interno do COMM. O Journey
OS já consolidou esse mecanismo no WRKS: descriptor estático em `config/module-descriptors.ts`
(fallback) + `ModuleShellIntegrationService` para registro em runtime.

## Decisão

1. O COMM expõe um **`CommShellIntegrationService`** (`libs/comm/integration`) e um
   **`COMM_MODULE_DESCRIPTOR`** (derivado de `comm.contract.ts`), registrados no Shell via
   `@journeyos/comm`.
2. O Shell registra o COMM em `apps/journey-os-web/src/app/config/module-descriptors.ts` (fallback
   estático) **e/ou** em runtime via `ModuleShellIntegrationService` — o mesmo mecanismo do WRKS.
3. O menu/deep links derivam das **permissões** via `NavigationService` (Access Layer): "Mensagens"
   (`comm.mensagem.ler`), "Roteamento" (`comm.roteamento.ler`) e "Canais" (`comm.canal.ler`) só
   aparecem com a permissão correspondente.
4. A navegação e o breadcrumb do COMM vêm de `libs/comm/navigation` (`comm.nav.config.ts`); o COMM
   **não** monta menu ad-hoc.

## Alternativas consideradas

1. **Rotas hardcoded no Shell** — rejeitada: acopla Shell ao COMM e quebra a descoberta uniforme.
2. **Cada módulo importado eagerly pelo Shell** — rejeitada: viola lazy loading e infla bundle.
3. **Registro só em runtime (sem descriptor estático)** — rejeitada: perde o fallback determinístico
   que o WRKS usa para build/lint verdes sem runtime.

## Consequências

- **Positivas:** Shell desacoplado; descoberta uniforme entre módulos; navegação derivada de RBAC;
  paridade com WRKS (build/lint do Shell continuam verdes ao adicionar o descriptor).
- **Negativas:** exige manter `comm.contract.ts` ↔ descriptor sincronizados (o generator cuida disso).

## Referências

- `02-architecture-blueprint.md` §5 · `04-frontend-architecture-direction.md` §7
- `docs/architecture/frontend/standards/access-layer-contracts.md`
- WRKS ADR-004 + registro no Shell (`WRKS_MODULE_DESCRIPTOR`, master plan Wave 0)
