Feature: Maturity Score (6D) computation

  # Covers SPEC-03 (Maturity Score 6D) and contracts/techlab-ai-integration.md.

  Background:
    Given the empresa "emp_acme" is ATIVA
    And the qualification rule version 3 is active for "emp_acme"

  Scenario: The score is explainable with a per-dimension breakdown
    Given a lead "rafael@acme.com" with known signals
    When the Maturity Score is computed
    Then the score has a value between 0 and 100
    And the breakdown contains the dimensions PERFIL, ENGAJAMENTO, INTENCAO, CAPACIDADE, URGENCIA, ADERENCIA
    And the breakdown records which conditions contributed

  Scenario: Recomputing with the same rule and signals is idempotent
    Given a lead "rafael@acme.com" scored under rule version 3
    When the Maturity Score is computed again with the same signals
    Then the aggregate score is unchanged
    And no duplicate maturity_score row is created

  Scenario: TechLab AI assist enriches the score when available
    Given the qualification assist feature is enabled
    And TechLab AI is available
    And a lead "rafael@acme.com" has free-text survey notes
    When the Maturity Score is computed
    Then the score reflects the AI-suggested contributions
    And the score is flagged assist_ia true

  Scenario: TechLab AI failure degrades to the deterministic score
    Given the qualification assist feature is enabled
    And TechLab AI is unavailable
    And a lead "rafael@acme.com" has free-text survey notes
    When the Maturity Score is computed
    Then the deterministic score is produced
    And the score is flagged assist_ia false
    And the request still succeeds

  Scenario: An AI suggestion alone cannot flip qualification state
    Given a lead "ana@acme.com" whose deterministic score is below the threshold
    When TechLab AI suggests contributions that would cross the threshold
    Then the lead state is not changed to "QUALIFICADO" by the AI suggestion alone
