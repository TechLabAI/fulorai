# Brief — ASST (Asset Hub) · Frontend

> Fonte estruturada para `/fe-architect-specs`, `/fe-architect-backlog` e `/fe-architect-scaffold`.
> **Compartilhado com o BE** (`docs/architecture/backend/services/asst-service/_brief.md`). O FE
> consome a mesma linguagem ubíqua e os mesmos contratos (`/api/v1/assets/**`, eventos, permissões
> `asst.*`); aqui o recorte é a **experiência do usuário** (telas, fluxos, estado de UI) sobre a API
> do `asst-service`.
> Módulo de **domínio independente** (`type: standard`) — depende apenas de WRKS (auth/empresa/RBAC);
> independente de LEAD, COMM, JRNY e SALE no FE.

| # | Item | Conteúdo |
|---|------|----------|
| 1 | **Nome canônico / Prefixo** | module `asst` / **ASST** · app lazy `apps/asst` · libs `libs/asst/*` · Nx scope `scope:asst` · npmScope `@journeyos` · issue prefix `FE-ASST-NNN` |
| 2 | **Problema que resolve (UX)** | Marina (Head de Growth) coordena a produção de dezenas de ativos de conteúdo por campanha — landing pages, sequências de e-mail, criativos, roteiros, documentos e scripts de SDR — hoje espalhados em Drive + Notion + Canva + threads de WhatsApp, **sem versão vigente confiável, sem trilha de aprovação e sem reuso estruturado**. O FE ASST dá a **superfície única** para: catalogar e buscar assets, compor rascunhos com o **Asset Studio** (IA via TechLab AI), navegar pelo histórico de versões imutáveis, submeter para aprovação e (para o aprovador) **aprovar/rejeitar/publicar**. Um asset publicado vira insumo de primeira classe para COMM/JRNY/SALE. |
| 3 | **Persona principal / secundária** | **Principal:** `HEAD_GROWTH` (Marina) — cria, organiza, compõe (Asset Studio) e submete assets; coordena o time de copy/criativo. **Secundária:** `INFOPRODUTOR` (Rafael) — **autoridade de publicação**: aprova/rejeita e publica assets submetidos. **Terciária:** `SDR` (Lucas) — consumidor de leitura de assets publicados (scripts), restrito por `data_scope`. **Consumidores-máquina:** COMM/JRNY/SALE consomem assets publicados via API BE (não pela UI ASST). |
| 4 | **Recorte do MVP (in)** | (a) **Catálogo / busca**: lista de assets por `tipoAsset` (`LANDING_PAGE`, `EMAIL`, `CRIATIVO`, `ROTEIRO`, `DOCUMENTO`, `SCRIPT_SDR`) com filtros por tipo/tag/estado + busca full-text; (b) **Criação + metadados**: criar asset (`RASCUNHO`), editar título/descrição/tags; (c) **Versionamento**: visualizar histórico de `versao_asset` imutáveis, conteúdo da versão, versão vigente publicada, criar nova versão manual (conteúdo estruturado/texto + binário **referenciado por URL**); (d) **Asset Studio**: compor/editar conteúdo via IA (`POST /studio/compose`) a partir de brief + contexto → nova versão `RASCUNHO` com `origem=ASSET_STUDIO`; (e) **Approval workflow**: submeter (`RASCUNHO→EM_REVISAO`), aprovar/rejeitar, publicar (`APROVADO→PUBLICADO`); fila de aprovações para o aprovador; (f) **Guards de acesso** (`authGuard`, `empresaGuard`, `accessGuard('asst.*')`). |
| 5 | **Fora de escopo (MVP)** | **Upload/hospedagem de binários pesados** (vídeo/imagem) — binários são **referenciados por URL externa**, nunca enviados pelo FE ASST (sem chunked-upload, sem transcoding); edição colaborativa em tempo real (co-editing/CRDT); editor rich-text/WYSIWYG avançado (MVP edita conteúdo estruturado/texto simples); A/B testing de variantes; brand kit / design system; tradução multilíngue; aprovação multi-nível com SLA (MVP é single-step); entrega pública/CDN. |
| 6 | **Integrações externas obrigatórias** | **`asst-service` via `@journeyos/shared/access-http-base`** (todas as chamadas `/api/v1/assets/**`, header `X-Empresa-Id`/JWT automáticos). O **Asset Studio** chama o BE (`/studio/compose`) que delega à TechLab AI — o FE **nunca** chama provider de IA nem a TechLab AI direto. Sem widgets 3rd-party no MVP. |
| 7 | **Serviços do Hub (deps FE)** | `@journeyos/shared/auth-session` (sessão/JWT — **obrigatório**), `@journeyos/shared/empresa-context` (empresa ativa — **obrigatório**), `@journeyos/shared/access-decision` (`AccessDecisionService` + `NavigationService` — **obrigatório**), `@journeyos/shared/access-http-base` (HTTP + interceptors — **obrigatório**), `@journeyos/shared/ui-components` · `ui-feedback` · `ui-tokens` (sempre), `@journeyos/shared/error-model` (mapear `ProblemDetail` → `AppError`), `@journeyos/shared/observability` (recomendado — timing de composição, taxa de aprovação). Candidatos a **patterns shared**: smart-table (catálogo), approval-widget (workflow), timeline (histórico de versões). ASST **não** depende de nenhum outro módulo de domínio. |
| 8 | **Evento-âncora do domínio (UX)** | **"Asset publicado"** — o golden path do FE: *criar asset → compor no Asset Studio → submeter → aprovar → publicar*. Publicar torna a versão vigente disponível para consumo cross-módulo. O momento de UI mais crítico é a **transição de estado** (submit/approve/publish), que muda o que cada persona pode fazer e dispara a degradação graciosa do Asset Studio quando a IA está indisponível. |

---

## Notas de contexto (Journey OS · FE)

- **Stack:** Angular 18+ · Nx 19+ · TypeScript strict · Signals-first (sem NgRx) · Standalone + OnPush · Jest (unit) · Playwright (e2e). npmScope `@journeyos`.
- **Padrão canônico:** `module-pattern` (slicing de libs por módulo — ver CLAUDE.md). App lazy em `apps/asst`, libs em `libs/asst/{access,data-access,feature-*,integration,navigation,ui,styles}`.
- **IA é capacidade delegada (FE):** o Asset Studio chama **somente** o `asst-service` (`/studio/compose`); o FE nunca conhece a TechLab AI. Falha da IA (`503 asst.studio.ia-indisponivel`) **degrada apenas o Asset Studio** — catálogo, versionamento e aprovação continuam intactos (ver ADR-005).
- **Versão imutável:** a UI nunca edita uma `versao_asset` existente in-place; corrigir = criar nova versão. O histórico é navegável e a versão vigente é deterministicamente identificável (`versaoVigenteId`).
- **Aprovação separa autoria de publicação:** quem cria (`HEAD_GROWTH`) não é necessariamente quem publica (`INFOPRODUTOR`); a UI reflete a state machine (ações de submit/approve/publish gated por permissão `asst.*`).
- **Multi-empresa:** todo asset é escopado por `empresaId` ativo (via `EmpresaContextService`); troca de empresa invalida o catálogo em tela antes de mostrar o da nova empresa (sem vazamento cross-empresa — LGPD).
- **Type:** `standard` (autopilot) → A5 (e2e-validate) **aplicável** (specs Playwright gerados do SPEC-08).

## Referências canônicas consumidas

- `docs/architecture/backend/services/asst-service/_brief.md` — brief BE (espelho)
- `docs/architecture/backend/services/asst-service/{01,03}-*.md` — vision + domain framing BE
- `docs/architecture/backend/services/asst-service/contracts/api-contract.md` — superfície REST `/api/v1/assets/**`
- `docs/architecture/frontend/standards/nx-boundaries.md` — tags + direções permitidas
- `docs/architecture/frontend/standards/access-layer-contracts.md` — contratos da Access Layer
- `docs/architecture/frontend/standards/asset-driven-ui.md` — UI como assets/patterns reusáveis
- `docs/architecture/shared/blueprint-core.md` — modelo mental App + módulos + shared
