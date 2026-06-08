# COMM-006 -- Dispatch worker + máquina de entrega + evento-âncora

## Contexto
Golden path central: o worker consome o job de disparo, envia ao provedor via adapter de canal e
avança a máquina de entrega, emitindo o evento-âncora `journey-os.mensagem.enviada`.

## Spec de referencia
- SPEC-02-message-dispatch-lifecycle
- SPEC-09-messaging-architecture
- SPEC-03-channel-routing

## Escopo
- `EnviarMensagemService` (worker): lê outbox/fila, seleciona `CanalEnvioAdapter` via `CanalEnvioPort` (COMM-010), envia sob Resilience4j.
- Sucesso → `ENVIADA` + `EventoEntrega(ENVIADA)` + emite `journey-os.mensagem.enviada` (âncora).
- Falha após retries → `FALHADA` + `EventoEntrega(FALHADA)` + emite `journey-os.mensagem.falhada` + DLQ.
- Transições monotônicas via `TransicaoEntregaService`.

## Resultado esperado
Mensagem ENFILEIRADA é enviada ao provedor e transita para ENVIADA/FALHADA com evento de domínio.

## Criterios de aceite
- [ ] Envio OK → `ENVIADA` + `journey-os.mensagem.enviada` (idempotente em mensagemId).
- [ ] Falha após N retries → `FALHADA` + `journey-os.mensagem.falhada` + job na DLQ.
- [ ] Cada transição grava exatamente um `EventoEntrega`.

## Dependencias
- COMM-005 (precede)
- COMM-010 (CanalEnvioPort)

## Estimativa
L

## Prioridade
P2
