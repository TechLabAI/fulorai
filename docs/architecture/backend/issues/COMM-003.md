# COMM-003 -- Template CRUD API (criar/ler/listar/editar/ativar/arquivar)

## Contexto
Superfície REST de templates com DTO records e ProblemDetail; estados RASCUNHO→ATIVO→ARQUIVADO.

## Spec de referencia
- SPEC-01-api-surface
- SPEC-02-message-dispatch-lifecycle

## Escopo
- `TemplateController`: `POST /api/v1/templates`, `GET /{id}`, `GET /` (filtros), `PATCH /{id}`, `POST /{id}/ativar`, `POST /{id}/arquivar`.
- `TemplateService` (`@Transactional`): criar (RASCUNHO), editar (bump versão + valida placeholders), ativar, arquivar.
- DTO records request/response; `@RestControllerAdvice` → ProblemDetail (`comm.template.*`).
- Validações: canal/tipo no enum; nome obrigatório; e-mail exige assunto; placeholder não declarado → 422.

## Resultado esperado
CRUD de template funcional; só template `ATIVO` é despachável (validado em COMM-005).

## Criterios de aceite
- [ ] `POST /templates` cria em RASCUNHO e retorna 201 + Location.
- [ ] `POST /{id}/ativar` move RASCUNHO→ATIVO.
- [ ] corpo com placeholder não declarado → 422 `comm.template.variavel-nao-declarada`.
- [ ] EMAIL sem assunto → 422 `comm.template.assunto-obrigatorio`.

## Dependencias
- COMM-002 (precede)

## Estimativa
M

## Prioridade
P1
