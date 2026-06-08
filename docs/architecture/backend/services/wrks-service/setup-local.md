# Setup Local — wrks-service

## HTTP port

`8081` (business services start at 8081; GWY 8080, REG 8761).

## Local dependencies

| Dependency | Purpose | Local |
|---|---|---|
| PostgreSQL 15+ | `journeyos_global` (IAM source of truth) | `docker-compose.dev.yml` |
| `journey-os-migrations` (MIG) | prepares `journeyos_global` schema (WRKS runs `ddl-auto=validate`) | `./gradlew :journey-os-migrations:bootRun` **first** |
| Redis/Valkey | session + AccessDecision cache + logout blacklist | `docker-compose.dev.yml` |
| Keycloak | OIDC IdP (authentication) | `docker-compose.dev.yml` |
| Kafka (AWS MSK / local broker) | domain events + audit consumer | `docker-compose.dev.yml` |
| Elasticsearch 9.x | `audit-events` index | elastic-stack overlay |
| Eureka (REG) | service discovery | `./gradlew :services:journey-os-service-registry:bootRun` |

## Environment variables

```bash
# Database
WRKS_DB_URL=jdbc:postgresql://localhost:5432/journeyos
WRKS_DB_USER=journeyos
WRKS_DB_PASSWORD=${WRKS_DB_PASSWORD}
WRKS_DB_GLOBAL_SCHEMA=journeyos_global

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=${REDIS_PASSWORD:-}

# Keycloak (OIDC)
KEYCLOAK_ISSUER_URI=http://localhost:8088/realms/journey-os
KEYCLOAK_CLIENT_ID=wrks-service
KEYCLOAK_CLIENT_SECRET=${KEYCLOAK_CLIENT_SECRET}

# JWT issuance (WRKS-owned RS256 keypair; JWKS exposed at /api/v1/iam/.well-known/jwks.json)
WRKS_JWT_PRIVATE_KEY=${WRKS_JWT_PRIVATE_KEY}        # PEM (dev: generated keypair)
WRKS_JWT_ISSUER=https://journey-os.local
WRKS_JWT_AUDIENCE=journey-os-api

# Kafka
KAFKA_BOOTSTRAP_SERVERS=localhost:9092

# Elasticsearch
ELASTIC_URIS=http://localhost:9200
ELASTIC_AUDIT_INDEX=audit-events

# Eureka
EUREKA_SERVICE_URL=http://localhost:8761/eureka

# MIG provisioning trigger
MIG_BASE_URL=http://localhost:8090
```

## Bring-up & test

```bash
# 0. infra
docker compose -f docker/docker-compose.dev.yml up -d   # postgres, redis, keycloak, kafka, elastic

# 1. migrations first (prepares journeyos_global)
./gradlew :journey-os-migrations:bootRun

# 2. registry
./gradlew :services:journey-os-service-registry:bootRun

# 3. wrks-service
./gradlew :services:wrks-service:bootRun

# checks
./gradlew :services:wrks-service:architectureCheck   # BLOCKING (ArchUnit)
./gradlew :services:wrks-service:test                # unit
./gradlew :services:wrks-service:integrationTest     # Testcontainers + BDD
```

## Smoke

```bash
curl -s localhost:8081/actuator/health
curl -s localhost:8081/api/v1/iam/.well-known/jwks.json
```
