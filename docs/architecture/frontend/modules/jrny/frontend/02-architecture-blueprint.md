# 02 — Architecture Blueprint — JRNY (Journey & Routing) · Frontend

> Fronteiras, atores, fluxos golden-path e estrutura de libs do FE JRNY.
> Espelha `jrny-service` (BE). module `jrny` · scope `scope:jrny`.

## 1. System Boundary

O FE JRNY é **cliente do API gateway** via `@journeyos/shared/access-http-base` — todas as chamadas
vão para `/api/v1/journeys/**` e `/api/v1/routing/**` do `jrny-service` com JWT + `X-Empresa-Id`
injetados pelos interceptors da Access Layer. **Nenhuma** chamada direta a sistemas legados, a
provedores de IA, ou a outros microsserviços de domínio. Referências cruzadas (asset publicado de
ASST via `assetRefId`; lead no decision log) viajam como **ids** resolvidos pelo BE/cross-link — o FE
não faz fan-out cross-módulo.

## 2. External Actors and Systems

| Ator / Sistema | Relação |
|---|---|
| **Browser autenticado** (Marina/Rafael/Lucas) | Sessão via `@journeyos/shared/auth-session` (JWT bearer). |
| **`jrny-service`** (BE) | Única origem de dados — via `@journeyos/shared/access-http-base`. |
| **WRKS** (Access Layer) | `AccessDecisionService` resolve permissões `jrny.*`; `EmpresaContextService` fixa a empresa ativa. |
| **TechLab AI** (`orchestration`) | **Indireto/BE-side.** O FE só **reflete** `assistIa` nas decisões; nunca chama IA. |
| **ASST / LEAD** | Referências por id (asset publicado no estágio; lead no decision log). Sem chamada FE. |
| **Shell** `journey-os-web` | Descobre/registra JRNY via `JRNY_MODULE_DESCRIPTOR` + `ModuleShellIntegrationService`. |

## 3. End-to-End User Flows

### Golden path A — Autoria (Marina + Rafael)

```
[Lista de jornadas] --criar rascunho--> [Journey Builder (RASCUNHO)]
        |                                      |
        | abrir                                | +estágio / reordenar / editar estágio
        v                                      v
[Jornada PUBLICADA: read-only]         [Editor de estágio: tipo/nome/asset/terminal]
        ^                                      |
        | publicar (Rafael)                    | definir regras
        |                                      v
        +------------------------------ [Routing Engine: regras versionadas]
                                               |
                                       publicar (≥1 estágio) --> PUBLICADA  --> emite jornada.publicada (BE)
```

### Golden path B — Auditoria (Lucas)

```
[Buscar lead] --> [Estado de jornada do lead]
                         |  estágio corrente + jornada/versão
                         v
                  [Decision log (timeline)]
                   gatilho · regra(v) · alvo · [assist IA ✓ | determinístico] · motivo
                   (inclui SEM_MUDANCA / NAO_ROTEADO)
```

### Edge cases (UI)

- **Publicar jornada sem estágio** → bloqueado, mensagem útil (`422 jrny.jornada.sem-estagio`).
- **Editar jornada PUBLICADA** → CTA "criar nova versão" (`POST /nova-versao`), nunca edição direta
  (`409 jrny.jornada.transicao-invalida`).
- **Ordem de estágio duplicada** → erro inline no editor (`409 jrny.estagio.ordem-duplicada`).
- **Condição de regra inválida** → erro inline (`422 jrny.regra.condicao-invalida`).
- **Estágio-destino fora da jornada** → erro inline (`422 jrny.regra.estagio-invalido`).
- **Lead sem inscrição** → estado vazio amigável (`404 jrny.inscricao.nao-encontrada`).
- **IA indisponível na decisão** → badge neutro "roteamento determinístico" (não é erro).
- **Troca de empresa** → invalida builder/lista em tela antes de carregar os da nova empresa.
- **Permissão negada** → rota/ação escondida por `AccessDecisionService`; acesso direto → 403 amigável.

## 4. Internal Boundaries (estrutura de libs — `module-pattern`)

```
apps/jrny/                                  # host fino (type:app, scope:jrny) — carrega @journeyos/jrny
libs/jrny/
  shell-entry/   (type:domain)             # entry como library @journeyos/jrny
                                            #   jrny.routes.ts · jrny.contract.ts · jrny.permission-map.ts
                                            #   jrny.feature-flags.ts · jrny.nav.config.ts · jrny.bootstrap.ts
                                            #   jrny.descriptor.ts (JRNY_MODULE_DESCRIPTOR)
  feature-journey-list/    (type:feature)  # lista/criação de jornadas
  feature-journey-builder/ (type:feature)  # builder: estágios ordenados + máquina de estados
  feature-stage-editor/    (type:feature)  # edição de um estágio (tipo/nome/asset/terminal/config)
  feature-routing-engine/  (type:feature)  # CRUD de regras versionadas
  feature-decision-log/    (type:feature)  # estado de jornada + trilha de decisões (read-only)
  feature-journey-analytics/ (type:feature)# funil + telemetria (read-only)
  data-access/   (type:data-access)        # services HTTP + facades de signal
  access/        (type:domain)             # guards do módulo (jrny.*)
  integration/   (type:domain)             # JrnyShellIntegrationService
  navigation/    (type:domain)             # breadcrumb/menu state
  ui/            (type:ui)                  # componentes locais (stage-list, decision-timeline, funnel-chart, assist-badge)
  styles/        (type:ui)                  # SCSS isolado
apps/jrny-e2e/                              # Playwright (gerado dos .feature)
```

Tags Nx: `scope:jrny` em todas as libs + `type:{app,feature,domain,data-access,ui}`. Direções de
dependência conforme `nx-boundaries.md`; proibido importar `scope:` de outro módulo de domínio.

## 5. Cross-cutting Concerns

- **Auth/entitlement** — `authGuard` + `empresaGuard` + `accessGuard('jrny.*')` em `libs/jrny/access`;
  visibilidade de menu/ações filtrada por `AccessDecisionService` + `NavigationService`.
- **Imutabilidade do publicado** — `computed()` derivando "editável?" a partir de `estadoJornada`;
  toda a UI de edição respeita o gate `RASCUNHO`.
- **Observability** — `@journeyos/shared/observability`: latência do builder, tempo até publicar,
  taxa de decisões com assist IA, p95 das chamadas de leitura do decision log.
- **Design tokens** — `@journeyos/shared/ui-tokens`; sem cores hardcoded (faixas de estágio/decisão
  têm rótulo textual, nunca só cor — a11y).
- **i18n** — pt-BR como base (humano), termos técnicos em en-US; strings via mecanismo padrão do Shell.
- **Error model** — `ProblemDetail` (RFC 7807) → `AppError` via `@journeyos/shared/error-model` →
  feedback via `@journeyos/shared/ui-feedback`.

---

## Referências

- `01-architectural-vision.md` · `03-domain-framing-frontend.md` · `04-frontend-architecture-direction.md`
- BE: `jrny-service/contracts/api-contract.md` · `adr/ADR-005-routing-engine-model.md`
- `docs/architecture/frontend/standards/{module-pattern,nx-boundaries,access-layer-contracts}.md`
