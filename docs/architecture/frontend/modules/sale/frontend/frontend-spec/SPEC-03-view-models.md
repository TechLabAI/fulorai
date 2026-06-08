# SPEC-03 — View Models — SALE · Frontend

> View-models por tela (Signals), eventos de UI e estados. Derivados das respostas do BE — a UI
> nunca expõe entidades cruas. Fonte: `03-domain-framing-frontend.md` §2 + BE `data-model.md`.

## Tipos de domínio (FE)

```typescript
type EstadoOportunidade = 'NOVA' | 'EM_ANDAMENTO' | 'GANHA' | 'PERDIDA' | 'DESCARTADA';
type EstagioPipeline    = string;                  // estágio configurável (ex.: NOVA, CONTATO, PROPOSTA)
type StatusCompra       = 'CONFIRMADA' | 'ESTORNADA' | 'CANCELADA';
type BaseLegal          = 'CONSENTIMENTO' | 'LEGITIMO_INTERESSE' | 'EXECUCAO_CONTRATO' | 'OBRIGACAO_LEGAL';
type TipoModeloAtribuicao = 'LAST_TOUCH' | 'FIRST_TOUCH' | 'LINEAR';
type TipoTouchpoint     = 'ORIGEM_LEAD' | 'JORNADA' | 'CAMPANHA' | 'DIRETO';

type Money = { valor: number; moeda: string };     // NUMERIC(15,2) + ISO-4217
```

## feature-pipeline

```typescript
type OpportunityCardVm = {
  id: string; titulo: string;                       // lead/oferta resumido
  estagio: EstagioPipeline; estado: EstadoOportunidade;
  valorEstimado: Money; responsavelNome: string | null; probabilidade: number;  // 0..100
  arrastavel: boolean;                              // estado ∉ {GANHA,PERDIDA} && perm sale.oportunidade.mover
};
type PipelineColumnVm = {
  estagio: EstagioPipeline; titulo: string;
  cards: OpportunityCardVm[]; total: number; somaValor: Money;
};
type PipelineVM = {
  colunas: Signal<PipelineColumnVm[]>;              // na ordem do pipeline
  oportunidades: Signal<OpportunityCardVm[]>;       // flat (fonte do board)
  filtro: Signal<{ responsavel?: string; estado?: EstadoOportunidade; q?: string }>;
  movingCardId: Signal<string | null>;             // card em PATCH otimista
  podeMover: Signal<boolean>;                        // perm sale.oportunidade.mover
  podeCriar: Signal<boolean>;                        // perm sale.oportunidade.criar
  loading: Signal<boolean>;
  error: Signal<AppError | null>;
};
// eventos UI: onFiltroChange(filtro), onMoverEstagio(id, destino), onAbrir(id), onCriar(payload)
```

## feature-opportunity

```typescript
type StageHistoryItemVm = {
  id: string; deEstagio: EstagioPipeline | null; paraEstagio: EstagioPipeline;
  atorNome: string | null; ocorridoEm: string;
};
type OpportunityDetailVm = {
  id: string; titulo: string; leadId: string | null;
  estagio: EstagioPipeline; estado: EstadoOportunidade;
  valorEstimado: Money; responsavelNome: string | null; probabilidade: number;
  motivoPerda: string | null;
};
type OpportunityDetailVM = {
  oportunidade: Signal<OpportunityDetailVm | null>;
  historico: Signal<StageHistoryItemVm[]>;          // append-only, newest-first
  podeFechar: Signal<boolean>;                       // estado ∉ {GANHA,PERDIDA} && perm sale.oportunidade.fechar
  saving: Signal<boolean>;
  naoEncontrada: Signal<boolean>;                    // 404 sale.oportunidade.nao-encontrada
  error: Signal<AppError | null>;
};
// eventos UI: onGanhar(), onPerder(motivo), onAbrirLead(leadId)
```

## feature-offer

```typescript
type OfferRowVm = {
  id: string; nome: string; sku: string | null;
  preco: Money; versao: number; ativo: boolean; vigenteDe: string | null; vigenteAte: string | null;
};
type OfferListVM = {
  ofertas: Signal<OfferRowVm[]>;
  filtro: Signal<{ q?: string; ativo?: boolean }>;
  podeCriar: Signal<boolean>;                        // perm sale.oferta.criar
  loading: Signal<boolean>;
  error: Signal<AppError | null>;
};
type OfferDetailVM = {
  oferta: Signal<OfferRowVm | null>;
  versoes: Signal<OfferRowVm[]>;                     // versões anteriores (imutáveis)
  editavel: Signal<boolean>;                          // perm sale.oferta.editar
  saving: Signal<boolean>;
  erros: Signal<{ campo: string; mensagem: string }[]>;
};
// eventos UI lista: onFiltroChange(filtro), onCriar(payload), onAbrir(id)
// eventos UI detalhe: onSalvar(patch /* gera nova versão */), onDesativar(), onCancelar()
```

## feature-purchase

```typescript
type PurchaseRowVm = {
  id: string; idExterno: string; origem: string; contatoRef: string;
  valorTotal: Money; status: StatusCompra; confirmadaEm: string;
};
type PurchaseItemVm = {
  id: string; ofertaNome: string | null; descricao: string | null;
  quantidade: number; valorUnitario: Money; valorTotal: Money;
};
type AttributionLineVm = {
  id: string; touchpoint: string; tipoTouchpoint: TipoTouchpoint;
  valorAtribuido: Money; versaoModelo: number;
};
type PurchaseListVM = {
  compras: Signal<PurchaseRowVm[]>;
  filtro: Signal<{ contato?: string; status?: StatusCompra; periodo?: { de: string; ate: string } }>;
  loading: Signal<boolean>;
  error: Signal<AppError | null>;
};
type PurchaseDetailVM = {
  compra: Signal<(PurchaseRowVm & { baseLegal: BaseLegal; nomeComprador: string | null; emailComprador: string | null; oportunidadeId: string | null }) | null>;
  itens: Signal<PurchaseItemVm[]>;
  atribuicao: Signal<AttributionLineVm[]>;          // breakdown explicável; Σ = valorTotal
  podeAjustar: Signal<boolean>;                       // perm estornar/cancelar && status CONFIRMADA
  saving: Signal<boolean>;
  naoEncontrada: Signal<boolean>;                    // 404 sale.compra.nao-encontrada
  error: Signal<AppError | null>;
};
// eventos UI lista: onFiltroChange(filtro), onAbrir(id)
// eventos UI detalhe: onEstornar(), onCancelar()
```

## feature-attribution

```typescript
type AttributionModelVm = {
  versao: number; tipo: TipoModeloAtribuicao; ativo: boolean; vigenteDe: string | null; criadoEm: string;
};
type AttributionVM = {
  modelos: Signal<AttributionModelVm[]>;             // por versao desc
  modeloAtivo: Signal<AttributionModelVm | null>;    // null → fallback LAST_TOUCH
  podeCriar: Signal<boolean>;                         // perm sale.atribuicao.criar
  podeAtivar: Signal<boolean>;                        // perm sale.atribuicao.ativar
  saving: Signal<boolean>;
  loading: Signal<boolean>;
  error: Signal<AppError | null>;
};
// eventos UI: onCriarModelo(tipo), onAtivar(versao)
```

## feature-revenue-dashboard

```typescript
type RevenueFunnelSliceVm = { origem: string; receita: Money; qtdCompras: number };
type LtvContactVm = { contatoRef: string; valorTotal: Money; numCompras: number; ultimaCompraEm: string | null };
type RevenueDashboardVM = {
  funilReceita: Signal<RevenueFunnelSliceVm[]>;      // por origem
  ltvTopContatos: Signal<LtvContactVm[]>;            // ordenado por valorTotal desc
  periodo: Signal<{ de: string; ate: string }>;
  loading: Signal<boolean>;
  error: Signal<AppError | null>;
};
// eventos UI: onPeriodoChange(periodo), onRecarregar()
```

## Derivações (computed)

- `arrastavel = estado !== 'GANHA' && estado !== 'PERDIDA' && hasPerm('sale.oportunidade.mover')`
- `podeFechar = estado !== 'GANHA' && estado !== 'PERDIDA' && hasPerm('sale.oportunidade.fechar')`
- `podeAjustar = status === 'CONFIRMADA' && (hasPerm('sale.compra.estornar') || hasPerm('sale.compra.cancelar'))`
- `coluna.somaValor` — soma de `valorEstimado` dos cards na coluna (por moeda)
- `modeloAtivo` — `null` ⇒ a UI exibe o fallback determinístico **LAST_TOUCH**
- `Σ atribuicao[].valorAtribuido === compra.valorTotal` (conservação de receita — exibida; nunca total opaco)

## Critérios de aceite (EARS)

- `THE SYSTEM SHALL derive every SALE view-model from BE responses and SHALL NOT expose raw BE entities to components.`
- `THE SYSTEM SHALL compute arrastavel as (estado not in {GANHA,PERDIDA} AND user has sale.oportunidade.mover).`
- `THE SYSTEM SHALL compute podeFechar as false WHILE the opportunity estado is GANHA or PERDIDA.`
- `WHILE no attribution model is active, THE SYSTEM SHALL present the LAST_TOUCH fallback as the effective model.`
- `THE SYSTEM SHALL present the attribution breakdown such that the sum of valorAtribuido equals the compra valorTotal.`

## Referências
- `03-domain-framing-frontend.md` · `SPEC-04-data-access.md` · BE `data-model.md` (§3) · `api-contract.md`
