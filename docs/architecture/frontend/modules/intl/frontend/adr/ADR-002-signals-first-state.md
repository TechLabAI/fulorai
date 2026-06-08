# ADR-002 — Estado Signals-first (sem NgRx)

- **Status:** accepted

## Contexto

INTL tem estado de UI não-trivial: conversa corrente do Copilot (lista de mensagens com inserção
otimista e bolha `PENDENTE`), filtros + paginação da Base de Conhecimento, e dashboards de
Analytics. É tentador alcançar um store global (NgRx), mas o padrão do Journey OS FE é Signals.

## Decisão

Usar **Signals** como mecanismo único de estado de UI, **sem NgRx**:

- Cada facade em `libs/intl/data-access` mantém `signal<T>` **privado** + expõe `.asReadonly()`.
- Derivações via `computed()` (ex.: `podeEnviar = !temPendente() && textoValido()`).
- Efeitos (`effect()`) para reagir à troca de empresa (reset de conversa/listas).
- RxJS só na borda de HTTP e no `AbortController` de cancelamento de pergunta.

## Alternativas consideradas

- **NgRx** — rejeitada: peso desproporcional ao escopo; diverge do padrão do projeto; boilerplate.
- **`BehaviorSubject` manual nas facades** — rejeitada: Signals dão derivação/leitura mais simples
  e integram melhor com `OnPush`.

## Consequências

- **Positivas:** menos boilerplate; consistência com WRKS; `OnPush` natural; testes de facade
  simples.
- **Negativas:** orquestração de fluxos assíncronos complexos (otimismo + cancelamento) fica na
  facade — exige disciplina (coberta por testes unitários da `CopilotFacade`).

## Referências

- `docs/architecture/frontend/standards/access-layer-contracts.md`
- WRKS ADR-002 (espelho) · `05-state-and-data-flow.md`
