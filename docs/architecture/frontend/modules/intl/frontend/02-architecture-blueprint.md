# 02 — Architecture Blueprint — INTL · Frontend

> Fronteiras do sistema, atores externos, fluxos e estrutura interna de libs (module-pattern).

## 1. System Boundary

O FE INTL é **cliente do API Gateway** via `@journeyos/shared/access-http-base`. Não fala com
Elasticsearch, TechLab AI ou Kafka diretamente — toda inteligência é mediada pelo `intl-service`
(`/api/v1/{copilot,knowledge,analytics}`). O FE **nunca** chama um provedor de IA; ele renderiza o
resultado já fundamentado/degradado que o BE produz. Autenticação e autorização vêm da Access Layer
alimentada por WRKS — INTL **consome**, não produz, sessão/empresa/RBAC.

## 2. External Actors and Systems

- **Browser autenticado** (sessão OIDC via `@journeyos/shared/auth-session`, alimentada por WRKS).
- **`intl-service`** (BE) através de `@journeyos/shared/access-http-base` — interceptors injetam
  `Authorization`, `X-Empresa-Id` e `X-Correlation-Id`.
- **Access Layer (WRKS)** — `AccessDecisionService` (permissões `intl.*`), `EmpresaContextService`
  (empresa ativa), `NavigationService` (menu derivado).
- **Shell (`journey-os-web`)** — registra INTL via `module-descriptors.ts` e o carrega lazy.
- Sem widgets/3rd-party no MVP.

## 3. End-to-End User Flows

### Golden path — perguntar ao Copilot

```
[Sidebar] Inteligência ▸ Copilot
        │
        ▼
┌─────────────────────────────────────────────────────────────┐
│  Copilot — empresa: Acme Cursos                              │
│ ┌─────────────┬─────────────────────────────────────────┐  │
│ │ Conversas   │  ▸ "Por que o funil caiu esta semana?"   │  │
│ │ ───────────  │                                          │  │
│ │ • Hoje 14:02 │  ⟳ pensando…           [Cancelar]        │  │
│ │ • Ontem      │  ───────────────────────────────────────  │  │
│ │ • + Nova     │  ◂ Resposta  [RESPONDIDA]                 │  │
│ │             │    "A queda concentra-se na etapa de…"    │  │
│ │             │    Citações: [#lead-8821] [#funnel-doc]   │  │
│ │             │  ┌───────────────────────────────────┐    │  │
│ │             │  │ Pergunte algo…            [Enviar]│    │  │
│ │             │  └───────────────────────────────────┘    │  │
│ └─────────────┴─────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

Fluxo: abrir/῾selecionar conversa → digitar → `pensando` (otimista, citações ausentes) →
`200` com `status` → renderiza badge + citações **ou** estado degradado. Persistência e evento são
do BE; o FE só reflete.

### Edge cases / alternativas

- **`NAO_FUNDAMENTADA`** → badge âmbar + texto "sem evidência suficiente"; **sem** chips de citação.
- **`DEGRADADA`** (IA off) → badge cinza "modo recuperação" + tooltip; mostra evidência recuperada
  se houver, sem síntese.
- **Cancelamento** → aborta a requisição (AbortController), volta a `idle`, mantém a pergunta no
  input.
- **`403`** numa rota → `accessGuard` redireciona/oculta; menu nem mostra o item.
- **Troca de empresa** (topbar do Shell) → cancela in-flight, limpa conversa corrente, recarrega.

### Knowledge — indexar nó

```
[Lista de nós] → [+ Novo nó] → form (titulo, conteudo, tags) → Salvar (201, RASCUNHO)
                                                   │
                                                   ▼
                                            [Indexar] → indexando… → INDEXADO (202)
                                                   │
                                                   └─ 503 embedding-unavailable → "tentar de novo"
```

## 4. Internal Boundaries (libs — padrão module-pattern)

```
apps/intl/                              # host fino: carrega o entry-lib @journeyos/intl
libs/intl/shell-entry/                  # ENTRY como library (importPath @journeyos/intl, ADR-006)
  intl.contract.ts                      # ModuleMenuMetadata + permissions + flags
  intl.bootstrap.ts                     # init/destroy lifecycle
  intl.routes.ts                        # MODULE_ROUTES[]
  intl.permission-map.ts
  intl.feature-flags.ts
  intl.nav.config.ts
  intl.descriptor.ts                    # INTL_MODULE_DESCRIPTOR (registro no Shell)
libs/intl/
  access/                               # guards específicos do módulo
  data-access/                          # HTTP (CopilotApi, KnowledgeApi, AnalyticsApi) + facades signal
  feature-copilot/                      # chat + conversas + citações
  feature-knowledge/                    # lista/busca + form de nó + indexar/arquivar
  feature-analytics/                    # dashboards funil + uso do copiloto
  integration/                          # IntlShellIntegrationService
  navigation/                           # breadcrumbs/menu state
  ui/ (opcional)                        # componentes locais (chat-bubble, citation-chip, stat-card)
  styles/                               # SCSS isolado (@journeyos/shared/ui-tokens)
```

## 5. Cross-cutting Concerns

- **Auth/entitlement** — `authGuard` + `empresaGuard` + `accessGuard('intl.*')` via
  `AccessDecisionService`; menu derivado por `NavigationService`.
- **Observability** — `@journeyos/shared/observability`: timing pergunta→resposta, `custoTokens`,
  taxa de degradação (espelha o sucesso-signal do BE).
- **Design tokens** — `@journeyos/shared/ui-tokens`; estados via `@journeyos/shared/ui-feedback`
  (skeleton de dashboard, empty da base de conhecimento, error normalizado).
- **Erros** — `ProblemDetail → AppError` via `@journeyos/shared/error-model`; mapear
  `503 ai-unavailable`/`embedding-unavailable` para mensagens de "retry", não erro fatal.
- **i18n** — pt-BR como locale primário (consistente com `project-context.locale`).

---

## Referências

- `01-architectural-vision.md` · `04-frontend-architecture-direction.md` · `05-state-and-data-flow.md`
- BE: `docs/architecture/backend/services/intl-service/02-architecture-blueprint.md`
- `docs/architecture/frontend/standards/nx-boundaries.md`
