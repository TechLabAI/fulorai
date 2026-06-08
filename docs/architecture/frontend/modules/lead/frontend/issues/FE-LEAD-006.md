## [FE-LEAD-006] Qualification data-access: QualificationApiService + QualificationFacade

**Status (validação):** INTACT — pós-validação 2026-06-05
**Maturidade:** 8 — Inicial
**Done/Total:** 0/4 itens

**Status:** 🔲 ABERTA
**GitHub:** [#TBD]

**Outcome:**
`QualificationApiService` (list/create/activate) + `QualificationFacade` com signals (`versoes`,
`versaoAtiva`, `activating`, `error`). Ativar marca a nova versão como ativa e limpa a anterior.

**Context / Problem statement:**
- Governança de regras versionadas; ativação atômica no BE (recalcula afetados). Fonte: SPEC-04, SPEC-07.
- Bloqueia: FE-LEAD-016 (feature-qualification-rules).

**Approach (execution path):**
1) `QualificationApiService` (`/api/v1/qualification/rules`, `.../{versao}/activate`).
2) `QualificationFacade`: `list`, `create` (versão inativa), `activate(versao)` → atualiza `versaoAtiva`.

**Non-goals:** UI do editor de versão (FE-LEAD-016); requalificar lead (FE-LEAD-004).

**Layer(s):** frontend / `libs/lead/data-access`
**Bounded context:** lead

**Service execution spec(s):** `frontend-spec/SPEC-04-data-access.md`

**Architecture alignment:** Signals-first; tag `scope:lead` `type:data-access`.

**Implementation checklist (by file):**
- 🔲 `libs/lead/data-access/src/lib/qualification-api.service.ts` — _MISSING_
- 🔲 `libs/lead/data-access/src/lib/qualification.facade.ts` — _MISSING_

**Tests**
- 🔲 `nx test lead-data-access` PASS — _MISSING_ · 🔲 `nx lint lead-data-access` PASS — _MISSING_

**Milestone:** Wave P2 / Data access
**Labels:** type:feature · layer:frontend · scope:lead · priority:P2

**Acceptance criteria:**
- `npx nx test/lint/build lead-data-access` PASS
- `WHEN` versão ativada, `versaoAtiva` reflete a nova e a anterior é limpa (SPEC-04 EARS)

**Dependencies:** FE-LEAD-002, INT-FE-LEAD-001
**API / Contract impact:** `GET/POST /qualification/rules`, `POST /qualification/rules/{versao}/activate`.
**Risks / Notes:** tratar `404 regra-nao-encontrada` / `409 sem-regra-ativa` (FE-LEAD-008).
