# SPEC-02 — Message Dispatch & Delivery State Machine (core orchestration)

> EARS guide linkado. Núcleo do domínio COMM. Relaciona SPEC-03 (routing), SPEC-09 (events/outbox/worker), ADR-003, ADR-005.

## Objetivo

Especificar o caminho central: aceitar um pedido de disparo, renderizar o conteúdo de forma
imutável, enfileirar, enviar ao provedor de canal via worker resiliente e acompanhar o ciclo de
vida de entrega através de uma máquina de estados monotônica alimentada por callbacks.

## Escopo

- **In:** render de template+variáveis (snapshot imutável); persistência de `Mensagem`; outbox + worker de disparo; máquina de estados `PENDENTE→ENFILEIRADA→ENVIADA→ENTREGUE→LIDA`/`FALHADA`; registro append-only de `EventoEntrega`; emissão de eventos de domínio.
- **Out:** resolução de canal/template (SPEC-03); detalhes de cada provedor (SPEC-10); idempotência fina (SPEC-05).

## Decisões técnicas

- **Aceite assíncrono:** `POST /messages` valida, renderiza, persiste `PENDENTE`, grava outbox na mesma TX, retorna `202 ENFILEIRADA` (ADR-003).
- **Worker de disparo:** lê outbox/fila, seleciona o `CanalEnvioAdapter` (SPEC-03), chama o provedor sob Resilience4j (timeout/CB/retry); sucesso → `ENVIADA`, falha após retries → `FALHADA`.
- **Snapshot imutável:** `conteudo_renderizado` é congelado no envio; edições posteriores do template não afetam mensagens já enviadas.
- **Callbacks:** webhook do provedor normaliza para `EventoEntrega` e avança `ENTREGUE`/`LIDA`/`FALHADA` (bounce tardio).
- **Transições monotônicas:** sem regressão de estado; cada transição grava exatamente um `EventoEntrega`.

## Implementação

- Use cases: `RotearMensagemService` (SPEC-03), `EnviarMensagemService` (worker), `RegistrarEventoEntregaService` (callbacks).
- Domain services: `RenderTemplateService` (substitui `{{variaveis}}`), `TransicaoEntregaService` (valida transições da máquina).
- Estados (`EstadoEntrega` enum): `PENDENTE`, `ENFILEIRADA`, `ENVIADA`, `ENTREGUE`, `LIDA`, `FALHADA`.

## Casos de borda

- Provedor confirma entrega antes do ack do envio (corrida) → transição idempotente; ordem por `ocorrido_em`.
- Bounce tardio após `ENVIADA`/`ENTREGUE` → `FALHADA` (transição permitida); reprocesso = nova `Mensagem`.
- Read receipt em canal que não suporta leitura → estado para em `ENTREGUE` (sem `LIDA`).
- Mensagem agendada (`agendado_para`) → permanece `PENDENTE`/`ENFILEIRADA` até a janela.

## Critérios de aceite (EARS)

- `WHEN a dispatch is accepted, THE SYSTEM SHALL render the content from the ATIVO template and persist it as an immutable conteudo_renderizado snapshot.`
- `WHILE a message is ENFILEIRADA, THE SYSTEM SHALL transition it only to ENVIADA or FALHADA.`
- `WHEN the channel provider accepts the send, THE SYSTEM SHALL set estado_entrega=ENVIADA, record an EventoEntrega(ENVIADA), and emit journey-os.mensagem.enviada.`
- `WHEN a valid provider callback reports delivery, THE SYSTEM SHALL set estado_entrega=ENTREGUE and emit journey-os.mensagem.entregue.`
- `IF the dispatch exhausts the configured provider retries, THEN THE SYSTEM SHALL set estado_entrega=FALHADA, record the reason, and emit journey-os.mensagem.falhada.`
- `THE SYSTEM SHALL apply only monotonic delivery-state transitions and SHALL reject an invalid transition with 409 error.code 'comm.mensagem.estado-invalido'.`
- `THE SYSTEM SHALL never mutate conteudo_renderizado after the message has been ENVIADA.`
- `WHEN any delivery-state transition occurs, THE SYSTEM SHALL append exactly one evento_entrega row.`
