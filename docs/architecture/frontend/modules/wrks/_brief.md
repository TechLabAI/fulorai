# Brief — WRKS (Workspace & Identity) · Frontend

> Fonte estruturada para `/fe-architect-specs`, `/fe-architect-backlog` e `/fe-architect-scaffold`.
> **Compartilhado com o BE** (`docs/architecture/backend/services/wrks-service/_brief.md`). O FE
> consome a mesma linguagem ubíqua e os mesmos contratos de RBAC/sessão; aqui o recorte é a
> **experiência do usuário** (telas, fluxos, estado de UI) sobre a API do `wrks-service`.
> Módulo de **fundação FE** (`type: standard`) — sem ele nenhum outro módulo FE autentica,
> resolve `empresa-context` nem aplica RBAC.

| # | Item | Conteúdo |
|---|------|----------|
| 1 | **Nome canônico / Prefixo** | module `wrks` / **WRKS** · app lazy `apps/wrks` · libs `libs/wrks/*` · Nx scope `scope:wrks` · npmScope `@journeyos` · issue prefix `WRKS-FE-NNN` |
| 2 | **Problema que resolve (UX)** | Rafael (CEO da operação) monta uma equipe de 4–8 pessoas e precisa de **uma tela única** para: entrar (login OIDC), escolher em qual `empresa` (workspace) vai operar, convidar gente, atribuir papéis canônicos e configurar a operação. Marina e Lucas precisam de um login que respeite o que cada um pode ver. Hoje isso é planilha + acessos soltos por ferramenta; o FE WRKS dá a **superfície de identidade, seleção de empresa e administração** do Journey OS — e é a precondição de UI de todos os demais módulos. |
| 3 | **Persona principal / secundária** | **Principal:** `INFOPRODUTOR` (Rafael) — admin do workspace: convida usuários, atribui papéis, configura empresa e org structure. **Secundária:** `HEAD_GROWTH` (Marina) — gerencia sua business unit/team. **Terciária:** `SDR` (Lucas) — login + troca de empresa, acesso restrito (a UI de admin some para ele via RBAC). **Consumidor-máquina:** o **Shell** (`journey-os-web`) e **todos os demais módulos FE**, que dependem da Access Layer alimentada por WRKS. |
| 4 | **Recorte do MVP (in)** | (a) **Login / OIDC callback** (Keycloak via `@journeyos/shared/auth-session`); (b) **Seleção de empresa** (lista de `usuario_empresa` ativas → `switchTo` sem reload, novo JWT); (c) **Workspace dashboard + settings** (dados da empresa, parâmetros, org structure: business units / teams); (d) **Gestão de usuários** (lista, convite, ativar/desativar, atribuir papel + `data_scope`); (e) **RBAC viewer** (papéis canônicos e suas permissões — somente leitura no MVP); (f) **Guards de acesso** (`authGuard`, `empresaGuard`, `accessGuard(<perm>)`) consumindo `AccessDecisionService`; (g) **Troca de empresa em runtime** (re-avalia navegação + invalida caches escopados, sem refresh completo). |
| 5 | **Fora de escopo (MVP)** | MFA/TOTP/WebAuthn (FE só exibe flag `mfa-required`); editor de papéis customizados (papéis são canônicos do grupo — só leitura); self-service signup + billing; tela de auditoria avançada (auditoria é consumo BE; FE pode ter um viewer simples só se priorizado em wave tardia); gestão de catálogos fiscais; aprovação 2-step de convites; UI de emergency access / API keys. |
| 6 | **Integrações externas obrigatórias** | **Keycloak** (redirect OIDC — apenas autenticação; FE nunca decide autorização localmente); **`wrks-service` via `@journeyos/shared/access-http-base`** (todas as chamadas IAM/workspace, header `X-Empresa-Id` automático). Sem widgets 3rd-party no MVP. |
| 7 | **Serviços do Hub (deps FE)** | `@journeyos/shared/auth-session` (sessão/JWT — **obrigatório**), `@journeyos/shared/empresa-context` (empresa ativa — **obrigatório**, e WRKS é quem **alimenta** a lista), `@journeyos/shared/access-decision` (`AccessDecisionService` + `NavigationService` — **obrigatório**), `@journeyos/shared/access-http-base` (HTTP + interceptors — **obrigatório**), `@journeyos/shared/ui-components` · `ui-feedback` · `ui-tokens` (sempre), `@journeyos/shared/error-model` (mapear `ProblemDetail`), `@journeyos/shared/observability` (recomendado). WRKS **não** depende de nenhum outro módulo de domínio. |
| 8 | **Evento-âncora do domínio (UX)** | **"Sessão estabelecida + empresa selecionada"** — o golden path do FE: o usuário entra, escolhe a empresa, e o app passa de `no-context` para `operando(empresa)`. O evento de UI mais relevante cross-módulo é a **troca de empresa** (`EmpresaContextService.switchTo`), que re-deriva navegação e acesso para a plataforma FE inteira. |

---

## Notas de contexto (Journey OS · FE)

- **Stack:** Angular 18+ · Nx 19+ · TypeScript strict · Signals-first (sem NgRx) · Standalone + OnPush · Jest (unit) · Playwright (e2e). npmScope `@journeyos`.
- **Padrão canônico:** `module-pattern` (slicing de libs por módulo — ver CLAUDE.md). App lazy em `apps/wrks`, libs em `libs/wrks/{access,data-access,feature-*,integration,navigation,ui,styles}`.
- **Access Layer é cross-cutting:** WRKS **produz** o material (sessão, lista de empresas, AccessDecision vindos do BE) mas a UI consome **sempre** via `@journeyos/shared/access-*`. Nenhuma feature do WRKS reimplementa auth, lê `localStorage` ou decide RBAC inline (ver `access-layer-contracts.md`).
- **Multi-empresa:** `EmpresaContextService` é a única fonte de verdade do `empresaId` ativo no FE; nunca ler do JWT decodificado. Troca de empresa = cancela in-flight + invalida cache escopado + re-avalia nav (ver ADR-005).
- **Type:** `standard` (autopilot) → A5 (e2e-validate) **aplicável** (specs Playwright gerados do SPEC-08).
- **Particularidade FE:** WRKS é o **único módulo cujas telas operam parcialmente fora do contexto de empresa** (login e seleção de empresa acontecem antes de haver `empresaId`). Os guards diferenciam rotas pré-contexto (`authGuard` só) de rotas pós-contexto (`authGuard` + `empresaGuard`).

## Referências canônicas consumidas

- `docs/architecture/backend/services/wrks-service/_brief.md` — brief BE (espelho)
- `docs/architecture/backend/services/wrks-service/{01,03}-*.md` — vision + domain framing BE
- `docs/architecture/frontend/standards/nx-boundaries.md` — tags + direções permitidas
- `docs/architecture/frontend/standards/access-layer-contracts.md` — contratos da Access Layer
- `docs/architecture/shared/blueprint-core.md` — modelo mental App + módulos + shared
