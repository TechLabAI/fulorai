# Setup Local — asst-service

## HTTP port

`8083` (business services start at 8081: WRKS 8081, LEAD 8082, ASST 8083; GWY 8080, REG 8761).

## Local dependencies

| Dependency | Purpose | Local |
|---|---|---|
| PostgreSQL 15+ | tenant schema `emp_<slug>` (asset source of truth) | `docker-compose.dev.yml` |
| `journey-os-migrations` (MIG) | prepares `emp_<slug>` schema (ASST runs `ddl-auto=validate`) | `./gradlew :journey-os-migrations:bootRun` **first** |
| `wrks-service` (WRKS) | JWT validation (JWKS) + `AccessDecision` (`asst.*`) | `./gradlew :services:wrks-service:bootRun` |
| TechLab AI | `document_composition` (Asset Studio) + classification (Asset Intelligence) | `docker run -p 8090:8090 ghcr.io/DaniloAmaral-Dev/techlab-ai:latest` |
| Elasticsearch 9.x | `assets` index (search + Asset Intelligence) | elastic-stack overlay |
| Kafka (AWS MSK / local broker) | domain events (publish/consume) | `docker-compose.dev.yml` |
| Eureka (REG) | service discovery | `./gradlew :services:journey-os-service-registry:bootRun` |

## Environment variables

```bash
# Database (tenant schema resolved at runtime via EmpresaContextHolder)
ASST_DB_URL=jdbc:postgresql://localhost:5432/journeyos
ASST_DB_USER=journeyos
ASST_DB_PASSWORD=${ASST_DB_PASSWORD}

# WRKS (identity / AccessDecision)
WRKS_BASE_URL=http://localhost:8081
WRKS_JWKS_URI=http://localhost:8081/api/v1/iam/.well-known/jwks.json

# TechLab AI (document_composition) — never call an AI provider directly
TECHLAB_AI_BASE_URL=http://localhost:8090
TECHLAB_AI_JWT_ENABLED=false
TECHLAB_AI_TIMEOUT_MS=20000
TECHLAB_AI_CB_FAILURE_RATE=50

# Elasticsearch
ELASTIC_URIS=http://localhost:9200
ELASTIC_ASSETS_INDEX=assets

# Kafka
KAFKA_BOOTSTRAP_SERVERS=localhost:9092

# Eureka
EUREKA_SERVICE_URL=http://localhost:8761/eureka
```

## Bring-up & test

```bash
# 0. infra
docker compose -f docker/docker-compose.dev.yml up -d   # postgres, kafka, elastic
docker run --rm -d -p 8090:8090 -e TECHLAB_AI_JWT_ENABLED=false \
  -e TECHLAB_AI_ANTHROPIC_API_KEY=$ANTHROPIC_API_KEY ghcr.io/DaniloAmaral-Dev/techlab-ai:latest

# 1. migrations first (prepares emp_<slug>)
./gradlew :journey-os-migrations:bootRun

# 2. registry + WRKS (identity)
./gradlew :services:journey-os-service-registry:bootRun
./gradlew :services:wrks-service:bootRun

# 3. asst-service
./gradlew :services:asst-service:bootRun

# checks
./gradlew :services:asst-service:architectureCheck   # BLOCKING (ArchUnit)
./gradlew :services:asst-service:test                # unit
./gradlew :services:asst-service:integrationTest     # Testcontainers + BDD
```

## Smoke

```bash
curl -s localhost:8083/actuator/health
# create asset (Bearer JWT from WRKS required)
curl -s -X POST localhost:8083/api/v1/assets -H "Authorization: Bearer $JWT" \
  -H 'Content-Type: application/json' \
  -d '{"tipoAsset":"EMAIL","titulo":"Boas-vindas"}'
```
