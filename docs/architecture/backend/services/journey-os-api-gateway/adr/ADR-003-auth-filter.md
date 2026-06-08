# ADR-003 — Autenticação na borda via filtro global de JWT

- **Status:** accepted

## Contexto

A autenticação precisa ser consistente em toda a malha. Validar JWT em cada serviço duplica
código e risco. O WRKS é o emissor dos tokens. Decidir **onde** e **como** validar o JWT.

## Decisão

Implementar um **`GlobalFilter`** no gateway que valida o JWT **uma vez na borda**:

- Verifica assinatura usando a **chave pública / JWKS do WRKS** (preferencialmente em memória,
  com refresh periódico — sem round-trip por requisição).
- Valida claims padrão: `exp`, `iss`, `aud`, e a presença de `empresaId`.
- Em falha → `401`/`403` com ProblemDetail (RFC 7807); a requisição **não** é encaminhada.
- Rotas na **allowlist** (login, webhooks assinados, health) pulam a validação.
- O resultado (`JwtClaims`) alimenta a resolução de tenant (ADR-004) e a chave de rate-limit
  (ADR-005). Headers de identidade vindos do cliente são **removidos** antes do encaminhamento.

Defesa em profundidade: serviços sensíveis ainda podem revalidar o token (não confiar cegamente
no header), mas o gateway é a primeira e principal barreira.

## Alternativas consideradas

1. **Validação por serviço (sem gateway):** duplicação e inconsistência; rejeitada.
2. **Introspecção remota do token a cada request (opaque token):** latência e acoplamento ao
   WRKS no caminho quente; rejeitada em favor de JWT auto-contido + JWKS cacheado.
3. **Spring Security Resource Server reativo "puro":** viável; pode ser usado como base do
   adapter de validação, mas a orquestração de tenant/allowlist exige filtro custom. Combinado.

## Consequências

**Positivas:** auth centralizada e barata; serviços recebem contexto confiável; ponto único para
políticas. **Negativas:** o gateway torna-se crítico para segurança (mitigado por testes e
defesa em profundidade); dependência da disponibilidade da chave do WRKS (ver R-4).

## Referências

- WRKS — emissão de JWT / JWKS
- `docs/architecture/backend/services/journey-os-api-gateway/03-initial-domain-framing.md` (INV-2, INV-3)
