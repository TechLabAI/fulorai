# SPEC-03 — View Models — JRNY · Frontend

> View-models por tela (Signals), eventos de UI e estados. Derivados das respostas do BE — a UI
> nunca expõe entidades cruas. Fonte: `03-domain-framing-frontend.md` §2.

## Tipos de domínio (FE)

```typescript
type EstadoJornada = 'RASCUNHO' | 'PUBLICADA' | 'ARQUIVADA';
type TipoEstagio   = 'CAPTURA' | 'NUTRICAO' | 'QUALIFICACAO' | 'OFERTA' | 'FECHAMENTO' | 'POS_VENDA';
type AssistIa      = 'USADO' | 'IGNORADO' | 'INDISPONIVEL';
type ResultadoDecisao = 'ROTEADO' | 'SEM_MUDANCA' | 'NAO_ROTEADO';
type EstadoInscricao  = 'ATIVA' | 'CONCLUIDA' | 'ENCERRADA';

type CondicaoPredicado = { campo: string; op: '='|'<>'|'>'|'>='|'<'|'<='|'in'|'nin'|'existe'; valor: unknown };
type Condicao = { operador: 'E' | 'OU'; predicados: CondicaoPredicado[] };
```

## feature-journey-list

```typescript
type JourneyListItemVm = {
  id: string; nome: string; descricao: string | null;
  estadoJornada: EstadoJornada; versao: number; qtdEstagios: number;
  atualizadoEm: string | null; podeEditar: boolean;   // RASCUNHO && perm
};
type JourneyListVM = {
  journeys: Signal<JourneyListItemVm[]>;
  loading: Signal<boolean>;
  error: Signal<AppError | null>;
  filtro: Signal<{ estado?: EstadoJornada; q?: string; page: number; size: number }>;
  podeCriar: Signal<boolean>;                          // perm jrny.jornada.criar
};
// eventos UI: onFiltroChange(filtro), onCriar(nome, descricao), onAbrir(id), onNovaVersao(id)
```

## feature-journey-builder

```typescript
type StageItemVm = {
  id: string; ordem: number; tipoEstagio: TipoEstagio; nome: string;
  assetRefId: string | null; assetRefLabel: string | null;
  terminal: boolean; temRegrasSaindo: boolean;
};
type JourneyBuilderVM = {
  journey: Signal<{ id: string; nome: string; descricao: string|null; estadoJornada: EstadoJornada; versao: number } | null>;
  estagios: Signal<StageItemVm[]>;
  editavel: Signal<boolean>;                           // estadoJornada === 'RASCUNHO' && perm
  acoesDisponiveis: Signal<('publicar'|'arquivar'|'nova-versao'|'add-estagio')[]>;
  podePublicar: Signal<boolean>;                       // editavel && estagios.length >= 1
  motivoBloqueio: Signal<string | null>;               // ex.: "adicione ≥1 estágio"
  saving: Signal<boolean>;
  error: Signal<AppError | null>;
};
// eventos UI: onEditarMeta(patch), onAddEstagio(), onAbrirEstagio(stageId),
//             onReordenar(ordemIds: string[]), onRemoverEstagio(stageId),
//             onPublicar(), onArquivar(), onNovaVersao()
```

## feature-stage-editor

```typescript
type StageEditorVM = {
  stage: Signal<{ id?: string; ordem: number; tipoEstagio: TipoEstagio; nome: string;
                  assetRefId: string|null; terminal: boolean; config: Record<string, unknown> } | null>;
  editavel: Signal<boolean>;                           // jornada RASCUNHO && perm
  saving: Signal<boolean>;
  erros: Signal<{ campo: string; mensagem: string }[]>;
};
// eventos UI: onSalvar(stage), onCancelar(), onAssetSelecionado(id, label)
```

## feature-routing-engine

```typescript
type RoutingRuleVm = {
  id: string; jornadaId: string;
  estagioOrigemId: string | null; estagioOrigemNome: string | null;   // null = regra de entrada
  estagioDestinoId: string; estagioDestinoNome: string;
  condicaoResumo: string;                              // ex.: "score ≥ 70 E INTENCAO ≥ 80"
  prioridade: number; versao: number; ativa: boolean;
};
type RoutingRulesVM = {
  rules: Signal<RoutingRuleVm[]>;                      // ordenadas por prioridade asc
  estagios: Signal<{ id: string; nome: string }[]>;    // para os seletores origem/destino
  loading: Signal<boolean>;
  error: Signal<AppError | null>;
  podeEditar: Signal<boolean>;                         // perm jrny.regra.criar|editar
};
// eventos UI: onCriarRegra(rule), onEditarRegra(id, patch), onToggleAtiva(id), onCondicaoChange(condicao)
```

## feature-decision-log

```typescript
type LeadJourneyStateVm = {
  leadId: string; jornadaNome: string | null; jornadaVersao: number | null;
  estagioCorrenteNome: string | null; tipoEstagioCorrente: TipoEstagio | null;
  estado: EstadoInscricao | null; entrouEm: string | null;
  semInscricao: boolean;
};
type DecisionItemVm = {
  id: string; gatilho: string; regraVersaoLabel: string | null;   // "regra #3 v2" | null (sem regra)
  resultado: ResultadoDecisao; estagioAlvoNome: string | null;
  assistIa: AssistIa; motivo: string; decididoEm: string;
};
type DecisionLogVM = {
  estadoJornada: Signal<LeadJourneyStateVm | null>;
  decisoes: Signal<DecisionItemVm[]>;                  // newest-first, paginado
  loading: Signal<boolean>;
  error: Signal<AppError | null>;
  semInscricao: Signal<boolean>;
};
// eventos UI: onCarregarMais(), onAbrir(leadId)
```

## feature-journey-analytics

```typescript
type JourneyAnalyticsVM = {
  funil: Signal<{ tipoEstagio: TipoEstagio; qtdLeads: number }[]>;
  taxaAssistIa: Signal<number>;                        // % de decisões com assistIa=USADO
  totalDecisoes: Signal<number>;
  loading: Signal<boolean>;
  error: Signal<AppError | null>;
};
// eventos UI: onRecarregar()
```

## Derivações (computed)

- `editavel = estadoJornada === 'RASCUNHO' && hasPerm('jrny.jornada.editar')`
- `podePublicar = editavel && estagios().length >= 1`
- `acoesDisponiveis` — função de `estadoJornada` + permissões (RASCUNHO → publicar/arquivar/add; PUBLICADA → nova-versao/arquivar; ARQUIVADA → ∅)
- `condicaoResumo` — render textual da `Condicao` (combinador + predicados legíveis)
- `assistBadge` — `USADO → 'IA ✓'` · `IGNORADO|INDISPONIVEL → 'roteamento determinístico'` (neutro)

## Critérios de aceite (EARS)

- `THE SYSTEM SHALL derive every JRNY view-model from BE responses and SHALL NOT expose raw BE entities to components.`
- `THE SYSTEM SHALL compute editavel as (estadoJornada === RASCUNHO AND user has jrny.jornada.editar).`
- `THE SYSTEM SHALL compute podePublicar as false WHILE the journey has zero stages.`
- `THE SYSTEM SHALL map assistIa USADO to an "IA" badge and assistIa IGNORADO or INDISPONIVEL to a neutral "determinístico" badge.`
- `THE SYSTEM SHALL render condicaoResumo as a human-readable summary of the condicao predicate.`

## Referências
- `03-domain-framing-frontend.md` · `SPEC-04-data-access.md` · BE `data-model.md` (§3, §5) · `api-contract.md`
