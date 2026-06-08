# ADR-005 — Atribuição de receita: determinística, explicável + idempotência de compra

**Status:** proposed

## Contexto

O valor central do SALE para growth (Marina) é responder **"de onde veio cada real?"**. Isso exige
ligar a receita de uma `compra` aos *touchpoints* (origem do lead, jornada, campanha) de forma
**explicável** e **estável**. Ao mesmo tempo, a fonte de compra (checkout/gateway) pode reenviar o
mesmo pedido (webhook duplicado), e contar receita em dobro é inaceitável. É a decisão crítica do
domínio SALE. O Journey OS **não** usa IA para isto no MVP — atribuição é determinística.

## Decisão

1. **Idempotência da compra**: `compra` é única por (`id_externo` + `origem`) no schema do tenant
   (UNIQUE). Reprocessar o mesmo pedido retorna a compra existente — **nenhuma** receita nova.
   Chave de idempotência = `id_externo` + `origem`.
2. **Conservação de receita**: a receita reconhecida de uma compra é a soma dos `item_compra`; a
   soma das parcelas atribuídas (`atribuicao.valor_atribuido`) é **igual** à receita reconhecida
   (invariantes 2 e 4 de `03`).
3. **Modelo de atribuição versionado**: o cálculo usa `modelo_atribuicao` **versionado** e ativo.
   Default **`last-touch`** (todo o crédito ao último touchpoint); `first-touch` e `linear`
   (crédito distribuído igualmente) configuráveis. Toda `atribuicao` registra a `versao_modelo`.
4. **Explicável**: persiste o **breakdown** (`atribuicao` por touchpoint + tipo) — nunca só o total.
   Mudar o modelo (Marina) gera nova versão e re-atribui as compras afetadas (lote pequeno síncrono
   no MVP), emitindo `receita.atribuida` de forma rastreável.
5. **Determinístico**: o mesmo conjunto (compra + touchpoints + versão de modelo) → a mesma
   atribuição; o **LTV** é função determinística das compras confirmadas do contato.
6. **SALE registra, não cobra**: a compra entra **já confirmada** por sistema externo; SALE não
   executa pagamento — a confiança vem da idempotência + status reconhecido.

## Alternativas consideradas

- **Atribuição data-driven/probabilística (ML)**: maior potencial, mas opaca, exige dados/treino e
  MLOps; viola "receita rastreável, nunca caixa-preta". Rejeitada no MVP (mantida como evolução via
  capacidade `analytics` da TechLab AI).
- **Idempotência só por chave primária interna**: não protege contra reenvio do mesmo pedido externo.
  Rejeitada em favor de UNIQUE(`id_externo`,`origem`).
- **Receita mutável editável após confirmação**: simples, mas quebra auditoria financeira. Rejeitada
  em favor de estado explícito (`ESTORNADA`/`CANCELADA`) com delta append-only.

## Consequências

**Positivas:** ROI por origem/campanha auditável; receita nunca duplicada; calibração do modelo por
config (sem deploy); resiliência a webhooks duplicados.

**Negativas:** manter modelos versionados e a re-atribuição coerente exige disciplina; a qualidade da
atribuição depende da completude dos touchpoints (R1 em `06`), que melhora ao integrar JRNY/COMM
(pós-MVP). Por isso esta ADR está **proposed** até a validação nas specs e a definição da fonte de
compra/`contato_ref`.

## Referências

- `03-initial-domain-framing.md` (invariantes 1–5) · `01-architectural-vision.md` (princípios 1–3)
- `05-persistence-model.md` (idempotência/imutabilidade da receita)
- ADR-001 (domain service puro) · ADR-003 (eventos `compra.confirmada`/`receita.atribuida`)
