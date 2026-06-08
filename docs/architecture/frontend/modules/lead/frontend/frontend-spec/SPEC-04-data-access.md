# SPEC-04 — Data Access — LEAD · Frontend

> Services HTTP + facades de signal por recurso. Todas as chamadas via `@journeyos/shared/access-http-base`
> (interceptors injetam `Authorization`, `X-Empresa-Id`, `X-Correlation-Id`). Sem `BehaviorSubject` manual.

## Tabela mestre

| Resource | Endpoint (base) | Service | Facade | Operations | Cache? |
|---|---|---|---|---|---|
| Lead | `GET/POST /api/v1/leads` | `LeadApiService` | `LeadListFacade` / `LeadDetailFacade` | list, get, update, qualify, anonimizar, expurgar | no (fila fresca; última fila em memória por sessão) |
| Survey | `GET/POST /api/v1/surveys` | `SurveyApiService` | `SurveyFacade` | list, get, create, update, responder | no |
| QualificationRule | `GET/POST /api/v1/qualification/rules` | `QualificationApiService` | `QualificationFacade` | list, create, activate | no |
| Segment | `GET/POST /api/v1/segments` | `SegmentApiService` | `SegmentFacade` | list, get, create, update, delete, listLeads | no |

## Detalhe por operação

### LeadApiService → LeadListFacade / LeadDetailFacade
- `list(filtro, page, size)` → `GET /api/v1/leads?segmento=&estado=&q=&page=&size=` (Elastic-backed, paginado).
- `get(id)` → `GET /api/v1/leads/{id}` → inclui `perfil` + `score` (breakdown 6D + `versaoRegra` + `assistIa`).
- `update(id, atributos)` → `PUT /api/v1/leads/{id}` → BE recalcula; facade faz refetch do score.
- `qualify(id)` → `POST /api/v1/leads/{id}/qualify` → retorna breakdown atualizado.
- `anonimizar(id)` → `POST /api/v1/leads/{id}/anonimizar` (terminal LGPD).
- `expurgar(id)` → `DELETE /api/v1/leads/{id}` (LGPD — right to be forgotten).

### SurveyApiService → SurveyFacade
- `list()` / `get(id)` / `create(payload)` / `update(id, payload)` → `/api/v1/surveys[...]`.
- `responder(leadId, surveyId, respostas)` → `POST /api/v1/leads/{leadId}/surveys/{surveyId}/respostas`
  → BE faz upsert de atributos `origem=SURVEY` + recompute do score.

### QualificationApiService → QualificationFacade
- `list()` → `GET /api/v1/qualification/rules`.
- `create(payload)` → `POST /api/v1/qualification/rules` (nova versão, **inativa**).
- `activate(versao)` → `POST /api/v1/qualification/rules/{versao}/activate` (desativa a anterior atomicamente; BE recalcula afetados).

### SegmentApiService → SegmentFacade
- `list()` / `get(id)` / `create` / `update` / `delete(id)` (soft) → `/api/v1/segments[...]`.
- `listLeads(id, page, size)` → `GET /api/v1/segments/{id}/leads` (ordenado por Maturity Score desc).

## DTOs FE

- VMs mapeiam os shapes do BE (ver `03 §2`); enquanto `@journeyos/shared/contracts` (OpenAPI do LEAD)
  não existe, os tipos vivem em `libs/lead/data-access/models` e são substituídos quando o BE expor o
  contrato gerado.
- O campo `assistIa` é **lido diretamente** da resposta do score (não inferido pelo FE).

## Error mapping (resumo — detalhe no SPEC-07)

| BE `error.code` | HTTP | Tratamento FE |
|---|---|---|
| `lead.lead.anonimizado` | 409 | desabilita edição/qualify + aviso |
| `lead.qualification.sem-regra-ativa` | 409 | "Requalificar" desabilitado + CTA ativar regra |
| `lead.qualification.regra-nao-encontrada` | 404 | erro na ativação de versão |
| `lead.lead.base-legal-invalida` | 422 | erro de campo no formulário de perfil |
| `lead.segment.predicado-invalido` | 422 | erro de campo no editor de segmento |
| `lead.survey.pergunta-invalida` | 422 | erro de campo na captura de resposta |
| `lead.ia.indisponivel` | 200 | **não é erro** → badge "score determinístico" |

## Critérios de aceite (EARS)

- `THE SYSTEM SHALL route every LEAD data request through @journeyos/shared/access-http-base so that auth and empresa headers are injected automatically.`
- `WHEN a lead profile is updated, THE SYSTEM SHALL refetch the Maturity Score so the breakdown reflects the BE recompute.`
- `WHEN a qualification rule version is activated, THE SYSTEM SHALL mark that version as active in the QualificationFacade and SHALL clear the previously active flag.`
- `WHEN the active empresa changes, THE SYSTEM SHALL invalidate the in-memory lead queue before issuing any request for the new empresa.`
- `IF a list request fails, THEN THE SYSTEM SHALL expose the error via the facade error signal without throwing to the component tree.`

## Referências
- BE: `lead-service/contracts/api-contract.md` · `05-state-and-data-flow.md` · ADR-002
