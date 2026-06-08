# COMM-013 -- Idempotência (disparo + Studio + consumers) + concorrência otimista

## Contexto
Garantir que disparos, composições, callbacks e consumo de eventos sejam idempotentes, e que
transições de entrega concorrentes não corrompam o estado.

## Spec de referencia
- SPEC-05-idempotency-concurrency
- SPEC-02-message-dispatch-lifecycle

## Escopo
- Disparo idempotente por `chave_idempotencia` (UNIQUE); replay retorna a mensagem existente (200).
- Template Studio idempotente por `Idempotency-Key` (uma chamada à IA).
- Consumers persistem `eventId` em `processed_events` antes de efeito.
- Webhook idempotente por `(provedorMessageId, tipo)`.
- Concorrência otimista (`@Version`/checagem de estado) nas transições.

## Resultado esperado
Reprocessos, cliques duplos e reentregas não geram envios/efeitos duplicados.

## Criterios de aceite
- [ ] Dois `POST /messages` com mesma key → uma mensagem, provedor chamado ≤ 1 vez.
- [ ] Webhook duplicado → uma transição, um evento.
- [ ] Evento reentregue (mesmo `eventId`) → no-op.
- [ ] Duas transições concorrentes → uma aplica, a outra 409 `comm.mensagem.estado-invalido`.

## Dependencias
- COMM-006 (precede)

## Estimativa
M

## Prioridade
P5
