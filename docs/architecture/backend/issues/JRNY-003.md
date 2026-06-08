# JRNY-003 -- API Journey Builder (CRUD jornada + estágios + publicar/arquivar/nova-versão)

## Contexto
Superfície REST de definição de jornada (`/api/v1/journeys/**`). Controllers + DTO records +
`@RestControllerAdvice` (ProblemDetail RFC 7807). `JornadaService`/`EstagioService` orquestram a
máquina de estados de publicação (RULE-03/04).

## Spec de referencia
- SPEC-01-api-surface
- SPEC-03-journey-builder

## Escopo
- `JourneyController`: `POST /` (cria RASCUNHO v1), `GET /{id}`, `GET /` (page), `PATCH /{id}`,
  `POST /{id}/publicar`, `POST /{id}/arquivar`, `POST /{id}/nova-versao`.
- `StageController` (`/{id}/estagios`): `POST`, `PATCH /{estagioId}`, `GET`.
- DTOs: `JornadaResponse`, `JornadaResumo`, `EstagioResponse`, requests correspondentes.
- `@RestControllerAdvice` mapeando os `error.code` de `api-contract.md §5` (422/404/409/401/403).
- `EstagioService.create` valida `tipoEstagio` ∈ enum, `ordem` única, jornada em RASCUNHO.

## Resultado esperado
Journey Builder operável via HTTP: criar jornada, adicionar estágios, publicar (RASCUNHO→PUBLICADA),
arquivar, derivar nova versão de uma PUBLICADA.

## Criterios de aceite
- [ ] `POST /` cria jornada em `RASCUNHO`/`versao=1` + `Location`.
- [ ] `POST /{id}/publicar` sem estágio → 422 `jrny.jornada.sem-estagio`; emite `jornada.publicada` quando válido.
- [ ] `PATCH` em jornada não-RASCUNHO → 409 `jrny.jornada.transicao-invalida`.
- [ ] `POST /{id}/nova-versao` cria cópia RASCUNHO `versao+1` sem mutar a publicada nem inscrições ativas.
- [ ] Controller nunca retorna `@Entity` (sempre DTO record).

## Dependencias
- JRNY-002 (precede)

## Estimativa
L

## Prioridade
P1
