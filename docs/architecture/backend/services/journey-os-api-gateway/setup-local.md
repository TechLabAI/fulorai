# Setup Local — GWY (`journey-os-api-gateway`)

> Gateway reativo (Spring Cloud Gateway / WebFlux). **Não usa PostgreSQL** e **não depende de
> `journey-os-migrations`**. Depende de REG (Eureka) e Redis.

## Porta HTTP

| Serviço | Porta local |
|---|---|
| `journey-os-api-gateway` | **8080** (edge público local) |
| `journey-os-service-registry` (REG) | 8761 |
| Redis | 6379 |

## Dependências locais

| Dependência | Para quê | Como subir |
|---|---|---|
| **REG (Eureka)** | Descoberta de rotas `lb://` | `./gradlew :services:journey-os-service-registry:bootRun` |
| **Redis** | Rate-limiter distribuído | `docker compose -f docker/docker-compose.dev.yml up -d redis` |
| **WRKS** | Chave pública / JWKS p/ validar JWT | rodar `wrks-service` (ou apontar `GWY_JWT_JWKS_URI` para mock) |
| Serviços downstream | Alvos de rota | sob demanda (rota responde 503 se ausente) |

## Variáveis de ambiente

```bash
# Servidor
SERVER_PORT=8080

# Eureka (REG)
GWY_EUREKA_SERVICE_URL=http://localhost:8761/eureka/

# Segurança / JWT (validação na borda — ADR-003)
GWY_JWT_JWKS_URI=http://localhost:8081/.well-known/jwks.json   # exposto pelo WRKS
GWY_JWT_ISSUER=https://auth.journeyos.local
GWY_JWT_AUDIENCE=journey-os

# Rate-limiting (ADR-005)
GWY_REDIS_HOST=localhost
GWY_REDIS_PORT=6379
GWY_RATELIMIT_REPLENISH_RATE=20      # tokens/segundo (default por rota)
GWY_RATELIMIT_BURST_CAPACITY=40

# CORS
GWY_CORS_ALLOWED_ORIGINS=http://localhost:4200   # SPA Angular em dev
```

> Nenhum segredo hardcoded: todos via `${VAR}` em `application.yml`.

## Ordem de subida (local)

```
1. REG (Eureka)        → :8761
2. Redis               → :6379
3. (WRKS, p/ JWKS)     → :8081
4. GWY (este serviço)  → :8080
5. Serviços de negócio → registram no Eureka; rotas resolvem automaticamente
```

## Subir e testar

```bash
# Build + ArchUnit (BLOQUEANTE)
./gradlew :services:journey-os-api-gateway:build
./gradlew :services:journey-os-api-gateway:architectureCheck

# Rodar
./gradlew :services:journey-os-api-gateway:bootRun

# Smoke
curl -s http://localhost:8080/actuator/health
curl -s http://localhost:8080/actuator/gateway/routes | jq .
```
