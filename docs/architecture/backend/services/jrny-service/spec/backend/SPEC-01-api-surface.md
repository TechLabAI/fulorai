# SPEC-01 — API Surface

> EARS guide: `docs/architecture/backend/standards/ears-notation.md`. Contract: `contracts/api-contract.md`.
> ADRs: ADR-001 (hexagonal), ADR-004 (multi-tenancy).

## Objetivo

Definir a superfície REST de `jrny-service` sob `/api/v1/journeys/**` (Journey Builder) e
`/api/v1/routing/**` (regras + consultas de roteamento), seus status codes, erros ProblemDetail
e autorização por permissões `jrny.*`.

## Escopo

- **In:** CRUD de jornada/estágio, publicação/arquivamento, nova versão; CRUD de regra de roteamento; consulta do estado de jornada do lead e do decision log.
- **Out:** execução de roteamento via HTTP (é dirigida por evento — SPEC-02); UI (FE); execução de ações de estágio (COMM/SALE).

## Decisões técnicas

- Hexagonal: controllers em `api/controller` (`JourneyController`, `RoutingRuleController`, `RoutingQueryController`), DTO records em `api/dto`, erros em `api/exception` (ADR-001).
- Auth Bearer JWT (WRKS RS256); autorização via `AccessDecision` (`jrny.*`).
- Tenant por claim JWT (`EmpresaContextHolder`), nunca por path/body (ADR-004).
- **Sem endpoint de "rotear agora":** o roteamento é assíncrono (gatilho de evento LEAD).

## Casos de borda

- Jornada/inscrição inexistente ou de outro tenant → 404.
- Publicar jornada sem estágios → 422; transição de estado inválida → 409.
- Estágio com ordem duplicada → 409; tipo de estágio inválido → 422.
- Permissão ausente → 403; JWT inválido → 401.

## Critérios de aceite (EARS)

- `WHEN a caller with jrny.jornada.criar posts a valid journey, THE SYSTEM SHALL create it in RASCUNHO at versao=1 and return 201 with a Location header.`
- `WHEN a caller with jrny.jornada.publicar publishes a RASCUNHO journey that has at least one stage, THE SYSTEM SHALL set estado=PUBLICADA and emit journey-os.jornada.publicada.`
- `IF a journey is published with no stage, THEN THE SYSTEM SHALL respond 422 error.code 'jrny.jornada.sem-estagio'.`
- `IF a stage is added with an ordem already used in the journey, THEN THE SYSTEM SHALL respond 409 error.code 'jrny.estagio.ordem-duplicada'.`
- `IF a routing rule's condicao references a field outside the documented snapshot grammar, THEN THE SYSTEM SHALL respond 422 error.code 'jrny.regra.condicao-invalida'.`
- `THE SYSTEM SHALL return only journeys, enrolments and decisions belonging to the caller's tenant schema on any read.`
- `IF a path references a journey or enrolment absent in the caller's tenant, THEN THE SYSTEM SHALL respond 404 error.code 'jrny.jornada.nao-encontrada' or 'jrny.inscricao.nao-encontrada'.`
- `IF the caller lacks the required jrny.* permission, THEN THE SYSTEM SHALL respond 403 error.code 'jrny.acesso.permissao-negada'.`
- `THE SYSTEM SHALL render every error as application/problem+json with type, title, status, detail, code and correlationId.`
