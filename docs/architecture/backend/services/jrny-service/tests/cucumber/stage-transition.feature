Feature: Stage transition, journey conclusion and tenant isolation

# Refs SPEC-02 (Routing Engine / transitions), SPEC-03 (terminal stages), SPEC-06 (tenant guard),
# SPEC-09 (events). ADR-004 (cross-empresa guard), ADR-005. Reusable steps in SPEC-08.

Background:
  Given an active empresa "emp_acme" with provisioned schema
  And a published journey "Funil de Lançamento" with stages "CAPTURA,NUTRICAO,QUALIFICACAO,OFERTA,FECHAMENTO"
  And the stage "FECHAMENTO" is marked terminal

Scenario: Advancing a lead emits a stage-transition event
  Given lead "lead-1" is enrolled at stage "NUTRICAO"
  When the Routing Engine advances lead "lead-1" to stage "QUALIFICACAO"
  Then the lead current stage is "QUALIFICACAO"
  And a "journey-os.estagio.transicionado" event is emitted with origin "NUTRICAO" and destination "QUALIFICACAO"

Scenario: Reaching a terminal stage concludes the journey
  Given lead "lead-2" is enrolled at stage "OFERTA"
  When the Routing Engine advances lead "lead-2" to stage "FECHAMENTO"
  Then the enrolment state is "CONCLUIDA"
  And a "journey-os.jornada.concluida" event is emitted for lead "lead-2"

Scenario: A score change re-routes a lead to a later stage
  Given lead "lead-3" is enrolled at stage "NUTRICAO"
  And TechLab AI orchestration is unavailable
  When a "journey-os.lead.score.atualizado" event arrives for lead "lead-3" with score 85 and dimension INTENCAO 90
  Then the lead current stage is "OFERTA"
  And a "journey-os.estagio.transicionado" event is emitted

Scenario: A segment change triggers re-evaluation
  Given lead "lead-4" is enrolled at stage "NUTRICAO"
  And a rule routes to "QUALIFICACAO" when segment "INTERESSADOS" is entered
  When a "journey-os.lead.segmento.alterado" event arrives for lead "lead-4" with action "ENTROU" segment "INTERESSADOS"
  Then the lead current stage is "QUALIFICACAO"
  And a decisao_roteamento is written with result "ROTEADO"

Scenario: Publishing a new asset version refreshes stage content without re-routing
  Given the stage "OFERTA" references asset "asset-9"
  And lead "lead-5" is enrolled at stage "OFERTA"
  When a "journey-os.asset.versao.publicada" event arrives for asset "asset-9"
  Then the stage "OFERTA" content reference is refreshed
  And the lead current stage is still "OFERTA"
  And no decisao_roteamento is written for lead "lead-5"

Scenario: A lead has at most one active enrolment per journey
  Given lead "lead-6" already has an active enrolment in "Funil de Lançamento"
  When a "journey-os.lead.qualificado" event arrives again for lead "lead-6"
  Then no second active enrolment is created for lead "lead-6" in "Funil de Lançamento"

Scenario: Cross-empresa read is blocked
  Given lead "lead-7" is enrolled in empresa "emp_acme"
  And an authenticated user "intruso" from empresa "emp_other" with permission "jrny.roteamento.ler"
  When intruso queries the journey state of lead "lead-7"
  Then the response status is 404
  And the error code is "jrny.inscricao.nao-encontrada"

Scenario: The decision log answers why a lead is in its stage
  Given lead "lead-8" was routed to "OFERTA" by a rule
  And an authenticated user "lucas" with permission "jrny.roteamento.ler"
  When lucas queries the routing decisions of lead "lead-8"
  Then the result lists the decision that routed to "OFERTA"
  And the decision shows the fired rule and the input snapshot
