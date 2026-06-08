# 02 — Architecture Blueprint — COMM · Frontend

> Fronteiras do sistema, atores externos, fluxos ponta-a-ponta e organização interna de libs.

## 1. System Boundary

O FE COMM é um **cliente do API gateway** do Journey OS. Todas as chamadas passam por
`@journeyos/shared/access-http-base` (`HttpClient` + interceptors de JWT, `X-Empresa-Id`,
`X-Correlation-Id` e normalização de erro) e batem **somente** no `comm-service`
(`/api/v1/{templates,messages,routing-rules,channels}`). O FE **não** chama:

- provedores de IA / a TechLab AI direto (só o BE faz, atrás de `/templates/{id}/studio/compose`);
- provedores de canal (Meta/Twilio/SES/Telegram) — o FE só conhece `canal`;
- outros microsserviços de domínio direto (assets publicados são lidos pelo **BE** ao renderizar/compor).

## 2. External Actors and Systems

- **Browser autenticado** (sessão via Access Layer / `auth-session`) — Marina, Lucas, Rafael.
- **`comm-service`** (BE) através de `@journeyos/shared/access-http-base` — única origem de dados.
- **Shell** (`journey-os-web`) — hospeda o módulo lazy, provê layout, navegação e contexto de empresa.
- **Provedores de canal** — invisíveis ao FE; só o BE os conhece (adapters). O FE vê o resultado (`provedor`, `provedorMessageId`, estado de entrega).
- **TechLab AI** — invisível ao FE; acessada só pelo BE no Template Studio.

## 3. End-to-End User Flows

### Golden path — disparo rastreável (Lucas)

```
[Catálogo de templates] --escolhe ATIVO--> [Disparo 1:1]
        |                                       | (template ATIVO + leadId + variaveis + Idempotency-Key)
        v                                       v
  filtros canal/tipo/estado            POST /messages -> 202 ENFILEIRADA
                                                |
                                                v
                                   [Detalhe da mensagem] timeline:
                                   ENFILEIRADA -> ENVIADA -> ENTREGUE -> LIDA
                                   (polling com backoff até estado terminal)
```

### Golden path — autoria de template + Studio (Marina)

```
[Catálogo] --novo--> [Editor: RASCUNHO]
   corpo + {{variaveis}} + (vínculo asset opcional)
        |                         \
        | (Ativar)                 --> [Template Studio] brief+contexto
        v                                   | POST /studio/compose
   RASCUNHO -> ATIVO                         v
                              200: novo corpo RASCUNHO (revisar) | 503 degradado
```

### Alternativas / edge cases

- **Template não-ATIVO no disparo** → `409 comm.template.nao-ativo`: a UI bloqueia o envio e orienta ativar.
- **Sem canal resolvido** (sem `canal` e roteamento não acha) → `422 comm.roteamento.sem-canal`: UI sugere escolher canal manualmente ou criar regra.
- **Canal sem config ativa** → `422 comm.canal.nao-configurado`: CTA para `/comm/channels`.
- **Variável obrigatória ausente** → `422 comm.mensagem.variavel-ausente`: form destaca a variável faltante.
- **EMAIL sem assunto** → `422 comm.template.assunto-obrigatorio`: validação síncrona no editor.
- **Placeholder não declarado** → `422 comm.template.variavel-nao-declarada`: validação síncrona antes do PATCH.
- **IA indisponível** → `503 comm.studio.ia-indisponivel`: `studioState='degradado'`, corpo do template **inalterado**, CTA "editar manualmente".
- **Provedor fora** → mensagem entra em `FALHADA` (com `motivoFalha`); a timeline exibe a falha e o `503 comm.canal.provedor-indisponivel` quando aplicável.

## 4. Internal Boundaries (libs — padrão module-pattern)

```
apps/comm/                                   # host fino lazy (type:app, scope:comm)
libs/comm/shell-entry/                       # entry como library @journeyos/comm (ADR-006)
    comm.contract.ts        # ModuleMenuMetadata + deepLinks + permissions + flags
    comm.routes.ts          # MODULE_ROUTES[]
    comm.bootstrap.ts        # init/destroy
    comm.permission-map.ts
    comm.feature-flags.ts
    comm.nav.config.ts
libs/comm/feature-template-catalog/          # catálogo/busca + CRUD + editor + estado (type:feature)
libs/comm/feature-template-studio/           # composição assistida por IA (type:feature)
libs/comm/feature-routing-rules/             # CRUD de regras de roteamento (type:feature)
libs/comm/feature-messages/                  # disparo 1:1 + histórico + timeline de entrega (type:feature)
libs/comm/feature-channel-config/            # config de canais/provedores (type:feature)
libs/comm/data-access/                       # *ApiService + facades de signal (type:data-access)
libs/comm/access/                            # guards específicos (type:domain)
libs/comm/integration/                       # CommShellIntegrationService (type:domain)
libs/comm/navigation/                        # breadcrumbs/menu state (type:domain)
libs/comm/ui/                                # template-card, state-chip, delivery-timeline, canal-badge (type:ui)
libs/comm/styles/                            # SCSS isolado (type:ui)
```

> O editor de template vive **dentro** de `feature-template-catalog` (rota `/templates/:id`), não é
> lib separada. Disparo e histórico/rastreio vivem em `feature-messages`. Campaign manager fica fora
> do MVP (ver `06`).

## 5. Cross-cutting Concerns

- **Auth/entitlement**: `authGuard` + `empresaGuard` + `accessGuard('comm.<perm>')` via `AccessDecisionService` (`@journeyos/shared/access-decision`). Botões/ações gated por permissão (`computed()`).
- **Observabilidade**: `@journeyos/shared/observability` — timing de composição do Studio, taxa de entrega/leitura, latência do catálogo, duração de sessões de polling.
- **Design tokens**: `@journeyos/shared/ui-tokens` (cores/estados de entrega), primitivos `ui-components`, estados `ui-feedback`.
- **Erro**: `ProblemDetail` BE → `AppError` (`@journeyos/shared/error-model`) → mensagens via `ui-feedback`; mapeamento explícito de `409`/`422`/`503` (ver `05` §5).
- **i18n**: strings em pt-BR (locale primário); chaves de tradução preparadas, sem segunda língua no MVP.
- **Multi-empresa**: `EmpresaContextService` é a fonte da empresa ativa; trocar empresa limpa signals de catálogo/mensagens antes de recarregar.

---

## Referências

- `01-architectural-vision.md` · `04-frontend-architecture-direction.md` · `05-state-and-data-flow.md`
- BE API: `docs/architecture/backend/services/comm-service/contracts/api-contract.md`
- `docs/architecture/frontend/standards/nx-boundaries.md`
