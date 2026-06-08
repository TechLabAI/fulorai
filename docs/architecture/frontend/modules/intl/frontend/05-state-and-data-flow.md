# 05 — State and Data Flow — INTL

> Topologia de estado, padrão de acesso a dados, cache, updates otimistas, erros e navegação.

## 1. State Topology

| Estado | Onde vive | Forma |
|---|---|---|
| Sessão / JWT | `@journeyos/shared/auth-session` (global) | consumido |
| Empresa ativa | `@journeyos/shared/empresa-context` (global) | consumido; troca → reset INTL |
| AccessDecision (`intl.*`) | `@journeyos/shared/access-decision` (global) | consumido por guards/menu |
| Lista de conversas | `libs/intl/data-access` (CopilotFacade) | `signal<ConversaListItemVM[]>` |
| Conversa corrente (mensagens) | `CopilotFacade` | `signal<MensagemVM[]>` + `signal<status>` |
| Base de Conhecimento (lista + filtros) | `KnowledgeFacade` | `signal<Page<NoConhecimentoRowVM>>` + `signal<filtros>` |
| Nó em edição | `KnowledgeFacade` | `signal<NoConhecimentoFormVM \| null>` |
| Dashboards (funil / uso) | `AnalyticsFacade` | `signal<FunilVM>` · `signal<CopilotUsageVM>` |

Nenhum estado de INTL é global; tudo fica nas facades de `data-access`, escopado pela empresa ativa.

## 2. Data Access Pattern

- `HttpClient` em `*ApiService` (`CopilotApiService`, `KnowledgeApiService`, `AnalyticsApiService`)
  → facade emite signals. Sem `BehaviorSubject` manual.
- Interceptors de `access-http-base` injetam `Authorization`, `X-Empresa-Id`, `X-Correlation-Id`.
- **Copilot — perguntar:** facade insere otimisticamente `MensagemVM(USUARIO)` + bolha
  `COPILOTO(PENDENTE)`, dispara `POST .../perguntar` com um `AbortController`; no `200` substitui a
  bolha pelo `RespostaCopilotoResponse` (texto + `status` + `citacoes`).
- **Knowledge — indexar:** `POST /nos/{id}/indexar` (202) → atualiza `status` do row para `INDEXADO`;
  `503` → mantém `RASCUNHO` e expõe ação "tentar de novo".

## 3. Cache Strategy

- **Padrão = chamar a API a cada navegação** (sem cache especulativo).
- Exceção justificada: a **conversa corrente** é mantida em memória enquanto a tela do Copilot
  estiver montada (não re-fetch a cada digitação); o histórico vem de `GET /copilot/conversas/{id}`
  ao (re)selecionar uma conversa.
- Dashboards de Analytics: re-fetch ao mudar período/granularidade; sem cache entre sessões.
- **Troca de empresa invalida todos os caches em memória do INTL** (efeito de reset).

## 4. Optimistic Updates

- **Único caso otimista justificado: o envio de pergunta do Copilot** — a bolha do usuário e a
  bolha `PENDENTE` aparecem antes da resposta para dar feedback imediato (< 100 ms).
  - **Rollback:** erro de transporte/4xx → a bolha `COPILOTO` vira `ERRO` (com retry); a bolha do
    usuário permanece (a pergunta não se perde). Cancelamento → ambas as bolhas pendentes são
    removidas e o texto volta ao input.
- Knowledge e Analytics **não** usam updates otimistas (confirmam no response).

## 5. Error Handling

- `ProblemDetail` (RFC 7807) → `AppError` via `@journeyos/shared/error-model`; mensagens via
  `@journeyos/shared/ui-feedback`.
- Mapa de tratamento:
  - `401` → tratado pela Access Layer (re-auth).
  - `403` → guard oculta a rota; se vier em runtime, banner "sem permissão".
  - `404` (conversa/nó inexistente) → empty state + voltar à lista.
  - `409` (indexação concorrente) → "este nó está sendo indexado; recarregue".
  - `503` (`embedding-unavailable`) → **não-fatal**: ação "tentar de novo".
  - **Copilot nunca recebe `5xx` por falha de IA** — degrada para `200/DEGRADADA`, que é estado de
    UI, não erro.

## 6. Breadcrumbs e Navigation State

`libs/intl/navigation/` alimenta `BreadcrumbItem[]`:

```
Inteligência ▸ Copilot
Inteligência ▸ Copilot ▸ <título da conversa>
Inteligência ▸ Conhecimento
Inteligência ▸ Conhecimento ▸ Novo nó | <título do nó>
Inteligência ▸ Analítica ▸ Funil | Uso do Copilot
```

O menu (`NavigationService`) só mostra deep-links cujo `perm` o `AccessDecisionService` permite.

---

## Referências

- `03-domain-framing-frontend.md` (VMs e transições) · `04-frontend-architecture-direction.md`
- `docs/architecture/frontend/standards/access-layer-contracts.md`
- BE: `docs/architecture/backend/services/intl-service/contracts/api-contract.md`
