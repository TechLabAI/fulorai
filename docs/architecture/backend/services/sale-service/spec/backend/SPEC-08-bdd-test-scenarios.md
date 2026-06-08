# SPEC-08 — BDD Test Scenarios (SALE)

## Objective
Map EARS acceptance criteria to executable Cucumber scenarios (D-218 gate: every SHALL → a scenario).

## Scope
- **In:** feature inventory, reusable steps, example data, traceability to SPECs.
- **Out:** unit tests (per service), Pact contracts (post-MVP).

## Feature inventory

| Feature file | Covers | Key SHALL clauses |
|---|---|---|
| `sales-pipeline.feature` | SPEC-02, api §1, oportunidade.* events | create/move/win/lose, lead→opportunity dedup |
| `purchase-revenue.feature` | SPEC-02/05, api §3, compra.confirmada | idempotent ingestion, revenue conservation, estorno |
| `revenue-attribution.feature` | SPEC-03, api §4/§5, receita.atribuida/ltv.atualizado | last/linear-touch, conservation, deterministic LTV |

## Reusable steps (documented here, not in `.feature`)
- `Given the empresa "<slug>" is ATIVA` — establishes `EmpresaContextHolder`.
- `Given a default LAST_TOUCH attribution model version 1 is active` — seeds `modelo_atribuicao`.
- `Then the event "<topic>" is published` — asserts outbox/Kafka emission.
- `Then the response status is <code>` / `And the error code is "<code>"` — ProblemDetail assertions.

## Example data
- Buyer `rafael@acme.com`; offer `curso-pro` 1997.00 BRL; order ids `HOT-9981`, `HOT-7000..7002`.

## Acceptance criteria (EARS)
- `THE SYSTEM SHALL provide a Cucumber scenario for every SHALL clause across SPEC-01..10 and the contracts.`
- `WHEN the BDD suite runs, THE SYSTEM SHALL execute all features under src/test/resources/features against a Testcontainers PostgreSQL + Kafka.`

## References
- `tests/cucumber/*.feature`; `be-spec-to-bdd.py` (generate); `testing-conventions.md`.
