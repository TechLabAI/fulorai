# SPEC-02 — Component Hierarchy — SALE · Frontend

> Árvore de componentes por feature lib. Smart = consome facade (declara os signals que lê);
> Presentational = recebe `input()` e emite `output()`. Pages terminam em `PageComponent`.
> Todos **standalone** + **OnPush**.

## feature-pipeline

```
SalePipelinePageComponent (smart, route entry)
│  lê: colunas(), oportunidades(), filtro(), movingCardId(), podeMover(), podeCriar(), loading(), error()
├── PipelineToolbarComponent (presentational)   in: filtro · out: filtroChange, criar
├── PipelineBoardComponent (presentational, cdkDropListGroup)  in: colunas, movingCardId · out: moverEstagio
│   └── PipelineColumnComponent (presentational, cdkDropList)   in: coluna · out: drop
│       └── OpportunityCardComponent (presentational, cdkDrag)  in: oportunidade, arrastavel · out: abrir
└── CreateOpportunityDialogComponent (smart, abre on "criar")   out: criada(OpportunityCardVm)
```

> Drag-and-drop via **Angular CDK DragDrop** (importado **só** neste feature lib — orçamento de bundle, ADR-005).
> Soltar um card dispara `moverEstagio(id, destino)` → `PATCH /oportunidades/{id}/estagio` com **optimistic move + rollback**.
> Cards `GANHA`/`PERDIDA` têm `arrastavel = false` (fechamento terminal). Fallback de teclado/lista para a11y.

## feature-opportunity

```
OpportunityDetailPageComponent (smart, route entry)
│  lê: oportunidade(), historico(), podeFechar(), saving(), naoEncontrada(), error()
├── OpportunityHeaderComponent (presentational)   in: oportunidade · (titulo, valor, responsavel, probabilidade, estado)
├── StageHistoryTimelineComponent (presentational)  in: historico · (de→para estágio, ator, quando)
│   └── StageHistoryItemComponent (presentational)   in: item
├── WinOpportunityButtonComponent (presentational)   in: habilitado · out: ganhar
└── LoseOpportunityDialogComponent (smart, motivo obrigatório)  out: perdida(motivo)
```

> "Perder" abre dialog que exige `motivo` (validação inline; confia no `422 motivo-obrigatorio`). Em deal
> `GANHA`/`PERDIDA`, os botões ganhar/perder ficam desabilitados (terminal).

## feature-offer

```
OfferListPageComponent (smart, route entry)
│  lê: ofertas(), filtro(), podeCriar(), loading(), error()
├── OfferFilterBarComponent (presentational)   in: filtro · out: filtroChange
├── OfferRowComponent (presentational)         in: oferta · out: abrir
└── CreateOfferDialogComponent (smart, abre on "criar")  out: criada(OfferRowVm)

OfferDetailPageComponent (smart, route entry)
│  lê: oferta(), versoes(), editavel(), saving(), erros()
├── OfferVersionListComponent (presentational)  in: versoes · (histórico imutável de versões)
├── OfferFormComponent (presentational)         in: oferta, editavel, erros · out: salvar (nova versão), cancelar
└── DeactivateOfferButtonComponent (presentational)  in: habilitado · out: desativar
```

> Editar **salva como nova versão** (a versão exibida nunca é mutada). `OfferVersionListComponent`
> lista as versões anteriores como read-only.

## feature-purchase

```
PurchaseListPageComponent (smart, route entry)
│  lê: compras(), filtro(), loading(), error()
├── PurchaseFilterBarComponent (presentational)   in: filtro · out: filtroChange
└── PurchaseRowComponent (presentational)          in: compra · out: abrir

PurchaseDetailPageComponent (smart, route entry)
│  lê: compra(), itens(), atribuicao(), podeAjustar(), saving(), naoEncontrada(), error()
├── PurchaseSummaryComponent (presentational)       in: compra · (valorTotal, status, baseLegal/consentimento, comprador)
├── PurchaseItemsTableComponent (presentational)    in: itens · (oferta, qtd, valor)
├── AttributionBreakdownComponent (presentational)  in: atribuicao · (touchpoint, tipo, valor, versão do modelo)
└── PurchaseAdjustActionsComponent (presentational) in: habilitado, status · out: estornar, cancelar
```

> **Sem criação** de compra no FE (ingestão server-to-server). `AttributionBreakdownComponent` **sempre**
> mostra o detalhe por touchpoint + a versão do modelo — nunca só o total opaco (receita explicável).
> Estornar/cancelar exigem confirmação destrutiva (modal).

## feature-attribution

```
AttributionPageComponent (smart, route entry)
│  lê: modelos(), modeloAtivo(), podeCriar(), podeAtivar(), saving(), loading(), error()
├── AttributionModelListComponent (presentational)  in: modelos · out: ativar
│   └── AttributionModelRowComponent (presentational)  in: modelo · out: ativar
├── CreateAttributionModelDialogComponent (smart)    out: criada(AttributionModelVm)
└── AttributionBreakdownPreviewComponent (presentational)  in: breakdown · (preview do efeito do modelo)
```

> Criar versão nasce **inativa**; ativar uma versão **re-atribui** as compras afetadas (BE) e desativa a
> anterior. Enquanto nenhuma versão estiver ativa, o badge mostra fallback **LAST_TOUCH** (determinístico).
> Modelos multi-touch ficam atrás da flag `sale.attribution-multitouch`.

## feature-revenue-dashboard

```
RevenueDashboardPageComponent (smart, route entry)
│  lê: funilReceita(), ltvTopContatos(), periodo(), loading(), error()
├── RevenueFunnelChartComponent (presentational)   in: funilReceita (por origem) — SVG/CSS leve
├── RevenuePeriodFilterComponent (presentational)  in: periodo · out: periodoChange
└── LtvTopContactsTableComponent (presentational)  in: ltvTopContatos · (contato, valorTotal, numCompras)
```

## Componentes locais compartilhados (`libs/sale/ui`)

`OpportunityStateChipComponent` (`NOVA`/`EM_ANDAMENTO`/`GANHA`/`PERDIDA`/`DESCARTADA`, rótulo textual),
`PurchaseStatusChipComponent` (`CONFIRMADA`/`ESTORNADA`/`CANCELADA`), `MoneyComponent` (formata
`NUMERIC(15,2)` + `moeda`), `AttributionTypeBadgeComponent` (`ORIGEM_LEAD`/`JORNADA`/`CAMPANHA`/`DIRETO`),
`EmptyStateComponent` (reusa `@journeyos/shared/ui-feedback`). O **board Kanban** (`kanban-board`,
`kanban-column`, `opportunity-card`) também mora em `libs/sale/ui`.

## Critérios de aceite (EARS)

- `THE SYSTEM SHALL render every SALE route through a smart *PageComponent that consumes a facade and never calls HttpClient directly.`
- `WHEN a card is dropped into another column, THE SYSTEM SHALL move the card optimistically and call PATCH /oportunidades/{id}/estagio.`
- `WHILE an opportunity is GANHA or PERDIDA, THE SYSTEM SHALL render its card as non-draggable and SHALL disable the win/lose actions.`
- `THE SYSTEM SHALL render every purchase AttributionBreakdownComponent with touchpoint, tipo, valor and model versão together.`
- `THE SYSTEM SHALL gate the create-opportunity, edit-offer, deactivate-offer, refund/cancel and activate-model affordances behind their respective permissions.`

## Referências
- `03-domain-framing-frontend.md` (VMs) · `SPEC-03-view-models.md` · `adr/ADR-005-kanban-pipeline-rendering.md`
