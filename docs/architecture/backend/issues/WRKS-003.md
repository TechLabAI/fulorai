# WRKS-003 -- API surface /api/v1/iam/** (controllers + DTO records + ProblemDetail)

## Contexto
Superfície REST do serviço sob `/api/v1/iam/**`, DTOs como records e tratamento de erro
RFC 7807 via `IamExceptionHandler`.

## Spec de referencia
- SPEC-01-api-surface
- SPEC-06-security

## Escopo
- Controllers: `SessaoController`, `AccessController`, `EmpresaController`, `UsuarioController`,
  `PapelController`, `BusinessUnitController`, `TeamController`, `AuditoriaController`.
- DTO records (request/response) em `api/dto`; nunca retornar `@Entity`.
- `IamExceptionHandler` (@RestControllerAdvice) → `ProblemDetail` com catálogo de `error.code`
  (api-contract §error). `X-Correlation-Id` gerado/propagado.
- `empresa_id` derivado do claim JWT (nunca de body/path).

## Resultado esperado
Endpoints respondem (stubs ligados aos services nas issues seguintes); erros em `application/problem+json`.

## Criterios de aceite
- [ ] `api.*` não depende de `infrastructure.*` (RULE-04).
- [ ] Todos os erros retornam `application/problem+json` com `error.code` + `correlationId`.
- [ ] Validação de body → 422 `validation` com `error.fields`.
- [ ] OpenAPI reflete os endpoints do api-contract.

## Dependencias
- WRKS-002 (precede)

## Estimativa
M

## Prioridade
P1
