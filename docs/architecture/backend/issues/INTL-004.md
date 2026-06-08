# INTL-004 -- API Analytics (leitura cross-index)

## Contexto
Expor a leitura analítica consolidada (read-only) sobre os *facts* projetados pelos módulos.

## Spec de referência
- SPEC-01, SPEC-03, `contracts/api-contract.md §3`

## Escopo
`AnalyticsController` + DTOs: `GET /analytics/funil` e `GET /analytics/copilot`. Agregação via
`IntlSearchPort` (plugada em P4), sempre filtrando `empresa`. Nenhuma escrita.

## Resultado esperado
`/api/v1/analytics/**` retorna agregações por `empresa`.

## Critérios de aceite
- [ ] `GET /analytics/funil` agrega *facts* por período/empresa
- [ ] `GET /analytics/copilot` retorna custo/taxa de fundamentação/degradação
- [ ] Endpoint é estritamente read-only

## Dependências
- INTL-001 (precede)

## Estimativa
S

## Prioridade
P1
