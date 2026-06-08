# ADR-002 — Estado Signals-first (sem NgRx) — JRNY

- **Status:** accepted
- **Transversal:** sim

## Contexto

O estado de UI do JRNY (lista de jornadas, jornada em edição, estágios, regras, estado de jornada do
lead, decisões, analytics) é predominantemente **local por feature** e derivável. O projeto padronizou
Signals como mecanismo de estado de UI, evitando o overhead de NgRx.

## Decisão

Estado de UI via **Angular Signals**, encapsulado em **facades** na lib `data-access`:

- `signal<T>` **privado** + exposição `.asReadonly()` pública.
- Derivações via `computed()` (jornada editável?, ações disponíveis por estado+permissão, resumo da
  condição da regra, versão de regra ativa, visibilidade do badge `assistIa`, funil).
- `effect()` para reagir à **troca de empresa** (invalidar jornadas/builder em tela).
- **Sem NgRx** e **sem `BehaviorSubject` manual**. RxJS apenas na borda HTTP (interop pontual).

Estado transversal (sessão/empresa/RBAC) **não** é duplicado no JRNY — vem de `@journeyos/shared/access-*`.

> **Nota de complexidade:** JRNY compartilha o estado "jornada em edição" entre builder, stage-editor e
> routing-engine. A consolidação desse estado fica numa facade do `data-access` (ou em `libs/jrny/facade`
> se a Specs justificar) — sempre Signals, nunca NgRx.

## Alternativas consideradas

- **NgRx Store/Effects** — rejeitada: complexidade desproporcional ao estado local do módulo, mesmo
  sendo o mais complexo; o compartilhamento builder↔regras é resolvível com facade + signals.
- **`BehaviorSubject` em services** — rejeitada: mais verboso e propenso a leaks que signals.

## Consequências

**Positivas:** menos boilerplate; reatividade fina; OnPush natural; testes simples. **Negativas:**
disciplina necessária para não vazar `signal` mutável (mitigado por `.asReadonly()` e revisão de
boundaries); o estado compartilhado do builder exige uma facade bem desenhada.

## Referências

- ADR-002 dos módulos WRKS/ASST/INTL/LEAD/COMM · `standards/module-pattern.md`
