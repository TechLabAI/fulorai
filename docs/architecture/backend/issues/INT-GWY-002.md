# INT-GWY-002 -- Integração WRKS JWKS (JwtVerifier adapter)

## Contexto
Adapter que obtém a(s) chave(s) pública(s) do WRKS (JWKS) e valida assinaturas de JWT na borda,
com cache em memória e refresh sob `kid` desconhecido (tolerância a rotação de chave).

## Spec de referencia
- contracts/integration-contracts.md (§2)
- SPEC-06-security (§1)
- adr/ADR-003-auth-filter

## Escopo
- `infrastructure/security/JwksJwtVerifier` implementando `JwtVerifierPort`/`TokenKeyProviderPort`.
- Cache de chaves + refresh periódico; suporte a múltiplos `kid` ativos.
- Config `${GWY_JWT_JWKS_URI}`, `${GWY_JWT_ISSUER}`, `${GWY_JWT_AUDIENCE}`.

## Resultado esperado
Validação de JWT performática e resiliente a rotação de chave.

## Criterios de aceite
- [ ] Assinatura validada com chave do JWKS (cache em memória).
- [ ] `kid` desconhecido dispara um refresh do JWKS antes de rejeitar.
- [ ] JWKS indisponível → continua validando com a última chave em cache + alarme.
- [ ] Teste com WireMock simulando o JWKS do WRKS.

## Dependencias
- GWY-006 (ports)

## Estimativa
M

## Prioridade
P5
