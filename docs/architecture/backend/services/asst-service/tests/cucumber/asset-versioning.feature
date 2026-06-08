Feature: Asset versioning and Asset Studio composition

# Refs SPEC-02 (lifecycle), SPEC-03 (Asset Studio), SPEC-05 (idempotency)
# ADR-005 (immutable versioning). Reusable steps in SPEC-08.

Background:
  Given an active empresa "emp_acme" with provisioned schema
  And an authenticated user "marina" with permissions "asst.asset.editar,asst.studio.compor"
  And an asset "Boas-vindas" of type "EMAIL" in state "RASCUNHO"

Scenario: Create a new manual version assigns the next sequential number
  When marina creates a manual version with content "Olá {{nome}}"
  Then the response status is 201
  And the version number is 1
  And the version origin is "MANUAL"
  And the version state is "RASCUNHO"

Scenario: A second version increments the number
  Given the asset "Boas-vindas" already has version 1
  When marina creates a manual version with content "Olá de novo"
  Then the version number is 2

Scenario: Existing versions are immutable
  Given the asset "Boas-vindas" has version 1
  When marina attempts to modify version 1
  Then the response status is 409
  And the error code is "asst.versao.imutavel"

Scenario: Asset Studio produces an AI draft version with provenance
  Given TechLab AI document_composition is available
  When marina composes in the Studio with brief "e-mail de boas-vindas leve"
  Then the response status is 201
  And the version origin is "ASSET_STUDIO"
  And the version state is "RASCUNHO"
  And the version records the composition brief

Scenario: Asset Studio degrades when TechLab AI is unavailable
  Given TechLab AI document_composition is unavailable
  When marina composes in the Studio with brief "qualquer"
  Then the response status is 503
  And the error code is "asst.studio.ia-indisponivel"
  And no new version is created

Scenario: Composition is idempotent on the Idempotency-Key
  Given TechLab AI document_composition is available
  When marina composes in the Studio with Idempotency-Key "abc-123"
  And marina composes again with the same Idempotency-Key "abc-123"
  Then only one version is created
  And TechLab AI is called exactly once
