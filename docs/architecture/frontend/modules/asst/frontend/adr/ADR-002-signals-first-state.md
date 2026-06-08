# ADR-002 — Estado Signals-first (sem NgRx)

- **Status:** accepted

## Contexto

O ASST gerencia estado de tela com várias superfícies: catálogo paginado com filtros, detalhe de
asset com histórico de versões, estado do Asset Studio (composing/degradado/draft) e fila de
aprovação. Precisa de um modelo de estado reativo, simples e local, alinhado ao restante do Journey
OS FE (Signals-first, sem store global).

## Decisão

1. Todo estado de tela vive em **Signals locais nas facades** de `libs/asst/data-access`:
   `signal<T>` privado + `.asReadonly()` público (`catalogo`, `assetSelecionado`, `versoes`,
   `studioState`, `filaAprovacao`, `loading`, `error`).
2. **Sem NgRx, sem `BehaviorSubject` manual.** `Observable` de HTTP é convertido para signal na facade.
3. Derivações via `computed()`: ações disponíveis por estado do asset, versão vigente destacada,
   contagem da fila, visibilidade de botões por permissão.
4. Estado transversal (sessão/empresa/RBAC) **não** é replicado no ASST — é consumido da Access Layer
   (`@journeyos/shared/access-*`).

## Alternativas consideradas

1. **NgRx (store/effects)** — rejeitada: overhead desproporcional ao escopo; o Journey OS padronizou
   Signals-first.
2. **`BehaviorSubject` por facade** — rejeitada: mais boilerplate, menos integrado ao change detection
   `OnPush`, propenso a leaks.
3. **Estado em componentes (sem facade)** — rejeitada: dificulta reuso entre features e teste isolado.

## Consequências

- **Positivas:** menos boilerplate; integração natural com `OnPush`; estado testável na facade;
  consistência com WRKS e os demais módulos.
- **Negativas:** disciplina para não vazar `signal` mutável; padrões de cancelamento/invalidação na
  troca de empresa precisam ser explícitos (ver ADR-005 multi-empresa global / ADR-005 deste módulo).

## Referências

- `04-frontend-architecture-direction.md` §6 · `05-state-and-data-flow.md`
- `docs/architecture/frontend/standards/module-pattern.md`
- WRKS ADR-002 (signals-first)
