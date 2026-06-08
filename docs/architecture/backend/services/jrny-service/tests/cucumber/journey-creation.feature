Feature: Journey Builder creation, publication and versioning

# Refs SPEC-01 (API surface), SPEC-03 (Journey Builder), SPEC-06 (security/tenant guard)
# ADR-005 (versioning: PUBLICADA is immutable in place). Reusable steps in SPEC-08.

Background:
  Given an active empresa "emp_acme" with provisioned schema
  And an authenticated user "marina" with permissions "jrny.jornada.criar,jrny.jornada.editar,jrny.estagio.criar"
  And an authenticated user "rafael" with permissions "jrny.jornada.publicar,jrny.jornada.arquivar,jrny.jornada.editar"

Scenario: Create a valid journey in RASCUNHO
  When marina creates a journey named "Funil de Lançamento"
  Then the response status is 201
  And the journey state is "RASCUNHO"
  And the journey version is 1

Scenario: Reject a journey with a blank name
  When marina creates a journey named ""
  Then the response status is 422
  And the error code is "jrny.jornada.nome-obrigatorio"

Scenario Outline: Add stages of each supported type to a draft journey
  Given a journey "Funil de Lançamento" in state "RASCUNHO"
  When marina adds a stage of type "<tipo>" at position <ordem> named "<nome>"
  Then the response status is 201
  And the stage type is "<tipo>"
  Examples:
    | tipo          | ordem | nome           |
    | CAPTURA       | 1     | Captura        |
    | NUTRICAO      | 2     | Nutrição       |
    | QUALIFICACAO  | 3     | Qualificação   |
    | OFERTA        | 4     | Oferta         |
    | FECHAMENTO    | 5     | Fechamento     |
    | POS_VENDA     | 6     | Pós-venda      |

Scenario: Reject a stage with an invalid type
  Given a journey "Funil de Lançamento" in state "RASCUNHO"
  When marina adds a stage of type "WEBINAR" at position 1 named "Webinar"
  Then the response status is 422
  And the error code is "jrny.estagio.tipo-invalido"

Scenario: Reject a stage that reuses an existing position
  Given a journey "Funil de Lançamento" in state "RASCUNHO" with a stage at position 1
  When marina adds a stage of type "NUTRICAO" at position 1 named "Outra"
  Then the response status is 409
  And the error code is "jrny.estagio.ordem-duplicada"

Scenario: Publish a draft journey that has stages
  Given a journey "Funil de Lançamento" in state "RASCUNHO" with 5 stages
  When rafael publishes the journey
  Then the response status is 200
  And the journey state is "PUBLICADA"
  And a "journey-os.jornada.publicada" event is enqueued in the outbox

Scenario: Cannot publish a journey without stages
  Given a journey "Funil Vazio" in state "RASCUNHO" with 0 stages
  When rafael publishes the journey
  Then the response status is 422
  And the error code is "jrny.jornada.sem-estagio"

Scenario: A published journey cannot be edited in place
  Given a journey "Funil de Lançamento" in state "PUBLICADA"
  When marina edits the journey metadata
  Then the response status is 409
  And the error code is "jrny.jornada.transicao-invalida"

Scenario: Editing a published journey creates a new draft version
  Given a journey "Funil de Lançamento" in state "PUBLICADA" at version 1
  When rafael creates a new version of the journey
  Then a draft journey at version 2 exists
  And the published version 1 is unchanged

Scenario: Archiving a journey keeps its stages and rules
  Given a journey "Funil Antigo" in state "PUBLICADA"
  When rafael archives the journey
  Then the journey state is "ARQUIVADA"
  And the journey stages and rules are still retained

Scenario: An archived journey does not enroll new leads
  Given a journey "Funil Antigo" in state "ARQUIVADA"
  When a lead qualifies for the archived journey
  Then no enrolment is created for the archived journey

Scenario: Listing returns only journeys of the caller's tenant
  Given a journey "Funil A" exists in empresa "emp_acme"
  And a journey "Funil B" exists in empresa "emp_other"
  When marina lists journeys
  Then the result contains "Funil A"
  And the result does not contain "Funil B"
