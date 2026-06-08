# INT-GWY-001 -- Integração Eureka (descoberta lb://)

## Contexto
Integrar o gateway ao REG (Eureka) para registro próprio e descoberta dinâmica dos serviços de
negócio, habilitando o roteamento `lb://<service-id>`.

## Spec de referencia
- contracts/integration-contracts.md (§1)
- SPEC-01-api-surface

## Escopo
- Eureka client configurado (`${GWY_EUREKA_SERVICE_URL}`).
- `DiscoveryClient` RouteLocator habilitado.
- Cache local de registry para resiliência.

## Resultado esperado
Gateway descobre instâncias via Eureka; rotas `lb://` resolvem.

## Criterios de aceite
- [ ] Gateway registra-se no Eureka como `journey-os-api-gateway`.
- [ ] `lb://wrks-service` (e demais) resolve para instância saudável.
- [ ] Eureka indisponível temporariamente → usa cache local.
- [ ] `service-id` sem instância → 503 nas rotas correspondentes.

## Dependencias
- GWY-001 (precede)

## Estimativa
S

## Prioridade
P1
