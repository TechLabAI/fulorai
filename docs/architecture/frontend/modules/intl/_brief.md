# Brief — INTL (Intelligence & Platform) · Frontend

> Fonte estruturada para `/fe-architect-specs`, `/fe-architect-backlog` e `/fe-architect-scaffold`.
> **Compartilhado com o BE** (`docs/architecture/backend/services/intl-service/_brief.md`). O FE
> consome a mesma linguagem ubíqua e os mesmos contratos de Copilot/Conhecimento/Analytics; aqui o
> recorte é a **experiência do usuário** (telas, fluxos, estado de UI) sobre a API do `intl-service`.
> Módulo de **domínio + plataforma** (`type: standard`) — entrega a superfície de **AI Copilot**,
> **Base de Conhecimento** e **leitura analítica** do Journey OS.

| # | Item | Conteúdo |
|---|------|----------|
| 1 | **Nome canônico / Prefixo** | module `intl` / **INTL** · app lazy `apps/intl` · libs `libs/intl/*` · Nx scope `scope:intl` · npmScope `@journeyos` · issue prefix `FE-INTL-NNN` |
| 2 | **Problema que resolve (UX)** | Rafael (CEO) acumula dados em todos os módulos (leads, jornadas, mensagens, vendas) mas **não consegue perguntar em linguagem natural** ("por que esse funil caiu?", "qual copy converteu melhor?") nem **ver a analítica consolidada** espalhada por vários índices. Hoje é planilha + relatório manual. O FE INTL entrega: (a) uma **superfície de chat (AI Copilot)** onde se pergunta e se recebe **resposta fundamentada e citada**; (b) uma área de **curadoria da Base de Conhecimento** que alimenta o copiloto; (c) **dashboards analíticos** (funil, ROI, uso/custo do copiloto) — todos escopados à `empresa` ativa. |
| 3 | **Persona principal / secundária** | **Principal:** `INFOPRODUTOR` (Rafael) — usa o Copilot para perguntar sobre o negócio e lê analítica consolidada. **Secundária:** `HEAD_GROWTH` (Marina) — curadoria da Base de Conhecimento + analítica por origem/campanha; valida a fundamentação das respostas. **Terciária:** `SDR` (Lucas) — Copilot para resumos rápidos de contexto de lead/funil antes de uma call. **Consumidor-máquina:** o Shell e os demais módulos FE podem **deep-link** para o Copilot com contexto pré-carregado (pós-MVP). |
| 4 | **Recorte do MVP (in)** | (a) **AI Copilot (chat)** — abrir conversa, perguntar (RAG), renderizar resposta **com citações** (chips clicáveis para o documento-fonte), badges de status (`RESPONDIDA`/`NAO_FUNDAMENTADA`/`DEGRADADA`), histórico de conversa; (b) **Base de Conhecimento** — listar/buscar nós (`?q=&tag=&status=`), criar/editar nó manual, ação **indexar** (com estado assíncrono), arquivar; (c) **Analytics (read-only)** — dashboard de funil consolidado + painel de uso/custo do copiloto, filtros por período; (d) **Guards de acesso** (`authGuard`, `empresaGuard`, `accessGuard('intl.*')`) consumindo `AccessDecisionService`; (e) **Degradação graciosa na UI** — quando a resposta vem `DEGRADADA`/`NAO_FUNDAMENTADA`, a UI sinaliza claramente (sem mascarar como fato confirmado). |
| 5 | **Fora de escopo (MVP)** | Copilot com **ações/automações** (escrita de volta em outros módulos); **streaming token-a-token** (SSE) da resposta — MVP é request/response com estado "pensando" (ver ADR-005, sem endpoint de streaming no BE); **dashboard builder** / analytics preditivo / alerting; **editor rico de nós** (markdown avançado, anexos — MVP é texto + tags); **Integration Hub** (conectores 3rd-party); viewer de observabilidade (`app-logs`/`traces`/`metrics` — declarados no BE, sem UI de domínio no MVP); gestão de embeddings/reranking. |
| 6 | **Integrações externas obrigatórias** | **`intl-service` via `@journeyos/shared/access-http-base`** (todas as chamadas Copilot/Knowledge/Analytics, header `X-Empresa-Id` + `X-Correlation-Id` automáticos). Sem widgets 3rd-party no MVP. O FE **nunca** chama provedor de IA diretamente — toda IA é mediada pelo `intl-service` (que delega à TechLab AI). |
| 7 | **Serviços do Hub (deps FE)** | `@journeyos/shared/auth-session` (sessão/JWT — **obrigatório**), `@journeyos/shared/empresa-context` (empresa ativa — **obrigatório**; INTL **consome**, não alimenta), `@journeyos/shared/access-decision` (`AccessDecisionService` + `NavigationService` — **obrigatório**), `@journeyos/shared/access-http-base` (HTTP + interceptors — **obrigatório**), `@journeyos/shared/ui-components` · `ui-feedback` · `ui-tokens` (sempre), `@journeyos/shared/error-model` (mapear `ProblemDetail`, incl. `503 ai-unavailable`), `@journeyos/shared/observability` (recomendado — timing de pergunta→resposta, custo). **Dependência de domínio:** WRKS (auth/empresa/RBAC). Independente de LEAD/COMM/JRNY/SALE. |
| 8 | **Evento-âncora do domínio (UX)** | **"Copiloto respondeu"** — o golden path do FE: o usuário digita uma pergunta, a UI entra em estado `pensando`, e recebe de volta uma **resposta com citações** (ou um estado degradado claramente sinalizado). É o heartbeat da experiência: pergunta → resposta fundamentada e auditável renderizada com chips de citação. |

---

## Notas de contexto (Journey OS · FE)

- **Stack:** Angular 18+ · Nx 19+ · TypeScript strict · Signals-first (sem NgRx) · Standalone + OnPush · Jest (unit) · Playwright (e2e). npmScope `@journeyos`.
- **Padrão canônico:** `module-pattern` (slicing de libs por módulo — ver CLAUDE.md). App lazy em `apps/intl`, entry como library `@journeyos/intl` em `libs/intl/shell-entry` (ADR-006 global), demais libs em `libs/intl/{access,data-access,feature-*,integration,navigation,ui,styles}`.
- **Access Layer é cross-cutting:** INTL **consome** a sessão, a empresa ativa e o `AccessDecision` produzidos por WRKS; nenhuma feature reimplementa auth, lê `localStorage` ou decide RBAC inline (ver `access-layer-contracts.md`).
- **Fundamentação acima de fluência (espelho do BE):** a UI **nunca** apresenta uma resposta `NAO_FUNDAMENTADA`/`DEGRADADA` como fato confirmado — o status do BE vira um sinal visual explícito (badge + tooltip). Citações são chips clicáveis ancorados em `documentoId`/`indice`.
- **Multi-empresa:** INTL lê `empresaId` ativo só via `EmpresaContextService`; troca de empresa cancela perguntas in-flight, limpa a conversa corrente e recarrega Knowledge/Analytics escopados (nunca vaza dados cross-tenant na UI).
- **Type:** `standard` (autopilot) → A5 (e2e-validate) **aplicável** (specs Playwright gerados do SPEC-08).
- **Particularidade FE:** o Copilot tem **latência alta e variável** (RAG + composição de IA) — a UI precisa de um estado `pensando` robusto, cancelamento, e degradação visível; é o único módulo cuja resposta pode ser "parcial por design" (degradada).

## Referências canônicas consumidas

- `docs/architecture/backend/services/intl-service/_brief.md` — brief BE (espelho)
- `docs/architecture/backend/services/intl-service/{01,03}-*.md` — vision + domain framing BE
- `docs/architecture/backend/services/intl-service/contracts/api-contract.md` — endpoints `/api/v1/{copilot,knowledge,analytics}`
- `docs/architecture/frontend/standards/nx-boundaries.md` — tags + direções permitidas
- `docs/architecture/frontend/standards/access-layer-contracts.md` — contratos da Access Layer
- `docs/architecture/shared/blueprint-core.md` — modelo mental App + módulos + shared
