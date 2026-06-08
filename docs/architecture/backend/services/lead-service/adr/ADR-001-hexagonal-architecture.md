# ADR-001 — Hexagonal Architecture (Ports & Adapters)

**Status:** accepted

## Contexto

O `lead-service` é um microserviço de domínio do Journey OS. O monorepo impõe arquitetura
hexagonal estrita, verificada por ArchUnit bloqueante (`:lead-service:architectureCheck`).
O domínio de qualificação (cálculo do Maturity Score, motor de regras, avaliação de segmentos)
é rico em lógica de negócio e deve permanecer testável e independente de framework.

## Decisão

Adotar **Ports & Adapters** com as camadas canônicas em `com.journeyos.lead`:
`api` → `application` → `domain` ← `infrastructure`.

- `domain` (model + service) é **POJO puro**: zero Spring, zero JPA. Aqui vivem
  `MaturityScoreCalculator`, `QualificationRuleEngine`, `SegmentEvaluator`.
- `application.service` orquestra casos de uso, é o **único** lugar com `@Transactional` e
  `EmpresaContextHolder.require()`.
- `application.port.in/out` definem as fronteiras; `infrastructure` implementa os adapters
  (persistence, messaging, clients, search).
- `@FeignClient` apenas em `infrastructure.clients`; `api` não depende de `infrastructure`.

Regras RULE-01..09 valem integralmente.

## Alternativas consideradas

- **Camadas tradicionais (controller→service→repository)**: mais simples, mas acopla domínio a
  Spring/JPA e dificulta testar o motor de scoring isoladamente. Rejeitada.
- **Domain-only sem portas explícitas**: perde a inversão de dependência para TechLab AI/Elastic
  e enfraquece o ArchUnit. Rejeitada.

## Consequências

**Positivas:** motor de scoring testável sem container; trocar TechLab AI/Elastic/Kafka não toca
o domínio; consistência com os demais serviços do monorepo.

**Negativas:** mais boilerplate (portas + adapters + `DomainServiceConfig` para registrar os
domain services como `@Bean`). Aceito como custo padrão da plataforma.

## Referências

- `docs/architecture/backend/standards/hexagonal-patterns.md`
- RULE-01..09 (CLAUDE.md)
