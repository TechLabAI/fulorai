Feature: Template authoring, composition and rendering

# Refs SPEC-01 (API), SPEC-02 (rendering), SPEC-10 (TechLab AI). ADR-003.
# Reusable steps in SPEC-08.

Background:
  Given an active empresa "emp_acme" with provisioned schema
  And an authenticated user "marina" with permissions "comm.template.criar,comm.template.editar,comm.template.publicar,comm.studio.compor"

Scenario: Create a template in RASCUNHO
  When marina creates a template "Boas-vindas" for channel "WHATSAPP" of type "TRANSACIONAL" with body "Olá {{nome}}!"
  Then the response status is 201
  And the template state is "RASCUNHO"
  And the template declares variable "nome"

Scenario: Reject a body referencing an undeclared variable
  When marina creates a template "Quebrado" for channel "EMAIL" with body "Olá {{nome}}" and declared variables ""
  Then the response status is 422
  And the error code is "comm.template.variavel-nao-declarada"

Scenario: Email template requires a subject
  When marina creates a template "Newsletter" for channel "EMAIL" with no subject
  Then the response status is 422
  And the error code is "comm.template.assunto-obrigatorio"

Scenario: Reject an invalid channel
  When marina creates a template "X" for channel "PIGEON"
  Then the response status is 422
  And the error code is "comm.template.canal-invalido"

Scenario: Activate a draft template makes it dispatchable
  Given a RASCUNHO template "Boas-vindas" for channel "WHATSAPP"
  When marina activates the template "Boas-vindas"
  Then the template state is "ATIVO"

Scenario: Template Studio composes a draft body via TechLab AI
  Given a RASCUNHO template "Promo" for channel "WHATSAPP"
  And TechLab AI document_composition is available
  When marina composes the template "Promo" from brief "oferta black friday curso"
  Then the response status is 200
  And the template body is updated in state "RASCUNHO"
  And the briefComposicao is recorded on the template

Scenario: Template Studio degrades gracefully when TechLab AI is down
  Given a RASCUNHO template "Promo" for channel "WHATSAPP"
  And TechLab AI is unavailable
  When marina composes the template "Promo" from brief "oferta"
  Then the response status is 503
  And the error code is "comm.studio.ia-indisponivel"
  And the template body is unchanged

Scenario: Rendering substitutes declared variables
  Given an ATIVO template "Boas-vindas" for channel "WHATSAPP" with body "Olá {{nome}}!"
  When the message to lead "lead-1" is rendered with variables nome="Rafael"
  Then the rendered content is "Olá Rafael!"
