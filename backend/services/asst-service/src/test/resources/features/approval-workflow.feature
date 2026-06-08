Feature: Asset approval and publication workflow

# Refs SPEC-02 (state machine), SPEC-01 (API), SPEC-09 (events). ADR-005.
# Reusable steps in SPEC-08.

Background:
  Given an active empresa "emp_acme" with provisioned schema
  And an authenticated user "marina" with permissions "asst.asset.submeter"
  And an authenticated user "rafael" with permissions "asst.asset.aprovar,asst.asset.publicar"
  And an asset "Oferta Black" of type "LANDING_PAGE" in state "RASCUNHO" with a draft version

Scenario: Submit a draft asset moves it to EM_REVISAO
  When marina submits the asset for review
  Then the asset state is "EM_REVISAO"

Scenario: Approve an asset under review
  Given the asset "Oferta Black" is in state "EM_REVISAO"
  When rafael approves the asset with comment "ok, publicar"
  Then the asset state is "APROVADO"
  And an approval record exists with reviewer "rafael" and decision "APROVADO"
  And a "journey-os.asset.aprovado" event is emitted

Scenario: Reject an asset under review notifies the author
  Given the asset "Oferta Black" is in state "EM_REVISAO"
  When rafael rejects the asset with comment "ajustar headline"
  Then the asset state is "REJEITADO"
  And a "journey-os.asset.rejeitado" event is emitted with comment "ajustar headline"

Scenario: Publish an approved asset sets the current version and emits the anchor event
  Given the asset "Oferta Black" is in state "APROVADO"
  When rafael publishes the asset
  Then the asset state is "PUBLICADO"
  And the asset has a current published version
  And a "journey-os.asset.versao.publicada" event is emitted

Scenario: Cannot publish an asset that is not approved
  Given the asset "Oferta Black" is in state "EM_REVISAO"
  When rafael publishes the asset
  Then the response status is 409
  And the error code is "asst.estado.transicao-invalida"

Scenario: Publishing a new version keeps the previous published version
  Given the asset "Oferta Black" has published version 1
  And version 2 is "APROVADO"
  When rafael publishes the asset
  Then the current published version is 2
  And version 1 is still retained

Scenario: Consuming services only see published versions
  Given the asset "Oferta Black" has draft version 3 and published version 2
  When the COMM service requests the published version via AssetQueryClient
  Then it receives version 2
  And it never receives version 3
