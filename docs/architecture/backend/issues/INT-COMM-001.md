# INT-COMM-001 -- Eureka discovery (REG) + GWY edge route

## Contexto
Registro do `comm-service` no Eureka e roteamento via API Gateway.

## Spec de referencia
- hub-integration.md §4
- SPEC-07-observability-health

## Escopo
- `eureka-client` apontando para `EUREKA_SERVICE_URL`; `spring.application.name=comm-service`.
- Rotas GWY para `/api/v1/{templates,messages,routing-rules,channels}/**`; webhook via rota de edge dedicada.

## Resultado esperado
COMM descoberto por outros serviços; acessível atrás do gateway.

## Criterios de aceite
- [ ] `comm-service` aparece no Eureka.
- [ ] Requisição via GWY chega ao COMM com JWT validado.

## Dependencias
- (nenhuma)

## Estimativa
S

## Prioridade
P1
