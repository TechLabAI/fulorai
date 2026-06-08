# SPEC-01 — API Surface

> EARS guide: `docs/architecture/backend/standards/ears-notation.md`. Contract: `contracts/api-contract.md`.

## Objetivo

Definir a superfície REST de `asst-service` sob `/api/v1/assets/**`, seus status codes, erros
ProblemDetail e autorização por permissões `asst.*`.

## Escopo

- **In:** CRUD de asset, versões, Asset Studio, workflow de aprovação, busca, leitura de versão publicada.
- **Out:** UI; entrega/render de conteúdo (COMM); upload de binário (referência por URL apenas).

## Decisões técnicas

- Hexagonal: controllers em `api/controller`, DTO records em `api/dto`, erros em `api/exception` (ADR-001).
- Auth Bearer JWT (WRKS RS256); autorização via `AccessDecision` (`asst.*`).
- Tenant por claim JWT (`EmpresaContextHolder`), nunca por path/body (ADR-004).

## Implementação

- `AssetController` (`/`, `/{id}`, `/{id}/versoes`, `/{id}/published`, `/{id}/arquivar`).
- `AssetStudioController` (`/{id}/studio/compose`).
- `AssetApprovalController` (`/{id}/submit`, `/{id}/approve`, `/{id}/publish`).
- `ApiExceptionHandler` (`@RestControllerAdvice`) → ProblemDetail (`shared/contratos/error-model.md`).

## Casos de borda

- Asset inexistente / de outro tenant → 404.
- Transição de estado inválida → 409.
- Permissão ausente → 403; JWT inválido → 401.

## Critérios de aceite (EARS)

- `WHEN a caller with asst.asset.criar posts a valid asset, THE SYSTEM SHALL create it in RASCUNHO and return 201 with a Location header.`
- `THE SYSTEM SHALL return only assets belonging to the caller's tenant schema on any read.`
- `IF a path references an asset absent in the caller's tenant, THEN THE SYSTEM SHALL respond 404 error.code 'asst.asset.nao-encontrado'.`
- `IF the caller lacks the required asst.* permission, THEN THE SYSTEM SHALL respond 403 error.code 'asst.acesso.permissao-negada'.`
- `THE SYSTEM SHALL render every error as application/problem+json with type, title, status, detail, code and correlationId.`
