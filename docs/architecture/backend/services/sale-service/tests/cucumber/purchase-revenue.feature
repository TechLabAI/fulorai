Feature: Purchase ingestion and revenue recognition

  # Covers SPEC-02, SPEC-05 (idempotency), api-contract §3, event-contracts compra.confirmada

  Background:
    Given the empresa "emp_acme" is ATIVA
    And an oferta "curso-pro" priced at 1997.00 BRL exists

  Scenario: Registering a confirmed purchase recognizes revenue and emits the anchor event
    When a confirmed order "HOT-9981" from "hotmart" is registered for "rafael@acme.com" buying "curso-pro" x1
    Then a compra is recognized with total 1997.00
    And the event "journey-os.compra.confirmada" is published
    And revenue attribution runs for that compra
    And the LTV of "rafael@acme.com" is recomputed

  Scenario: Re-registering the same order does not double-count revenue
    Given the order "HOT-9981" from "hotmart" was already registered
    When the order "HOT-9981" from "hotmart" is registered again
    Then the existing compra is returned with duplicada=true
    And the event "journey-os.compra.confirmada" is not published again
    And the recognized revenue is unchanged

  Scenario: A purchase whose items do not sum to the total is rejected
    When a confirmed order "HOT-7000" with total 1997.00 but items summing 1500.00 is registered
    Then the response status is 422
    And the error code is "sale.compra.receita-inconsistente"

  Scenario: A purchase without legal basis is rejected
    When a confirmed order "HOT-7001" is registered without baseLegal
    Then the response status is 422
    And the error code is "sale.compra.base-legal-invalida"

  Scenario: A direct sale without an opportunity still recognizes revenue
    When a confirmed order "HOT-7002" from "hotmart" is registered for "novo@acme.com" with no oportunidade
    Then a compra is recognized with status "CONFIRMADA"
    And the event "journey-os.compra.confirmada" is published

  Scenario: Reversing a purchase adjusts revenue and LTV without deleting history
    Given a confirmed compra "HOT-9981" for "rafael@acme.com" of 1997.00
    When the compra is estornada
    Then the compra status becomes "ESTORNADA"
    And the LTV of "rafael@acme.com" excludes that purchase
    And the historical compra row is retained
