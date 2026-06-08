# INT-JRNY-002 -- AccessEvaluateClient (WRKS) + invalidação de cache por modelo.acesso.alterado

## Contexto
Autorização `jrny.*` resolvida via WRKS `AccessDecision` (Feign), com cache curto invalidado pelo
evento `journey-os.modelo.acesso.alterado`.

## Spec de referencia
- hub-integration.md
- integration-contracts.md
- SPEC-06-security

## Escopo
- `@FeignClient(name="wrks-service")` `AccessEvaluateClient` (`POST /access/evaluate`); `url_prop=journey-os.wrks.url`.
- `AccessDecisionPort` + adapter com cache curto (TTL) por (principal, empresa, permissão).
- Consumer `ModeloAcessoAlteradoConsumer` evicta as entradas afetadas.
- Resilience4j (timeout + fallback negativo seguro: nega em dúvida).
- Propagação de `correlationId`/`tenantId` nos headers.

## Resultado esperado
Decisões de acesso `jrny.*` consistentes e atualizadas em ≤ janela de cache após mudança de modelo.

## Criterios de aceite
- [ ] `AccessEvaluateClient` resolve `jrny.*` via WRKS.
- [ ] `modelo.acesso.alterado` evicta cache afetado.
- [ ] WRKS indisponível → fallback nega acesso (sem permitir por omissão).

## Dependencias
- INT-JRNY-001 (discovery)

## Estimativa
M

## Prioridade
P5
