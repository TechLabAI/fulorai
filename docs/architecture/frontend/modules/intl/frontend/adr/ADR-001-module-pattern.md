# ADR-001 — Padrão module-pattern (slicing canônico de libs)

- **Status:** accepted

## Contexto

INTL precisa de uma estrutura de libs Nx consistente com os demais módulos do Journey OS FE
(WRKS já adotou). O módulo tem três features (Copilot, Knowledge, Analytics) + camadas de acesso,
data-access, integração e navegação.

## Decisão

Adotar **100%** o padrão canônico `module-pattern`
(`docs/architecture/frontend/standards/module-pattern.md`):

- `apps/intl` (host fino) + `libs/intl/shell-entry` (entry-lib `@journeyos/intl`).
- `libs/intl/{feature-copilot,feature-knowledge,feature-analytics}` (`type:feature`).
- `libs/intl/{data-access,access,integration,navigation,ui,styles}` com tags Nx canônicas
  (`type:*` + `scope:intl`).
- Direções de dependência regidas por `nx-boundaries.md`; **proibido** importar `scope:<outro>`.

## Alternativas consideradas

- **Lib única `libs/intl`** sem slicing — rejeitada: viola boundaries, impede lazy por feature,
  diverge de WRKS.
- **Estrutura ad-hoc por feature** — rejeitada: perde a consistência cross-módulo que o Shell e o
  gerador `@journeyos/internal:module` assumem.

## Consequências

- **Positivas:** consistência com WRKS e com o gerador de scaffold; lazy-loading por feature;
  ArchUnit/ESLint boundaries aplicáveis; onboarding previsível.
- **Negativas:** mais libs para gerenciar; overhead de configuração por lib (mitigado pelo gerador).

## Referências

- `docs/architecture/frontend/standards/module-pattern.md`
- `docs/architecture/frontend/standards/nx-boundaries.md`
- WRKS ADR-001 (espelho)
