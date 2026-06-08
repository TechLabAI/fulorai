# INT-COMM-002 -- WRKS AccessEvaluateClient (Feign + Resilience4j) + JWKS

## Contexto
Integração com WRKS para validação de JWT (JWKS) e resolução de `AccessDecision` (`comm.*`).

## Spec de referencia
- hub-integration.md §1
- SPEC-06-security

## Escopo
- `AccessEvaluateClient` `@FeignClient(name="wrks-service")` → `POST /api/v1/iam/access/evaluate`.
- Validação de JWT contra `WRKS_JWKS_URI`; cache de `AccessDecision` invalidado por `modelo.acesso.alterado`.
- Resilience4j (timeout/CB); fallback para decisão em cache válida quando WRKS fora.

## Resultado esperado
Autorização `comm.*` resolvida via WRKS, resiliente a indisponibilidade transitória.

## Criterios de aceite
- [ ] JWT validado contra JWKS; sem permissão → 403.
- [ ] WRKS fora + cache válido → serve do cache até TTL.

## Dependencias
- COMM-001 (precede)

## Estimativa
M

## Prioridade
P5
