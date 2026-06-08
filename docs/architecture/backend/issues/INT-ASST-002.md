# INT-ASST-002 -- WRKS AccessDecision (Feign) + validação JWKS

## Contexto
Integração de autorização: `asst-service` valida JWT contra JWKS de WRKS e resolve permissões
`asst.*` via AccessDecision.

## Spec de referencia
- hub-integration.md
- SPEC-06-security

## Escopo
- `AccessEvaluateClient` `@FeignClient(name="wrks-service")` → `POST /api/v1/iam/access/evaluate`.
- Validação de JWT contra `WRKS_JWKS_URI`.
- Cache de AccessDecision; invalidação por `modelo.acesso.alterado`.
- Resilience4j (timeout/circuit breaker); fallback p/ cache válido.

## Resultado esperado
Autorização consistente; WRKS indisponível com cache válido → serve do cache.

## Criterios de aceite
- [ ] AccessDecision resolvido e cacheado por (usuario, empresa).
- [ ] JWT inválido → 401; permissão ausente → 403.
- [ ] WRKS down com cache válido → autorização servida do cache.

## Dependencias
- WRKS (existente); ASST-012

## Estimativa
M

## Prioridade
P5
