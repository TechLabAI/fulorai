# ADR-002 — Estado Signals-first (sem NgRx) — SALE

- **Status:** accepted
- **Transversal:** sim

## Contexto

O estado de UI do SALE (board do pipeline, oportunidade selecionada, ofertas, compras, modelos de
atribuição, breakdown, funil de receita, LTV) é predominantemente **local por feature** e derivável. O
projeto padronizou Signals como mecanismo de estado de UI, evitando o overhead de NgRx. O caso do
**Kanban** (mover card com optimistic update + rollback — ADR-005) é bem servido por signals + um
snapshot do último estado confirmado.

## Decisão

Estado de UI via **Angular Signals**, encapsulado em **facades** na lib `data-access`:

- `signal<T>` **privado** + exposição `.asReadonly()` pública.
- Derivações via `computed()` (soma de valor por coluna do Kanban, ações disponíveis por estado da
  oportunidade + permissão, versão de modelo ativa, conservação de receita no breakdown).
- `effect()` para reagir à **troca de empresa** (invalidar board/seleção/listas em tela).
- **Optimistic move** do Kanban mantém o último estado confirmado do `board` para **rollback** em falha
  (ADR-005) — sem necessidade de store global.
- **Sem NgRx** e **sem `BehaviorSubject` manual**. RxJS apenas na borda HTTP (interop pontual).

Estado transversal (sessão/empresa/RBAC) **não** é duplicado no SALE — vem de `@journeyos/shared/access-*`.

## Alternativas consideradas

- **NgRx Store/Effects** — rejeitada: complexidade desproporcional ao estado local do módulo (mesmo com
  o Kanban, o optimistic+rollback cabe num signal com snapshot).
- **`BehaviorSubject` em services** — rejeitada: mais verboso e propenso a leaks que signals.

## Consequências

**Positivas:** menos boilerplate; reatividade fina; OnPush natural; testes simples; rollback do Kanban
trivial com snapshot de signal. **Negativas:** disciplina necessária para não vazar `signal` mutável
(mitigado por `.asReadonly()` e revisão de boundaries).

## Referências

- ADR-002 dos módulos WRKS/ASST/INTL/LEAD/COMM · `standards/module-pattern.md` · ADR-005 (Kanban)
