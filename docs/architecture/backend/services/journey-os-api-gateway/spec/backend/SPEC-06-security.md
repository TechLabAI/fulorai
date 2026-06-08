# SPEC-06 — Security — GWY

> Acceptance criteria em EARS. ADRs: ADR-003 (auth filter), ADR-004 (tenant), ADR-005 (rate-limit).

## Objetivo

Definir a segurança de borda do gateway: validação de JWT, prevenção de spoofing de tenant,
CORS, cabeçalhos de segurança e tratamento de rotas públicas.

## Escopo

**In:** validação de JWT (assinatura+claims), allowlist pública, anti-spoofing de headers, CORS,
security headers, propagação de identidade.
**Out:** emissão/renovação de tokens (WRKS), autorização fina de negócio (serviços de destino),
terminação TLS (ALB).

## 1. Validação de JWT (Spring Security reactive)

**Acceptance criteria (EARS):**
- IF uma requisição a rota não-pública não tiver `Authorization: Bearer`, THEN THE SYSTEM SHALL responder `401`.
- IF a assinatura do JWT for inválida, THEN THE SYSTEM SHALL responder `401`.
- IF `exp` estiver no passado, THEN THE SYSTEM SHALL responder `401`.
- IF `iss` ≠ `${GWY_JWT_ISSUER}` ou `aud` ≠ `${GWY_JWT_AUDIENCE}`, THEN THE SYSTEM SHALL responder `401`.
- IF o JWT for válido mas faltar o claim `empresaId`, THEN THE SYSTEM SHALL responder `403`.
- THE SYSTEM SHALL validar a assinatura usando JWKS do WRKS (chaves em cache, refresh periódico).

## 2. Anti-spoofing de tenant/identidade

**Acceptance criteria (EARS):**
- THE SYSTEM SHALL remover `X-Empresa-Id`, `X-Tenant-Schema` e `X-Principal-Id` recebidos do cliente antes de qualquer processamento.
- WHEN uma requisição autenticada é encaminhada, THE SYSTEM SHALL definir `X-Empresa-Id` **exclusivamente** a partir do claim `empresaId`.
- THE SYSTEM SHALL derivar `X-Principal-Id` do claim `sub`.

## 3. Rotas públicas (allowlist)

| Rota | Justificativa |
|---|---|
| `/auth/login`, `/auth/refresh` | Pré-autenticação (emissão de token no WRKS). |
| `/actuator/health`, `/actuator/info` | Sondas de plataforma. |
| `/webhooks/**` | Validação por assinatura no serviço de destino. |

**Acceptance criteria (EARS):**
- WHERE a rota estiver na allowlist, THE SYSTEM SHALL encaminhar sem exigir JWT.
- WHILE em rota pública, THE SYSTEM SHALL ainda aplicar rate-limit por IP.

## 4. CORS

**Acceptance criteria (EARS):**
- THE SYSTEM SHALL responder preflight `OPTIONS` na borda conforme `${GWY_CORS_ALLOWED_ORIGINS}`.
- IF a `Origin` não estiver na allowlist, THEN THE SYSTEM SHALL omitir os headers CORS de permissão.
- THE SYSTEM SHALL centralizar a política CORS no gateway (serviços downstream não reimplementam CORS).

## 5. Security headers

**Acceptance criteria (EARS):**
- THE SYSTEM SHALL adicionar `X-Content-Type-Options: nosniff` às respostas.
- WHERE em produção (TLS à frente), THE SYSTEM SHALL adicionar `Strict-Transport-Security`.
- THE SYSTEM SHALL não vazar headers internos de topologia (ex.: nomes de instância) ao cliente.

## 6. Segredos

**Acceptance criteria (EARS):**
- THE SYSTEM SHALL ler toda configuração sensível via `${VAR}` (nenhum segredo hardcoded).

## Casos de borda

- Rotação de chave do WRKS: aceitar múltiplos `kid` ativos; refresh sob `kid` desconhecido (1x).
- JWT válido para `empresa` inexistente: o gateway propaga; a autorização final é do serviço.

## Critérios de aceite (resumo)

- 401/403 corretos por classe de falha; headers de identidade sempre derivados do claim.
