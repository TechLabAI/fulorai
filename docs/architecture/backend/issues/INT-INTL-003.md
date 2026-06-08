# INT-INTL-003 -- Integração Elasticsearch (elastic-client-lib)

## Contexto
Recuperação RAG, leitura analítica e projeções próprias passam pelo `elastic-client-lib`.

## Spec de referência
- SPEC-03, SPEC-10, `contracts/hub-integration.md §5`, `integrations/elastic-data-contract.md`

## Escopo
Adapters `IntlSearchPort`/`IntlIndexPort` sobre `SearchPort`/`IndexPort` do `elastic-client-lib`;
bloco de rastreabilidade de 8 campos; DLQ `journey-os_dlq`; filtro `empresa`; doc-id determinístico.

## Resultado esperado
Plataforma de dados governada (contrato D-269) operacional.

## Critérios de aceite
- [ ] Projeção válida indexa; inválida → DLQ
- [ ] Leitura sempre filtra `empresa`
- [ ] Idempotência por doc-id
- [ ] Sem escrita em facts de outros módulos

## Dependências
- INTL-010

## Estimativa
M

## Prioridade
P4
