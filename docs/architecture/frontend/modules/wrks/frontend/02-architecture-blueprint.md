# 02 — Architecture Blueprint — WRKS · Frontend

> Como o WRKS FE se encaixa no Shell (`journey-os-web`), suas fronteiras internas (padrão
> `module-pattern`) e os concerns cross-cutting que consome.

## 1. System Boundary

O WRKS FE é um **cliente do API Gateway** (`journey-os-api-gateway`), falando com o
`wrks-service` exclusivamente via `@journeyos/shared/access-http-base` (HttpClient + interceptors).
Não faz chamadas diretas a Keycloak além do **redirect OIDC** padrão (gerido por
`@journeyos/shared/auth-session`); não conhece banco, schema ou Redis — isso é detalhe BE.

```
[Browser]
  └─ journey-os-web (Shell, scope:web)
       └─ apps/wrks (lazy: wrks.module.ts)           ← este módulo
            └─ libs/wrks/* (features, data-access, access, integration, navigation)
                 └─ @journeyos/shared/access-http-base → GWY → wrks-service
                 └─ @journeyos/shared/auth-session     → redirect OIDC → Keycloak
```

Fronteira dura: WRKS FE **não importa** outro módulo de domínio; o único reuso é via
`@journeyos/shared/*` (nx-boundaries).

## 2. External Actors and Systems

| Ator / Sistema | Relação |
|---|---|
| **Usuário autenticado (browser)** | Interage com login, seleção de empresa e administração. Sessão via `auth-session` (JWT em memória; **nunca** `localStorage` direto). |
| **Keycloak (IdP OIDC)** | Apenas autenticação. O FE faz redirect e processa o callback; **não** decide autorização. |
| **`wrks-service` (via GWY)** | Toda a API de IAM/workspace: empresas, usuários, papéis, AccessDecision, sessão. Header `X-Empresa-Id` injetado pelo interceptor. |
| **Shell (`journey-os-web`)** | Hospeda o WRKS via lazy loading, expõe topbar (troca de empresa) e consome `NavigationService`. |
| **Demais módulos FE** | Consumidores indiretos: dependem da Access Layer que o WRKS popula. |

Sem 3rd-party widgets no MVP.

## 3. End-to-End User Flows

### Golden path — login → seleção de empresa → operar

```
┌────────────┐   login    ┌──────────────┐  callback   ┌───────────────────┐
│  /login    │──────────▶ │  Keycloak    │───────────▶ │ /auth/callback     │
│ (anônimo)  │  redirect  │  (OIDC)      │   code      │ exchange → sessão  │
└────────────┘            └──────────────┘             └─────────┬─────────┘
                                                                  │ authenticated
                                                                  ▼
                                          ┌──────────────────────────────────┐
                                          │ tem N empresas?                    │
                                          │   N>1 → /empresa-select            │
                                          │   N=1 → switchTo(auto) → dashboard │
                                          │   N=0 → estado "sem acesso"        │
                                          └─────────┬──────────────────────────┘
                                                    │ switchTo(empresaId) (novo JWT)
                                                    ▼
                                  ┌─────────────────────────────────────────┐
                                  │ EmpresaContext setado → Shell re-deriva   │
                                  │ navegação → /wrks/workspace (dashboard)   │
                                  └─────────────────────────────────────────┘
```

### Fluxo — convidar usuário (persona Rafael, `wrks.user.convidar`)

```
/wrks/users → [Convidar] → form(email, papel, data_scope)
   → POST convite → otimista? NÃO (depende de validação BE: anti-escalonamento INV-1)
   → sucesso: linha "convidado" na tabela | erro: ProblemDetail → ui-feedback
```

### Edge cases

- **Token expira durante navegação** → interceptor dispara `refresh` (rotation) via `auth-session`;
  se falhar, redirect para `/login` preservando `returnUrl`.
- **`modelo_acesso_versao` mudou** (RBAC alterado no BE) → próxima AccessDecision retorna versão
  nova → `NavigationService` re-deriva menu; ações que o usuário perdeu somem.
- **Usuário sem empresa ativa** (N=0) → tela "sem acesso / aguardando convite".
- **Troca de empresa com requisição em voo** → cancelada; cache escopado invalidado (ADR-005).

## 4. Internal Boundaries (padrão `module-pattern`)

```
apps/wrks/                                  # module entry (NgModule lazy)
└── src/app/wrks-module/
    ├── wrks.module.ts                      # único NgModule do módulo
    ├── wrks.contract.ts                    # ModuleMenuMetadata + permissions + flags
    ├── wrks.bootstrap.ts                   # init/destroy lifecycle (registro no Shell)
    ├── wrks.routes.ts                      # WRKS_ROUTES[]
    ├── wrks.permission-map.ts              # mapa de permissões do módulo
    ├── wrks.feature-flags.ts               # flags (defaultState)
    └── wrks.nav.config.ts                  # config de navegação/breadcrumb

libs/wrks/                                  # module libs
├── access/            (type:domain)        # guards específicos: empresaGuard, accessGuard(<perm>)
├── data-access/       (type:data-access)   # *ApiService (HTTP) + signal facades
├── feature-login/     (type:feature)       # login + OIDC callback
├── feature-empresa-select/ (type:feature)  # seleção de empresa
├── feature-workspace/ (type:feature)       # dashboard + settings + org structure
├── feature-users/     (type:feature)       # gestão de usuários e papéis
├── feature-rbac-viewer/ (type:feature)     # papéis × permissões (leitura)
├── integration/       (type:domain)        # WrksShellIntegrationService
├── navigation/        (type:domain)        # breadcrumbs/menu state do WRKS
├── ui/                (type:ui, opcional)   # componentes locais (cartão de empresa, etc.)
└── styles/            (type:ui)             # SCSS isolado
```

> `facade/` não é necessário no MVP (WRKS não tem orquestração cross-feature pesada); pode ser
> introduzido depois via ADR se a complexidade justificar.

## 5. Cross-cutting Concerns

| Concern | Como o WRKS resolve |
|---|---|
| **Auth / entitlement** | `@journeyos/shared/auth-session` (sessão) + `@journeyos/shared/access-decision` (`AccessDecisionService.can(<perm>)`). Guards: `authGuard`, `empresaGuard`, `accessGuard(<perm>)`. |
| **Empresa-context** | `@journeyos/shared/empresa-context` — WRKS **alimenta** a lista (via `feature-empresa-select`) e **consome** o sinal de empresa ativa. |
| **Navegação / menu** | `NavigationService` deriva menu/breadcrumb das decisões; `libs/wrks/navigation` fornece a config do módulo. |
| **Observability** | `@journeyos/shared/observability` — eventos de bootstrap (timing de login), troca de empresa, convites. |
| **Design tokens / UI** | `@journeyos/shared/ui-tokens`, `ui-components`, `ui-feedback` (empty/loading/error). |
| **Erros** | `ProblemDetail` (RFC 7807) do BE → `AppError` via `@journeyos/shared/error-model` → mensagens via `ui-feedback`. |
| **i18n** | pt-BR primário (humano), en-US para chaves técnicas; estratégia herdada do Shell. |

---

## Referências

- `03-domain-framing-frontend.md`, `04-frontend-architecture-direction.md`, `05-state-and-data-flow.md`
- `docs/architecture/frontend/standards/nx-boundaries.md`
- `docs/architecture/frontend/standards/access-layer-contracts.md`
- `docs/architecture/shared/blueprint-core.md`
