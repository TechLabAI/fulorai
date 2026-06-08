# SPEC-05 — Idempotency & Concurrency — GWY

> Acceptance criteria em EARS. ADR relacionado: ADR-005 (rate-limiting).

## Objetivo

Definir o comportamento do gateway sob concorrência (rate-limiting distribuído consistente entre
réplicas) e suas garantias quanto a idempotência de encaminhamento.

## Escopo

**In:** consistência do rate-limiter entre instâncias; preservação de semântica idempotente das
requisições; política de retry de borda.
**Out:** idempotência de operações de negócio (responsabilidade dos serviços downstream).

## Rate-limiting distribuído

O gateway roda com **N réplicas** atrás do ALB. O limite deve ser global por chave, não por
instância — daí o backing store Redis (token bucket do `RequestRateLimiter`).

**Acceptance criteria (EARS):**
- THE SYSTEM SHALL manter o contador de rate-limit no Redis, compartilhado entre todas as instâncias do gateway.
- WHEN duas requisições da mesma `RateLimitKey` chegam a instâncias diferentes, THE SYSTEM SHALL aplicar o limite de forma agregada (não por instância).
- WHEN o limite é excedido, THE SYSTEM SHALL responder `429` com `Retry-After` e **não** encaminhar.
- WHERE a rota for pública/anônima, THE SYSTEM SHALL usar a chave por IP.
- WHERE a requisição for autenticada, THE SYSTEM SHALL usar a chave por `empresaId` (e/ou `sub`).

## Idempotência de encaminhamento

O gateway é um proxy stateless; **não** introduz efeitos colaterais próprios.

**Acceptance criteria (EARS):**
- THE SYSTEM SHALL encaminhar cada requisição **no máximo uma vez** ao downstream no caminho feliz (sem retry implícito em métodos não-idempotentes).
- IF ocorrer falha de conexão em `GET`/`HEAD`/`OPTIONS` (idempotentes), THEN THE SYSTEM SHALL poder reencaminhar conforme política de retry configurada.
- IF a requisição for `POST`/`PATCH`/`PUT`/`DELETE`, THEN THE SYSTEM SHALL **não** reencaminhar automaticamente em falha (evitar efeito duplicado), respondendo `504`/`503`.
- WHERE o cliente enviar `Idempotency-Key`, THE SYSTEM SHALL propagá-lo intacto ao downstream (o gateway não o interpreta).

## Concorrência interna

- Stack reativa (WebFlux/Netty): processamento não-bloqueante; sem estado mutável compartilhado
  por requisição além do contexto reativo.

**Acceptance criteria (EARS):**
- THE SYSTEM SHALL processar requisições concorrentes sem compartilhar estado mutável de requisição entre fluxos.
- THE SYSTEM SHALL propagar `X-Correlation-Id` por requisição via contexto reativo (sem vazamento entre fluxos).

## Casos de borda

- Redis indisponível: aplicar política de falha (default fail-open) — ver `integration-contracts.md`.
- Relógio/janela do token bucket: definido pelo `replenishRate`/`burstCapacity` por rota.

## Critérios de aceite (resumo)

- Limite agregado verificável com ≥2 instâncias do gateway apontando ao mesmo Redis.
- Nenhum reenvio automático de método mutante.
