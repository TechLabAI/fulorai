# SPEC-02 — Component Hierarchy — COMM · Frontend

> Árvore de componentes por feature lib. Smart components consomem facades (signals); presentational
> recebem `input()` e emitem `output()`. Todos `standalone` + `OnPush`. Pages terminam em `PageComponent`.

## feature-template-catalog

```
TemplateCatalogPageComponent (smart, /comm/templates)
├── lê: catalogoTemplates(), loading(), error(), filtro()
├── CommToolbarComponent (pres.) — busca + filtros (canal/tipo/estado)  [output: filterChange]
├── TemplateListComponent (pres.) — [input: items] [output: open, novo]
│   └── TemplateCardComponent (pres.) — [input: template] (usa StateChipComponent + CanalBadgeComponent)
└── NewTemplateDialogComponent (smart, dialog) — cria RASCUNHO [output: created]

TemplateEditorPageComponent (smart, /comm/templates/:id)
├── lê: templateSelecionado(), loading(), error()
├── TemplateMetaFormComponent (pres.) — nome/canal/tipo/assunto/vínculo asset  [output: save]
├── TemplateBodyEditorComponent (pres.) — corpo + chips de {{variavel}} + validação síncrona
│       [input: corpo, variaveis] [output: change, insertPlaceholder]
├── TemplateStateActionsComponent (pres.) — Ativar / Arquivar (gated)  [output: activate, archive]
└── (link → Studio) /comm/templates/:id/studio
```

## feature-template-studio

```
TemplateStudioPageComponent (smart, /comm/templates/:id/studio)
├── lê: studioState(), templateSelecionado(), error()
├── StudioBriefFormComponent (pres.) — brief + contexto + assetOrigem  [output: compose]
├── StudioComposingComponent (pres.) — estado "compondo…" (bloqueia o form)
├── StudioDraftPreviewComponent (pres.) — preview do corpo gerado  [output: aceitarRascunho]
└── StudioDegradedBannerComponent (pres.) — banner 503 + CTA "editar manualmente"
```

## feature-routing-rules

```
RoutingRulesPageComponent (smart, /comm/routing-rules)
├── lê: regras(), loading(), error()
├── RoutingRuleListComponent (pres.) — ordenada por prioridade  [input: regras] [output: editar, nova]
│   └── RoutingRuleRowComponent (pres.) — canal preferido + fallback + ativa
└── RoutingRuleDialogComponent (smart, dialog) — criar/editar regra  [output: saved]
        └── ChannelPickerComponent (pres.) — escolhe canal preferido/fallback (só canais)
```

## feature-messages

```
MessagesListPageComponent (smart, /comm/messages)
├── lê: mensagens(), loading(), error(), filtro()
├── CommToolbarComponent (pres.) — filtros (lead/canal/estado/período)
├── MessageListComponent (pres.) — [input: items] [output: open]
│   └── MessageRowComponent (pres.) — estado de entrega + canal (StateChip/CanalBadge)
└── DispatchDialogComponent (smart, dialog) — disparo 1:1 (template ATIVO + leadId + variaveis)
        [output: dispatched]  (envia Idempotency-Key; desabilita o botão durante o request)

MessageDetailPageComponent (smart, /comm/messages/:id)
├── lê: mensagemSelecionada(), eventosEntrega(), estadoTerminal()
├── inicia/encerra polling (startPolling/stopPolling) — ADR-005
├── MessageSummaryComponent (pres.) — canal/provedor/tentativas/motivoFalha
└── DeliveryTimelineComponent (pres.) — [input: eventos] timeline ENFILEIRADA→…→LIDA/FALHADA
```

## feature-channel-config

```
ChannelConfigPageComponent (smart, /comm/channels)
├── lê: canais(), loading(), error()
├── ChannelListComponent (pres.) — [input: canais] [output: editar, novo]
│   └── ChannelRowComponent (pres.) — canal/provedor/identidade + credencialRef MASCARADA + ativo
└── ChannelConfigDialogComponent (smart, dialog) — criar/editar config  [output: saved]
        (campo credencialRef tratado como referência; nunca exibe/coleta segredo em claro)
```

## UI compartilhada do módulo (`libs/comm/ui`)

`StateChipComponent` (estado de template/mensagem), `CanalBadgeComponent` (WHATSAPP/EMAIL/TELEGRAM/SMS),
`DeliveryTimelineComponent` (promovível a `@journeyos/shared/patterns-timeline`), `CommToolbarComponent`.

## Critérios de aceite (EARS)

- **C-02.1 (Ubiquitous):** `THE SYSTEM SHALL implementar todos os componentes COMM como standalone com ChangeDetectionStrategy OnPush`
- **C-02.2 (Ubiquitous):** `THE SYSTEM SHALL restringir o consumo de facades aos componentes smart Page e Dialog enquanto os presentational recebem input e emitem output`
- **C-02.3 (Event-driven):** `WHEN o usuário clica em um template do catálogo, THE SYSTEM SHALL navegar para o TemplateEditorPageComponent em /comm/templates/:id`
- **C-02.4 (State-driven):** `WHILE studioState é composing, THE SYSTEM SHALL bloquear o StudioBriefFormComponent e exibir o StudioComposingComponent`
- **C-02.5 (State-driven):** `WHILE a mensagem aberta não está em estado terminal, THE SYSTEM SHALL manter o DeliveryTimelineComponent atualizado por polling`
- **C-02.6 (Unwanted):** `IF o ChannelConfigDialogComponent recebe um segredo de provedor, THEN THE SYSTEM SHALL tratá-lo apenas como credencialRef e nunca exibi-lo em claro`

## Referências

- SPEC-01 (rotas) · SPEC-03 (view-models) · `02-architecture-blueprint.md` §4
