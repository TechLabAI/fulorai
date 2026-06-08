# 05 — State and Data Flow — LEAD · Frontend

> Topologia de estado, padrão de acesso a dados, cache, optimistic updates, erros e breadcrumbs.

## 1. State Topology

- **Local (por feature lib, via facade em `data-access`)** — signals privados + `.asReadonly()`:
  - `feature-lead-list`: `fila`, `filtros`, `paginacao`, `loading`, `error`.
  - `feature-lead-detail`: `leadSelecionado`, `score`, `acoes`, `editState`, `loading`, `error`.
  - `feature-maturity-score`: `scoreRadar` (de um lead) e `distribuicao` (base), `loading`, `error`.
  - `feature-segmentation`: `segmentos`, `predicadoEmEdicao`, `previewContagem`.
  - `feature-survey`: `surveys`, `perguntas`, `respostasEmEdicao`.
  - `feature-qualification-rules`: `versoes`, `versaoAtiva`, `activating`.
- **Transversal (NÃO no LEAD)** — sessão, empresa ativa e RBAC vivem em `@journeyos/shared/access-*`.
  O LEAD **consome** (`AuthSessionService`, `EmpresaContextService`, `AccessDecisionService`) e **reage**
  à troca de empresa (effect que invalida a fila/seleção em tela).

## 2. Data Access Pattern

- `HttpClient` (via `access-http-base`) encapsulado em services de `data-access`
  (`LeadApiService`, `SurveyApiService`, `QualificationApiService`, `SegmentApiService`).
- O service chama a API e **a facade emite signals** — sem `BehaviorSubject` manual.
- Mapeamento de endpoints → facade:
  - `GET /leads` (paged, Elastic) → `LeadListFacade.fila`.
  - `GET /leads/{id}` (perfil + breakdown) → `LeadDetailFacade.leadSelecionado` + `.score`.
  - `PUT /leads/{id}` → atualiza perfil; o BE recalcula → refetch do score.
  - `POST /leads/{id}/qualify` → atualiza `.score` com o novo breakdown.
  - `POST /leads/{id}/anonimizar` · `DELETE /leads/{id}` → ações LGPD (terminais).
  - `GET/POST /segments`, `GET /segments/{id}/leads` → `SegmentFacade`.
  - `GET/POST /surveys`, `POST /leads/{leadId}/surveys/{surveyId}/respostas` → `SurveyFacade`.
  - `GET/POST /qualification/rules`, `POST /qualification/rules/{versao}/activate` → `QualificationFacade`.

## 3. Cache Strategy

- **Padrão = chamar a API a cada navegação** (fila e detalhe sempre frescos — score muda no BE).
- Sem cache persistente no MVP. Exceção justificável: manter a **última fila** em memória durante a
  sessão da mesma empresa para voltar do detalhe sem refetch — invalidada na troca de empresa
  (documentar no SPEC se adotado).
- Distribuição/dashboard pode usar TTL curto (ex.: refetch sob ação de refresh), nunca stale silencioso.

## 4. Optimistic Updates

- **Evitar** no MVP para score/qualify (o resultado é autoridade do BE — mostrar `submitting` e refetch).
- Aceitável para **edição de campos de perfil triviais** (feedback imediato) com **rollback** ao erro
  (`PUT` falhou → reverter para o último valor confirmado + toast de erro). Documentar a estratégia de
  rollback por campo no SPEC-04.

## 5. Error Handling

- `ProblemDetail` (RFC 7807) do BE → `AppError` via `@journeyos/shared/error-model` → mensagem via
  `@journeyos/shared/ui-feedback`.
- Mapeamentos-chave:
  - `409 lead.lead.anonimizado` → desabilita edição/qualify + aviso "lead anonimizado".
  - `409 lead.qualification.sem-regra-ativa` → "Requalificar" desabilitado + CTA "ativar uma regra".
  - `404 lead.qualification.regra-nao-encontrada` → erro na ativação de versão.
  - `422 lead.lead.base-legal-invalida` / `422 lead.segment.predicado-invalido` /
    `422 lead.survey.pergunta-invalida` → erro de formulário no campo correspondente.
  - **`lead.ia.indisponivel` NÃO é erro** — o BE devolve 200 com `assistIa=false`; a UI mostra o badge
    "score determinístico", nunca um toast de erro.
- Erros transversais `iam.*` (JWT) são tratados pela Access Layer (redirect/login), não pelo LEAD.

## 6. Breadcrumbs e Navigation State

- `libs/lead/navigation` alimenta `BreadcrumbItem[]`:
  - `/lead/leads` → `Leads`
  - `/lead/leads/:id` → `Leads / {nome|leadId}`
  - `/lead/maturity` → `Leads / Maturity Score`
  - `/lead/segments` → `Leads / Segmentos` (`/segments/:id/leads` → `… / {nomeSegmento}`)
  - `/lead/surveys` → `Leads / Surveys`
  - `/lead/qualification` → `Leads / Regras`
- O menu lateral (deep links do `lead.contract.ts`) é filtrado por permissão via `NavigationService`.

---

## Referências

- `04-frontend-architecture-direction.md` · `03-domain-framing-frontend.md`
- BE: `docs/architecture/backend/services/lead-service/contracts/api-contract.md` (códigos de erro + EARS)
- `docs/architecture/frontend/standards/access-layer-contracts.md`
