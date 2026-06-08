# ADR-002 — Estratégia de roteamento (descoberta dinâmica via Eureka)

- **Status:** accepted

## Contexto

O gateway precisa encaminhar requisições para 7 serviços de negócio (WRKS, LEAD, JRNY, ASST,
COMM, SALE, INTL), cujas instâncias e endereços variam (escala horizontal, ambientes). Hardcodar
host:porta acoplaria o gateway à topologia e quebraria a cada deploy/scale.

## Decisão

Usar **descoberta dinâmica** via Eureka (REG) com URIs `lb://<service-id>` e o
`DiscoveryClient` Route Locator do Spring Cloud Gateway, complementado por rotas declaradas em
`application.yml`/`RouteLocator` quando for preciso predicado/filtro específico por serviço.

- Cada serviço se registra no Eureka com seu `spring.application.name` (service-id).
- O gateway resolve `lb://wrks-service`, `lb://lead-service`, etc., com balanceamento client-side.
- Predicados por path versionado (ex.: `/api/v1/leads/**` → `lb://lead-service`).

## Alternativas consideradas

1. **Rotas estáticas (host:porta no yaml):** simples em dev, frágil em produção; rejeitada como
   padrão (aceitável só como fallback pontual).
2. **Service mesh (Istio/Linkerd) para roteamento L7:** poderoso, mas peso operacional alto e fora
   do escopo atual; o roteamento de aplicação fica no gateway. Rejeitada para o MVP.
3. **DNS-based discovery (sem Eureka):** o projeto já adota Eureka (REG) como padrão; manter
   consistência. Rejeitada.

## Consequências

**Positivas:** rotas resilientes a mudanças de topologia; balanceamento client-side; alinhamento
com REG. **Negativas:** dependência forte do Eureka (mitigada por cache de registry no cliente e
health checks); necessidade de manter `service-id`s consistentes (ver services-catalog).

## Referências

- `docs/architecture/backend/services/journey-os-service-registry/` (REG)
- Spring Cloud Gateway — `DiscoveryClient` Route Definition Locator
