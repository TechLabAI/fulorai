# ADR-001 — Padrão module-pattern (slicing canônico de libs)

- **Status:** accepted

## Contexto

O Journey OS FE é um workspace Nx multi-módulo com boundaries enforced por ESLint
(`nx-boundaries.md`). Cada módulo de negócio precisa de uma estrutura **previsível e idêntica**
para que generators, boundaries e o pipeline de arquitetura funcionem sem casos especiais. WRKS,
por ser a fundação, define o exemplo de referência.

## Decisão

WRKS adota **100% o padrão canônico `module-pattern`**: app lazy em `apps/wrks` e libs fatiadas em
`libs/wrks/{access, data-access, feature-*, integration, navigation, ui, styles}`, cada uma com
tags `type:*` + `scope:wrks` conforme `nx-boundaries.md`. O entry `wrks.module.ts` concentra
contrato, rotas, permission-map, feature-flags e nav config.

## Alternativas consideradas

1. **Lib única por módulo** (tudo em `libs/wrks`) — rejeitada: viola lazy por feature e infla bundle.
2. **Slicing livre por feature sem padrão fixo** — rejeitada: quebra generators e dependency rules;
   gera drift entre módulos.
3. **Estrutura por camada técnica global** (todas as features juntas) — rejeitada: viola
   `scope:<módulo>` e o isolamento entre módulos.

## Consequências

- **Positivas:** previsibilidade total; generators e boundaries funcionam sem exceção; onboarding
  trivial (todo módulo é igual); affected-CI preciso.
- **Negativas:** mais libs/arquivos de boilerplate por módulo; exige disciplina nas tags.

## Referências

- `docs/architecture/frontend/standards/nx-boundaries.md`
- `02-architecture-blueprint.md` §4 · `04-frontend-architecture-direction.md` §3
