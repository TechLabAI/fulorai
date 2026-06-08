# SPEC-02 — Component Hierarchy — LEAD · Frontend

> Árvore de componentes por feature lib. Smart components consomem facades (signals); presentational
> recebem `input()` e emitem `output()`. Pages terminam em `PageComponent`. Todos standalone + OnPush.

## feature-lead-list

```
LeadListPageComponent (smart, route entry)        # lê LeadListFacade: fila, filtros, loading, error
+-- LeadFilterBarComponent (presentational)        # input: filtros; output: filtroChange
+-- JosSmartTable / LeadTableComponent (presentational)
|   +-- LeadRowComponent (presentational)          # input: LeadRowVM; output: select
|   |   +-- ScoreBadgeComponent (ui)               # input: total, faixa, assistIa
|   |   +-- LeadStateChipComponent (ui)            # input: estado
|   +-- JosEmptyState / JosLoading / JosError      # @journeyos/shared/ui-feedback
+-- LeadPaginatorComponent (presentational)        # input: paginacao; output: pageChange
```

## feature-lead-detail

```
LeadDetailPageComponent (smart, route entry)      # lê LeadDetailFacade: leadSelecionado, score, acoes
+-- LeadProfilePanelComponent (presentational)     # input: perfil; output: salvarPerfil (editing)
|   +-- BaseLegalBadgeComponent (ui)               # input: baseLegal
+-- ScoreBreakdownComponent (smart-ish/presentational)  # input: MaturityScoreVM
|   +-- ScoreRadarComponent (ui)                   # input: dimensoes[6]; tabela alternativa a11y
|   +-- DimensionBarComponent (ui) ×6              # input: dimensao, valor, peso
|   +-- ScoreBadgeComponent (ui)                   # total + faixa + badge assistIa
+-- LeadActionsBarComponent (presentational)       # outputs: requalificar, anonimizar, expurgar
|                                                  #   (cada ação gated por permissão + estado)
+-- SurveyAnswerDialogComponent (smart)            # responder survey para o lead (output: respostas)
+-- ConfirmDialogComponent (ui)                    # confirmação de ações LGPD (anonimizar/expurgar)
```

## feature-maturity-score

```
MaturityDashboardPageComponent (smart, route entry)  # lê MaturityFacade: distribuicao, loading, error
+-- MaturityDistributionChartComponent (ui)        # input: histograma + saúde por dimensão
+-- ScoreRadarComponent (ui)                       # reuso: média 6D da base
+-- AssistIaShareComponent (ui)                    # input: pctComAssistIa (transparência)
```

## feature-segmentation

```
SegmentListPageComponent (smart, route entry)     # lê SegmentFacade: segmentos, loading, error
+-- SegmentRowComponent (presentational)           # input: SegmentoVM; outputs: editar, excluir, abrirFila
+-- SegmentEditorDialogComponent (smart)           # criar/editar predicado; output: salvar
    +-- PredicatePreviewComponent (presentational)  # input: previewContagem
```

## feature-survey

```
SurveyListPageComponent (smart, route entry)      # lê SurveyFacade: surveys, loading, error
+-- SurveyRowComponent (presentational)            # output: abrir
SurveyEditorPageComponent (smart, route entry)    # editar survey + perguntas; output: salvar
+-- QuestionEditorComponent (presentational) ×N    # input: PerguntaVM; output: change
SurveyAnswerDialogComponent (smart)               # (reusado no detalhe do lead) capturar respostas
```

## feature-qualification-rules

```
QualificationRulesPageComponent (smart, route entry)  # lê QualificationFacade: versoes, versaoAtiva
+-- RuleVersionRowComponent (presentational)       # input: RegraVersaoVM; outputs: ativar, ver
+-- RuleVersionEditorDialogComponent (smart)       # criar nova versão (inativa); output: salvar
```

## Regras

- Smart components declaram explicitamente os signals lidos (via facade); presentational são puros.
- Componentes de visualização do score (`ScoreRadarComponent`, `DimensionBarComponent`,
  `ScoreBadgeComponent`, `MaturityDistributionChartComponent`) vivem em `libs/lead/ui` e são candidatos
  a promoção a `@journeyos/shared/*` (asset-driven-ui).
- `ScoreBreakdownComponent` **sempre** renderiza as 6 dimensões + versão de regra + badge `assistIa`
  (invariante de domínio — ADR-005).

## Critérios de aceite (EARS)

- `THE SYSTEM SHALL render every LEAD page component as standalone with OnPush change detection.`
- `THE SYSTEM SHALL render ScoreBreakdownComponent with all six dimensions, the rule version, and the assistIa badge whenever a Maturity Score is shown.`
- `WHEN a presentational component needs to change state, THE SYSTEM SHALL emit an output to its smart parent instead of mutating a facade directly.`
- `WHERE the score-radar is shown, THE SYSTEM SHALL also provide an accessible textual table of the six dimensions for screen readers.`

## Referências
- `03-domain-framing-frontend.md` (VMs) · `SPEC-03-view-models.md` · ADR-005
