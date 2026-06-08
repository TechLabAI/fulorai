Feature: User administration and anti-escalation

  # Covers SPEC-02 / SPEC-06 (security, anti-escalation) and api-contract §4.

  Background:
    Given the empresa "emp_acme" is ATIVA
    And the canonical roles INFOPRODUTOR (level 3), HEAD_GROWTH (level 2), SDR (level 1) are seeded

  Scenario: Admin creates a new user
    Given the caller has permission "wrks.usuario.criar"
    When the caller creates a usuario "novo@acme.com"
    Then the response status is 201
    And the event "journey-os.usuario.criado" is published

  Scenario: Duplicate email is rejected
    Given a usuario "rafael@acme.com" already exists and is active
    When the caller creates a usuario "rafael@acme.com"
    Then the response status is 409
    And the error code is "wrks.usuario.duplicado"

  Scenario: Assigning a role above the caller's own is forbidden
    Given the caller is associated as "HEAD_GROWTH" with "emp_acme"
    When the caller associates a user as "INFOPRODUTOR" with "emp_acme"
    Then the response status is 403
    And the error code is "wrks.papel.escalonamento"

  Scenario: Assigning an equal-or-lower role is allowed
    Given the caller is associated as "HEAD_GROWTH" with "emp_acme"
    When the caller associates a user as "SDR" with "emp_acme"
    Then the response status is 200
    And the event "journey-os.usuario.empresa.associado" is published

  Scenario Outline: Cross-empresa isolation on user listing
    Given the caller's JWT is scoped to "<empresa>"
    When the caller lists users
    Then only users associated with "<empresa>" are returned
    And no user data from another empresa is exposed

    Examples:
      | empresa  |
      | emp_acme |
      | emp_beta |
