# ADR-002 — Estado Signals-first (sem NgRx) — LEAD

- **Status:** accepted
- **Transversal:** sim

## Contexto

O estado de UI do LEAD (fila, lead selecionado, score, segmentos, surveys, regras) é
predominantemente **local por feature** e derivável. O projeto padronizou Signals como mecanismo de
estado de UI, evitando o overhead de NgRx.

## Decisão

Estado de UI via **Angular Signals**, encapsulado em **facades** na lib `data-access`:

- `signal<T>` **privado** + exposição `.asReadonly()` pública.
- Derivações via `computed()` (faixa do score, ações disponíveis por estado+permissão, versão de regra
  ativa, contagem por segmento, visibilidade do badge `assistIa`).
- `effect()` para reagir à **troca de empresa** (invalidar fila/seleção em tela).
- **Sem NgRx** e **sem `BehaviorSubject` manual**. RxJS apenas na borda HTTP (interop pontual).

Estado transversal (sessão/empresa/RBAC) **não** é duplicado no LEAD — vem de `@journeyos/shared/access-*`.

## Alternativas consideradas

- **NgRx Store/Effects** — rejeitada: complexidade desproporcional ao estado local do módulo.
- **`BehaviorSubject` em services** — rejeitada: mais verboso e propenso a leaks que signals.

## Consequências

**Positivas:** menos boilerplate; reatividade fina; OnPush natural; testes simples. **Negativas:**
disciplina necessária para não vazar `signal` mutável (mitigado por `.asReadonly()` e revisão de boundaries).

## Referências

- ADR-002 dos módulos WRKS/ASST/INTL · `standards/module-pattern.md`
