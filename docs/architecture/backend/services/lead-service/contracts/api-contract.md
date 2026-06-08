# API Contract — LEAD (`/api/v1/leads/**`, `/surveys`, `/qualification`, `/segments`)

> REST surface of `lead-service`. All error responses use `application/problem+json` (RFC 7807,
> `shared/contratos/error-model.md`). EARS invariants per endpoint.
> Guide: `docs/architecture/backend/standards/ears-notation.md`.

## Conventions

- Base path: `/api/v1`.
- Auth: Bearer JWT (RS256) issued by WRKS; validated via WRKS JWKS. No anonymous endpoints
  except `/actuator/health`. Public capture (landing pages) is mediated by GWY/integration with a
  service token — not anonymous on LEAD.
- Tenant: `empresa_id` travels as a JWT claim → `EmpresaContextHolder`. `X-Empresa-Id` accepted for
  debug/log only; never overrides the claim.
- Mandatory headers: `Authorization`, `X-Correlation-Id` (propagated/generated).
- Authorization: `lead.*` permissions evaluated via WRKS `AccessDecision` (cached; invalidated by
  `journey-os.modelo.acesso.alterado`).

---

## 1. Leads — `/leads`  · perm `lead.lead.*`

| Verb | Path | Permission | Notes |
|---|---|---|---|
| POST | `/leads` | `lead.lead.criar` | idempotent capture (dedup by `chave_natural`) |
| GET | `/leads` | `lead.lead.read` | paged, filter by segment/score/state; backed by Elastic |
| GET | `/leads/{id}` | `lead.lead.read` | includes profile + score breakdown |
| PUT | `/leads/{id}` | `lead.lead.editar` | profile attributes (manual) |
| POST | `/leads/{id}/anonimizar` | `lead.lead.anonimizar` | LGPD anonymization (terminal) |
| DELETE | `/leads/{id}` | `lead.lead.expurgar` | LGPD physical purge (right to be forgotten) |

- Request (POST): `{ "email": "...", "telefone": "...", "nome": "...", "fonte": "meta-ads", "baseLegal": "CONSENTIMENTO", "atributos": { ... } }`
- Response 201: `{ "leadId": "uuid", "estadoQualificacao": "EM_QUALIFICACAO", "duplicado": false }`.

- `WHEN a lead is captured with a chave_natural not yet present in the empresa, THE SYSTEM SHALL create a new lead in state EM_QUALIFICACAO and publish journey-os.lead.capturado.`
- `WHEN a lead is captured with a chave_natural that already exists, THE SYSTEM SHALL merge the incoming attributes into the existing lead and SHALL NOT create a duplicate (response duplicado=true).`
- `IF baseLegal is absent or not in the allowed set, THEN THE SYSTEM SHALL reject with 422 error.code 'lead.lead.base-legal-invalida'.`
- `WHEN a lead is anonymized, THE SYSTEM SHALL clear PII columns, set estado_qualificacao=ANONIMIZADO, and retain aggregate score rows.`
- `IF a lead is in ANONIMIZADO, THEN THE SYSTEM SHALL reject further profile edits with 409 error.code 'lead.lead.anonimizado'.`

## 2. Surveys — `/surveys`  · perm `lead.survey.*`

| Verb | Path | Permission |
|---|---|---|
| GET/POST | `/surveys` | `lead.survey.read` / `lead.survey.criar` |
| GET/PUT | `/surveys/{id}` | `read` / `editar` (creates new version) |
| POST | `/leads/{leadId}/surveys/{surveyId}/respostas` | `lead.survey.responder` |

- `WHEN survey answers are submitted for a lead, THE SYSTEM SHALL upsert the matching atributo_perfil rows (origem=SURVEY) and SHALL trigger a Maturity Score recompute.`
- `IF an answer references a pergunta not belonging to the survey, THEN THE SYSTEM SHALL reject with 422 error.code 'lead.survey.pergunta-invalida'.`

## 3. Qualification rules — `/qualification/rules`  · perm `lead.qualification.*`

| Verb | Path | Permission |
|---|---|---|
| GET | `/qualification/rules` | `lead.qualification.read` |
| POST | `/qualification/rules` | `lead.qualification.criar` (new version, inactive) |
| POST | `/qualification/rules/{versao}/activate` | `lead.qualification.ativar` |
| POST | `/leads/{id}/qualify` | `lead.qualification.executar` (force recompute) |

- `WHEN a qualification rule version is activated, THE SYSTEM SHALL deactivate the previous active version atomically and SHALL recompute affected leads' scores.`
- `WHEN /leads/{id}/qualify is invoked, THE SYSTEM SHALL recompute the Maturity Score using the active rule version and return the breakdown.`
- `IF activating a rule version that does not exist, THEN THE SYSTEM SHALL respond 404 error.code 'lead.qualification.regra-nao-encontrada'.`
- `WHILE no qualification rule is active, THE SYSTEM SHALL reject qualify requests with 409 error.code 'lead.qualification.sem-regra-ativa'.`

## 4. Segments — `/segments`  · perm `lead.segment.*`

| Verb | Path | Permission |
|---|---|---|
| GET/POST | `/segments` | `lead.segment.read` / `lead.segment.criar` |
| GET/PUT/DELETE | `/segments/{id}` | `read` / `editar` / `excluir` (soft) |
| GET | `/segments/{id}/leads` | `lead.segment.read` (paged, priority order) |

- `WHEN a lead's profile or score changes, THE SYSTEM SHALL re-evaluate active segment predicates and publish journey-os.lead.segmento.alterado for each membership change.`
- `THE SYSTEM SHALL list segment leads ordered by Maturity Score descending by default.`

---

## Error catalogue (LEAD)

| error.code | HTTP | category |
|---|---|---|
| `lead.lead.base-legal-invalida` | 422 | validation |
| `lead.lead.nao-encontrado` | 404 | not_found |
| `lead.lead.anonimizado` | 409 | conflict |
| `lead.survey.pergunta-invalida` | 422 | validation |
| `lead.qualification.regra-nao-encontrada` | 404 | not_found |
| `lead.qualification.sem-regra-ativa` | 409 | business_rule |
| `lead.segment.predicado-invalido` | 422 | validation |
| `lead.ia.indisponivel` | 200* | degraded (assist skipped, not an error response) |

> `lead.ia.indisponivel` is **not** a client error — TechLab AI failure degrades to the deterministic
> score (assist_ia=false) and the request still succeeds (see SPEC-03 / `techlab-ai-integration.md`).
> Cross-cutting `iam.*` JWT codes are emitted on token validation (see WRKS `api-contract.md`).
