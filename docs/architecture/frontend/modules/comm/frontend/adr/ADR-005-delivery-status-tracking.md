# ADR-005 — Rastreio do ciclo de vida da mensagem por polling com backoff

- **Status:** accepted

## Contexto

O diferencial de UX do COMM é o **rastreio**: depois de disparar, Lucas (SDR) precisa ver o status da
mensagem evoluir `ENFILEIRADA → ENVIADA → ENTREGUE → LIDA` (ou `FALHADA`) em **tempo quase real**
(Success Signal do `01`/`_brief.md`). O estado de entrega é avançado no **BE** por **callbacks
(webhooks) do provedor**, que chegam de forma assíncrona — o BE normaliza cada callback em um
`evento_entrega` e atualiza a `mensagem`. O contrato BE expõe **leitura**:
`GET /messages/{id}` (estado atual) e `GET /messages/{id}/events` (trilha cronológica). **Não há
endpoint de streaming** (SSE/WebSocket) no MVP do `comm-service`. O FE precisa refletir a evolução do
estado sem streaming, sem martelar o servidor e sem vazar timers.

## Decisão

1. **Polling com backoff, confinado à facade.** `MessageFacade` (`libs/comm/data-access`) expõe
   `startPolling(id)` / `stopPolling()`. Internamente usa um `interval` RxJS com **backoff**
   (ex.: começa em ~3 s e cresce até um teto, ex.: ~15 s), reconsultando `GET /messages/{id}` (+
   `/events` quando há avanço) e atualizando os signals `mensagemSelecionada` / `eventosEntrega`.
   O RxJS fica **dentro** da facade; a feature consome apenas os signals (ADR-002).
2. **Para no estado terminal.** Um `computed()` `estadoTerminal` (true para `LIDA`/`FALHADA`) encerra
   o polling automaticamente; a UI também encerra no `ngOnDestroy` da feature (cleanup obrigatório —
   sem timers órfãos). Há **teto de tentativas/tempo** para não pollar indefinidamente.
3. **Eventos append-only.** Os `eventos` são acumulados em memória entre ticks (a timeline não
   "pisca"); são descartados ao sair do detalhe e na troca de empresa (UINV-9).
4. **Sem otimismo no disparo.** A mensagem só aparece após o `202` (estado real `ENFILEIRADA`); o
   polling começa a partir daí (UINV-8).
5. **Feature flag.** `comm.delivery-tracking` (`defaultState: on`) permite desligar o polling
   (degrada para refresh manual) sem afetar o disparo nem o resto do módulo.

## Alternativas consideradas

1. **WebSocket / SSE (push real-time)** — rejeitada no MVP: **não há endpoint** no `comm-service`;
   exigiria nova superfície BE + infra de fan-out. Reavaliar via novo ADR se o volume/latência
   justificar push.
2. **Polling de intervalo fixo curto** (ex.: 2 s constante) — rejeitada: martela o servidor para
   mensagens que demoram (provedor lento); o backoff equilibra responsividade × carga.
3. **Sem rastreio ao vivo** (só refresh manual) — rejeitada: perde o Success Signal "ver o status
   mudar em tempo quase real"; vira o modo degradado (flag off), não o padrão.
4. **Polling na lista inteira** (todas as mensagens) — rejeitada: custo desproporcional; o polling é
   por **mensagem selecionada/aberta**, não pela lista (a lista recarrega por navegação).

## Consequências

- **Positivas:** rastreio quase-tempo-real sem nova superfície BE; carga controlada por backoff;
  timers isolados e testáveis na facade; cleanup determinístico evita leaks; flag permite degradar.
- **Negativas:** latência de atualização limitada pelo intervalo (não é push instantâneo); exige
  disciplina de cleanup (destroy/terminal/empresa-switch). Migrar para push é um novo ADR isolado
  atrás da facade.

## Referências

- BE: `docs/architecture/backend/services/comm-service/contracts/api-contract.md` §2 (`/messages`, `/messages/{id}/events`) e §6 (webhooks)
- BE: `comm-service` SPEC-02 (message-dispatch-lifecycle) · estados de entrega
- `03-domain-framing-frontend.md` (UINV-8) · `05-state-and-data-flow.md` §2–4
- ADR-002 (signals-first; RxJS confinado à facade)
