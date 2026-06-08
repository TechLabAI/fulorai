Feature: Asset creation and cataloguing

# Refs SPEC-01 (API surface), SPEC-02 (lifecycle), SPEC-06 (security/tenant guard)
# Reusable steps documented in SPEC-08-bdd-test-scenarios.md

Background:
  Given an active empresa "emp_acme" with provisioned schema
  And an authenticated user "marina" with permission "asst.asset.criar"

Scenario: Create a valid asset in RASCUNHO
  When marina creates an asset of type "EMAIL" with title "Boas-vindas"
  Then the response status is 201
  And the asset state is "RASCUNHO"
  And the asset has no current published version
  And a "journey-os.asset.criado" event is enqueued in the outbox

Scenario: Reject asset with an invalid type
  When marina creates an asset of type "PODCAST" with title "Episódio 1"
  Then the response status is 422
  And the error code is "asst.asset.tipo-invalido"

Scenario: Reject asset with a blank title
  When marina creates an asset of type "EMAIL" with title ""
  Then the response status is 422
  And the error code is "asst.asset.titulo-obrigatorio"

Scenario: Listing returns only assets of the caller's tenant
  Given an asset "Promo A" exists in empresa "emp_acme"
  And an asset "Promo B" exists in empresa "emp_other"
  When marina lists assets
  Then the result contains "Promo A"
  And the result does not contain "Promo B"

Scenario Outline: Create asset for each supported type
  When marina creates an asset of type "<tipo>" with title "<titulo>"
  Then the response status is 201
  And the asset state is "RASCUNHO"
  Examples:
    | tipo         | titulo            |
    | LANDING_PAGE | Página de captura |
    | EMAIL        | Sequência D1      |
    | CRIATIVO     | Reels manhã       |
    | ROTEIRO      | VSL oferta        |
    | DOCUMENTO    | Ebook isca        |
    | SCRIPT_SDR   | Abordagem fria    |
