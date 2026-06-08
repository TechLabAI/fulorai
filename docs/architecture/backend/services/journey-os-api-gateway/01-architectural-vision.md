# 01 — Architectural Vision — GWY (API Gateway)

> Serviço: `journey-os-api-gateway` · Pacote: `com.journeyos.gwy` · Tipo: **infra (gateway)**

## 1. Intent

Prover o **edge único** do Journey OS: a única porta de entrada HTTP pública pela qual todo
tráfego (SPA, integrações externas, webhooks) acessa os microserviços de negócio. O gateway
concentra preocupações transversais de borda — roteamento dinâmico, autenticação, resolução de
tenant, rate-limiting e CORS — para que os serviços de domínio permaneçam focados em regras de
negócio e confiem em um contexto de requisição já validado e enriquecido.

## 2. Problem Statement

Em uma malha de microserviços (WRKS, LEAD, JRNY, ASST, COMM, SALE, INTL), expor cada serviço
diretamente cria duplicação de segurança (validação de JWT, CORS, rate-limit em cada serviço),
acoplamento do cliente a topologia/portas internas, e ausência de um ponto consistente para
correlação de requisições e resolução do `empresa` (tenant). Sem um gateway, o frontend
precisaria conhecer endereços de N serviços e cada serviço reimplementaria a borda de segurança.

## 3. Personas

| Persona | Tipo | Necessidade |
|---|---|---|
| **SPA Angular (`journey-os-web`)** | Consumidor primário | Um único `base-url` estável; CORS e auth consistentes; latência de borda baixa. |
| **Clientes/Integrações externas** | Consumidor primário | Endpoint público para webhooks (Hotmart, Meta Ads, ActiveCampaign) com rate-limit e auth previsíveis. |
| **Plataforma / SRE** | Operador | Configurar rotas, limites e políticas; observar tráfego de borda (métricas, tracing). |

## 4. MVP Scope (in)

1. Roteamento reativo (Spring Cloud Gateway / WebFlux) para todos os serviços de negócio.
2. Descoberta dinâmica de rotas via Eureka (REG), usando `lb://<service-id>`.
3. Filtro **global** de autenticação: validação de assinatura e claims do JWT emitido pelo WRKS.
4. Resolução e propagação de contexto de tenant: `X-Empresa-Id`, `X-Tenant-Schema`, e
   `X-Correlation-Id` (gerado se ausente) para os serviços downstream.
5. Rate-limiting distribuído por chave (tenant / usuário / IP) com `RequestRateLimiter` + Redis.
6. CORS centralizado e cabeçalhos de segurança (HSTS, X-Content-Type-Options, etc.).
7. Observabilidade de borda: Actuator (`/actuator/health`, `/actuator/gateway/routes`), métricas
   Micrometer, propagação de trace.

## 5. Out of Scope (MVP)

- Lógica de negócio ou validações de domínio.
- Composição/agregação de respostas (BFF) e transformação de payloads de negócio.
- Persistência de dados de domínio (o gateway é stateless; só usa Redis para rate-limit).
- Emissão/renovação de tokens (responsabilidade do **WRKS**).
- Terminação TLS (delegada ao ALB/Ingress da AWS).
- Cache de respostas de domínio; circuit-breaking avançado por rota (futuro, ver riscos).

## 6. Architectural Principles

- **Edge stateless:** nenhuma decisão depende de estado local persistente; estado distribuído
  (rate-limit) vive no Redis.
- **Confie, mas valide na borda:** o JWT é validado uma vez no gateway; downstream confia no
  contexto propagado (defesa em profundidade ainda recomendada nos serviços críticos).
- **Descoberta, não hardcode:** rotas resolvem service-ids via Eureka; nunca host:porta fixos.
- **Transparência de domínio:** o gateway não conhece regras de negócio; encaminha e enriquece.
- **Hexagonal mesmo no edge:** decisões de borda (auth, rate-limit, tenant) modeladas como
  políticas testáveis isoladas do framework (ver ADR-001).

## 7. Success Signals

- Frontend e integrações usam **um único** host público; nenhum serviço de negócio exposto direto.
- 100% das rotas resolvidas via Eureka (zero endpoints hardcoded).
- JWT inválido/ausente rejeitado na borda (401/403) antes de atingir qualquer serviço.
- `X-Empresa-Id` e `X-Correlation-Id` presentes em 100% das requisições downstream.
- Rate-limit aplicado e observável; p99 de overhead do gateway dentro do orçamento de latência.
