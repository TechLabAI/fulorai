# COMM-004 -- Roteamento: RegraRoteamento CRUD + resolução de canal/template

## Contexto
Regras priorizadas que resolvem canal preferido + fallback e template a partir de condições.

## Spec de referencia
- SPEC-03-channel-routing
- SPEC-01-api-surface

## Escopo
- `RoteamentoController`: `POST /api/v1/routing-rules`, `GET /` (ordenado por prioridade), `GET /{id}`, `PATCH /{id}`.
- `RoteamentoService` (`@Transactional`): CRUD de `regra_roteamento`.
- `ResolucaoRoteamentoService` (domain): avalia regras ativas por prioridade ascendente; casa `condicoes`; resolve preferido; tenta `canais_fallback` quando o lead não tem endereço do preferido.
- Falha explícita (sem canal) → 422 `comm.roteamento.sem-canal`.

## Resultado esperado
Dado um lead/contexto, o roteamento devolve deterministicamente canal + template (ou falha explícita).

## Criterios de aceite
- [ ] Regra de menor `prioridade` avaliada primeiro.
- [ ] Sem endereço do preferido → usa `canais_fallback` em ordem.
- [ ] Nenhum canal resolvível → 422 `comm.roteamento.sem-canal`.

## Dependencias
- COMM-003 (precede)

## Estimativa
M

## Prioridade
P2
