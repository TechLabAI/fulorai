# 03 — Domain Framing (Frontend) — SALE

> Linguagem ubíqua (espelho do BE), View Models, UI Events, transições de estado e invariantes
> client-side. **Não redefinir o domínio** — referência: `_brief.md` + BE `03-initial-domain-framing.md`
> + `contracts/api-contract.md`.

## 1. Ubiquitous Language (espelho do BE)

| Termo | Significado (FE) |
|---|---|
| **Oportunidade** (`oportunidade`) | Negócio em andamento (deal) vinculado a um lead, movendo por estágios até ganho/perda. Card do Kanban. |
| **Estágio** (`estagio`) | Coluna configurável do pipeline (ex.: `NOVA` → `CONTATO` → `PROPOSTA` → `GANHA`/`PERDIDA`). |
| **Responsável** | Usuário (SDR/closer) dono da oportunidade; resolve `data_scope` de visibilidade na UI. |
| **Oferta** (`oferta`) | Item vendável (produto/serviço) com preço, moeda e vigência; **versionado** (editar = nova versão). |
| **Compra** (`compra`) | Pedido **confirmado** por sistema externo; reconhece receita. Consultável (read) + ajustável (estornar/cancelar). |
| **Item de compra** (`item_compra`) | Linha de uma compra: oferta + quantidade + valor. |
| **Id externo** (`id_externo`) | Identificador do pedido no checkout/gateway (chave de idempotência — server-to-server, não exposto na UI de criação). |
| **Touchpoint** | Ponto de contato que recebe crédito de atribuição (origem do lead, jornada, campanha). |
| **Modelo de atribuição** (`modelo_atribuicao`) | Regra **versionada** de distribuição da receita (`LAST_TOUCH`/`FIRST_TOUCH`/`LINEAR`). Apenas uma **ativa** por vez. |
| **Atribuição** (`atribuicao`) | Distribuição da receita de uma compra entre touchpoints, com a `versaoModelo` que a produziu (breakdown). |
| **Receita reconhecida** | Valor de uma compra confirmada, contabilizado uma única vez (idempotência no BE). |
| **LTV** (`ltv`) | Lifetime Value: valor vitalício de um contato = soma das compras confirmadas + breakdown. |
| **Campanha / Origem** | Iniciativa/fonte à qual a receita pode ser atribuída (apoio Elastic `campaign-events`/`revenue-events`). |

## 2. View Models (rascunho)

```ts
// Pipeline / Kanban (feature-pipeline)
type PipelineBoardVM = {
  estagios: KanbanColumnVM[];          // colunas na ordem do pipeline
};
type KanbanColumnVM = {
  estagio: string;                     // 'NOVA' | 'CONTATO' | 'PROPOSTA' | 'GANHA' | 'PERDIDA' | ...
  total: number;                       // contagem de cards
  somaValor: number;                   // soma do valor estimado na coluna
  cards: OportunidadeCardVM[];
};
type OportunidadeCardVM = {
  oportunidadeId: string;
  titulo: string;                      // lead/contato + oferta
  leadId: string;
  valorEstimado: number; moeda: 'BRL';
  responsavelId: string; responsavelNome: string;
  probabilidade: number;               // 0..100
  estagio: string;
  estado: 'NOVA' | 'EM_ANDAMENTO' | 'GANHA' | 'PERDIDA' | 'DESCARTADA';
};

// Detalhe (feature-opportunity)
type OportunidadeDetailVM = {
  oportunidadeId: string;
  lead: { leadId: string; nome?: string };
  valorEstimado: number; moeda: 'BRL'; probabilidade: number;
  responsavel: { id: string; nome: string };
  estagio: string;
  estado: 'NOVA' | 'EM_ANDAMENTO' | 'GANHA' | 'PERDIDA' | 'DESCARTADA';
  motivoPerda?: string;
  historicoEstagio: StageHistoryVM[];
  acoesDisponiveis: OportunidadeAcao[]; // derivado de estado + permissões (ganhar/perder/mover)
};
type StageHistoryVM = { de?: string; para: string; ator: string; em: string };

// Oferta (feature-offer)
type OfertaVM = {
  id: string; nome: string; sku: string;
  preco: number; moeda: 'BRL'; versao: number;
  ativo: boolean; vigenteDe: string; vigenteAte?: string;
};

// Compra (feature-purchase)
type CompraRowVM = {
  compraId: string; contatoRef: string;
  valorTotal: number; moeda: 'BRL';
  status: 'CONFIRMADA' | 'ESTORNADA' | 'CANCELADA';
  origem: string; confirmadaEm: string;
};
type CompraDetailVM = {
  compraId: string; contatoRef: string; origem: string; baseLegal: string;
  status: 'CONFIRMADA' | 'ESTORNADA' | 'CANCELADA';
  valorTotal: number; moeda: 'BRL';
  itens: ItemCompraVM[];
  atribuicao: AtribuicaoBreakdownVM;   // breakdown sempre presente (explicável)
};
type ItemCompraVM = { ofertaId: string; ofertaNome: string; quantidade: number; valorUnitario: number; valorTotal: number };

// Atribuição (feature-attribution)
type ModeloAtribuicaoVM = { versao: number; tipo: 'LAST_TOUCH'|'FIRST_TOUCH'|'LINEAR'; ativo: boolean; vigenteDe: string };
type AtribuicaoBreakdownVM = {
  versaoModelo: number; tipoModelo: 'LAST_TOUCH'|'FIRST_TOUCH'|'LINEAR';
  receitaReconhecida: number;
  parcelas: { touchpoint: string; tipoTouchpoint: string; valorAtribuido: number }[]; // soma == receita
};

// Dashboard de receita (feature-revenue-dashboard)
type RevenueFunnelVM = {
  periodo: { de: string; ate: string };
  porOrigem: { origem: string; receita: number; numCompras: number }[];
};
type LtvRowVM = { contatoRef: string; valorTotal: number; numCompras: number; primeiraCompraEm: string; ultimaCompraEm: string };
```

## 3. UI Events

- `PipelineFiltrado(responsavel?, estado?)` → recarrega o board.
- `EstagioMovido(oportunidadeId, deEstagio, paraEstagio)` → `PATCH /oportunidades/{id}/estagio`
  (**optimistic**: move o card antes da resposta; **rollback** ao erro — ver ADR-005).
- `OportunidadeSelecionada(id)` → navega ao detalhe; carrega perfil + histórico.
- `OportunidadeGanha(id)` → `POST /oportunidades/{id}/ganhar`.
- `OportunidadePerdida(id, motivo)` → `POST /oportunidades/{id}/perder` (motivo **obrigatório**).
- `OfertaSalva(payload)` (cria nova versão) / `OfertaDesativada(id)` → governança de catálogo.
- `CompraEstornada(id)` / `CompraCancelada(id)` → ajuste de receita (confirmação obrigatória).
- `VersaoModeloCriada(payload)` / `VersaoModeloAtivada(versao)` → governança de atribuição.
- `BreakdownSolicitado(compraId)` → `GET /compras/{id}/atribuicao`.

## 4. State Transitions (UI)

```
Pipeline / Detalhe (carregamento):  idle → loading → success | empty | error
Mover estágio (drag):               idle → moving(optimistic) → success | rollback(409 ja-fechada) | error
Ganhar/Perder:                      ready → submitting → fechada | blocked(422 motivo-obrigatorio) | error(409 ja-fechada)
Oferta (edição):                    view → editing → saving → nova-versão | invalid(422 preco-invalido)
Compra (ajuste):                    confirmada → adjusting → estornada|cancelada | error
Ativação de modelo:                 inativa → activating → ativa (anterior desativada, afetadas re-atribuídas) | error(404 modelo-nao-encontrado)
```

## 5. Invariants (client-side)

- O **breakdown de atribuição** de uma compra é **sempre** renderizado com a `versaoModelo` + a soma das
  parcelas; o total atribuído **nunca** aparece sozinho (explicabilidade — ver `ADR-005`).
- A soma das parcelas atribuídas exibidas deve **bater** com a receita reconhecida (conservação de
  receita); divergência é tratada como erro de dados, não silenciada.
- **Perder** uma oportunidade exige `motivo` não-vazio antes do `POST` (espelha `422
  sale.oportunidade.motivo-obrigatorio`).
- Oportunidade já `GANHA`/`PERDIDA` **não** pode mover estágio nem fechar de novo na UI; o drag é
  rejeitado e revertido (espelha `409 sale.oportunidade.ja-fechada`).
- **Editar oferta** nunca muta a versão anterior — sempre cria uma nova versão; preço negativo é
  bloqueado client-side e confirmado pelo BE (`422 sale.oferta.preco-invalido`).
- O FE **não** dispara `POST /compras` (ingestão server-to-server); a UI só consulta + estorna/cancela.
- Estornar/cancelar **não** remove a compra da lista — muda o `status` (histórico append-only).
- Valor monetário sempre exibido com **moeda** + formatação por locale; estágio/origem não dependem só de cor.
- Troca de empresa limpa todo o board/seleção/listas em tela antes de carregar dados da nova empresa.

---

## Referências

- BE: `docs/architecture/backend/services/sale-service/03-initial-domain-framing.md` + `contracts/api-contract.md`
- `05-state-and-data-flow.md` (data flow detalhado) · `ADR-005` (renderização do Kanban + optimistic move)
- `docs/architecture/frontend/standards/access-layer-contracts.md`
