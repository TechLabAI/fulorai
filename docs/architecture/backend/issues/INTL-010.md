# INTL-010 -- Elastic adapter (SearchPort/IndexPort) + rastreabilidade + DLQ

## Contexto
Implementar a integração com Elasticsearch via `elastic-client-lib` e o contrato de dados (D-269).

## Spec de referência
- SPEC-03, SPEC-10, `contracts/hub-integration.md §5`, `integrations/elastic-data-contract.md`

## Escopo
Adapters `IntlSearchPort` (recuperação RAG + analítica, filtro `empresa`) e `IntlIndexPort`
(projeção `ai-copilot-events`/`knowledge-nodes` com bloco de rastreabilidade de 8 campos; doc-id
determinístico; roteamento DLQ `journey-os_dlq`). `TraceabilityValidator` (domain POJO).

## Resultado esperado
Projeção válida indexa; inválida vai à DLQ; toda leitura filtra `empresa`.

## Critérios de aceite
- [ ] Todo doc projetado carrega os 8 campos + `empresa`; violação → DLQ
- [ ] Doc-id determinístico (idempotência)
- [ ] Recuperação/analítica sempre com filtro `empresa`
- [ ] INTL não escreve facts de outros módulos

## Dependências
- INTL-001 (precede); INT-INTL-003 (contrato)

## Estimativa
L

## Prioridade
P4
