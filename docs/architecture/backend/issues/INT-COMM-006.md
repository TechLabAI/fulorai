# INT-COMM-006 -- ASST AssetQueryClient + Elastic communication-events projection

## Contexto
Duas integrações de leitura/projeção: consumir assets publicados do ASST como fonte de template e
projetar o ciclo de vida de entrega no índice Elastic `communication-events` (fact).

## Spec de referencia
- hub-integration.md §1
- integration-contracts.md §2
- SPEC-10-integrations

## Escopo
- `AssetQueryClient` `@FeignClient(name="asst-service")` → `GET /api/v1/assets/{id}/published` (impl `AssetQueryPort`); só versões publicadas; ASST fora → corpo embutido/cache (best-effort).
- `CommSearchAdapter` (impl `CommSearchPort`): indexa cada `evento_entrega` em `communication-events` (direct-java-client), filtrado por `empresaId`; best-effort, não bloqueia disparo.
- Reconciliação do índice a partir de `evento_entrega` (fonte da verdade no PostgreSQL).

## Resultado esperado
Templates podem referenciar assets publicados; analytics de entrega disponível no Elastic.

## Criterios de aceite
- [ ] `AssetQueryClient` retorna só versões publicadas; ASST fora não derruba CRUD/disparo.
- [ ] Evento de entrega indexado em `communication-events` (best-effort).
- [ ] Elastic fora → disparo/callback seguem; índice reconciliado depois.

## Dependencias
- COMM-009 (AssetQuery relaciona)
- COMM-014 (projeção de eventos)

## Estimativa
M

## Prioridade
P4
