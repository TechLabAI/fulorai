Feature: Lead capture and deduplication

  # Covers SPEC-02 (orchestration) and api-contract §1.

  Background:
    Given the empresa "emp_acme" is ATIVA
    And an active qualification rule version is seeded for "emp_acme"

  Scenario: Capturing a new lead creates it and publishes the captured event
    Given no lead exists with email "rafael@acme.com" in "emp_acme"
    When a lead is captured with email "rafael@acme.com" source "meta-ads" baseLegal "CONSENTIMENTO"
    Then the response status is 201
    And the lead state is "EM_QUALIFICACAO"
    And the event "journey-os.lead.capturado" is published

  Scenario: Capturing the same natural key merges instead of duplicating
    Given a lead exists with email "rafael@acme.com" in "emp_acme"
    When a lead is captured again with email "rafael@acme.com" source "landing-page"
    Then the response status is 201
    And the response field "duplicado" is true
    And only one lead exists with email "rafael@acme.com" in "emp_acme"

  Scenario: Capture without a legal basis is rejected
    When a lead is captured with email "ana@acme.com" and no baseLegal
    Then the response status is 422
    And the error code is "lead.lead.base-legal-invalida"

  Scenario: Anonymized lead cannot be edited
    Given a lead "ana@acme.com" in "emp_acme" is in state "ANONIMIZADO"
    When an editor updates the profile of that lead
    Then the response status is 409
    And the error code is "lead.lead.anonimizado"

  Scenario: A captured lead is never visible from another empresa
    Given a lead exists with email "rafael@acme.com" in "emp_acme"
    When a user authenticated for "emp_other" lists leads
    Then the lead "rafael@acme.com" is not returned

  Scenario Outline: Natural key normalization deduplicates equivalent contacts
    Given a lead exists with email "<existing>" in "emp_acme"
    When a lead is captured with email "<incoming>" source "form"
    Then the response field "duplicado" is <merged>
    Examples:
      | existing          | incoming          | merged |
      | rafael@acme.com   | RAFAEL@ACME.COM   | true   |
      | rafael@acme.com   | other@acme.com    | false  |
