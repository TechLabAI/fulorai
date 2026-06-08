# Setup Local — jrny-service

## HTTP port

`8084` (business services: WRKS 8081, LEAD 8082, ASST 8083, JRNY 8084; GWY 8080, REG 8761).

## Local dependencies

| Dependency | Purpose | Local |
|---|---|---|
| PostgreSQL 15+ | tenant schema `emp_<slug>` (journeys/stages/rules/enrolments/decisions — source of truth) | `docker-compose.dev.yml` |
| `journey-os-migrations` (MIG) | prepares `emp_<slug>` schema (JRNY runs `ddl-auto=validate`) | `./gradlew :journey-os-migrations:bootRun` **first** |
| `wrks-service` (WRKS) | JWT validation (JWKS) + `AccessDecision` (`jrny.*`) | `./gradlew :services:wrks-service:bootRun` |
| `asst-service` (ASST) | `AssetQueryClient` — published asset content referenced by stages | `./gradlew :services:asst-service:bootRun` |
| TechLab AI | `orchestration` (Routing Engine assist) — **optional**, deterministic fallback | `docker run -p 8090:8090 ghcr.io/DaniloAmaral-Dev/techlab-ai:latest` |
| Elasticsearch 9.x | `journey-events` + `routing-decisions` indices (fact projections) | elastic-stack overlay |
| Kafka (AWS MSK / local broker) | domain events (consume LEAD/ASST/WRKS, produce routing events) | `docker-compose.dev.yml` |
| Eureka (REG) | service discovery | `./gradlew :services:journey-os-service-registry:bootRun` |

> LEAD is **not** a hard bring-up dependency for JRNY: JRNY consumes LEAD events asynchronously.
> Running LEAD locally is only needed to exercise the live routing trigger end-to-end.

## Environment variables

```bash
# Database (tenant schema resolved at runtime via EmpresaContextHolder)
JRNY_DB_URL=jdbc:postgresql://localhost:5432/journeyos
JRNY_DB_USER=journeyos
JRNY_DB_PASSWORD=${JRNY_DB_PASSWORD}

# WRKS (identity / AccessDecision)
WRKS_BASE_URL=http://localhost:8081
WRKS_JWKS_URI=http://localhost:8081/api/v1/iam/.well-known/jwks.json

# ASST (published asset content referenced by stages)
ASST_BASE_URL=http://localhost:8083

# TechLab AI (orchestration) — never call an AI provider directly; assist is OPTIONAL
TECHLAB_AI_BASE_URL=http://localhost:8090
TECHLAB_AI_JWT_ENABLED=false
TECHLAB_AI_TIMEOUT_MS=2000
TECHLAB_AI_CB_FAILURE_RATE=50

# Elasticsearch (fact projections)
ELASTIC_URIS=http://localhost:9200
ELASTIC_JOURNEY_EVENTS_INDEX=journey-events
ELASTIC_ROUTING_DECISIONS_INDEX=routing-decisions

# Kafka
KAFKA_BOOTSTRAP_SERVERS=localhost:9092

# Eureka
EUREKA_SERVICE_URL=http://localhost:8761/eureka
```

> **Routing assist timeout** is short by design (`TECHLAB_AI_TIMEOUT_MS=2000`): the decision waits
> for the recommendation only for a brief window, then falls back to deterministic rules. This is
> the inverse of ASST's Studio (which can wait 20 s) — JRNY's golden path must stay fast.

## Bring-up & test

```bash
# 0. infra
docker compose -f docker/docker-compose.dev.yml up -d   # postgres, kafka, elastic
docker run --rm -d -p 8090:8090 -e TECHLAB_AI_JWT_ENABLED=false \
  -e TECHLAB_AI_ANTHROPIC_API_KEY=$ANTHROPIC_API_KEY ghcr.io/DaniloAmaral-Dev/techlab-ai:latest

# 1. migrations first (prepares emp_<slug>)
./gradlew :journey-os-migrations:bootRun

# 2. registry + WRKS (identity) + ASST (stage content)
./gradlew :services:journey-os-service-registry:bootRun
./gradlew :services:wrks-service:bootRun
./gradlew :services:asst-service:bootRun

# 3. jrny-service
./gradlew :services:jrny-service:bootRun

# checks
./gradlew :services:jrny-service:architectureCheck   # BLOCKING (ArchUnit)
./gradlew :services:jrny-service:test                # unit
./gradlew :services:jrny-service:integrationTest     # Testcontainers + BDD
```

## Smoke

```bash
curl -s localhost:8084/actuator/health
# create a journey (Bearer JWT from WRKS required)
curl -s -X POST localhost:8084/api/v1/journeys -H "Authorization: Bearer $JWT" \
  -H 'Content-Type: application/json' \
  -d '{"nome":"Funil de Lançamento","descricao":"5 estágios"}'

# query a lead's journey state (consumed by COMM/SALE via JourneyQueryClient)
curl -s localhost:8084/api/v1/routing/leads/{leadId}/journey -H "Authorization: Bearer $JWT"
```
