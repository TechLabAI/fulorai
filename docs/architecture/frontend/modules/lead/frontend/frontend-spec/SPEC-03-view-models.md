# SPEC-03 — View Models — LEAD · Frontend

> View-models por tela como signal shapes. `Signal<T>` somente leitura expostos pelas facades;
> eventos UI são callbacks emitidos pelas pages. Tipos base em `03-domain-framing-frontend.md` §2.

## feature-lead-list

```typescript
type LeadListVM = {
  fila: Signal<LeadRowVM[]>;
  filtros: Signal<LeadFiltroVM>;
  paginacao: Signal<{ page: number; size: number; total: number }>;
  loading: Signal<boolean>;
  error: Signal<AppError | null>;
};
type LeadFiltroVM = { segmento?: string; dimensao?: DimensaoKey; estado?: EstadoLead; q?: string };

// Eventos UI (callbacks da page):
// onFiltroChange(filtro: LeadFiltroVM), onPageChange(page, size), onSelect(leadId: string)
```

## feature-lead-detail

```typescript
type LeadDetailVM = {
  lead: Signal<LeadDetailData | null>;
  score: Signal<MaturityScoreVM | null>;
  acoes: Signal<LeadAcao[]>;          // derivado de estado + permissões (computed)
  editState: Signal<'view' | 'editing' | 'saving'>;
  loading: Signal<boolean>;
  error: Signal<AppError | null>;
};
type LeadAcao = 'editar' | 'requalificar' | 'anonimizar' | 'expurgar' | 'responderSurvey';

// Eventos UI:
// onSalvarPerfil(atributos), onRequalificar(), onAnonimizar(), onExpurgar(),
// onResponderSurvey(surveyId, respostas)
```

## feature-maturity-score

```typescript
type MaturityDashboardVM = {
  distribuicao: Signal<MaturityDistributionVM | null>;
  loading: Signal<boolean>;
  error: Signal<AppError | null>;
};
// MaturityScoreVM (radar individual) e MaturityDistributionVM definidos em 03 §2.
// Evento UI: onRefresh()
```

## feature-segmentation

```typescript
type SegmentListVM = {
  segmentos: Signal<SegmentoVM[]>;
  editor: Signal<{ aberto: boolean; predicado: string; previewContagem: number | null }>;
  loading: Signal<boolean>;
  error: Signal<AppError | null>;
};
// Eventos UI: onCriar(), onEditar(id), onExcluir(id), onPreview(predicado), onSalvar(segmento), onAbrirFila(id)
```

## feature-survey

```typescript
type SurveyListVM = { surveys: Signal<SurveyVM[]>; loading: Signal<boolean>; error: Signal<AppError | null> };
type SurveyEditorVM = {
  survey: Signal<SurveyVM | null>;
  perguntas: Signal<PerguntaVM[]>;
  dirty: Signal<boolean>;
  error: Signal<AppError | null>;
};
// Eventos UI: onSalvarSurvey(survey), onAddPergunta(p), onResponder(leadId, surveyId, respostas)
```

## feature-qualification-rules

```typescript
type QualificationRulesVM = {
  versoes: Signal<RegraVersaoVM[]>;
  versaoAtiva: Signal<number | null>;
  activating: Signal<boolean>;
  error: Signal<AppError | null>;
};
// Eventos UI: onCriarVersao(payload), onAtivar(versao), onVerVersao(versao)
```

## Tipos compartilhados (derivados do BE)

```typescript
type DimensaoKey = 'PERFIL' | 'ENGAJAMENTO' | 'INTENCAO' | 'CAPACIDADE' | 'URGENCIA' | 'ADERENCIA';
type EstadoLead = 'EM_QUALIFICACAO' | 'QUALIFICADO' | 'ANONIMIZADO';
type Faixa = 'FRIO' | 'MORNO' | 'QUENTE';
// MaturityScoreVM: { total, dimensoes: DimensaoVM[6], versaoRegra, assistIa, calculadoEm }
```

## Critérios de aceite (EARS)

- `THE SYSTEM SHALL expose every view-model field as a read-only Signal produced by a data-access facade.`
- `WHEN a lead is in estado ANONIMIZADO, THE SYSTEM SHALL compute the acoes signal without "editar" and without "requalificar".`
- `THE SYSTEM SHALL derive the score faixa from the aggregate total together with a textual label, never from colour alone.`
- `IF the score response carries assistIa false, THEN THE SYSTEM SHALL set the view-model badge to "score determinístico" rather than an error flag.`

## Referências
- `03-domain-framing-frontend.md` §2 (tipos base) · `SPEC-04-data-access.md` (facades) · ADR-002, ADR-005
