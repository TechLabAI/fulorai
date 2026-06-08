# ADR-001 — Arquitetura hexagonal (Ports & Adapters) em COMM

**Status:** accepted

## Contexto

O monorepo Journey OS impõe arquitetura hexagonal a todos os microserviços de negócio, com
regras ArchUnit bloqueantes (RULE-01..09). COMM concentra regras de domínio relevantes —
máquina de estados de entrega, resolução de roteamento, idempotência de disparo, render de
template — que precisam ser testáveis isoladamente, além de fronteiras com infra muito volátil
(múltiplos provedores de canal, TechLab AI, Elasticsearch, Kafka, PostgreSQL).

## Decisão

Adotar o layout hexagonal canônico (`services-catalog.md` §3) com base de pacote
`com.journeyos.comm`:

- `domain/` — POJOs/records + domain services (resolução de roteamento, transição de entrega, render de template), **zero** Spring/JPA (RULE-01/02). O domínio conhece apenas `canal` — nunca um SDK de provedor.
- `application/` — use cases (`@Service`, `@Transactional` exclusivo aqui — RULE-03) + ports `in`/`out` (incluindo `CanalEnvioPort`, `ComposicaoIaPort`, `AssetQueryPort`).
- `api/` — controllers + DTO records + `@RestControllerAdvice` (ProblemDetail RFC 7807); não depende de `infrastructure` (RULE-04).
- `infrastructure/` — adapters (persistence JPA, clients Feign WRKS/ASST + TechLab AI, **channels** com um adapter por canal, messaging Kafka/outbox, search Elastic, security); não depende de `api` (RULE-05); `@FeignClient` só aqui (RULE-06).

`architectureCheck` (ArchUnit) é bloqueante antes de commit.

## Alternativas consideradas

- **Camadas tradicionais (controller→service→repository):** mais simples, mas acopla a máquina de entrega, o roteamento e a abstração de provedor a JPA/Spring/SDKs, dificultando testar as invariantes. Rejeitada (viola padrão do monorepo).
- **Domínio anêmico:** perde as invariantes de idempotência/roteamento/transição no domínio. Rejeitada.

## Consequências

**Positivas:** regras de roteamento/entrega testáveis sem Spring; troca de provedor/canal (novo adapter sob `CanalEnvioPort`) sem tocar domínio; conformidade automática via ArchUnit.

**Negativas:** mais classes/ports (boilerplate); curva de aprendizado para portas in/out.

## Referências

- `docs/architecture/backend/standards/hexagonal-patterns.md`
- `adr/ADR-005-channel-adapter-pattern.md` (o port `CanalEnvioPort` materializa o princípio aqui)
- ADR global: `docs/architecture/backend/adr/ADR-001-hexagonal-architecture.md`
