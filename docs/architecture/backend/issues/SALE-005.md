# SALE-005 — PipelineService (máquina de estágios + ganho/perda)

## Contexto
Domain service POJO que governa a transição de estágios e o fechamento (ganha/perdida) da
oportunidade, registrando `historico_estagio`.

## Spec de referencia
- SPEC-02, `03-initial-domain-framing.md` §4

## Escopo
`PipelineService` (domain, zero Spring): mover estágio, ganhar, perder (com motivo); invariantes de
terminalidade. Endpoints `PATCH .../estagio`, `POST .../ganhar`, `POST .../perder`.

## Resultado esperado
Pipeline operável com histórico e fechamento consistente.

## Criterios de aceite
- [ ] mover estágio adiciona `historico_estagio` (append-only)
- [ ] ganhar → `estado=GANHA`; perder sem motivo → 422 `sale.oportunidade.motivo-obrigatorio`
- [ ] fechar oportunidade já fechada → 409 `sale.oportunidade.ja-fechada`
- [ ] `PipelineService` registrado em `DomainServiceConfig` (@Bean)

## Dependencias
- SALE-002 (precede)

## Estimativa
M

## Prioridade
P2
