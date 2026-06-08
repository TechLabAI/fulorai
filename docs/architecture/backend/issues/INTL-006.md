# INTL-006 -- Fundamentação + degradação (status da resposta)

## Contexto
Garantir as invariantes de fundamentação (INV-2) e degradação graciosa do copiloto.

## Spec de referência
- SPEC-02, ADR-005

## Escopo
`RankingFundamentacaoService` (domain POJO) + lógica de status: `RESPONDIDA` (citação ⊆ evidência),
`NAO_FUNDAMENTADA` (evidência insuficiente ou sem citação válida), `DEGRADADA` (TechLab AI
indisponível — recuperação-apenas, `modelo=null`/`custo=0`). Descartar citação fora da evidência.

## Resultado esperado
Resposta nunca apresenta fato alucinado como fundamentado; falha de IA não vira `5xx`.

## Critérios de aceite
- [ ] Evidência insuficiente → `NAO_FUNDAMENTADA` (sem fato confirmado)
- [ ] TechLab AI off → `DEGRADADA` com `200` (evidência sem síntese)
- [ ] Citação fora da evidência recuperada é descartada
- [ ] Evento de degradada registra `modelo=null`, `custoTokens=0`

## Dependências
- INTL-005 (precede)

## Estimativa
M

## Prioridade
P2
