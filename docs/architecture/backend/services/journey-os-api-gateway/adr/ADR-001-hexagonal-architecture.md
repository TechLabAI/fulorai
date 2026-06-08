# ADR-001 — Hexagonal architecture no edge reativo

- **Status:** accepted

## Contexto

O monorepo Journey OS impõe arquitetura hexagonal (Ports & Adapters) e regras ArchUnit
(RULE-01..09) a todos os microserviços. O GWY é um caso atípico: é um **gateway reativo**
(Spring Cloud Gateway / WebFlux), cuja "lógica" são filtros e configuração de rotas — detalhes
muito acoplados ao framework. Surge a dúvida: aplicar hexagonal mesmo sem domínio de negócio?

## Decisão

Aplicar hexagonal de forma **adaptada ao edge**:

- `domain/model` contém value objects puros (`JwtClaims`, `TenantContext`, `RateLimitKey`,
  `RoutePolicy`, `EdgeDecision`) — zero Spring, zero `jakarta.persistence`.
- `application/service` modela as **políticas de borda** como casos de uso testáveis
  (`AuthenticateRequest`, `ResolveTenant`, `RateLimitDecision`) atrás de ports `in`/`out`.
- `infrastructure/` concentra todo o acoplamento ao Spring Cloud Gateway: `GlobalFilter`s,
  `RouteLocator`, adaptadores de Eureka, Redis e validação de JWT.
- Mantêm-se as regras hexagonais aplicáveis; RULE-02 e RULE-08 são trivial/N-A por não haver JPA.

## Alternativas consideradas

1. **Camada única "framework-first"** (tudo em config/filtros): simples, mas deixa as decisões de
   auth/tenant/rate-limit não-testáveis isoladamente e diverge do padrão do monorepo. Rejeitada.
2. **Hexagonal completo com persistência:** desnecessário — o gateway é stateless. Rejeitada.

## Consequências

**Positivas:** políticas de borda testáveis em isolamento; aderência ao padrão do monorepo;
ArchUnit aplicável; troca de mecanismo (ex.: validador de JWT) sem tocar no domínio.

**Negativas:** alguma cerimônia (ports/adapters) para lógica fina; risco de over-engineering se
as políticas forem triviais — mitigado mantendo `domain`/`application` enxutos.

## Referências

- `docs/architecture/backend/standards/hexagonal-patterns.md`
- CLAUDE.md — RULE-01..09
