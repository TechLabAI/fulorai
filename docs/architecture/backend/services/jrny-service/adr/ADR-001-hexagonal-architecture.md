# ADR-001 — Arquitetura hexagonal (Ports & Adapters) em JRNY

**Status:** accepted

## Contexto

O monorepo Journey OS impõe arquitetura hexagonal a todos os microserviços de negócio, com
regras ArchUnit bloqueantes (RULE-01..09). JRNY concentra regras de domínio críticas — o
Routing Engine (avaliação determinística de regras versionadas), a máquina de estados de
publicação de jornada, as invariantes de inscrição e a imutabilidade do decision log — que
precisam ser testáveis isoladamente, além de fronteiras com infra volátil (TechLab AI,
Elasticsearch, Kafka, PostgreSQL, Feign WRKS/ASST).

## Decisão

Adotar o layout hexagonal canônico (`services-catalog.md` §3) com base de pacote
`com.journeyos.jrny`:

- `domain/` — POJOs/records + domain services (`MotorRoteamento`, transição de estado, avaliador de condição), **zero** Spring/JPA (RULE-01/02).
- `application/` — use cases (`@Service`, `@Transactional` exclusivo aqui — RULE-03) + ports `in`/`out`.
- `api/` — controllers + DTO records + `@RestControllerAdvice` (ProblemDetail RFC 7807); não depende de `infrastructure` (RULE-04).
- `infrastructure/` — adapters (persistence JPA, clients Feign WRKS/ASST + cliente TechLab AI, messaging Kafka, search Elastic, security); não depende de `api` (RULE-05); `@FeignClient` só aqui (RULE-06).

`architectureCheck` (ArchUnit) é bloqueante antes de commit.

## Alternativas consideradas

- **Camadas tradicionais (controller→service→repository):** mais simples, mas acopla o Routing Engine e as invariantes de jornada/decisão a JPA/Spring, dificultando testar as regras determinísticas isoladamente. Rejeitada (viola padrão do monorepo).
- **Domínio anêmico:** perde as invariantes de roteamento/versionamento/decisão no domínio (vazam para serviços/JPA). Rejeitada.

## Consequências

**Positivas:** Routing Engine e máquina de estados testáveis sem Spring; troca de adapter (Elastic, cliente TechLab AI, Feign ASST) sem tocar domínio; conformidade automática via ArchUnit.

**Negativas:** mais classes/ports (boilerplate); curva de aprendizado para portas in/out.

## Referências

- `docs/architecture/backend/standards/hexagonal-patterns.md`
- ADR global: `docs/architecture/backend/adr/ADR-001-hexagonal-architecture.md`
