Feature: Revenue attribution and LTV

  # Covers SPEC-03 (attribution + LTV), api-contract §4, §5, event-contracts receita.atribuida / ltv.atualizado

  Background:
    Given the empresa "emp_acme" is ATIVA
    And a default LAST_TOUCH attribution model version 1 is active for "emp_acme"

  Scenario: Last-touch attribution credits the last touchpoint with the full revenue
    Given a lead "rafael@acme.com" whose last touchpoint is campaign "meta-ads"
    When a confirmed purchase of 1997.00 is registered for "rafael@acme.com"
    Then the revenue 1997.00 is attributed to touchpoint "meta-ads" of type "CAMPANHA"
    And the event "journey-os.receita.atribuida" is published with model version 1

  Scenario: Attribution conserves revenue
    When a confirmed purchase of 1997.00 is attributed
    Then the sum of attributed amounts equals 1997.00

  Scenario: Linear attribution splits revenue evenly across touchpoints
    Given a LINEAR attribution model version 2 is activated for "emp_acme"
    And a purchase of 1000.00 with touchpoints "meta-ads" and "email"
    When the purchase is attributed
    Then "meta-ads" is credited 500.00
    And "email" is credited 500.00

  Scenario: Activating a new attribution model re-attributes affected purchases
    Given a purchase attributed under model version 1
    When attribution model version 2 is activated
    Then model version 1 becomes inactive
    And the purchase is re-attributed under model version 2
    And the event "journey-os.receita.atribuida" is published

  Scenario: LTV sums a contact's confirmed purchases deterministically
    Given "rafael@acme.com" has confirmed purchases of 1997.00 and 1997.00
    When the LTV is computed
    Then the LTV valor_total is 3994.00
    And num_compras is 2
    And the event "journey-os.ltv.atualizado" is published

  Scenario: With no active model attribution falls back to LAST_TOUCH
    Given no attribution model is active for "emp_acme"
    When a confirmed purchase is attributed
    Then the attribution uses the LAST_TOUCH strategy
