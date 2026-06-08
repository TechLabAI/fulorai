Feature: Routing Engine decision on lead qualification

# Refs SPEC-02 (Routing Engine & orchestration), SPEC-05 (idempotency), SPEC-09 (messaging)
# ADR-005 (deterministic first, AI assist optional, immutable decision log). Steps in SPEC-08.

Background:
  Given an active empresa "emp_acme" with provisioned schema
  And a published journey "Funil de Lançamento" with stages "CAPTURA,NUTRICAO,QUALIFICACAO,OFERTA,FECHAMENTO"
  And an entry rule routes a lead to "CAPTURA"
  And a rule with priority 10 routes to "OFERTA" when "scoreAgregado >= 80 AND dimensoes.INTENCAO >= 80"
  And a rule with priority 20 routes to "NUTRICAO" when "scoreAgregado < 50"

Scenario: A qualified hot lead is enrolled and routed to OFERTA
  Given TechLab AI orchestration is unavailable
  When a "journey-os.lead.qualificado" event arrives for lead "lead-1" with score 85 and dimension INTENCAO 90
  Then an active enrolment is created for lead "lead-1"
  And the lead current stage is "OFERTA"
  And a decisao_roteamento is written with result "ROTEADO"
  And the decision assist_ia is "INDISPONIVEL"
  And a "journey-os.lead.roteado" event is emitted
  And a "journey-os.estagio.transicionado" event is emitted

Scenario: Priority ordering decides between competing rules
  Given TechLab AI orchestration is unavailable
  When a "journey-os.lead.qualificado" event arrives for lead "lead-2" with score 85 and dimension INTENCAO 90
  Then the rule with priority 10 is the fired rule
  And the lead current stage is "OFERTA"

Scenario: AI assist is used and recorded when available
  Given TechLab AI orchestration is available and recommends "OFERTA" with confidence 0.9
  When a "journey-os.lead.qualificado" event arrives for lead "lead-3" with score 82 and dimension INTENCAO 85
  Then a decisao_roteamento is written with result "ROTEADO"
  And the decision assist_ia is "USADO"
  And the decision snapshot records the AI suggestion and confidence

Scenario: A mandatory guard rule overrides the AI recommendation
  Given a mandatory guard rule routes to "NUTRICAO" when "estadoQualificacao = NAO_QUALIFICADO"
  And TechLab AI orchestration is available and recommends "OFERTA" with confidence 0.95
  When a "journey-os.lead.qualificado" event arrives for lead "lead-4" with state "NAO_QUALIFICADO"
  Then the lead current stage is "NUTRICAO"
  And the decision assist_ia is "IGNORADO"

Scenario: No applicable journey produces a NAO_ROTEADO decision
  Given the lead "lead-5" matches no published journey
  When a "journey-os.lead.qualificado" event arrives for lead "lead-5"
  Then a decisao_roteamento is written with result "NAO_ROTEADO"
  And no "journey-os.lead.roteado" event is emitted

Scenario: Re-evaluation with no firing rule logs SEM_MUDANCA
  Given lead "lead-6" is enrolled at stage "NUTRICAO"
  And TechLab AI orchestration is unavailable
  When a "journey-os.lead.score.atualizado" event arrives for lead "lead-6" with score 40
  Then a decisao_roteamento is written with result "SEM_MUDANCA"
  And the lead current stage is still "NUTRICAO"
  And no "journey-os.lead.roteado" event is emitted

Scenario: A score increase re-routes an enrolled lead
  Given lead "lead-7" is enrolled at stage "NUTRICAO"
  And TechLab AI orchestration is unavailable
  When a "journey-os.lead.score.atualizado" event arrives for lead "lead-7" with score 85 and dimension INTENCAO 90
  Then the lead current stage is "OFERTA"
  And a decisao_roteamento is written with result "ROTEADO"
  And a "journey-os.estagio.transicionado" event is emitted

Scenario: Every decision records the input snapshot that produced it
  Given TechLab AI orchestration is unavailable
  When a "journey-os.lead.qualificado" event arrives for lead "lead-8" with score 85 and dimension INTENCAO 90
  Then the decisao_roteamento records the input snapshot with score 85
  And the decision records the gatilho "lead.qualificado"

Scenario: A decisao_roteamento is immutable once written
  Given a decisao_roteamento exists for lead "lead-9"
  When a correction is attempted on that decision
  Then the original decision is unchanged
  And a new decisao_roteamento is written instead

Scenario: Re-consuming the same qualification event is idempotent
  Given a "journey-os.lead.qualificado" event with eventId "evt-100" was already processed for lead "lead-10"
  When the same "journey-os.lead.qualificado" event with eventId "evt-100" arrives again
  Then no duplicate enrolment is created for lead "lead-10"
  And no duplicate decisao_roteamento is written
