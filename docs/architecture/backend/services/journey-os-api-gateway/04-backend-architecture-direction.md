# 04 — Backend Architecture Direction — GWY (API Gateway)

> Serviço: `journey-os-api-gateway` · Pacote: `com.journeyos.gwy` · Tipo: **infra (gateway)**

## 1. Stack

- **Java 21**, **Spring Boot 3.5.0**.
- **Spring Cloud Gateway** sobre **WebFlux (reativo)** — ⚠️ **não** usa Spring MVC/servlet.
- **Spring Cloud Netflix Eureka Client** — descoberta de serviços (REG).
- **Spring Data Redis Reactive** — backing store do `RequestRateLimiter`.
- **Spring Security (reactive)** — validação de JWT na borda (resource server / filtro custom).
- **Gradle 8.x (Kotlin DSL)**; Micrometer + Actuator para observabilidade.
- **Sem JPA / sem PostgreSQL** neste serviço (ver ADR-004 e 05-persistence-model).

> Nota de versão: o projeto fixa Spring Boot **3.5.0**; alinhar a versão do Spring Cloud (train
> compatível, ex.: 2024.x) no `build.gradle.kts` durante o scaffold.

## 2. Service Boundary

**Single service**, processo único e stateless. Não há decomposição interna em subserviços. O
escopo é estritamente edge; qualquer necessidade de agregação/BFF futura será um serviço
separado, não o gateway.

## 3. Package Organization

Base: `com.journeyos.gwy`. Layout hexagonal adaptado ao edge reativo:

```
com.journeyos.gwy/
├── api/
│   └── exception/        # ErrorWebExceptionHandler → ProblemDetail (RFC 7807)
├── application/
│   ├── service/          # AuthenticateRequest, ResolveTenant, RateLimitDecision (políticas)
│   └── port/
│       ├── in/           # casos de uso de borda
│       └── out/           # JwtVerifierPort, TokenKeyProviderPort, RateLimiterPort
├── domain/
│   └── model/            # JwtClaims, TenantContext, RateLimitKey, RoutePolicy, EdgeDecision (POJOs)
└── infrastructure/
    ├── config/           # RouteLocator, GatewayConfig, CorsConfig, RedisConfig, DomainServiceConfig
    ├── filter/           # GlobalFilter: Correlation, Auth, TenantPropagation, (KeyResolver rate-limit)
    ├── security/         # validação de JWT (adapter de JwtVerifierPort), JWKS/chave pública WRKS
    └── ratelimit/        # adapter Redis de RateLimiterPort, KeyResolver
```

> Observação: como não há `@RestController` de negócio, `api/` contém apenas o handler de erro de
> borda. Os `GlobalFilter`/config do Spring Cloud Gateway vivem em `infrastructure` (são detalhes
> de framework), mantendo `domain` e `application` livres de Spring (ADR-001).

## 4. Hub Service Dependencies

- **REG (Eureka):** obrigatório — registro do próprio gateway e descoberta de alvos `lb://`.
- **WRKS:** dependência de **confiança** (não Feign): fornece a chave pública/JWKS para validar
  JWT. O gateway não chama endpoints de negócio do WRKS no caminho quente.
- **Demais serviços (LEAD/JRNY/ASST/COMM/SALE/INTL):** apenas alvos de rota; sem acoplamento de
  código (sem Feign client gerado para eles).

## 5. External Integrations

- **Redis** (AWS ElastiCache) — rate-limit distribuído.
- **ALB/Ingress AWS** — à frente do gateway (TLS, L7 externo).
- Integrações externas de negócio (Hotmart/Meta/ActiveCampaign) **transitam** pelo gateway como
  tráfego, mas suas regras pertencem aos serviços de destino (ex.: COMM/SALE/INTL).

## 6. Async vs Sync Decisions

- **Tudo síncrono e reativo** no caminho da requisição (request/response HTTP não-bloqueante).
- **Sem mensageria** (Kafka não é usado pelo gateway).
- I/O para Redis e Eureka é não-bloqueante (stack reativa); validação de JWT preferencialmente
  com chave pública em memória (sem round-trip por requisição), atualizada periodicamente.
