# SPEC-03 — Revenue Attribution & LTV (SALE)

## Objective
Define the deterministic, explainable revenue attribution model and the LTV computation — the
critical domain decision of SALE (ADR-005).

## Scope
- **In:** attribution models (`LAST_TOUCH`/`FIRST_TOUCH`/`LINEAR`), versioning/activation, re-attribution, revenue conservation, LTV recompute.
- **Out:** opportunity lifecycle (SPEC-02), data-driven/ML attribution (post-MVP), payment.

## Technical decisions
- Domain services (POJO, ADR-001): `AttributionEngine` (distributes revenue across touchpoints by model), `LtvCalculator` (sums confirmed purchases per `contato_ref`).
- Attribution is **deterministic** and references the active `modelo_atribuicao.versao` (audit).
- Touchpoints (MVP): lead origin, campaign, journey (when present), or `DIRETO` fallback.
- **No TechLab AI** — attribution/LTV never call an AI provider in the MVP.

## Implementation & acceptance criteria (EARS)
### Attribution
- `WHEN revenue is recognized for a compra, THE SYSTEM SHALL distribute it across touchpoints using the active attribution model and persist one atribuicao row per touchpoint.`
- `THE SYSTEM SHALL ensure the sum of atribuicao.valor_atribuido for a compra equals compra.valor_total (revenue conservation).`
- `WHERE the active model is LAST_TOUCH, THE SYSTEM SHALL credit the full revenue to the last touchpoint.`
- `WHERE the active model is LINEAR, THE SYSTEM SHALL split the revenue evenly across the known touchpoints.`
- `WHILE no attribution model is active, THE SYSTEM SHALL apply LAST_TOUCH as the fallback.`
- `WHEN an attribution model version is activated, THE SYSTEM SHALL deactivate the previous one atomically and re-attribute affected compras, publishing journey-os.receita.atribuida.`
- `THE SYSTEM SHALL record versao_modelo on every atribuicao for auditability.`

### LTV
- `WHEN a compra is confirmed, estornada or cancelada, THE SYSTEM SHALL recompute the contact LTV as the deterministic sum of its CONFIRMADA purchases and publish journey-os.ltv.atualizado.`
- `THE SYSTEM SHALL exclude ESTORNADA and CANCELADA purchases from the LTV running total.`
- `THE SYSTEM SHALL be deterministic: the same set of confirmed purchases yields the same LTV.`

## Edge cases
- No identifiable touchpoint → single `DIRETO` attribution carrying the full revenue.
- Rounding in LINEAR split: the remainder cent is assigned to the first touchpoint so the sum stays exact.
- Reversal after re-attribution: LTV and attribution both reflect the new state; history retained.

## Acceptance
- BDD `revenue-attribution.feature` passes; conservation and determinism asserted.

## References
- ADR-005; `contracts/data-model.md` (atribuicao, ltv); `contracts/event-contracts.md`.
