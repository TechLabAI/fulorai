# SPEC-02 — Component Hierarchy — JRNY · Frontend

> Árvore de componentes por feature lib. Smart = consome facade (declara os signals que lê);
> Presentational = recebe `input()` e emite `output()`. Pages terminam em `PageComponent`.
> Todos **standalone** + **OnPush**.

## feature-journey-list

```
JourneyListPageComponent (smart, route entry)
│  lê: journeys(), loading(), error(), filtro(), podeCriar()
├── JourneyFilterBarComponent (presentational)   in: filtro · out: filtroChange
├── JourneyRowComponent (presentational)         in: journey · out: abrir, novaVersao
└── CreateJourneyDialogComponent (smart, abre on "criar")  out: criada(JourneyListItemVm)
```

## feature-journey-builder

```
JourneyBuilderPageComponent (smart, route entry)
│  lê: journey(), estagios(), editavel(), acoesDisponiveis(), saving(), error()
├── JourneyHeaderComponent (presentational)   in: journey, editavel · out: editarMeta, publicar, arquivar, novaVersao
├── StageListComponent (presentational, sortable)  in: estagios, editavel · out: reordenar, abrirEstagio, removerEstagio, addEstagio
│   └── StageCardComponent (presentational)    in: stage, editavel · out: abrir, remover
└── PublishBarComponent (presentational)       in: journey, podePublicar, motivoBloqueio · out: publicar
```

> Reordenação: drag-handle **e** setas ↑/↓ + teclado (a11y, ADR-005). Sem lib de canvas.

## feature-stage-editor

```
StageEditorPageComponent (smart, route entry)
│  lê: stage(), editavel(), saving(), erros()
├── StageFormComponent (presentational)        in: stage, editavel, erros · out: salvar, cancelar
└── AssetRefPickerComponent (smart)            in: assetRefId · out: assetSelecionado(id, label)
```

## feature-routing-engine

```
RoutingRulesPageComponent (smart, route entry)
│  lê: rules(), estagios(), loading(), error(), podeEditar()
├── RuleRowComponent (presentational)          in: rule · out: editar, toggleAtiva
└── RuleEditorDialogComponent (smart)          in: rule?, estagios · out: salva(RoutingRuleVm)
    └── ConditionBuilderComponent (presentational)  in: condicao, camposDisponiveis · out: condicaoChange
```

> `ConditionBuilderComponent` é **formulário estruturado** (combinador `E`/`OU` + predicados
> `campo/op/valor`) espelhando a gramática de snapshot do BE (`data-model.md §5`); **não** é
> query-builder visual livre. Validação client-side mínima + confia no `422 condicao-invalida`.

## feature-decision-log

```
DecisionLogPageComponent (smart, route entry)
│  lê: estadoJornada(), decisoes(), loading(), error(), semInscricao()
├── LeadJourneyStateCardComponent (presentational)  in: estado · (estágio corrente, jornada/versão)
└── DecisionTimelineComponent (presentational)      in: decisoes · out: carregarMais
    └── DecisionItemComponent (presentational)      in: decisao
        └── AssistBadgeComponent (presentational)   in: assistIa (USADO|IGNORADO|INDISPONIVEL)
```

> `AssistBadgeComponent`: `USADO` → "IA ✓"; `IGNORADO`/`INDISPONIVEL` → badge **neutro**
> "roteamento determinístico" (jamais erro — ADR-005). `DecisionItemComponent` sempre renderiza
> gatilho + regra(versão) + alvo + assist + motivo (proibido mostrar alvo sem o "por quê").

## feature-journey-analytics

```
JourneyAnalyticsPageComponent (smart, route entry)
│  lê: funil(), saudeRoteamento(), loading(), error()
├── FunnelChartComponent (presentational)       in: funil (por tipoEstagio) — SVG/CSS leve
└── RoutingHealthCardComponent (presentational) in: taxaAssistIa, totalDecisoes
```

## Componentes locais compartilhados (`libs/jrny/ui`)

`StageTypeBadgeComponent` (rótulo textual do tipo, nunca só cor), `JourneyStateChipComponent`
(`RASCUNHO`/`PUBLICADA`/`ARQUIVADA`), `AssistBadgeComponent`, `EmptyStateComponent` (reusa
`@journeyos/shared/ui-feedback`).

## Critérios de aceite (EARS)

- `THE SYSTEM SHALL render every JRNY route through a smart *PageComponent that consumes a facade and never calls HttpClient directly.`
- `WHILE a journey is not editable, THE SYSTEM SHALL render StageListComponent and JourneyHeaderComponent in read-only (no add/reorder/remove affordances).`
- `THE SYSTEM SHALL operate stage reordering by both pointer drag and keyboard, exposing an accessible name for each stage.`
- `THE SYSTEM SHALL render every DecisionItemComponent with gatilho, regra version, alvo, assist badge and motivo together.`
- `WHEN assistIa is IGNORADO or INDISPONIVEL, THE SYSTEM SHALL render a neutral "roteamento determinístico" badge and SHALL NOT render an error state.`

## Referências
- `03-domain-framing-frontend.md` (VMs) · `SPEC-03-view-models.md` · `adr/ADR-005-canvas-builder-rendering.md`
