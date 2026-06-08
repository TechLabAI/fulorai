Feature: Access decision and RBAC propagation

  # Covers SPEC-03 (RBAC & AccessDecision) and api-contract §2, §5.

  Background:
    Given the empresa "emp_acme" is ATIVA
    And the canonical roles INFOPRODUTOR, HEAD_GROWTH, SDR are seeded

  Scenario: Evaluate returns role, explicit permissions and version
    Given "lucas@acme.com" is associated with "emp_acme" as "SDR"
    When a service calls "/api/v1/iam/access/evaluate" for that user and empresa
    Then the response status is 200
    And the decision role is "SDR"
    And the decision contains an explicit permission list
    And the decision contains the current modelo_acesso_versao

  Scenario: Cached decision is served without hitting PostgreSQL while version matches
    Given an AccessDecision for "lucas@acme.com" on "emp_acme" is cached in Redis
    And the cached modelo_acesso_versao matches the current version
    When a service calls "/api/v1/iam/access/evaluate" again
    Then the decision is served from Redis
    And PostgreSQL is not queried

  Scenario: Evaluate for an inactive association is not found
    Given "lucas@acme.com" has an inactive association with "emp_acme"
    When a service calls "/api/v1/iam/access/evaluate" for that user and empresa
    Then the response status is 404
    And the error code is "wrks.usuario.associacao-nao-encontrada"

  Scenario: Changing a role bundle bumps the version and publishes the event
    Given the role "HEAD_GROWTH" has a permission bundle
    When an admin updates "/api/v1/iam/papeis/HEAD_GROWTH/permissoes"
    Then modelo_acesso_versao is incremented in the same transaction
    And the event "journey-os.modelo.acesso.alterado" is published with the new version

  Scenario: Stale access-model version forces a refresh
    Given a JWT carries a modelo_acesso_versao lower than the current version
    When the user calls any protected endpoint
    Then the response status is 401
    And the error code is "iam.sessao.versao-desatualizada"

  Scenario: Unknown permission code is rejected when editing a bundle
    When an admin assigns a permission not present in the canonical catalogue
    Then the response status is 422
    And the error code is "wrks.papel.permissao-desconhecida"

  Scenario: JWKS is publicly available for token validation
    When GWY requests "/api/v1/iam/.well-known/jwks.json"
    Then the response status is 200
    And the RS256 public key set is returned without authentication
