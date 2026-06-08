---
service: journey-os-api-gateway
module: GWY
package: com.journeyos.gwy
type: gateway
isInfra: true
reactive: true
port: 8080
status: specs
specSet: reduced
dependsOn:
  - journey-os-service-registry   # Eureka (discovery)
  - wrks-service                  # JWT issuer (JWKS / public key)
  - redis                         # distributed rate-limiter backing store
produces: []                      # no domain events
consumes: []                      # no domain events
techlabAi: none
---

# Spec — GWY (API Gateway) · `journey-os-api-gateway`

> Edge único do Journey OS (Spring Cloud Gateway / WebFlux reativo). Módulo de
> **infraestrutura**: roteamento, autenticação de borda, resolução/propagação de tenant,
> rate-limiting e CORS. **Sem domínio de negócio, sem persistência relacional, sem eventos.**
>
> Visão e decisões: ver `01..06-*.md` e `adr/ADR-001..005`.

## Mapa de specs (conjunto reduzido — gateway)

| Artefato | Conteúdo | EARS |
|---|---|---|
| `contracts/api-contract.md` | Superfície de borda: rotas lógicas, headers, erros RFC 7807, auth | sim |
| `contracts/integration-contracts.md` | Eureka (REG), WRKS (JWKS), Redis, serviços downstream | sim |
| `events/event-catalog.md` | (vazio — sem eventos de domínio) | — |
| `spec/backend/SPEC-01-api-surface.md` | Pipeline de filtros + tabela de rotas + predicados | sim |
| `spec/backend/SPEC-05-idempotency-concurrency.md` | Rate-limit distribuído, encaminhamento idempotente | sim |
| `spec/backend/SPEC-06-security.md` | Validação de JWT, anti-spoofing de tenant, CORS, headers | sim |
| `spec/backend/SPEC-07-observability-health.md` | Actuator, métricas, tracing, correlação | sim |
| `diagrams/c4-{context,container,component}.puml` | Diagramas C4 | — |
| `setup-local.md` | Porta + variáveis de ambiente + ordem de subida | — |

## SPECs não aplicáveis (gateway)

| SPEC | Motivo |
|---|---|
| SPEC-02 core orchestration | A "orquestração" do gateway é o pipeline de filtros (coberto em SPEC-01). |
| SPEC-03 sub-feature | Sem sub-feature de domínio. |
| SPEC-04 data model + migrations | Sem banco relacional; não depende de `journey-os-migrations`. |
| SPEC-08 BDD scenarios | Sem domínio de negócio; testes de borda via integração (ver SPEC-01/06). |
| SPEC-09 messaging | Kafka não é usado pelo gateway. |
| SPEC-10 integrations | Coberto por `contracts/integration-contracts.md` (Eureka/Redis/WRKS). |
| techlab-ai-integration | Gateway não consome TechLab AI. |

## Referências

- `docs/architecture/backend/standards/ears-notation.md`
- `docs/architecture/backend/standards/hexagonal-patterns.md`
- `docs/architecture/backend/standards/platform-patterns.md`
