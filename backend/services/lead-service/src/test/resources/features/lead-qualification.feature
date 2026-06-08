Feature: Lead qualification and segmentation

  # Covers SPEC-02 (orchestration), SPEC-03 (score), api-contract §3, §4.

  Background:
    Given the empresa "emp_acme" is ATIVA
    And the qualification rule version 3 is active with threshold 60 for "emp_acme"

  Scenario: A lead crossing the threshold becomes qualified and emits the anchor event
    Given a lead "rafael@acme.com" with signals scoring above 60
    When the lead is qualified
    Then the lead state is "QUALIFICADO"
    And the event "journey-os.lead.qualificado" is published with the aggregate score and rule version 3

  Scenario: A lead below the threshold is not qualified
    Given a lead "ana@acme.com" with signals scoring below 60
    When the lead is qualified
    Then the lead state is "NAO_QUALIFICADO"
    And the event "journey-os.lead.qualificado" is published with state "NAO_QUALIFICADO"

  Scenario: Submitting survey answers triggers a recompute
    Given a lead "rafael@acme.com" already qualified
    When survey answers raising the INTENCAO signals are submitted for that lead
    Then the Maturity Score is recomputed
    And the event "journey-os.lead.score.atualizado" is published

  Scenario: Qualifying with no active rule is rejected
    Given no qualification rule is active for "emp_acme"
    When the lead "rafael@acme.com" is qualified
    Then the response status is 409
    And the error code is "lead.qualification.sem-regra-ativa"

  Scenario: Activating a new rule version recomputes affected leads
    Given a lead "rafael@acme.com" qualified under rule version 3
    When qualification rule version 4 is activated
    Then rule version 3 becomes inactive
    And the lead "rafael@acme.com" is recomputed under rule version 4

  Scenario: A lead crossing a segment predicate emits a segment-changed event
    Given a segment "prontos-para-compra" selects leads with aggregate score >= 70
    And a lead "rafael@acme.com" with aggregate score 78
    When segments are re-evaluated for that lead
    Then the lead joins segment "prontos-para-compra"
    And the event "journey-os.lead.segmento.alterado" is published with acao "ENTROU"
