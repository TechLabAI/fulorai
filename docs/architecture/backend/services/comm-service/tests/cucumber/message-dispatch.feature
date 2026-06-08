Feature: Message dispatch and delivery lifecycle

# Refs SPEC-02 (dispatch & delivery state machine), SPEC-01 (API), SPEC-05 (idempotency), SPEC-09 (events).
# ADR-003, ADR-005. Reusable steps in SPEC-08.

Background:
  Given an active empresa "emp_acme" with provisioned schema
  And an authenticated user "marina" with permissions "comm.mensagem.enviar,comm.mensagem.ler"
  And an active channel config "WHATSAPP" with provider "META_WABA"
  And an ATIVO template "Boas-vindas" for channel "WHATSAPP" with body "Olá {{nome}}!"

Scenario: Accept a dispatch enqueues the message
  When marina dispatches template "Boas-vindas" to lead "lead-1" with variables nome="Rafael"
  Then the response status is 202
  And the message delivery state is "ENFILEIRADA"
  And a "journey-os.mensagem.enfileirada" event is emitted

Scenario: Worker sends the message to the provider and emits the anchor event
  Given a message to lead "lead-1" is "ENFILEIRADA"
  When the dispatch worker sends it and the provider accepts it
  Then the message delivery state is "ENVIADA"
  And a delivery event "ENVIADA" is recorded
  And a "journey-os.mensagem.enviada" event is emitted

Scenario: Provider delivery callback advances the state
  Given a message to lead "lead-1" is "ENVIADA" with provider message id "wamid.123"
  When a valid provider webhook reports "ENTREGUE" for "wamid.123"
  Then the message delivery state is "ENTREGUE"
  And a "journey-os.mensagem.entregue" event is emitted

Scenario: Rendered content is an immutable snapshot
  Given a message to lead "lead-1" was sent with body "Olá Rafael!"
  When the template "Boas-vindas" body is later edited to "Oi {{nome}}!"
  Then the sent message rendered content is still "Olá Rafael!"

Scenario: Idempotent dispatch does not send twice
  When marina dispatches template "Boas-vindas" to lead "lead-1" with idempotency key "key-1"
  And marina dispatches template "Boas-vindas" to lead "lead-1" with idempotency key "key-1"
  Then exactly one message exists for idempotency key "key-1"
  And the provider was called at most once

Scenario: Dispatch fails after exhausting provider retries
  Given the channel provider "META_WABA" rejects all send attempts
  And a message to lead "lead-1" is "ENFILEIRADA"
  When the dispatch worker exhausts the configured retries
  Then the message delivery state is "FALHADA"
  And a "journey-os.mensagem.falhada" event is emitted

Scenario: Cannot dispatch using a non-ATIVO template
  Given a RASCUNHO template "Promo" for channel "WHATSAPP"
  When marina dispatches template "Promo" to lead "lead-1"
  Then the response status is 409
  And the error code is "comm.template.nao-ativo"

Scenario: Missing required variable rejects the dispatch
  When marina dispatches template "Boas-vindas" to lead "lead-1" with no variables
  Then the response status is 422
  And the error code is "comm.mensagem.variavel-ausente"
