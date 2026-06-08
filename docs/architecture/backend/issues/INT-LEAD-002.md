# INT-LEAD-002 -- WRKS AccessEvaluate Feign client + Resilience4j

## Contexto
Cliente Feign para `POST /api/v1/iam/access/evaluate` (WRKS), usado pela camada de segurança para
autorizar `lead.*`, com circuit breaker e fail-closed.

## Spec de referencia
- hub-integration.md
- integration-contracts.md
- SPEC-06-security

## Escopo
- `infrastructure.clients.AccessEvaluateClient` (`@FeignClient(name="wrks-service")`), `journey-os.wrks.url`.
- Resilience4j (timeout/circuit breaker); autorização **fail-closed** (503 sem cache).
- Mapeia `AccessDecisionResponse` para a decisão de autorização.

## Resultado esperado
Autorização `lead.*` resolvida via WRKS (com cache em INT-LEAD-004).

## Criterios de aceite
- [ ] Feign chama WRKS e mapeia `AccessDecisionResponse`.
- [ ] WRKS indisponível sem cache → fail-closed (503).
- [ ] `@FeignClient` apenas em `infrastructure.clients` (RULE-06).

## Dependencias
- INT-LEAD-001 (discovery)

## Estimativa
M

## Prioridade
P4
