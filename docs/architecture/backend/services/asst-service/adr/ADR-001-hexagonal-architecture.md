# ADR-001 — Arquitetura hexagonal (Ports & Adapters) em ASST

**Status:** accepted

## Contexto

O monorepo Journey OS impõe arquitetura hexagonal a todos os microserviços de negócio, com
regras ArchUnit bloqueantes (RULE-01..09). ASST concentra regras de domínio relevantes —
máquina de estados de aprovação, imutabilidade de versões, invariantes de publicação — que
precisam ser testáveis isoladamente, além de fronteiras com infra volátil (TechLab AI,
Elasticsearch, Kafka, PostgreSQL).

## Decisão

Adotar o layout hexagonal canônico (`services-catalog.md` §3) com base de pacote
`com.journeyos.asst`:

- `domain/` — POJOs/records + domain services (transição de estado, política de versão), **zero** Spring/JPA (RULE-01/02).
- `application/` — use cases (`@Service`, `@Transactional` exclusivo aqui — RULE-03) + ports `in`/`out`.
- `api/` — controllers + DTO records + `@RestControllerAdvice` (ProblemDetail RFC 7807); não depende de `infrastructure` (RULE-04).
- `infrastructure/` — adapters (persistence JPA, clients Feign WRKS + TechLab AI, messaging Kafka, search Elastic, security); não depende de `api` (RULE-05); `@FeignClient` só aqui (RULE-06).

`architectureCheck` (ArchUnit) é bloqueante antes de commit.

## Alternativas consideradas

- **Camadas tradicionais (controller→service→repository):** mais simples, mas acopla a máquina de estados e a imutabilidade de versão a JPA/Spring, dificultando testar as invariantes. Rejeitada (viola padrão do monorepo).
- **Domínio anêmico:** perde as invariantes de versionamento/aprovação no domínio. Rejeitada.

## Consequências

**Positivas:** regras de aprovação/versionamento testáveis sem Spring; troca de adapter (Elastic, provider de busca, cliente TechLab AI) sem tocar domínio; conformidade automática via ArchUnit.

**Negativas:** mais classes/ports (boilerplate); curva de aprendizado para portas in/out.

## Referências

- `docs/architecture/backend/standards/hexagonal-patterns.md`
- ADR global: `docs/architecture/backend/adr/ADR-001-hexagonal-architecture.md`
