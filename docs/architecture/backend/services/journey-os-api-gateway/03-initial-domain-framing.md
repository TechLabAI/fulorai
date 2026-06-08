# 03 — Initial Domain Framing — GWY (API Gateway)

> Serviço: `journey-os-api-gateway` · Pacote: `com.journeyos.gwy` · Tipo: **infra (gateway)**
>
> ⚠️ GWY é um módulo de **infraestrutura**: não possui agregados de negócio nem persistência
> transacional. O "domínio" aqui é o **domínio de borda** (edge concerns), modelado como
> políticas e value objects puros para manter as decisões testáveis fora do framework.

## 1. Ubiquitous Language

| Termo | Definição |
|---|---|
| **Route / Rota** | Predicado (path/método/host) + destino (`lb://<service-id>`) + filtros. |
| **Edge Filter** | Política de borda aplicada a toda requisição (auth, tenant, rate-limit, correlação). |
| **TenantContext** | `empresaId` + `schema` resolvidos do JWT e propagados downstream. |
| **JwtClaims** | Claims validados do token (sub, iss, aud, exp, `empresaId`, roles). |
| **RateLimitKey** | Chave de limitação (por tenant, usuário ou IP). |
| **Correlation Id** | Identificador único de requisição propagado ponta-a-ponta. |
| **Public Route** | Rota na allowlist que dispensa autenticação (ex.: login, webhook assinado). |

## 2. Aggregates and Entities (rascunho)

GWY **não tem agregados persistidos**. Conceitos modelados como **value objects imutáveis**
(domínio puro):

- `RoutePolicy` — descreve uma rota lógica (id, predicados, target service-id, flags públicas).
- `JwtClaims` — snapshot validado do token.
- `TenantContext` — `empresaId`, `schema`.
- `RateLimitKey` — tipo (TENANT|USER|IP) + valor.
- `EdgeDecision` — resultado de uma política (ALLOW | DENY(reason) | THROTTLE).

## 3. Domain Events (inicial)

**Nenhum evento de domínio publicado.** O gateway não produz nem consome eventos Kafka.
Sinais operacionais (autenticação negada, rate-limit excedido, rota sem destino) são expostos
como **métricas/logs**, não como eventos de domínio. Se no futuro houver necessidade de
auditoria de acesso, isso será delegado a um evento de auditoria do **WRKS** (`audit-events`),
não emitido pelo gateway.

## 4. State Transitions (alto nível)

O gateway é **stateless** por requisição. A "máquina de estados" é o pipeline de filtros:

```
RECEBIDA → CORRELACIONADA → AUTENTICADA → TENANT-RESOLVIDO → RATE-CHECADA → ROTEADA → RESPONDIDA
                  └── (público) ──────────┘                       └→ NEGADA (401/403/429/503)
```

Nenhum estado sobrevive à requisição, exceto contadores de rate-limit (TTL no Redis).

## 5. Invariants

- **INV-1:** Toda requisição roteada carrega `X-Correlation-Id` (gerado se ausente).
- **INV-2:** Nenhuma requisição não-pública é encaminhada sem JWT válido.
- **INV-3:** Toda requisição autenticada propaga `X-Empresa-Id` derivado do claim — nunca de
  header fornecido pelo cliente (anti-spoofing de tenant).
- **INV-4:** O gateway nunca resolve host:porta fixos; destinos sempre via `lb://` + Eureka.
- **INV-5:** O gateway não lê nem escreve em schemas de tenant no PostgreSQL.
