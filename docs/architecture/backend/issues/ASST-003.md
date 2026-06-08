# ASST-003 -- API surface: CRUD de asset + DTOs + ProblemDetail

## Contexto
Superfície REST `/api/v1/assets` para CRUD/catálogo do asset, com DTO records e tratamento de
erros RFC 7807.

## Spec de referencia
- SPEC-01-api-surface
- SPEC-06-security

## Escopo
- `AssetController`: `POST /`, `GET /{id}`, `GET /` (lista/filtros), `PATCH /{id}`, `POST /{id}/arquivar`.
- DTO records (`api/dto`): `CriarAssetRequest`, `AssetResponse`, `AssetResumo`, `AtualizarAssetRequest`.
- `ApiExceptionHandler` (`@RestControllerAdvice`) → ProblemDetail (`shared/contratos/error-model.md`).
- Validação de `tipoAsset`/`titulo`; mapeamento de erros (`asst.asset.*`).

## Resultado esperado
CRUD do asset funcional (sem versão/aprovação ainda), retornando DTO (nunca entity).

## Criterios de aceite
- [ ] `POST /` cria asset em RASCUNHO → 201 + Location.
- [ ] `tipoAsset` inválido → 422 `asst.asset.tipo-invalido`; título vazio → 422 `asst.asset.titulo-obrigatorio`.
- [ ] Controller não retorna `@Entity` (RULE — sempre DTO).
- [ ] `:asst-service:architectureCheck` PASS (RULE-04 — api não depende de infrastructure).

## Dependencias
- ASST-002 (precede)

## Estimativa
M

## Prioridade
P1
