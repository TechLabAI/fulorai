# Plano -- GWY (API Gateway)

> Serviço: `journey-os-api-gateway` · Pacote: `com.journeyos.gwy` · Tipo: **infra (gateway)** · Porta 8080
> 12 issues funcionais + 4 de integração. Sem persistência (P3) e sem BDD-domínio (P8).

## Status das prioridades
- P1 -- pendente
- P2 -- pendente
- P4 -- pendente
- P5 -- pendente
- P6 -- pendente
- P7 -- pendente

## 0. Leitura executiva

### Papel do serviço (de 01-architectural-vision.md)
Edge único do Journey OS: única porta de entrada HTTP pública. Concentra roteamento dinâmico,
autenticação de borda (validação de JWT), resolução/propagação de tenant (`empresa`),
rate-limiting e CORS, mantendo os serviços de negócio focados no domínio.

### MVP scope (de 01)
Spring Cloud Gateway reativo; rotas `lb://` via Eureka; filtro global de JWT; propagação de
`X-Empresa-Id`/`X-Correlation-Id`/`X-Principal-Id`; rate-limit distribuído (Redis); CORS;
observabilidade de borda.

### Diagnóstico inicial (gaps de 06)
SPOF (mitigado por réplicas stateless); rotação de chave do WRKS; política de falha do Redis
(fail-open default, confirmar em ops); compatibilidade Spring Cloud × Spring Boot 3.5.0;
formato exato dos claims do JWT (depende do WRKS).

## 1. Estratégia geral

### Objetivo macro
Entregar um edge reativo seguro e observável, sem lógica de negócio, com roteamento dinâmico e
contexto de tenant à prova de spoofing.

### Ordem das prioridades

| P | Título | Motivo |
|---|---|---|
| P1 | Bootstrap + roteamento | Base executável; rotas `lb://` são a função primária. |
| P2 | Pipeline de borda | Correlação, erros RFC 7807, anti-spoofing e domínio/políticas habilitam segurança. |
| P4 | Roteamento downstream + resiliência | Timeouts/idempotência antes de empilhar segurança pesada. |
| P5 | Segurança | Auth JWT, tenant, allowlist, CORS — núcleo de valor do gateway. |
| P6 | Rate-limiting | Proteção contra abuso, distribuída via Redis. |
| P7 | Observabilidade | Métricas/health/tracing fecham o serviço para produção. |

## 2. Plano por prioridade

### Prioridade 1 -- Bootstrap + roteamento
Status: pendente
#### Objetivo / Resultado esperado
Gateway reativo sobe, registra no Eureka, expõe Actuator e roteia via `lb://`.
#### Issues vinculadas
- GWY-001, GWY-002, INT-GWY-001
#### Specs cobertas
- SPEC-01, SPEC-07
#### Sequência de execução
- Fase 1: GWY-001 (app + Eureka + Actuator) · Fase 2: INT-GWY-001 (discovery) · Fase 3: GWY-002 (rotas)
#### Critérios de aceite
- `/actuator/gateway/routes` lista rotas; encaminhamento `lb://` funcional; 404/503 corretos.
#### Riscos
- Versão Spring Cloud × Boot 3.5.0 (smoke test de boot).
#### Instrução para implementador
Não hardcodar host:porta; toda config via `${VAR}`; rodar `architectureCheck`.

### Prioridade 2 -- Pipeline de borda
Status: pendente
#### Objetivo / Resultado esperado
Filtros de correlação, anti-spoofing e tratamento de erro, mais o domínio/políticas hexagonais.
#### Issues vinculadas
- GWY-003, GWY-004, GWY-005, GWY-006
#### Specs cobertas
- SPEC-01, SPEC-06, SPEC-07
#### Sequência de execução
- Fase 1: GWY-006 (domínio+ports) · Fase 2: GWY-004, GWY-005 (filtros) · Fase 3: GWY-003 (erro)
#### Critérios de aceite
- `X-Correlation-Id` sempre presente; headers de identidade do cliente removidos; erros RFC 7807.
- `architectureCheck` PASS (RULE-01/02 no domínio).
#### Riscos
- Ordem dos filtros incorreta quebra anti-spoofing — fixar via `getOrder()`.
#### Instrução para implementador
`domain.*` sem Spring/JPA; políticas como `@Bean` em `DomainServiceConfig`.

### Prioridade 4 -- Roteamento downstream + resiliência
Status: pendente
#### Objetivo / Resultado esperado
Timeouts por rota; sem retry em métodos mutantes; 503/504 corretos.
#### Issues vinculadas
- INT-GWY-004
#### Specs cobertas
- SPEC-05, integration-contracts
#### Sequência de execução
- Fase 1: timeouts/retry policy · Fase 2: mapeamento de erros 503/504.
#### Critérios de aceite
- Timeout → 504; sem instância → 503; POST/PUT/PATCH/DELETE não reenviados.
#### Riscos
- Retry indevido causando efeito duplicado — restringir a idempotentes.
#### Instrução para implementador
Propagar `Idempotency-Key` intacto; circuit-breaker fica como pós-MVP.

### Prioridade 5 -- Segurança
Status: pendente
#### Objetivo / Resultado esperado
JWT validado na borda; tenant propagado; allowlist pública; CORS centralizado.
#### Issues vinculadas
- GWY-007, GWY-008, GWY-009, GWY-010, INT-GWY-002
#### Specs cobertas
- SPEC-06, integration-contracts
#### Sequência de execução
- Fase 1: INT-GWY-002 (JWKS) · Fase 2: GWY-007 (auth) · Fase 3: GWY-008/009 (tenant/allowlist) · Fase 4: GWY-010 (CORS)
#### Critérios de aceite
- 401/403 por classe de falha; `X-Empresa-Id` só do claim; rotas públicas sem JWT; CORS na borda.
#### Riscos
- Rotação de chave do WRKS — tolerar múltiplos `kid` + refresh sob `kid` desconhecido.
#### Instrução para implementador
JWKS em cache; WireMock nos testes; nunca derivar tenant de header do cliente.

### Prioridade 6 -- Rate-limiting distribuído
Status: pendente
#### Objetivo / Resultado esperado
Limite agregado entre réplicas via Redis; 429 com `Retry-After`.
#### Issues vinculadas
- GWY-011, INT-GWY-003
#### Specs cobertas
- SPEC-05, integration-contracts
#### Sequência de execução
- Fase 1: INT-GWY-003 (adapter Redis) · Fase 2: GWY-011 (filtro + KeyResolver).
#### Critérios de aceite
- Limite agregado com ≥2 instâncias; chave por tenant/IP; fail-open + métrica se Redis cair.
#### Riscos
- Indisponibilidade do Redis — política de falha explícita e observável.
#### Instrução para implementador
Testcontainers para Redis; parâmetros por rota via `${VAR}`.

### Prioridade 7 -- Observabilidade + health
Status: pendente
#### Objetivo / Resultado esperado
Métricas por rota/status, contadores de auth/rate-limit, readiness sensível a Eureka/Redis, tracing.
#### Issues vinculadas
- GWY-012
#### Specs cobertas
- SPEC-07
#### Sequência de execução
- Fase 1: métricas + prometheus · Fase 2: readiness · Fase 3: tracing W3C.
#### Critérios de aceite
- `/actuator/prometheus` com métricas por `routeId`; readiness `OUT_OF_SERVICE` pré-registro; logs sem PII.
#### Riscos
- Cardinalidade de métricas — limitar labels a `routeId`/status/motivo.
#### Instrução para implementador
Não logar payloads/PII; sempre incluir `correlationId`.

## 3. Dependências externas
- REG (Eureka) — descoberta; WRKS — JWKS; Redis (ElastiCache) — rate-limit; ALB/Ingress — TLS.

## 4. Restrições arquiteturais
- ArchUnit RULE-01..09 (CLAUDE.md). RULE-02/08 trivial/N-A (sem JPA).
- Camadas hexagonais: filtros/config/adapters em `infrastructure`; políticas em `application`; modelos puros em `domain`.
- Sem `@Transactional` (sem banco). Sem chamadas diretas a provedores de IA (N/A aqui).
- Não depende de `journey-os-migrations`.

## 5. Referências
- `docs/architecture/backend/services/journey-os-api-gateway/01..06-*.md`
- `docs/architecture/backend/services/journey-os-api-gateway/adr/ADR-001..005`
- `docs/architecture/backend/services/journey-os-api-gateway/spec/backend/SPEC-01,05,06,07`
- `docs/architecture/backend/services/journey-os-api-gateway/contracts/{api-contract,integration-contracts}.md`
