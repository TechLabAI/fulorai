# ADR-002 — Estado Signals-first (sem NgRx)

- **Status:** accepted

## Contexto

O WRKS tem estado de tela moderado (listas de usuários, org structure, lista de empresas) e
**não** tem fluxos de estado global complexos — o estado transversal (sessão, empresa, RBAC) já
vive na Access Layer (`@journeyos/shared/access-*`). Precisamos de um modelo de estado simples,
reativo e alinhado ao Angular moderno.

## Decisão

Usar **Signals-first**: as facades em `libs/wrks/data-access` expõem `signal<T>` privado +
`.asReadonly()` público, com `computed()` para derivações. **Sem NgRx**, sem `BehaviorSubject`
manual. `Observable` de HTTP é convertido para signal na facade. Componentes são `OnPush` e leem
signals diretamente.

## Alternativas consideradas

1. **NgRx (store + effects)** — rejeitada: overhead desproporcional ao tamanho do estado; o estado
   global relevante já é responsabilidade da Access Layer.
2. **`BehaviorSubject` em services** — rejeitada: mais verboso, sujeito a memory leaks e menos
   ergonômico que signals com `OnPush`.
3. **Component-only state** — rejeitada: dificulta reuso entre componentes da mesma feature e teste.

## Consequências

- **Positivas:** menos boilerplate; change detection eficiente com `OnPush`; alinhado ao roadmap
  Angular; fácil de testar (signals síncronos).
- **Negativas:** padrões de signals ainda evoluindo; integração com fluxos RxJS pontuais exige
  cuidado (`toSignal`/`toObservable`).

## Referências

- `05-state-and-data-flow.md`
- `docs/architecture/frontend/standards/access-layer-contracts.md`
