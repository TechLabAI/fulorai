# INT-JRNY-001 -- Service discovery (Eureka/REG)

## Contexto
Registro do `jrny-service` no Service Registry (REG/Eureka) para descoberta pelos demais serviços
e roteamento pelo GWY.

## Spec de referencia
- integration-contracts.md
- SPEC-10-integrations

## Escopo
- `eureka-client` configurado (`EUREKA_SERVICE_URL`), `spring.application.name=jrny-service`.
- Health/instance metadata para o Eureka; heartbeat.
- Confirmar descoberta por WRKS/ASST (Feign por nome lógico).

## Resultado esperado
`jrny-service` aparece no painel Eureka e é resolvível por nome lógico.

## Criterios de aceite
- [ ] Serviço registra no Eureka ao subir.
- [ ] Resolvível como `jrny-service` por clientes Feign.
- [ ] `EUREKA_SERVICE_URL` via `${VAR}` (sem hardcode).

## Dependencias
- (nenhuma — precede JRNY-001)

## Estimativa
S

## Prioridade
P1
