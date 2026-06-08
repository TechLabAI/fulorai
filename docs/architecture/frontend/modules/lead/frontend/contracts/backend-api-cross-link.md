# Backend API Cross-link — LEAD (FE ↔ `lead-service`)

> O FE LEAD consome exclusivamente o `lead-service`. Esta nota cruza os endpoints usados pelo FE com
> o contrato BE autoritativo e registra diffs/gaps.

- **Fonte BE:** `docs/architecture/backend/services/lead-service/contracts/api-contract.md`
- **Base path:** `/api/v1` · **Auth:** Bearer JWT (WRKS) · **Tenant:** `empresa_id` via claim do JWT
  (`X-Empresa-Id` só para debug/log).

## Endpoints consumidos pelo FE

| FE feature / facade | Método + Path BE | Permissão | Observações |
|---|---|---|---|
| `feature-lead-list` / `LeadListFacade` | `GET /leads` | `lead.lead.read` | paginado, filtros por segmento/score/estado; Elastic-backed |
| `feature-lead-detail` / `LeadDetailFacade` | `GET /leads/{id}` | `lead.lead.read` | inclui perfil + **breakdown 6D** + `assistIa` + `versaoRegra` |
| `feature-lead-detail` (editar) | `PUT /leads/{id}` | `lead.lead.editar` | atributos manuais; dispara recompute no BE |
| `feature-lead-detail` (requalificar) | `POST /leads/{id}/qualify` | `lead.qualification.executar` | retorna breakdown atualizado |
| `feature-lead-detail` (LGPD) | `POST /leads/{id}/anonimizar` · `DELETE /leads/{id}` | `lead.lead.anonimizar` / `lead.lead.expurgar` | terminais |
| `feature-survey` / `SurveyFacade` | `GET/POST /surveys`, `GET/PUT /surveys/{id}` | `lead.survey.*` | versão nova ao editar |
| `feature-survey` (responder) | `POST /leads/{leadId}/surveys/{surveyId}/respostas` | `lead.survey.responder` | upsert atributos `origem=SURVEY` + recompute |
| `feature-qualification-rules` / `QualificationFacade` | `GET/POST /qualification/rules`, `POST /qualification/rules/{versao}/activate` | `lead.qualification.*` | ativação atômica + recálculo de afetados |
| `feature-segmentation` / `SegmentFacade` | `GET/POST /segments`, `GET/PUT/DELETE /segments/{id}`, `GET /segments/{id}/leads` | `lead.segment.*` | leads ordenados por score desc |

## Diffs / gaps conhecidos

- **`@journeyos/shared/contracts` (OpenAPI do LEAD) ainda não publicado** → DTOs FE provisórios em
  `libs/lead/data-access/models`; substituir quando o BE expor o contrato gerado.
- **Dashboard de distribuição** (`feature-maturity-score`): o BE pode ainda não ter endpoint de
  agregação dedicado → no MVP derivar de `GET /leads` facetado/paginado; confirmar com o `lead-service`
  antes do scaffold (registrado em `06-risks-gaps-assumptions.md` Gap).
- **Dimensões 6D** (`PERFIL/ENGAJAMENTO/INTENCAO/CAPACIDADE/URGENCIA/ADERENCIA`) são "propostas a
  validar" no brief BE → confirmar rótulos finais contra o `lead-service` (ADR-005 do BE).
- **`lead.ia.indisponivel`** é HTTP **200** (não erro) — o FE trata como badge, nunca como falha.

## Referências
- BE `lead-service/contracts/api-contract.md` · `event-contracts.md` · `adr/ADR-005-maturity-score-model.md`
- `docs/architecture/integrations/techlab-ai-integration.md` (capacidade `qualification`)
