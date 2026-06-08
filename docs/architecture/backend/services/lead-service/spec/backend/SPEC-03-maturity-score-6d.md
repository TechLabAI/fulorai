# SPEC-03 — Maturity Score (6D)

## Objective
Define the deterministic, explainable, AI-assisted computation of the 6-dimension Maturity Score.

## Scope
- **In:** the 6 dimensions, rule-driven contributions, aggregation, breakdown persistence, AI assist + fallback, idempotency of the result.
- **Out:** rule authoring API (SPEC-01), recompute orchestration (SPEC-02), ML/predictive scoring (post-MVP).

## The 6 dimensions
| Dimension | Meaning |
|---|---|
| `PERFIL` | Fit/ICP — matches the ideal customer profile. |
| `ENGAJAMENTO` | Interaction level (MVP: form/survey activity; cross-module signals post-MVP). |
| `INTENCAO` | Buying intent expressed via answers/signals. |
| `CAPACIDADE` | Budget / decision power. |
| `URGENCIA` | Timing / how soon. |
| `ADERENCIA` | Affinity to the offer/content (knowledge fit). |

## Technical decisions
- `MaturityScoreCalculator` (pure `domain.service`, ADR-001): given signals + active `regra_qualificacao`
  → `ScoreDimensao[]` + aggregate. Deterministic (ADR-005).
- Aggregate = weighted, clamped [0..100] function of the 6 dimension values (weights in the rule).
- Idempotency key `(lead_id, versao_regra, hash_sinais)` (SPEC-05).
- AI assist via `TechLabQualificationPort` (capability `qualification`); contributions tagged
  `origem=ASSIST_IA`; **fail-open** to deterministic on failure.

## Acceptance criteria (EARS)
- `THE SYSTEM SHALL compute exactly six dimension values (PERFIL, ENGAJAMENTO, INTENCAO, CAPACIDADE, URGENCIA, ADERENCIA), each in [0,100].`
- `THE SYSTEM SHALL persist a per-dimension breakdown recording the conditions that contributed (score_dimensao.contribuintes).`
- `THE SYSTEM SHALL derive the aggregate score deterministically from the dimension values and the active rule version.`
- `WHEN the same lead is recomputed with the same rule version and signal hash, THE SYSTEM SHALL produce the same aggregate score.`
- `WHERE the assist feature is enabled AND free-text signals exist, THE SYSTEM SHALL merge TechLab AI suggested contributions and set assist_ia=true.`
- `IF TechLab AI fails or its circuit breaker is open, THEN THE SYSTEM SHALL compute the deterministic score and set assist_ia=false WITHOUT failing the request.`
- `THE SYSTEM SHALL NOT let an AI-suggested contribution be the sole cause of a transition to QUALIFICADO or NAO_QUALIFICADO.`
- `WHEN the aggregate score is >= the active rule's limiar_qualificado, THE SYSTEM SHALL set estado_qualificacao=QUALIFICADO; otherwise NAO_QUALIFICADO.`

## Edge cases
- Missing signals for a dimension → that dimension scores 0 (not null); breakdown notes the gap.
- Rule with no conditions for a dimension → dimension contributes its neutral baseline.

## References
- ADR-005 (decision), ADR-001 (pure domain); `contracts/techlab-ai-integration.md`, `contracts/data-model.md` §3.9–3.10.
