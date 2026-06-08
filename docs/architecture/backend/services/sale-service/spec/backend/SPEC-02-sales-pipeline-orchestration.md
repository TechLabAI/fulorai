# SPEC-02 — Sales Pipeline Orchestration (SALE)

## Objective
Define the core use case: opportunity lifecycle through the pipeline and its progression to a
confirmed purchase / recognized revenue (the golden path, anchor `compra.confirmada`).

## Scope
- **In:** create/move/win/lose opportunity; create opportunity from `lead.qualificado`; recognize revenue on purchase; trigger attribution + LTV; emit `oportunidade.*` / `compra.confirmada`.
- **Out:** attribution/LTV computation detail (SPEC-03), idempotency mechanics (SPEC-05), payment processing (external, never in scope).

## Technical decisions
- Use cases in `application.service` (`@Transactional`, `EmpresaContextHolder.require()`).
- Domain services (POJO): `PipelineService` (stage machine + win/lose), invoked by the use case (ADR-001).
- Opportunity from lead is created by the `lead.qualificado` consumer, idempotent by `leadId` (SPEC-05).
- Revenue recognition and the attribution+LTV chain run in the same short transaction as the purchase.

## Implementation & acceptance criteria (EARS)
### Opportunity
- `WHEN an oportunidade is created, THE SYSTEM SHALL persist it in estado NOVA and publish journey-os.oportunidade.criada.`
- `WHEN an oportunidade stage changes, THE SYSTEM SHALL append a historico_estagio row and publish journey-os.oportunidade.estagio.alterado.`
- `WHEN an oportunidade is marked won, THE SYSTEM SHALL set estado=GANHA and publish journey-os.oportunidade.ganha.`
- `WHEN an oportunidade is marked lost, THE SYSTEM SHALL set estado=PERDIDA with motivo_perda and publish journey-os.oportunidade.perdida.`
- `IF an oportunidade already in GANHA or PERDIDA receives another close, THEN THE SYSTEM SHALL reject with 409 'sale.oportunidade.ja-fechada'.`

### From lead
- `WHEN journey-os.lead.qualificado is consumed, THE SYSTEM SHALL create an oportunidade in the initial stage for that lead, or update the existing open one (no duplicate).`

### Purchase → revenue
- `WHEN a confirmed purchase is registered, THE SYSTEM SHALL recognize revenue, run attribution (SPEC-03), recompute LTV (SPEC-03) and publish journey-os.compra.confirmada in one transaction boundary.`
- `WHEN a purchase links an oportunidade, THE SYSTEM SHALL associate the compra to that oportunidade.`

## Edge cases
- Direct sale (no opportunity): revenue recognized; attribution uses lead/contact origin.
- A purchase arriving for a lost opportunity still recognizes revenue (the deal record stays PERDIDA but the sale is real) — flagged for analytics.

## Acceptance
- BDD `sales-pipeline.feature` + `purchase-revenue.feature` pass; events asserted.

## References
- ADR-001, ADR-003, ADR-005; SPEC-03, SPEC-05; `contracts/event-contracts.md`.
