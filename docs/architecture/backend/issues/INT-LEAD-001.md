# INT-LEAD-001 -- Eureka discovery registration

## Contexto
Registrar o `lead-service` no Service Registry (REG/Eureka) para descoberta pelo Feign client de WRKS.

## Spec de referencia
- SPEC-10-integrations
- hub-integration.md

## Escopo
- Dependência `eureka-client`; `EUREKA_SERVICE_URL` via `${VAR}`.
- `spring.application.name=lead-service`; health do Eureka.

## Resultado esperado
`lead-service` aparece no painel do Eureka e é descoberto por outros serviços.

## Criterios de aceite
- [ ] Serviço registra no Eureka ao subir.
- [ ] Nome `lead-service` resolvível por Feign.

## Dependencias
- (nenhuma — precede LEAD-001)

## Estimativa
S

## Prioridade
P1
