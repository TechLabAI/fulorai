# 03 — Initial Domain Framing — SALE (Sales & Revenue)

> Rascunho de linguagem ubíqua, agregados e eventos. Refinado em `/be-architect-specs` (contracts/data-model).

## 1. Ubiquitous Language

| Termo (pt-BR) | Definição |
|---|---|
| **Oportunidade** (`oportunidade`) | Negócio em andamento (deal) vinculado a um lead/contato, movendo por estágios até ganho/perda. Agregado raiz do CRM. |
| **Estágio** (`estagio`) | Etapa configurável do pipeline (ex.: `NOVA` → `CONTATO` → `PROPOSTA` → `GANHA`/`PERDIDA`). |
| **Responsável** | Usuário (SDR/closer) dono da oportunidade; resolve `data_scope` de visibilidade. |
| **Oferta** (`oferta`) | Item vendável (produto/serviço) com preço, moeda e vigência; versionado. Agregado de catálogo. |
| **Compra** (`compra`) | Pedido **confirmado** por um sistema externo; reconhece receita. Agregado raiz de receita. |
| **Item de compra** (`item_compra`) | Linha de uma compra: oferta + quantidade + valor. |
| **Id externo** (`id_externo`) | Identificador do pedido no checkout/gateway (chave de idempotência da compra). |
| **Receita reconhecida** | Valor de uma compra confirmada, contabilizado uma única vez. |
| **Touchpoint** | Ponto de contato que pode receber crédito de atribuição (origem do lead, jornada, campanha). |
| **Modelo de atribuição** (`modelo_atribuicao`) | Regra versionada de como distribuir a receita entre touchpoints (`last`/`first`/`linear`-touch). |
| **Atribuição** (`atribuicao`) | Distribuição da receita de uma compra entre touchpoints segundo o modelo ativo. |
| **Campanha** (`campanha`) | Iniciativa de origem/promoção à qual receita pode ser atribuída (índice `campaign-events`). |
| **LTV** (`ltv`) | Lifetime Value: valor vitalício de um contato = soma das compras confirmadas + breakdown. |

## 2. Aggregates and Entities (rascunho inicial)

- **Oportunidade** (agregado raiz — CRM)
  - `Oportunidade` (id, empresa_id implícito por schema, lead_id, estagio, valor_estimado, probabilidade, responsavel_id, estado, motivo_perda, criado_em)
  - `HistoricoEstagio` (N: transições de estágio com timestamp e ator) — trilha do funil
- **Oferta** (agregado de catálogo, versionado)
  - `Oferta` (id, nome, sku, preco, moeda, versao, ativo, vigente_de, vigente_ate)
- **Compra** (agregado raiz — receita)
  - `Compra` (id, id_externo, origem, contato_ref, oportunidade_id?, valor_total, moeda, status, base_legal, confirmada_em)
  - `ItemCompra` (N: compra_id, oferta_id, quantidade, valor_unitario, valor_total)
- **Atribuicao** (agregado de receita)
  - `ModeloAtribuicao` (id, tipo, versao, ativo, vigente_de) — config versionada
  - `Atribuicao` (compra_id, touchpoint, tipo_touchpoint, valor_atribuido, versao_modelo, calculado_em) — breakdown
- **Ltv** (agregado de leitura materializado)
  - `Ltv` (contato_ref, valor_total, num_compras, primeira_compra_em, ultima_compra_em, atualizado_em)

## 3. Domain Events (inicial)

**Produzidos** (Kafka / AWS MSK):

| Evento | Quando | Principais consumidores |
|---|---|---|
| `journey-os.oportunidade.criada` | Oportunidade aberta (via lead qualificado ou API) | INTL (analytics), JRNY |
| `journey-os.oportunidade.estagio.alterado` | Transição de estágio do pipeline | INTL (funil), COMM (nutrição por estágio) |
| `journey-os.oportunidade.ganha` | Oportunidade marcada como ganha | INTL, COMM, WRKS (auditoria) |
| `journey-os.oportunidade.perdida` | Oportunidade marcada como perdida (com motivo) | INTL (analytics de perda) |
| `journey-os.compra.confirmada` | Pedido confirmado, receita reconhecida (**âncora**) | INTL (`revenue-events`), WRKS (auditoria), COMM (pós-venda) |
| `journey-os.receita.atribuida` | Receita distribuída entre touchpoints | INTL (ROI por origem/campanha) |
| `journey-os.ltv.atualizado` | LTV de um contato recalculado | INTL, LEAD (sinal de valor — pós-MVP) |

**Consumidos:**

| Evento | Origem | Reação |
|---|---|---|
| `journey-os.lead.qualificado` | LEAD | Cria/atualiza `oportunidade` no pipeline |
| `journey-os.lead.score.atualizado` | LEAD | Atualiza prioridade/valor estimado da oportunidade |
| `journey-os.empresa.provisionada` | WRKS | Seed de pipeline/estágios e ofertas default no novo `emp_<slug>` |
| `journey-os.modelo.acesso.alterado` | WRKS | Invalida cache de `AccessDecision` |

*(Pós-MVP: consumir `journey-os.routing.*` de JRNY p/ definir o responsável e sinais de COMM como touchpoints de atribuição.)*

## 4. State Transitions (alto nível)

**Estado da Oportunidade:**

```
NOVA ──▶ EM_ANDAMENTO ──(fecha)──▶ GANHA
  │            │                     
  │            └──(fecha)──▶ PERDIDA (com motivo)
  └────────────── DESCARTADA ◀──────────────┘
```

**Estado da Compra:**

```
CONFIRMADA ──(estorno)──▶ ESTORNADA
     │
     └──(cancelamento)──▶ CANCELADA
```

- `GANHA` normalmente precede uma `Compra` confirmada, mas a compra pode existir sem oportunidade (venda direta).
- `ESTORNADA`/`CANCELADA` ajustam a receita reconhecida e disparam recálculo de LTV; o histórico nunca é apagado.

## 5. Invariants

1. Uma compra é **única por `empresa` + (`id_externo` + `origem`)** (idempotência garante não duplicação de receita).
2. A `receita reconhecida` de uma `compra` é a soma dos `item_compra`; nunca recalculada por fonte externa após confirmada (salvo estorno/cancelamento rastreável).
3. Toda `Atribuicao` referencia um `modelo_atribuicao` existente e registra a `versao_modelo` que a produziu (auditoria/explicabilidade).
4. A soma das parcelas atribuídas de uma compra é **igual** à sua receita reconhecida (conservação de receita na atribuição).
5. O `Ltv` de um contato é função **determinística** das suas compras confirmadas (mesmo conjunto → mesmo LTV).
6. Toda `compra` tem `base_legal` definida (LGPD) antes do processamento.
7. Uma `Oportunidade` só transita para `GANHA`/`PERDIDA` uma vez (fechamento é terminal, salvo reabertura explícita).
8. Toda escrita ocorre no schema `emp_<slug>` do contexto corrente — nunca cross-empresa.

---

## Referências

- `02-architecture-blueprint.md` · `05-persistence-model.md`
- ADR-005 (Atribuição de receita / idempotência) · ADR-003 (messaging) · ADR-004 (multi-tenancy)
- Specs detalhados: `/be-architect-specs SALE` → `contracts/data-model.md`, `events/event-catalog.md`
