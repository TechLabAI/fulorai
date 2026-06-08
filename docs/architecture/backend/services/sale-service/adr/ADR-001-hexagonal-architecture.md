# ADR-001 — Hexagonal Architecture (Ports & Adapters)

**Status:** accepted

## Contexto

O `sale-service` é um microserviço de domínio do Journey OS. O monorepo impõe arquitetura
hexagonal estrita, verificada por ArchUnit bloqueante (`:sale-service:architectureCheck`).
O domínio de vendas (movimentação de pipeline, motor de atribuição de receita, cálculo de LTV)
é rico em lógica de negócio e regras de conservação financeira, e deve permanecer testável e
independente de framework.

## Decisão

Adotar **Ports & Adapters** com as camadas canônicas em `com.journeyos.sale`:
`api` → `application` → `domain` ← `infrastructure`.

- `domain` (model + service) é **POJO puro**: zero Spring, zero JPA. Aqui vivem
  `PipelineService`, `AttributionEngine`, `LtvCalculator`.
- `application.service` orquestra casos de uso, é o **único** lugar com `@Transactional` e
  `EmpresaContextHolder.require()`.
- `application.port.in/out` definem as fronteiras; `infrastructure` implementa os adapters
  (persistence, messaging, search, clients).
- `@FeignClient` apenas em `infrastructure.clients`; `api` não depende de `infrastructure`.

Regras RULE-01..09 valem integralmente.

## Alternativas consideradas

- **Camadas tradicionais (controller→service→repository)**: mais simples, mas acopla domínio a
  Spring/JPA e dificulta testar o motor de atribuição e a conservação de receita isoladamente. Rejeitada.
- **Domain-only sem portas explícitas**: perde a inversão de dependência para Elastic/Kafka/(futura)
  TechLab AI e enfraquece o ArchUnit. Rejeitada.

## Consequências

**Positivas:** motor de atribuição e LTV testáveis sem container; trocar Elastic/Kafka/fonte de
compra não toca o domínio; consistência com os demais serviços do monorepo.

**Negativas:** mais boilerplate (portas + adapters + `DomainServiceConfig` para registrar os
domain services como `@Bean`). Aceito como custo padrão da plataforma.

## Referências

- `docs/architecture/backend/standards/hexagonal-patterns.md`
- RULE-01..09 (CLAUDE.md)
