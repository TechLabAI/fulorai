# Brief — COMM (Communication Hub) · Frontend

> Fonte estruturada para `/fe-architect-specs`, `/fe-architect-backlog` e `/fe-architect-scaffold`.
> **Compartilhado com o BE** (`docs/architecture/backend/services/comm-service/_brief.md`). O FE
> consome a mesma linguagem ubíqua e os mesmos contratos (`/api/v1/{templates,messages,routing-rules,channels}`,
> eventos, permissões `comm.*`); aqui o recorte é a **experiência do usuário** (telas, fluxos, estado
> de UI) sobre a API do `comm-service`.
> Módulo de **domínio núcleo** (`type: standard`) — depende de WRKS (auth/empresa/RBAC) e de ASST
> (templates podem vincular um asset publicado como fonte de conteúdo); consumido por JRNY/SALE/LEAD
> via API BE (não pela UI COMM).

| # | Item | Conteúdo |
|---|------|----------|
| 1 | **Nome canônico / Prefixo** | module `comm` / **COMM** · app lazy `apps/comm` · libs `libs/comm/*` · Nx scope `scope:comm` · npmScope `@journeyos` · issue prefix `FE-COMM-NNN` |
| 2 | **Problema que resolve (UX)** | Marina (Head de Growth) e Lucas (SDR) precisam falar com leads no **canal e no momento certos** — WhatsApp, e-mail, Telegram, SMS — mas hoje a comunicação é fragmentada (ActiveCampaign + disparadores de WhatsApp + planilhas), **sem template aprovado, sem decisão explícita de canal e sem rastreio do que foi entregue/lido**. O FE COMM dá a **superfície única** para: catalogar e editar **templates** versionados (com placeholders `{{variavel}}` e composição assistida pelo **Template Studio**/IA), definir **regras de roteamento** (canal preferido + fallback por segmento/estágio/preferência/janela), **disparar** mensagens 1:1 de forma idempotente e **acompanhar o ciclo de vida** de cada mensagem (enfileirada → enviada → entregue → lida / falhada), além de **configurar canais/provedores** por empresa. |
| 3 | **Persona principal / secundária** | **Principal:** `HEAD_GROWTH` (Marina) — cria/edita templates (e usa o Template Studio), define regras de roteamento, acompanha entregabilidade. **Secundária:** `SDR` (Lucas) — dispara mensagens 1:1 para leads da sua fila e vê o status `ENVIADA → ENTREGUE → LIDA`; `data_scope` restringe quem ele enxerga. **Terciária:** `INFOPRODUTOR` (Rafael) — **configura canais** (provedores, identidade de remetente, referência de credencial). **Consumidores-máquina:** JRNY/SALE/LEAD acionam disparo via API BE (não pela UI COMM). |
| 4 | **Recorte do MVP (in)** | (a) **Catálogo de templates / busca**: lista por `canal` (`WHATSAPP`/`EMAIL`/`TELEGRAM`/`SMS`) e `tipo` (`TRANSACIONAL`/`MARKETING`/`NOTIFICACAO`) com filtros por canal/tipo/estado + busca; (b) **CRUD + editor de template**: criar (`RASCUNHO`), editar corpo com placeholders `{{variavel}}` (validação de variáveis declaradas vs usadas), `assunto` obrigatório p/ EMAIL, vínculo opcional a asset publicado do ASST, transições `RASCUNHO → ATIVO → ARQUIVADO`; (c) **Template Studio**: composição/edição assistida via IA (`POST /templates/{id}/studio/compose`) → novo corpo `RASCUNHO`, com degradação graciosa; (d) **Roteamento**: CRUD de `regra_roteamento` (condições + canal preferido + fallback + prioridade + template); (e) **Disparo + rastreio**: disparar mensagem 1:1 (idempotente) e acompanhar o ciclo de vida (`ENFILEIRADA → ENVIADA → ENTREGUE → LIDA` + `FALHADA`) via timeline + histórico/busca de mensagens; (f) **Config de canal por empresa**: `config_canal` com provedor + identidade de remetente + **referência** de credencial (nunca o segredo); (g) **Guards de acesso** (`authGuard`, `empresaGuard`, `accessGuard('comm.*')`). |
| 5 | **Fora de escopo (MVP)** | Caixa de entrada unificada / chat bidirecional em tempo real (inbox, 2-way, chatbot); **campaign manager avançado** com A/B testing e cadências complexas (UI de campanha avançada **não** entra no MVP FE); **editor visual de e-mail** drag-and-drop / WYSIWYG rico (MVP é editor de texto/HTML com placeholders); gestão legal completa de opt-in/opt-out (double opt-in); roteamento por custo (least-cost) entre provedores; deliverability scoring / warm-up; hospedagem própria de mídia (binários por URL, como no ASST); UI de webhooks (callbacks de provedor não têm tela — são server-to-server). |
| 6 | **Integrações externas obrigatórias** | **`comm-service` via `@journeyos/shared/access-http-base`** (todas as chamadas `/api/v1/{templates,messages,routing-rules,channels}/**`, JWT + `X-Empresa-Id`/Correlation automáticos). O **Template Studio** chama o BE (`/templates/{id}/studio/compose`) que delega à TechLab AI — o FE **nunca** chama provider de IA nem a TechLab AI direto. O FE **não** conhece provedores de canal (Meta/Twilio/SES/Telegram) — só `canal`; provedores vivem atrás de adapters no BE. Sem widgets 3rd-party no MVP. |
| 7 | **Serviços do Hub (deps FE)** | `@journeyos/shared/auth-session` (sessão/JWT — **obrigatório**), `@journeyos/shared/empresa-context` (empresa ativa — **obrigatório**), `@journeyos/shared/access-decision` (`AccessDecisionService` + `NavigationService` — **obrigatório**), `@journeyos/shared/access-http-base` (HTTP + interceptors — **obrigatório**), `@journeyos/shared/ui-components` · `ui-feedback` · `ui-tokens` (sempre), `@journeyos/shared/error-model` (mapear `ProblemDetail` → `AppError`: `409`, `422`, `503`), `@journeyos/shared/observability` (recomendado — timing de composição, taxa de entrega, latência do polling). Candidatos a **patterns shared**: smart-table (catálogo de templates/mensagens), timeline (ciclo de vida da mensagem), wizard-form-shell (config de canal). COMM **depende** de ASST apenas via API BE (lê assets publicados como fonte de template) — **não** importa `scope:asst` no FE. |
| 8 | **Evento-âncora do domínio (UX)** | **"Mensagem enviada"** — o golden path do FE: *escolher template ATIVO → (roteamento resolve canal) → disparar → acompanhar `ENVIADA → ENTREGUE → LIDA`*. O momento de UI mais crítico é o **rastreio do ciclo de vida** (status que evolui em tempo quase real a partir de callbacks do provedor, refletido no FE por polling — ADR-005) e a **degradação graciosa do Template Studio** quando a IA está indisponível (CRUD/roteamento/disparo intactos). |

---

## Notas de contexto (Journey OS · FE)

- **Stack:** Angular 18+ · Nx 19+ · TypeScript strict · Signals-first (sem NgRx) · Standalone + OnPush · Jest (unit) · Playwright (e2e). npmScope `@journeyos`.
- **Padrão canônico:** `module-pattern` (slicing de libs por módulo — ver CLAUDE.md). App lazy em `apps/comm`, libs em `libs/comm/{access,data-access,feature-*,integration,navigation,ui,styles}` + entry `libs/comm/shell-entry`.
- **IA é capacidade delegada (FE):** o Template Studio chama **somente** o `comm-service` (`/templates/{id}/studio/compose`); o FE nunca conhece a TechLab AI. Falha da IA (`503 comm.studio.ia-indisponivel`) **degrada apenas o Template Studio** — catálogo, edição, roteamento e disparo continuam intactos (princípio espelhado do ASST ADR-005).
- **Provedor é detalhe do BE:** o FE conhece apenas `canal`; nunca Meta/Twilio/SES/Telegram. Config de canal guarda só `credencialRef` (referência), **nunca** o segredo em claro.
- **Rastreio é quase-tempo-real por polling:** o BE recebe callbacks (webhooks) do provedor de forma assíncrona; **não há endpoint de streaming**. O FE reflete a evolução do estado de entrega por **polling com backoff** enquanto a mensagem está em estado não-terminal (ADR-005).
- **Multi-empresa:** todo template/mensagem/regra/canal é escopado por `empresaId` ativo (via `EmpresaContextService`); troca de empresa invalida o que está em tela antes de mostrar o da nova empresa (sem vazamento cross-empresa — LGPD).
- **Type:** `standard` (autopilot) → A5 (e2e-validate) **aplicável** (specs Playwright gerados do SPEC-08).

## Referências canônicas consumidas

- `docs/architecture/backend/services/comm-service/_brief.md` — brief BE (espelho)
- `docs/architecture/backend/services/comm-service/{01,03}-*.md` — vision + domain framing BE
- `docs/architecture/backend/services/comm-service/contracts/api-contract.md` — superfície REST `/api/v1/{templates,messages,routing-rules,channels}`
- `docs/architecture/backend/services/asst-service/contracts/api-contract.md` — assets publicados (fonte de template, consumido pelo BE)
- `docs/architecture/frontend/standards/nx-boundaries.md` — tags + direções permitidas
- `docs/architecture/frontend/standards/access-layer-contracts.md` — contratos da Access Layer
- `docs/architecture/shared/blueprint-core.md` — modelo mental App + módulos + shared
