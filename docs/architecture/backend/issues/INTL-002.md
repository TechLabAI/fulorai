# INTL-002 -- API Knowledge CRUD (nós de conhecimento)

## Contexto
Expor a curadoria da Base de Conhecimento via REST.

## Spec de referência
- SPEC-01, SPEC-03, `contracts/api-contract.md §2`

## Escopo
`KnowledgeController` + DTOs records: criar nó manual, indexar, listar/buscar, editar, arquivar.
Validação de payload; `ProblemDetail`.

## Resultado esperado
`/api/v1/knowledge/**` operacional (lógica de indexação plugada em P4).

## Critérios de aceite
- [ ] `POST /knowledge/nos` cria nó `RASCUNHO` v1
- [ ] `GET /knowledge/nos` lista paginado (q/tag/status)
- [ ] `PUT` incrementa versão; `DELETE` arquiva (sem hard-delete)
- [ ] Erros em RFC 7807

## Dependências
- INTL-001 (precede)

## Estimativa
M

## Prioridade
P1
