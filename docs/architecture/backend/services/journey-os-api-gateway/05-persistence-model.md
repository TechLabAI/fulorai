# 05 — Persistence Model — GWY (API Gateway)

> Serviço: `journey-os-api-gateway` · Pacote: `com.journeyos.gwy` · Tipo: **infra (gateway)**

## 1. Schema Strategy

**Nenhum schema PostgreSQL.** O gateway é stateless e **não participa** da estratégia
`schema-per-empresa` (`journeyos_global` / `t_<empresaId>`). Ele apenas **resolve** o `empresa`
do JWT e o **propaga** via header; nunca abre conexão com o banco de dados de domínio.

Consequências:
- Sem `DataSource`, sem JPA, sem Hibernate.
- RULE-02 (`domain` não importa `jakarta.persistence`) é trivialmente satisfeita.
- RULE-08 (`spring.jpa.open-in-view=false`) é **N/A** (não há JPA); não há propriedade `spring.jpa`.
- O serviço **não** depende de `journey-os-migrations`.

## 2. Initial Entities

Nenhuma entidade JPA. O único estado externo é o do **rate-limiter no Redis**:

| Estrutura (Redis) | Conteúdo | TTL |
|---|---|---|
| `rate-limit:{key}` | contador de tokens/janela (token bucket do `RequestRateLimiter`) | janela de limitação |

Onde `{key}` deriva de `RateLimitKey` (TENANT / USER / IP). Essas chaves são efêmeras e não
constituem dados de domínio.

## 3. Migration Strategy

**Não se aplica.** O gateway não cria nem valida schema relacional; portanto não há migrations
Flyway próprias e não usa `journey-os-migrations`. O Redis não requer migration (estruturas
criadas em runtime pelo rate-limiter).

## 4. Data Lifecycle

- **Contadores de rate-limit:** efêmeros, expiram por TTL no Redis; nenhuma retenção/arquivamento.
- **Logs/métricas de borda:** retenção governada pela plataforma de observabilidade (INTL /
  Elastic), fora do escopo do gateway.
- **Tokens:** o gateway não armazena tokens; valida e descarta por requisição.
- **LGPD:** o gateway não persiste dados pessoais; logs devem evitar registrar payloads/PII
  (apenas metadados de borda + `correlationId`).
