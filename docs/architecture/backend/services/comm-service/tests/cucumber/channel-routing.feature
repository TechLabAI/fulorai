Feature: Channel routing and provider-agnostic dispatch

# Refs SPEC-03 (routing & adapter pattern), SPEC-01 (API), SPEC-06 (config secrets). ADR-005.
# Reusable steps in SPEC-08.

Background:
  Given an active empresa "emp_acme" with provisioned schema
  And an authenticated user "marina" with permissions "comm.roteamento.criar,comm.canal.configurar,comm.mensagem.enviar"

Scenario: Configure a channel stores only a credential reference
  When marina configures channel "WHATSAPP" with provider "META_WABA" and credential reference "secret://comm/whatsapp"
  Then the response status is 201
  And the stored config never exposes the raw secret

Scenario: Routing resolves the preferred channel
  Given a routing rule "Quente" priority 10 with preferred channel "WHATSAPP" and fallback "EMAIL"
  And lead "lead-1" has a WhatsApp address
  When a dispatch is routed for lead "lead-1"
  Then the resolved channel is "WHATSAPP"

Scenario: Routing falls back when the preferred channel is unavailable for the lead
  Given a routing rule "Quente" priority 10 with preferred channel "WHATSAPP" and fallback "EMAIL"
  And lead "lead-1" has no WhatsApp address but has an email
  When a dispatch is routed for lead "lead-1"
  Then the resolved channel is "EMAIL"

Scenario: Routing fails explicitly when no channel can be resolved
  Given a routing rule "Quente" priority 10 with preferred channel "WHATSAPP" and fallback "EMAIL"
  And lead "lead-1" has neither a WhatsApp address nor an email
  When a dispatch is routed for lead "lead-1"
  Then the response status is 422
  And the error code is "comm.roteamento.sem-canal"

Scenario: Lower priority rule is evaluated first
  Given a routing rule "A" priority 10 with preferred channel "WHATSAPP"
  And a routing rule "B" priority 20 with preferred channel "EMAIL"
  When a dispatch is routed for a lead matching both rules
  Then the resolved channel is "WHATSAPP"

Scenario: Dispatch to a channel without active config is rejected
  Given a routing rule resolving channel "TELEGRAM"
  And no active channel config for "TELEGRAM"
  When marina dispatches to lead "lead-1"
  Then the response status is 422
  And the error code is "comm.canal.nao-configurado"

Scenario Outline: The correct provider adapter is selected per channel
  Given an active channel config "<canal>" with provider "<provedor>"
  When a message on channel "<canal>" is sent
  Then the "<provedor>" adapter performs the send
  Examples:
    | canal    | provedor      |
    | WHATSAPP | META_WABA     |
    | EMAIL    | SES           |
    | TELEGRAM | TELEGRAM_BOT  |
    | SMS      | TWILIO        |
