# SPEC-02 — Lead Qualification Orchestration (LEAD core)

## Objective
Define the golden-path use case: **capture → profile → qualify → segment → publish** — the heart of LEAD.

## Scope
- **In:** capture/dedup, profile consolidation, triggering the score (SPEC-03), segment re-evaluation, event publication.
- **Out:** the scoring math itself (SPEC-03); downstream routing/sales/comm (other modules).

## Technical decisions
- Orchestration lives in `application.service` (the only `@Transactional` layer). Domain rules
  (`QualificationRuleEngine`, `SegmentEvaluator`) are pure POJOs in `domain.service` (ADR-001).
- Capture is idempotent by `chave_natural` (SPEC-05). Events via transactional outbox (ADR-003).

## Implementation (flow)
1. Resolve `EmpresaContextHolder.require()`.
2. Capture: normalize `chave_natural`; create or merge `lead`/`perfil_lead`/`atributo_perfil`.
3. Publish `lead.capturado`.
4. Invoke `QualificationRuleEngine` with the active rule → per-dimension contributions.
5. Optionally call TechLab AI assist (SPEC-03); merge with fallback.
6. Persist `maturity_score` + `score_dimensao`; set `estado_qualificacao`.
7. Publish `lead.qualificado` (and `lead.score.atualizado` on recompute).
8. Re-evaluate segments; publish `lead.segmento.alterado` per change; (re)index in Elastic.

## Acceptance criteria (EARS)
- `WHEN a lead is captured, THE SYSTEM SHALL create-or-merge by chave_natural and publish journey-os.lead.capturado.`
- `WHEN profile signals change (capture, survey, manual edit), THE SYSTEM SHALL trigger a Maturity Score recompute.`
- `WHEN a recompute transitions the lead to QUALIFICADO, THE SYSTEM SHALL publish journey-os.lead.qualificado.`
- `WHEN a recompute changes the aggregate score without a state transition, THE SYSTEM SHALL publish journey-os.lead.score.atualizado.`
- `WHEN profile or score changes, THE SYSTEM SHALL re-evaluate active segment predicates and publish journey-os.lead.segmento.alterado per membership change.`
- `IF no qualification rule is active, THEN THE SYSTEM SHALL reject qualify requests with 409 'lead.qualification.sem-regra-ativa'.`
- `WHILE the empresa context is unresolved, THE SYSTEM SHALL NOT perform any data operation.`

## Edge cases
- Merge conflicts: last-write per `(lead, chave)` attribute, preserving `origem`.
- Recompute on rule activation runs as a small synchronous batch (MVP); large volumes deferred (R5).

## References
- ADR-002, ADR-003, ADR-005; SPEC-03, SPEC-05, SPEC-09; `contracts/event-contracts.md`.
