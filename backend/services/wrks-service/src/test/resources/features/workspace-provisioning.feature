Feature: Workspace (empresa) provisioning

  # Covers SPEC-02 / SPEC-05 (saga, idempotency) and api-contract §3.

  Background:
    Given the caller has permission "wrks.empresa.criar"

  Scenario: Creating an empresa starts provisioning and triggers MIG
    When the caller creates an empresa with slug "emp_nova"
    Then the empresa is persisted with status "PROVISIONANDO"
    And MIG is triggered to create schema "emp_nova"

  Scenario: Empresa becomes ATIVA only after MIG confirms
    Given the empresa "emp_nova" is PROVISIONANDO
    When MIG confirms the schema "emp_nova" was created
    Then the empresa status becomes "ATIVA"
    And the event "journey-os.empresa.provisionada" is published

  Scenario: Duplicate slug is rejected
    Given an empresa with slug "emp_acme" already exists
    When the caller creates an empresa with slug "emp_acme"
    Then the response status is 409
    And the error code is "wrks.empresa.slug-duplicado"

  Scenario: MIG failure keeps the empresa in PROVISIONANDO
    Given the empresa "emp_nova" is PROVISIONANDO
    When MIG provisioning fails
    Then the empresa remains "PROVISIONANDO"
    And the response status is 502
    And the error code is "wrks.empresa.provisionamento-falhou"

  Scenario: Re-triggering provisioning is idempotent
    Given the empresa "emp_nova" is PROVISIONANDO
    When the caller calls "/api/v1/iam/empresas/emp_nova/provisionar" again
    Then no duplicate schema is created
    And the empresa status is unchanged or becomes "ATIVA"
