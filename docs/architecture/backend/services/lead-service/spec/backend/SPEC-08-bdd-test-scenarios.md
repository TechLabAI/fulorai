# SPEC-08 — BDD Test Scenarios (LEAD)

## Objective
Map the EARS acceptance criteria to executable Cucumber features and document reusable steps.

## Feature files
| Feature | Covers |
|---|---|
| `tests/cucumber/lead-capture.feature` | SPEC-02 capture/dedup, api §1, LGPD edits, cross-empresa guard |
| `tests/cucumber/lead-qualification.feature` | SPEC-02/03 qualify, rule activation, segments, api §3/§4 |
| `tests/cucumber/maturity-score.feature` | SPEC-03 6D breakdown, idempotency, AI assist + fallback |

## Reusable step definitions (to implement in `*StepDefs`)
- `Given the empresa "<slug>" is ATIVA` — provisions a tenant schema (Testcontainers).
- `Given an active qualification rule version <n> with threshold <t>` — seeds `regra_qualificacao`.
- `When a lead is captured with email "<e>" source "<s>" baseLegal "<b>"` — POST `/leads`.
- `When the lead is qualified` — POST `/leads/{id}/qualify`.
- `Then the event "<topic>" is published ...` — asserts on the test Kafka broker (or outbox table).
- `Given TechLab AI is available|unavailable` — toggles a WireMock/stub for the assist port.

## Test pyramid
- **Unit:** `MaturityScoreCalculator`, `QualificationRuleEngine`, `SegmentEvaluator` (pure, no Spring).
- **Integration (Testcontainers + Cucumber):** capture→qualify→segment→publish golden path; singleton container pattern (no `@Testcontainers`/`@Container`).
- **Contract:** ProblemDetail + permissions per `api-contract.md`.

## Acceptance criteria (EARS)
- `THE SYSTEM SHALL have at least one BDD scenario for every SHALL clause in SPEC-01..06 and SPEC-09 (gate D-218).`
- `THE SYSTEM SHALL run BDD scenarios against a real PostgreSQL via the singleton Testcontainer.`

## References
- `tests/cucumber/*.feature`; `docs/architecture/backend/standards/testing-conventions.md`; D-218.
