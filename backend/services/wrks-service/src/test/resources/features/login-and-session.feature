Feature: Login and session

  # Covers SPEC-02 (identity & session) and api-contract §1.
  # Anchor golden path: OIDC login -> JWT issued -> empresa selected.

  Background:
    Given Keycloak is reachable
    And the empresa "emp_acme" is ATIVA
    And a usuario "rafael@acme.com" exists

  Scenario: Single-empresa user logs in and gets a tenant-scoped JWT
    Given "rafael@acme.com" has exactly one active association with "emp_acme" as "INFOPRODUTOR"
    When a valid OIDC code is presented to "/api/v1/iam/sessao/login"
    Then the response status is 200
    And a JWT is issued with claim empresa_id "emp_acme"
    And a rotating refresh-token cookie is set with httpOnly secure sameSite=strict

  Scenario: Multi-empresa user must select an empresa before a tenant JWT is issued
    Given "rafael@acme.com" has active associations with "emp_acme" and "emp_beta"
    When a valid OIDC code is presented without an empresaId
    Then the response status is 200
    And the response lists the available empresas
    And no tenant-scoped JWT is issued

  Scenario: User with no active association cannot log in
    Given "rafael@acme.com" has no active usuario_empresa
    When a valid OIDC code is presented to "/api/v1/iam/sessao/login"
    Then the response status is 422
    And the error code is "wrks.usuario.sem-empresa-ativa"

  Scenario: Invalid OIDC code is rejected
    When an invalid OIDC code is presented to "/api/v1/iam/sessao/login"
    Then the response status is 401
    And the error code is "iam.credenciais-invalidas"

  Scenario: Switching empresa issues a new JWT without re-authentication
    Given "rafael@acme.com" is logged in scoped to "emp_acme"
    And the user has an active association with "emp_beta"
    When the user calls "/api/v1/iam/sessao/trocar-empresa" with "emp_beta"
    Then the response status is 200
    And a new JWT is issued with claim empresa_id "emp_beta"

  Scenario: Switching to an empresa without access is forbidden
    Given "rafael@acme.com" is logged in scoped to "emp_acme"
    And the user has no active association with "emp_gamma"
    When the user calls "/api/v1/iam/sessao/trocar-empresa" with "emp_gamma"
    Then the response status is 403
    And the error code is "wrks.empresa.acesso-negado"

  Scenario: Logout blacklists the access token and clears the cookie
    Given "rafael@acme.com" is logged in
    When the user calls "/api/v1/iam/sessao/logout"
    Then the response status is 204
    And the access token jti is added to the Redis blacklist
    And the refresh-token cookie is cleared

  Scenario: Refresh rotates the refresh token
    Given "rafael@acme.com" holds a valid refresh token
    When the user calls "/api/v1/iam/sessao/refresh"
    Then the response status is 200
    And a new access token is issued
    And the previous refresh token is invalidated

  Scenario: Reused refresh token is rejected
    Given a refresh token that was already used once
    When the user calls "/api/v1/iam/sessao/refresh" with it again
    Then the response status is 401
    And the error code is "iam.refresh-invalido"
