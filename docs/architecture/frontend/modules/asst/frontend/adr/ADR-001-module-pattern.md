# ADR-001 — Padrão module-pattern (slicing canônico de libs)

- **Status:** accepted

## Contexto

O Journey OS FE é um workspace Nx multi-módulo com boundaries enforced por ESLint
(`nx-boundaries.md`). Cada módulo de negócio precisa de uma estrutura **previsível e idêntica** para
que o generator `@journeyos/internal:module`, os boundaries e o pipeline de arquitetura funcionem sem
casos especiais. ASST é o segundo módulo de domínio (após WRKS, a fundação) e deve replicar o padrão.

## Decisão

ASST adota **100% o padrão canônico `module-pattern`**: host fino em `apps/asst`, entry como library
em `libs/asst/shell-entry` (ADR-003/ADR-006) e libs fatiadas em
`libs/asst/{access, data-access, feature-asset-library, feature-asset-detail, feature-asset-studio,
feature-approval-workflow, integration, navigation, ui, styles}`, cada uma com tags `type:*` +
`scope:asst` conforme `nx-boundaries.md`. O `shell-entry` concentra contrato, rotas, permission-map,
feature-flags e nav config.

## Alternativas consideradas

1. **Lib única por módulo** (tudo em `libs/asst`) — rejeitada: viola lazy por feature e infla bundle.
2. **Slicing livre por feature sem padrão fixo** — rejeitada: quebra o generator e as dependency rules;
   gera drift entre módulos.
3. **Estrutura por camada técnica global** (todas as features de todos os módulos juntas) — rejeitada:
   viola `scope:<módulo>` e o isolamento entre módulos.

## Consequências

- **Positivas:** previsibilidade total; generator e boundaries funcionam sem exceção; onboarding
  trivial (todo módulo é igual ao WRKS); affected-CI preciso.
- **Negativas:** mais libs/arquivos de boilerplate por módulo; exige disciplina nas tags.

## Referências

- `docs/architecture/frontend/standards/nx-boundaries.md`
- `docs/architecture/frontend/standards/module-pattern.md`
- `02-architecture-blueprint.md` §4 · `04-frontend-architecture-direction.md` §3
- WRKS ADR-001 (referência de fundação)
