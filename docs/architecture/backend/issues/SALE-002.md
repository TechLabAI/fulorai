# SALE-002 — API CRUD de Oportunidade

## Contexto
Expor o recurso `/api/v1/oportunidades` (criar, listar, obter) com DTOs `record` e ProblemDetail.

## Spec de referencia
- SPEC-01, SPEC-02, `contracts/api-contract.md` §1

## Escopo
Controller + DTOs (request/response) + porta in `OportunidadeUseCase` + `OportunidadeService`
(create/findById/listAll). Sem regra de fechamento ainda (SALE-005).

## Resultado esperado
`POST/GET /oportunidades` funcionando com validação e erros RFC 7807.

## Criterios de aceite
- [ ] `POST /oportunidades` cria em estado NOVA e retorna 201
- [ ] `GET /oportunidades` e `GET /oportunidades/{id}` paginado/por id
- [ ] erros como `application/problem+json` com `error.code` estável
- [ ] DTO record, nenhuma `@Entity` retornada

## Dependencias
- SALE-001 (precede)

## Estimativa
M

## Prioridade
P1
