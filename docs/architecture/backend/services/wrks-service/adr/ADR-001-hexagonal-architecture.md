# ADR-001 — Arquitetura hexagonal (Ports & Adapters) em WRKS

**Status:** accepted

## Contexto

O monorepo Journey OS impõe arquitetura hexagonal a todos os microserviços de negócio, com
regras ArchUnit bloqueantes (RULE-01..09). WRKS, sendo a fundação de identidade, precisa de
domínio testável e independente de framework (regras de RBAC, anti-escalonamento, política de
sessão) e de fronteiras claras com infra volátil (Keycloak, Redis, Kafka, Elastic).

## Decisão

Adotar o layout hexagonal canônico (`services-catalog.md` §3) com base de pacote
`com.journeyos.wrks`:

- `domain/` — POJOs/records + domain services, **zero** Spring/JPA (RULE-01/02).
- `application/` — use cases (`@Service`, `@Transactional` exclusivo aqui — RULE-03) + ports `in`/`out`.
- `api/` — controllers + DTO records + `@RestControllerAdvice` (ProblemDetail RFC 7807); não depende de `infrastructure` (RULE-04).
- `infrastructure/` — adapters (persistence, clients Feign, messaging, cache, security); não depende de `api` (RULE-05); `@FeignClient` só aqui (RULE-06).

`architectureCheck` (ArchUnit) é bloqueante antes de commit.

## Alternativas consideradas

- **Camadas tradicionais (controller→service→repository)**: mais simples, mas acopla domínio a JPA/Spring e dificulta testar regras de RBAC isoladamente. Rejeitada (viola padrão do monorepo).
- **Domínio anêmico + lógica em serviços de aplicação**: perde as invariantes no domínio (anti-escalonamento, versão de acesso). Rejeitada.

## Consequências

**Positivas:** regras de acesso testáveis sem Spring; troca de adapter (ex.: Redis→outro cache, Keycloak→outro IdP) sem tocar domínio; conformidade automática via ArchUnit.

**Negativas:** mais classes/ports (boilerplate); curva de aprendizado para portas in/out.

## Referências

- `docs/architecture/backend/standards/hexagonal-patterns.md`
- ADR global: `docs/architecture/backend/adr/ADR-001-hexagonal-architecture.md`
