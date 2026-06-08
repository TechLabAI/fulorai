# ADR-004 — Integração com Shell via module registry

- **Status:** accepted

## Contexto

INTL precisa aparecer na navegação do Shell (`journey-os-web`) e ter suas rotas carregadas lazy,
sem que o Shell conheça os detalhes internos do módulo. O menu deve respeitar RBAC (`intl.*`).

## Decisão

Integrar via **module registry**:

- `libs/intl/shell-entry/intl.descriptor.ts` exporta `INTL_MODULE_DESCRIPTOR` (menu metadata +
  rota lazy + permissões + flags).
- O Shell registra esse descriptor em `apps/journey-os-web/src/app/config/module-descriptors.ts`
  (fallback estático) — o mesmo mecanismo usado por WRKS.
- Em runtime, `IntlShellIntegrationService` (`libs/intl/integration`) pode registrar/atualizar o
  módulo no `ModuleShellIntegration` (alinhado ao padrão; substituível por TCE em prod).
- O `NavigationService` filtra deep-links por permissão via `AccessDecisionService` — itens sem
  permissão **não aparecem**.

## Alternativas consideradas

- **Rotas hard-coded no Shell** — rejeitada: acopla o Shell a cada módulo; não escala.
- **Descriptor dentro do host `apps/intl`** — rejeitada: o Shell teria de importar a app (viola
  ADR-003/ADR-006).

## Consequências

- **Positivas:** Shell desacoplado; menu derivado de RBAC; consistente com WRKS; registro testável.
- **Negativas:** duas vias de registro (estático + runtime) a manter em sincronia (documentado no
  SPEC-06).

## Referências

- WRKS ADR-004 + SPEC-06 (espelho) · `docs/architecture/frontend/standards/bootstrap-flow.md`
- `apps/journey-os-web/src/app/config/module-descriptors.ts`
