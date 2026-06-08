# Brief — GWY (API Gateway)

> Fonte estruturada para `/be-architect-specs`, `/be-architect-backlog` e `/be-architect-scaffold`.
> Módulo de **infraestrutura** (`isInfra: true`) — sem domínio de negócio nem persistência transacional.

| # | Item | Conteúdo |
|---|------|----------|
| 1 | **Nome canônico / Prefixo** | `journey-os-api-gateway` / **GWY** · pacote `com.journeyos.gwy` |
| 2 | **Problema que resolve** | Ponto único de entrada (edge) para todo o tráfego HTTP do Journey OS. Centraliza roteamento para os microserviços de negócio, autenticação/validação de JWT, resolução do tenant (`empresa`), rate-limiting e CORS, evitando que cada serviço reimplemente essas preocupações de borda. |
| 3 | **Persona principal / secundária** | **Principal:** SPA Angular (`journey-os-web`) e clientes de API externos (webhooks de integrações Hotmart/Meta/ActiveCampaign) que consomem a API pública. **Secundária:** operadores de plataforma/SRE que configuram rotas, limites e políticas de segurança de borda. |
| 4 | **Recorte do MVP (in)** | Spring Cloud Gateway reativo (WebFlux); descoberta dinâmica de rotas via Eureka (REG) com `lb://`; filtro global de validação de JWT (assinatura + claims) delegando emissão ao WRKS; propagação de `X-Empresa-Id`, `X-Tenant-Schema` e `X-Correlation-Id` aos serviços downstream; rate-limiting por chave (tenant/usuário/IP) com Redis; CORS centralizado; health/actuator + tracing de borda. |
| 5 | **Fora de escopo (MVP)** | Lógica de negócio; composição/agregação de respostas (BFF); persistência de dados de domínio; terminação TLS (delegada ao ALB/Ingress da AWS); emissão de tokens (responsabilidade do WRKS); cache de respostas de domínio; transformação de payloads de negócio. |
| 6 | **Integrações externas obrigatórias** | **REG (Eureka)** — descoberta de serviços (obrigatória para roteamento `lb://`). **WRKS** — fonte da verdade de identidade/JWT (JWKS/chave pública para validação). **Redis** — backing store do rate-limiter distribuído. Todos os serviços de negócio downstream (WRKS, LEAD, JRNY, ASST, COMM, SALE, INTL) como alvos de rota. |
| 7 | **TechLab AI / eventos** | **TechLab AI: nenhum** — o gateway não chama capacidades de IA. Não produz nem consome eventos de domínio (Kafka). Interação inter-módulo limitada a roteamento HTTP e descoberta via REG. |
| 8 | **Evento-âncora do domínio** | Não há evento-âncora de negócio (módulo de infraestrutura, sem agregados). Conceito operacional central: **"Requisição roteada"** (request match → autenticação → enriquecimento de contexto → encaminhamento), tratado como decisão de borda stateless, não como evento de domínio publicado. |

---

## Notas de contexto (Journey OS)

- **Stack:** Java 21 · Spring Boot 3.5.0 · **Spring Cloud Gateway (reativo / WebFlux)** · Gradle 8.x (Kotlin DSL).
- **Descoberta:** Eureka (REG = `journey-os-service-registry`).
- **Multi-tenancy:** `schema-per-empresa`, schema global `journeyos_global`, termo `empresa`. O gateway **resolve e propaga** o contexto de tenant; **não** acessa schemas.
- **Mensageria:** Kafka (AWS MSK) — não utilizada pelo gateway.
- **Type:** `gateway` (autopilot) → A3 (specs-validate) = N/A; backlog/scaffold geram estrutura reduzida.
- **Particularidade arquitetural:** serviço **reativo**, sem JPA. RULE-02 (sem `jakarta.persistence`) e RULE-08 (`open-in-view`) tornam-se triviais/N-A; as demais regras hexagonais continuam valendo (ver ADR-001).
