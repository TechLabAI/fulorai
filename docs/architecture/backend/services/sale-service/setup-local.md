# Setup Local — sale-service

## HTTP port

`8086` (business services: WRKS 8081, LEAD 8082, ASST 8083, JRNY 8084, COMM 8085, SALE 8086; GWY 8080, REG 8761).

## Local dependencies

| Dependency | Purpose | Local |
|---|---|---|
| PostgreSQL 15+ | operational schema `emp_<slug>` | `docker-compose.dev.yml` |
| `journey-os-migrations` (MIG) | prepares `emp_<slug>` (SALE runs `ddl-auto=validate`) | `./gradlew :journey-os-migrations:bootRun` **first** |
| WRKS (`wrks-service`) | AccessDecision + JWKS (authorization) | `./gradlew :services:wrks-service:bootRun` |
| LEAD (`lead-service`) | `lead.qualificado` / `lead.score.atualizado` (creates oportunidade) | `./gradlew :services:lead-service:bootRun` (optional) |
| Kafka (AWS MSK / local broker) | domain events (`oportunidade.*`/`compra.*`/`receita.*`/`ltv.*`) + consume LEAD/WRKS | `docker-compose.dev.yml` |
| Elasticsearch 9.x | `revenue-events`, `campaign-events` indices | elastic-stack overlay |
| Eureka (REG) | service discovery | `./gradlew :services:journey-os-service-registry:bootRun` |

> **No TechLab AI dependency** — attribution/LTV are deterministic (ADR-005).

## Environment variables

```bash
# Database (tenant schemas emp_<slug>)
SALE_DB_URL=jdbc:postgresql://localhost:5432/journeyos
SALE_DB_USER=journeyos
SALE_DB_PASSWORD=${SALE_DB_PASSWORD}

# JWT validation (WRKS JWKS)
WRKS_JWKS_URI=http://localhost:8081/api/v1/iam/.well-known/jwks.json

# Redis (AccessDecision cache)
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=${REDIS_PASSWORD:-}

# Kafka
KAFKA_BOOTSTRAP_SERVERS=localhost:9092

# Elasticsearch
ELASTIC_URIS=http://localhost:9200
ELASTIC_REVENUE_INDEX=revenue-events
ELASTIC_CAMPAIGN_INDEX=campaign-events
ELASTIC_API_KEY=${ELASTIC_API_KEY:-}

# Purchase ingestion (service-token mediated via GWY)
SALE_COMPRA_SERVICE_TOKEN_ENABLED=true

# Eureka
EUREKA_SERVICE_URL=http://localhost:8761/eureka
```

## Bring-up & test

```bash
# 0. infra
docker compose -f docker/docker-compose.dev.yml up -d   # postgres, redis, kafka, elastic

# 1. migrations first (prepares emp_<slug>)
./gradlew :journey-os-migrations:bootRun

# 2. registry + WRKS (auth dependency)
./gradlew :services:journey-os-service-registry:bootRun
./gradlew :services:wrks-service:bootRun

# 3. sale-service
./gradlew :services:sale-service:bootRun

# checks
./gradlew :services:sale-service:architectureCheck   # BLOCKING (ArchUnit)
./gradlew :services:sale-service:test                # unit
./gradlew :services:sale-service:integrationTest     # Testcontainers + BDD
```

## Smoke

```bash
curl -s localhost:8086/actuator/health
# register a confirmed purchase (requires a valid WRKS-issued JWT / service token)
curl -s -X POST localhost:8086/api/v1/compras \
  -H "Authorization: Bearer $JWT" -H "Content-Type: application/json" \
  -d '{"idExterno":"HOT-9981","origem":"hotmart","contatoRef":"rafael@acme.com","baseLegal":"EXECUCAO_CONTRATO","itens":[{"ofertaId":null,"descricao":"curso-pro","quantidade":1,"valorUnitario":1997.00}]}'
```
