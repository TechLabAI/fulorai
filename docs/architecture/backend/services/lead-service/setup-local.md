# Setup Local — lead-service

## HTTP port

`8082` (business services start at 8081; WRKS 8081, LEAD 8082; GWY 8080, REG 8761).

## Local dependencies

| Dependency | Purpose | Local |
|---|---|---|
| PostgreSQL 15+ (pgvector) | operational schema `emp_<slug>` | `docker-compose.dev.yml` |
| `journey-os-migrations` (MIG) | prepares `emp_<slug>` (LEAD runs `ddl-auto=validate`) | `./gradlew :journey-os-migrations:bootRun` **first** |
| WRKS (`wrks-service`) | AccessDecision + JWKS (authorization) | `./gradlew :services:wrks-service:bootRun` |
| Kafka (AWS MSK / local broker) | domain events (`lead.*`) + WRKS events consume | `docker-compose.dev.yml` |
| Elasticsearch 9.x | `leads` index (queue/segmentation) | elastic-stack overlay |
| TechLab AI | capability `qualification` (optional assist) | `docker run ... ghcr.io/DaniloAmaral-Dev/techlab-ai:latest` |
| Eureka (REG) | service discovery | `./gradlew :services:journey-os-service-registry:bootRun` |

## Environment variables

```bash
# Database (tenant schemas emp_<slug>)
LEAD_DB_URL=jdbc:postgresql://localhost:5432/journeyos
LEAD_DB_USER=journeyos
LEAD_DB_PASSWORD=${LEAD_DB_PASSWORD}

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
ELASTIC_LEADS_INDEX=leads
ELASTIC_API_KEY=${ELASTIC_API_KEY:-}

# TechLab AI (capability: qualification) — optional assist
TECHLAB_AI_BASE_URL=http://localhost:8090
TECHLAB_AI_JWT_ENABLED=false
LEAD_QUALIFICATION_ASSIST_ENABLED=false   # stays false until P3 sync provides DTOs

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

# 3. lead-service
./gradlew :services:lead-service:bootRun

# checks
./gradlew :services:lead-service:architectureCheck   # BLOCKING (ArchUnit)
./gradlew :services:lead-service:test                # unit
./gradlew :services:lead-service:integrationTest     # Testcontainers + BDD
```

## Smoke

```bash
curl -s localhost:8082/actuator/health
# capture a lead (requires a valid WRKS-issued JWT)
curl -s -X POST localhost:8082/api/v1/leads \
  -H "Authorization: Bearer $JWT" -H "Content-Type: application/json" \
  -d '{"email":"rafael@acme.com","fonte":"meta-ads","baseLegal":"CONSENTIMENTO"}'
```
