# 06 — Risks, Gaps & Assumptions — GWY (API Gateway)

> Serviço: `journey-os-api-gateway` · Pacote: `com.journeyos.gwy` · Tipo: **infra (gateway)**

## 1. Riscos

| ID | Risco | Impacto | Mitigação |
|---|---|---|---|
| R-1 | **Single point of failure** — todo tráfego passa pelo gateway. | Alto | Múltiplas instâncias atrás do ALB; gateway stateless; health checks. |
| R-2 | Latência de borda adiciona overhead a cada requisição. | Médio | Stack reativa; validação de JWT em memória (sem round-trip); orçamento de p99. |
| R-3 | Drift entre rotas e topologia real de serviços. | Médio | Rotas dinâmicas via Eureka (`lb://`); evitar rotas estáticas. |
| R-4 | Rotação da chave de assinatura do WRKS quebra validação de JWT. | Alto | JWKS/cache com refresh periódico; tolerância a múltiplas chaves ativas. |
| R-5 | Redis indisponível degrada rate-limiting. | Médio | Política de fallback (fail-open vs fail-closed) a decidir na spec; alarmes. |
| R-6 | Spoofing de tenant via header forjado pelo cliente. | Alto | INV-3: `X-Empresa-Id` derivado **somente** do claim; stripping de headers de entrada. |
| R-7 | Incompatibilidade de versão Spring Cloud × Spring Boot 3.5.0. | Médio | Fixar train do Spring Cloud compatível no scaffold; smoke test de boot. |

## 2. Gaps Conhecidos

- Política de **fallback do rate-limiter** quando o Redis cai (fail-open/closed) — definir na spec.
- Estratégia de **circuit-breaker por rota** (Resilience4j) — fora do MVP, avaliar pós-MVP.
- Formato exato dos **claims do JWT** (nome do claim de `empresaId`, roles) — depende do WRKS.
- Lista de **rotas públicas** (allowlist) e tratamento de **webhooks assinados** — depende de COMM/SALE.
- Cabeçalhos de segurança e política de **CORS** definitivos (origens permitidas do frontend).

## 3. Suposições a Validar

- A1: WRKS expõe chave pública/JWKS estável para validação de JWT na borda.
- A2: REG (Eureka) estará disponível antes do gateway no boot local e em produção.
- A3: TLS é terminado **antes** do gateway (ALB/Ingress); o gateway fala HTTP interno.
- A4: Redis (ElastiCache) disponível como dependência de runtime do rate-limiter.
- A5: O `empresaId` está presente no claim do JWT para toda requisição autenticada.

## 4. Dependências Críticas

| Dependência | Tipo | Necessária para |
|---|---|---|
| **REG (Eureka)** | infra | Descoberta de rotas `lb://`. |
| **WRKS** | confiança | Chave de validação do JWT. |
| **Redis** | infra | Rate-limiting distribuído. |
| **ALB/Ingress AWS** | infra externa | Terminação TLS / exposição pública. |

> Ordem de subida local: **REG** → **GWY** → serviços de negócio. (GWY **não** depende de
> `journey-os-migrations`, pois não usa banco relacional.)
