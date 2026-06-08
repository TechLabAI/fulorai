# 02 — Architecture Blueprint — ASST · Frontend

> Como o ASST FE se encaixa no Shell (`journey-os-web`), suas fronteiras internas (padrão
> `module-pattern`) e os concerns cross-cutting que consome.

## 1. System Boundary

O ASST FE é um **cliente do API Gateway** (`journey-os-api-gateway`), falando com o `asst-service`
exclusivamente via `@journeyos/shared/access-http-base` (HttpClient + interceptors). Não conhece
PostgreSQL, Elasticsearch, Kafka nem a TechLab AI — tudo isso é detalhe BE atrás de `/api/v1/assets/**`.
O Asset Studio chama **somente** o BE (`POST /api/v1/assets/{id}/studio/compose`); o FE nunca conhece
nem chama a TechLab AI.

```
[Browser]
  └─ journey-os-web (Shell, scope:web)
       └─ apps/asst (lazy: @journeyos/asst shell-entry)        ← este módulo
            └─ libs/asst/* (features, data-access, access, integration, navigation)
                 └─ @journeyos/shared/access-http-base → GWY → asst-service → (TechLab AI, Elastic, PG, Kafka)
```

Fronteira dura: ASST FE **não importa** outro módulo de domínio (LEAD/COMM/JRNY/SALE/INTL); o único
reuso é via `@journeyos/shared/*` (nx-boundaries). COMM/JRNY/SALE consomem assets publicados pelo
**BE**, não pela UI ASST.

## 2. External Actors and Systems

| Ator / Sistema | Relação |
|---|---|
| **Usuário autenticado (browser)** | Marina (autoria/composição/submit), Rafael (aprovação/publicação), Lucas (leitura). Sessão via `auth-session`. |
| **`asst-service` (via GWY)** | Toda a API de assets: CRUD, versões, Asset Studio, approval workflow, busca. Header `X-Empresa-Id`/JWT injetados pelo interceptor. |
| **TechLab AI** | **Indireta** — o FE chama o BE (`/studio/compose`), que delega à TechLab AI. O FE nunca fala com a TechLab AI; só observa sucesso/`503 ia-indisponivel`. |
| **Shell (`journey-os-web`)** | Hospeda o ASST via lazy loading, expõe topbar (troca de empresa) e consome `NavigationService`. |
| **Demais módulos FE** | **Não** são atores da UI ASST; consomem assets publicados via BE. |

Sem 3rd-party widgets no MVP.

## 3. End-to-End User Flows

### Golden path — criar → compor → submeter → aprovar → publicar

```
┌──────────────┐  novo asset  ┌───────────────────┐  Asset Studio  ┌────────────────────┐
│ /asst/library │────────────▶│ /asst/assets/:id   │──────────────▶│ /asst/assets/:id    │
│ (catálogo)    │  RASCUNHO    │ (detalhe+versões)  │  brief+contexto│ /studio (compose)   │
└──────────────┘              └─────────┬─────────┘                └─────────┬──────────┘
                                         │ nova versão RASCUNHO              │ origem=ASSET_STUDIO
                                         │  (origem=MANUAL ou ASSET_STUDIO)  │ (ou 503 → degrada)
                                         ▼                                   ▼
                              ┌──────────────────────┐ submit  ┌──────────────────────────┐
                              │ revisar conteúdo da   │────────▶│ estado EM_REVISAO          │
                              │ versão                │         │ entra na fila de aprovação │
                              └──────────────────────┘         └────────────┬──────────────┘
                                                                            │ (persona Rafael)
                                                                            ▼
                                          ┌────────────────────────────────────────────────┐
                                          │ /asst/approvals → aprovar/rejeitar(comentário)   │
                                          │   APROVADO ──publish──▶ PUBLICADO (versão vigente)│
                                          │   REJEITADO ──▶ volta para autoria               │
                                          └────────────────────────────────────────────────┘
```

### Fluxo — Asset Studio (persona Marina, `asst.studio.compor`)

```
/asst/assets/:id/studio → form(brief, contexto, baseVersaoNumero?)
   → POST /studio/compose (loading explícito, sem otimismo)
   → 201: nova versão RASCUNHO (origem=ASSET_STUDIO) → abre para revisão
   → 503 asst.studio.ia-indisponivel: banner de degradação → "compor manualmente"; nenhuma versão criada
```

### Fluxo — aprovação (persona Rafael, `asst.asset.aprovar` / `asst.asset.publicar`)

```
/asst/approvals (assets EM_REVISAO) → abrir → ver versão submetida
   → [Aprovar] (comentário) → APROVADO  → [Publicar] → PUBLICADO (versaoVigenteId atualizado)
   → [Rejeitar] (comentário obrigatório) → REJEITADO → volta para autoria
```

### Edge cases

- **Transição inválida** (ex.: publicar asset não-`APROVADO`) → BE responde `409
  asst.estado.transicao-invalida` → UI mostra erro e **não** oferece a ação fora de estado (botões
  derivam do estado atual).
- **Versão imutável** → tentativa de editar versão existente é bloqueada na UI; a ação é "criar nova
  versão" (UINV).
- **IA indisponível** → só o Asset Studio degrada; o resto do fluxo continua.
- **Troca de empresa com catálogo carregado** → cancela in-flight + invalida catálogo antes de
  renderizar o da nova empresa.
- **Asset sem versão publicada** → detalhe mostra "nenhuma versão publicada"; consumidores recebem
  404 no BE (não é caso de UI ASST, mas o detalhe sinaliza o estado).

## 4. Internal Boundaries (padrão `module-pattern`)

```
apps/asst/                                  # host fino lazy (carrega @journeyos/asst)
libs/asst/shell-entry/                      # module entry (ADR-006: entry como library)
    ├── asst.contract.ts                    # ModuleMenuMetadata + permissions + flags
    ├── asst.bootstrap.ts                   # init/destroy lifecycle (registro no Shell)
    ├── asst.routes.ts                      # ASST_ROUTES[]
    ├── asst.permission-map.ts              # mapa de permissões do módulo
    ├── asst.feature-flags.ts               # flags (defaultState)
    └── asst.nav.config.ts                  # config de navegação/breadcrumb

libs/asst/                                  # module libs
├── access/            (type:domain)        # guards específicos: assetGuard, accessGuard('asst.*')
├── data-access/       (type:data-access)   # AssetApiService + StudioApiService + signal facades
├── feature-asset-library/  (type:feature)  # catálogo + busca + filtros + criação
├── feature-asset-detail/   (type:feature)  # detalhe + histórico de versões + nova versão manual
├── feature-asset-studio/   (type:feature)  # composição assistida por IA (compose)
├── feature-approval-workflow/ (type:feature)# fila + submit/aprovar/rejeitar/publicar
├── integration/       (type:domain)        # AsstShellIntegrationService
├── navigation/        (type:domain)        # breadcrumbs/menu state do ASST
├── ui/                (type:ui, opcional)  # componentes locais (asset-card, version-timeline, state-chip)
└── styles/            (type:ui)            # SCSS isolado
```

> `facade/` cross-feature pode ser introduzido depois via ADR se a orquestração entre catálogo /
> studio / aprovação justificar; no MVP cada feature usa as facades de `data-access`.

## 5. Cross-cutting Concerns

| Concern | Como o ASST resolve |
|---|---|
| **Auth / entitlement** | `@journeyos/shared/auth-session` (sessão) + `@journeyos/shared/access-decision` (`AccessDecisionService.can('asst.<perm>')`). Guards: `authGuard`, `empresaGuard`, `accessGuard('asst.*')`. |
| **Empresa-context** | `@journeyos/shared/empresa-context` — ASST **consome** o `empresaId` ativo; todo dado é escopado; troca invalida catálogo/detalhe. |
| **Navegação / menu** | `NavigationService` deriva menu/breadcrumb das permissões; `libs/asst/navigation` fornece a config do módulo. |
| **IA / Asset Studio** | Chamada ao BE via `data-access`; estado de loading/timeout/degradação tratado na facade do Studio; nunca chama TechLab AI direto (ADR-005). |
| **Observability** | `@journeyos/shared/observability` — timing de composição (Studio), taxa de aprovação/rejeição, latência do catálogo. |
| **Design tokens / UI** | `@journeyos/shared/ui-tokens`, `ui-components`, `ui-feedback` (empty/loading/error). Candidatos a patterns shared: smart-table, approval-widget, timeline. |
| **Erros** | `ProblemDetail` (RFC 7807) do BE → `AppError` via `@journeyos/shared/error-model` → mensagens via `ui-feedback` (inline em form / toast / página). Mapas: `403`, `409 transicao-invalida`, `503 ia-indisponivel`, `422`. |
| **i18n** | pt-BR primário (humano), en-US para chaves técnicas; estratégia herdada do Shell. |

---

## Referências

- `03-domain-framing-frontend.md`, `04-frontend-architecture-direction.md`, `05-state-and-data-flow.md`
- BE: `docs/architecture/backend/services/asst-service/contracts/api-contract.md`
- `docs/architecture/frontend/standards/nx-boundaries.md`
- `docs/architecture/frontend/standards/access-layer-contracts.md`
- `docs/architecture/frontend/standards/asset-driven-ui.md`
