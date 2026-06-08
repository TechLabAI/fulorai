# ADR-002 — Estado Signals-first (sem NgRx)

- **Status:** accepted

## Contexto

O COMM gerencia estado de tela com várias superfícies: catálogo paginado de templates com filtros,
editor de template com validação de placeholders, estado do Template Studio (composing/degradado/draft),
CRUD de regras de roteamento, lista/detalhe de mensagens com **timeline de entrega evoluindo por
polling** e config de canais. Precisa de um modelo de estado reativo, simples e local, alinhado ao
restante do Journey OS FE (Signals-first, sem store global).

## Decisão

1. Todo estado de tela vive em **Signals locais nas facades** de `libs/comm/data-access`:
   `signal<T>` privado + `.asReadonly()` público (`catalogoTemplates`, `templateSelecionado`,
   `studioState`, `regras`, `mensagens`, `mensagemSelecionada`, `eventosEntrega`, `canais`,
   `loading`, `error`).
2. **Sem NgRx, sem `BehaviorSubject` manual.** `Observable` de HTTP é convertido para signal na facade.
   O **polling de entrega** usa `interval` RxJS (com backoff) convertido para signal — o RxJS fica
   confinado à facade; a feature consome só o signal (ADR-005).
3. Derivações via `computed()`: ações disponíveis por estado do template, `estadoTerminal` da mensagem
   (controla o polling), contagem por estado de entrega, visibilidade de botões por permissão.
4. Estado transversal (sessão/empresa/RBAC) **não** é replicado no COMM — é consumido da Access Layer
   (`@journeyos/shared/access-*`).

## Alternativas consideradas

1. **NgRx (store/effects)** — rejeitada: overhead desproporcional ao escopo; o Journey OS padronizou
   Signals-first.
2. **`BehaviorSubject` por facade** — rejeitada: mais boilerplate, menos integrado ao change detection
   `OnPush`, propenso a leaks.
3. **Estado em componentes (sem facade)** — rejeitada: dificulta reuso entre features e teste isolado;
   o controle de polling precisa de um dono único (a facade) para parar no terminal/destroy.

## Consequências

- **Positivas:** menos boilerplate; integração natural com `OnPush`; estado e polling testáveis na
  facade; consistência com WRKS/ASST/INTL.
- **Negativas:** disciplina para não vazar `signal` mutável; padrões de cancelamento/invalidação na
  troca de empresa e de parada do polling precisam ser explícitos (ADR-005).

## Referências

- `04-frontend-architecture-direction.md` §6 · `05-state-and-data-flow.md`
- `docs/architecture/frontend/standards/module-pattern.md`
- WRKS ADR-002 / ASST ADR-002 (signals-first) · ADR-005 (polling de entrega)
