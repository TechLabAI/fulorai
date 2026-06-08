Feature: Sales pipeline (CRM) lifecycle

  # Covers SPEC-02 (orchestration), api-contract §1, event-contracts oportunidade.*

  Background:
    Given the empresa "emp_acme" is ATIVA
    And the default pipeline stages are seeded for "emp_acme"

  Scenario: An opportunity is created from a qualified lead
    Given a qualified lead "rafael@acme.com" exists
    When the event "journey-os.lead.qualificado" is consumed for that lead
    Then an oportunidade is created in stage "NOVA" in state "NOVA"
    And the event "journey-os.oportunidade.criada" is published

  Scenario: Creating an opportunity manually via API
    When a closer creates an oportunidade for lead "ana@acme.com" with estimated value 1997.00
    Then the oportunidade is persisted in state "NOVA"
    And the event "journey-os.oportunidade.criada" is published

  Scenario: Moving an opportunity through stages records history
    Given an oportunidade in stage "NOVA"
    When the closer moves it to stage "PROPOSTA"
    Then a historico_estagio row is appended from "NOVA" to "PROPOSTA"
    And the event "journey-os.oportunidade.estagio.alterado" is published

  Scenario: Winning an opportunity emits the won event
    Given an oportunidade in stage "PROPOSTA"
    When the closer marks it as won
    Then the oportunidade state is "GANHA"
    And the event "journey-os.oportunidade.ganha" is published

  Scenario: Losing an opportunity requires a reason
    Given an oportunidade in stage "PROPOSTA"
    When the closer marks it as lost without a reason
    Then the response status is 422
    And the error code is "sale.oportunidade.motivo-obrigatorio"

  Scenario: A closed opportunity cannot be closed again
    Given an oportunidade already in state "GANHA"
    When the closer marks it as won
    Then the response status is 409
    And the error code is "sale.oportunidade.ja-fechada"

  Scenario: A duplicate qualified-lead event does not create a second opportunity
    Given an open oportunidade already exists for lead "rafael@acme.com"
    When the event "journey-os.lead.qualificado" is consumed again for that lead
    Then no duplicate oportunidade is created
    And the existing oportunidade is updated
