# Brief — LEAD (Lead Intelligence & Qualification) · Frontend

> Fonte estruturada para `/fe-architect-specs`, `/fe-architect-backlog` e `/fe-architect-scaffold`.
> **Compartilhado com o BE** (`docs/architecture/backend/services/lead-service/_brief.md`). O FE
> consome a mesma linguagem ubíqua e os mesmos contratos (`/api/v1/leads/**`, `/surveys`,
> `/qualification`, `/segments`, eventos, permissões `lead.*`); aqui o recorte é a **experiência do
> usuário** (telas, fluxos, estado de UI) sobre a API do `lead-service`.
> Módulo de **domínio núcleo** (`type: standard`) — depende apenas de WRKS (auth/empresa/RBAC);
> é consumido a jusante por JRNY e SALE, mas **não** depende deles no FE.

| # | Item | Conteúdo |
|---|------|----------|
| 1 | **Nome canônico / Prefixo** | module `lead` / **LEAD** · app lazy `apps/lead` · libs `libs/lead/*` · Nx scope `scope:lead` · npmScope `@journeyos` · issue prefix `FE-LEAD-NNN` |
| 2 | **Problema que resolve (UX)** | Marina (Head de Growth) e Lucas (SDR) recebem leads de muitas fontes (Meta Ads, Hotmart, formulários, listas) e hoje não têm **uma fila única, priorizada e explicável**. O FE LEAD dá a **superfície única** para: ver a **fila priorizada** de leads por Maturity Score, abrir um lead e entender **por que** o score é alto/baixo (breakdown das 6 dimensões), monitorar a **saúde/distribuição** da base, desenhar **segmentos** dinâmicos, configurar **surveys** que enriquecem o perfil e versionar **regras de qualificação**. O resultado é uma operação de growth que prioriza com confiança e um SDR que sabe quem abordar e por quê. |
| 3 | **Persona principal / secundária** | **Principal:** `HEAD_GROWTH` (Marina) — desenha regras de qualificação e segmentos, monitora a distribuição do Maturity Score e a saúde da base, ajusta surveys. **Secundária:** `SDR` (Lucas) — consome a **fila priorizada** e o **breakdown explicável** do score para abordar bem; restrito por `data_scope`. **Terciária:** `INFOPRODUTOR` (Rafael) — visão consolidada da qualidade/volume qualificado. **Consumidores-máquina:** JRNY/SALE/INTL consomem `lead.qualificado`/`lead.score.atualizado` via API/eventos BE (não pela UI LEAD). |
| 4 | **Recorte do MVP (in)** | (a) **Fila/lista de leads**: lista priorizada por Maturity Score com filtros por segmento/dimensão/estado + busca (Elastic, `GET /leads`); (b) **Detalhe do lead**: perfil tipado + **breakdown 6D explicável** + ações (editar perfil, forçar `qualify`, anonimizar/expurgar LGPD); (c) **Maturity Score (visualização)**: **radar 6D** reusável + dashboard de **distribuição/saúde da base** (`feature-maturity-score`); (d) **Segmentação**: CRUD de `segmento` (predicado sobre perfil+score) + listagem de leads do segmento; (e) **Surveys**: definição de `survey` + `pergunta`; captura de respostas para um lead; (f) **Qualification rules**: listar versões, criar nova versão (inativa), **ativar** versão, forçar recálculo; (g) **Guards de acesso** (`authGuard`, `empresaGuard`, `accessGuard('lead.*')`). |
| 5 | **Fora de escopo (MVP)** | **Roteamento/atribuição** de lead a SDR/jornada (UI de **JRNY**); **pipeline/oportunidade/venda** (UI de **SALE**); **disparo de comunicação/nutrição** (UI de **COMM**); **editor visual de regras/predicados** (MVP usa formulário estruturado/expressão textual validada, não canvas drag-and-drop); importação em massa com pipeline assíncrono/upload de CSV (MVP: captura unitária mediada pelo BE/integrações); dedup probabilística/merge manual com UI de comparação (MVP confia no dedup determinístico do BE, expõe apenas `duplicado=true`); analytics preditivo por tenant. |
| 6 | **Integrações externas obrigatórias** | **`lead-service` via `@journeyos/shared/access-http-base`** (todas as chamadas `/api/v1/leads/**`, `/surveys`, `/qualification`, `/segments`; header `X-Empresa-Id`/JWT automáticos). O **assist de IA** do Maturity Score é **inteiramente BE-side** (capacidade `qualification` via TechLab AI) — o FE **nunca** chama IA; apenas **reflete** se o score usou assist (`assist_ia=true|false`) e degrada visualmente quando o BE marca o score como determinístico. Sem widgets 3rd-party no MVP. |
| 7 | **Serviços do Hub (deps FE)** | `@journeyos/shared/auth-session` (sessão/JWT — **obrigatório**), `@journeyos/shared/empresa-context` (empresa ativa — **obrigatório**), `@journeyos/shared/access-decision` (`AccessDecisionService` + `NavigationService` — **obrigatório**), `@journeyos/shared/access-http-base` (HTTP + interceptors — **obrigatório**), `@journeyos/shared/ui-components` · `ui-feedback` · `ui-tokens` (sempre), `@journeyos/shared/error-model` (mapear `ProblemDetail` → `AppError`), `@journeyos/shared/observability` (recomendado — latência da fila, tempo até qualify, taxa de uso de assist). Candidatos a **patterns shared**: smart-table (fila), chart/radar (Maturity Score 6D). LEAD **não** depende de nenhum outro módulo de domínio. |
| 8 | **Evento-âncora do domínio (UX)** | **"Lead qualificado"** — o golden path do FE: *abrir a fila priorizada → escolher um lead → entender o breakdown 6D → agir (qualify/editar/segmentar)*. O momento de UI mais crítico é a **leitura do Maturity Score explicável** (radar 6D + contribuição por dimensão + versão de regra + badge assist IA), porque é o que dá confiança de priorização. A reavaliação de segmento e a atualização de score são refletidas de forma rastreável na UI. |

---

## Notas de contexto (Journey OS · FE)

- **Stack:** Angular 18+ · Nx 19+ · TypeScript strict · Signals-first (sem NgRx) · Standalone + OnPush · Jest (unit) · Playwright (e2e). npmScope `@journeyos`.
- **Padrão canônico:** `module-pattern` (slicing de libs por módulo — ver CLAUDE.md). App lazy em `apps/lead`, libs em `libs/lead/{access,data-access,feature-*,integration,navigation,ui,styles}`.
- **Score explicável é o produto, nunca caixa-preta (FE):** toda exibição do Maturity Score mostra o **breakdown por dimensão** (6D), a **versão de regra** que o produziu e se houve **assist de IA**. A UI nunca apresenta apenas o número agregado (ADR-005).
- **IA é assist BE-side, refletido na UI:** falha de IA não é erro do FE — o BE retorna o score determinístico com `assist_ia=false`; a UI mostra um badge "score determinístico" em vez de quebrar (degradação graciosa, espelha `lead.ia.indisponivel` que **não** é erro HTTP).
- **Multi-empresa:** todo lead/segmento/survey é escopado por `empresaId` ativo (via `EmpresaContextService`); troca de empresa **invalida a fila/segmentos em tela** antes de mostrar os da nova empresa (sem vazamento cross-empresa — LGPD).
- **LGPD na UI:** o detalhe do lead expõe `base_legal`/consentimento e as ações **anonimizar**/**expurgar** (gated por `lead.lead.anonimizar`/`lead.lead.expurgar`); lead `ANONIMIZADO` desabilita edição de perfil na UI (espelha `409 lead.lead.anonimizado`).
- **Type:** `standard` (autopilot) → A5 (e2e-validate) **aplicável** (specs Playwright gerados do SPEC-08).

## Referências canônicas consumidas

- `docs/architecture/backend/services/lead-service/_brief.md` — brief BE (espelho)
- `docs/architecture/backend/services/lead-service/{01,03}-*.md` — vision + domain framing BE
- `docs/architecture/backend/services/lead-service/contracts/api-contract.md` — superfície REST `/api/v1/leads/**`, `/surveys`, `/qualification`, `/segments`
- `docs/architecture/backend/services/lead-service/adr/ADR-005-maturity-score-model.md` — modelo do Maturity Score (6D)
- `docs/architecture/frontend/standards/nx-boundaries.md` — tags + direções permitidas
- `docs/architecture/frontend/standards/access-layer-contracts.md` — contratos da Access Layer
- `docs/architecture/shared/blueprint-core.md` — modelo mental App + módulos + shared
