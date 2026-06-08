# Setup Local — comm-service

## HTTP port

`8085` (business services: WRKS 8081, LEAD 8082, ASST 8083, JRNY 8084, COMM 8085; GWY 8080, REG 8761).

## Local dependencies

| Dependency | Purpose | Local |
|---|---|---|
| PostgreSQL 15+ | tenant schema `emp_<slug>` (communication source of truth) | `docker-compose.dev.yml` |
| `journey-os-migrations` (MIG) | prepares `emp_<slug>` schema (COMM runs `ddl-auto=validate`) | `./gradlew :journey-os-migrations:bootRun` **first** |
| `wrks-service` (WRKS) | JWT validation (JWKS) + `AccessDecision` (`comm.*`) | `./gradlew :services:wrks-service:bootRun` |
| `asst-service` (ASST) | `AssetQueryClient` — published assets as template source | `./gradlew :services:asst-service:bootRun` |
| TechLab AI | `document_composition` (Template Studio) | `docker run -p 8090:8090 ghcr.io/DaniloAmaral-Dev/techlab-ai:latest` |
| Channel providers | actual send + delivery webhooks (sandbox/mocked locally) | mock/sandbox per provider |
| Elasticsearch 9.x | `communication-events` index (delivery analytics) | elastic-stack overlay |
| Kafka (AWS MSK / local broker) | domain events + dispatch outbox | `docker-compose.dev.yml` |
| Eureka (REG) | service discovery | `./gradlew :services:journey-os-service-registry:bootRun` |

## Environment variables

```bash
# Database (tenant schema resolved at runtime via EmpresaContextHolder)
COMM_DB_URL=jdbc:postgresql://localhost:5432/journeyos
COMM_DB_USER=journeyos
COMM_DB_PASSWORD=${COMM_DB_PASSWORD}

# WRKS (identity / AccessDecision)
WRKS_BASE_URL=http://localhost:8081
WRKS_JWKS_URI=http://localhost:8081/api/v1/iam/.well-known/jwks.json

# ASST (published assets as template source)
ASST_BASE_URL=http://localhost:8083

# TechLab AI (document_composition) — never call an AI provider directly
TECHLAB_AI_BASE_URL=http://localhost:8090
TECHLAB_AI_JWT_ENABLED=false
TECHLAB_AI_TIMEOUT_MS=20000
TECHLAB_AI_CB_FAILURE_RATE=50

# Channel providers (credentials are referenced via secret manager — never hardcoded)
# Values below are local sandbox placeholders resolved from config_canal.credencial_ref
COMM_WHATSAPP_BASE_URL=https://graph.facebook.com
COMM_EMAIL_BASE_URL=https://email.example
COMM_TELEGRAM_BASE_URL=https://api.telegram.org
COMM_SMS_BASE_URL=https://api.twilio.com
COMM_DISPATCH_MAX_RETRIES=3
COMM_WEBHOOK_VERIFY_SIGNATURE=true

# Elasticsearch
ELASTIC_URIS=http://localhost:9200
ELASTIC_COMMUNICATION_EVENTS_INDEX=communication-events

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

# 2. registry + WRKS (identity) + ASST (assets)
./gradlew :services:journey-os-service-registry:bootRun
./gradlew :services:wrks-service:bootRun
./gradlew :services:asst-service:bootRun

# 3. comm-service
./gradlew :services:comm-service:bootRun

# checks
./gradlew :services:comm-service:architectureCheck   # BLOCKING (ArchUnit)
./gradlew :services:comm-service:test                # unit
./gradlew :services:comm-service:integrationTest     # Testcontainers + BDD
```

## Smoke

```bash
curl -s localhost:8085/actuator/health
# create template (Bearer JWT from WRKS required)
curl -s -X POST localhost:8085/api/v1/templates -H "Authorization: Bearer $JWT" \
  -H 'Content-Type: application/json' \
  -d '{"nome":"Boas-vindas","canal":"WHATSAPP","tipoTemplate":"TRANSACIONAL","corpo":"Olá {{nome}}!"}'
# dispatch a message (idempotent)
curl -s -X POST localhost:8085/api/v1/messages -H "Authorization: Bearer $JWT" \
  -H 'Idempotency-Key: 4f1c...-demo' -H 'Content-Type: application/json' \
  -d '{"templateId":"<id>","leadId":"<leadId>","variaveis":{"nome":"Rafael"}}'
```
