# SPEC-02 — Component Hierarchy — INTL

> Árvore de componentes por feature lib. Smart components consomem facades (signals);
> presentational recebem `input()` e emitem `output()`. Pages terminam em `PageComponent`.
> Todos `standalone` + `ChangeDetectionStrategy.OnPush`.

## feature-copilot

```
CopilotPageComponent (smart, route /intl/copilot)
├── ConversationListComponent (presentational)        # lista lateral de conversas
│   └── ConversationListItemComponent (presentational) # @Input conversa; @Output select
├── NewConversationButtonComponent (presentational)    # @Output novaConversa
└── (redireciona/seleciona → /intl/copilot/:conversaId)

CopilotConversationPageComponent (smart, route /intl/copilot/:conversaId)
│   reads: messages(), status(), podeEnviar()  (CopilotFacade)
├── MessageThreadComponent (presentational)            # @Input messages
│   ├── ChatBubbleComponent (presentational, libs/intl/ui)   # @Input mensagem (USUARIO|COPILOTO)
│   │   ├── AnswerStatusBadgeComponent (presentational)      # @Input status
│   │   └── CitationChipComponent (presentational, libs/intl/ui) # @Input citacao; @Output abrir
│   └── ThinkingIndicatorComponent (presentational)         # bolha PENDENTE + Cancelar
├── CitationPanelComponent (smart, drawer)             # abre ao clicar citação; mostra trecho/metadados
└── QuestionInputComponent (presentational)            # @Input disabled; @Output enviar / cancelar
```

## feature-knowledge

```
KnowledgeListPageComponent (smart, route /intl/knowledge)
│   reads: page(), filtros(), loading(), error()  (KnowledgeFacade)
├── KnowledgeFilterBarComponent (presentational)       # @Output filterChange (q, tag, status)
├── KnowledgeTableComponent (presentational)           # @Input rows; @Output editar/indexar/arquivar
│   └── KnowledgeRowComponent (presentational)         # @Input no; badges fonte/status; ações por permissão
└── PaginatorComponent (presentational, libs/intl/ui ou shared)

KnowledgeNodeFormPageComponent (smart, routes /intl/knowledge/novo | /:id)
│   reads: no(), saving(), indexState(), error()  (KnowledgeFacade)
├── KnowledgeNodeFormComponent (presentational)        # @Input no; @Output salvar
│   └── TagInputComponent (presentational)             # @Input tags; @Output tagsChange
└── IndexActionComponent (presentational)              # @Input indexState; @Output indexar (com retry no 503)
```

## feature-analytics

```
AnalyticsPageComponent (smart, route /intl/analytics)
│   reads: funil(), copilotUsage(), periodo(), loading(), error()  (AnalyticsFacade)
├── PeriodFilterComponent (presentational)             # @Output periodoChange, granularidadeChange
├── FunnelChartComponent (presentational)              # @Input funil (etapas[])
│   └── FunnelStageComponent (presentational)          # @Input etapa { nome, total }
└── CopilotUsagePanelComponent (presentational)        # @Input usage
    └── StatCardComponent (presentational, libs/intl/ui) # @Input label, valor (totalRespostas, custoTokens, taxas)
```

## Regras

- **Smart**: `CopilotPageComponent`, `CopilotConversationPageComponent`, `CitationPanelComponent`,
  `KnowledgeListPageComponent`, `KnowledgeNodeFormPageComponent`, `AnalyticsPageComponent`.
- **Presentational** (sem injeção de facade): todos os demais — recebem `input()`, emitem `output()`.
- Componentes reutilizáveis de UI local (`ChatBubbleComponent`, `CitationChipComponent`,
  `StatCardComponent`) vivem em `libs/intl/ui`.
- Estados vazio/carregando/erro via `@journeyos/shared/ui-feedback` (skeleton de tabela/dashboard,
  empty da base, error normalizado).

## Critérios de aceite (EARS)

- `THE SYSTEM SHALL render every INTL route through a smart PageComponent that consumes a facade and never calls HttpClient directly.`
- `WHILE a copilot message is in PENDENTE state, THE SYSTEM SHALL render the thinking indicator and SHALL NOT render any citation chip.`
- `WHEN the user clicks a citation chip, THE SYSTEM SHALL open the citation panel with the source excerpt and metadata.`
- `WHERE a knowledge node index action returns 503, THE SYSTEM SHALL keep the node as RASCUNHO and SHALL offer a retry on the index action.`
- `THE SYSTEM SHALL render empty, loading and error states via the shared ui-feedback primitives.`
