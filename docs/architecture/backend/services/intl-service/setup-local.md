# Setup Local — intl-service

## HTTP port

`8087` (business services: WRKS 8081, LEAD 8082, ASST 8083, JRNY 8084, COMM 8085, SALE 8086, **INTL 8087**; GWY 8080, REG 8761).

## Local dependencies

| Dependency | Purpose | Local |
|---|---|---|
| PostgreSQL 15+ + pgVector | tenant schema `emp_<slug>` (conhecimento + conversas) | `docker-compose.dev.yml` |
| `journey-os-migrations` (MIG) | prepara `emp_<slug>` (INTL roda `ddl-auto=validate`) | `./gradlew :journey-os-migrations:bootRun` **primeiro** |
| `wrks-service` (WRKS) | JWT (JWKS) + `AccessDecision` (`intl.*`) | `./gradlew :services:wrks-service:bootRun` |
| `asst-service` (ASST) | `AssetQueryClient` — conteúdo de asset como fonte de conhecimento (opcional) | `./gradlew :services:asst-service:bootRun` |
| TechLab AI | `knowledge` + `orchestration` (AI Copilot RAG) | `docker run -p 8090:8090 ghcr.io/DaniloAmaral-Dev/techlab-ai:latest` |
| Elasticsearch 9.x + Kibana | índices `ai-copilot-events`/`knowledge-nodes` + recuperação/analítica | `docker compose -f infra/compose-elastic.yml up -d` |
| Kafka (AWS MSK / local broker) | eventos consumidos/publicados | `docker-compose.dev.yml` |
| Eureka (REG) | service discovery | `./gradlew :services:journey-os-service-registry:bootRun` |

## Environment variables

```bash
# Database (tenant schema resolvido em runtime via EmpresaContextHolder)
INTL_DB_URL=jdbc:postgresql://localhost:5432/journeyos
INTL_DB_USER=journeyos
INTL_DB_PASSWORD=${INTL_DB_PASSWORD}

# WRKS (identity / AccessDecision)
WRKS_BASE_URL=http://localhost:8081
WRKS_JWKS_URI=http://localhost:8081/api/v1/iam/.well-known/jwks.json

# ASST (asset publicado como fonte de conhecimento — opcional)
ASST_BASE_URL=http://localhost:8083

# TechLab AI (knowledge + orchestration) — nunca chamar provedor de IA direto
TECHLAB_AI_BASE_URL=http://localhost:8090
TECHLAB_AI_JWT_ENABLED=false
TECHLAB_AI_TIMEOUT_MS=20000
TECHLAB_AI_CB_FAILURE_RATE=50

# Elasticsearch (plataforma de dados)
ELASTICSEARCH_URL=http://localhost:9200
ELASTICSEARCH_INDEX_PREFIX=journey-os_

# Kafka
KAFKA_BOOTSTRAP_SERVERS=localhost:9092
KAFKA_CONSUMER_GROUP=intl-service

# Eureka
EUREKA_URL=http://localhost:8761/eureka
```

## Run & test

```bash
# 1. migrations primeiro
./gradlew :journey-os-migrations:bootRun
# 2. dependências (WRKS, REG, Elastic, Kafka, TechLab AI)
# 3. INTL
./gradlew :services:intl-service:bootRun
# testes
./gradlew :services:intl-service:test
./gradlew :services:intl-service:architectureCheck     # BLOQUEANTE
./gradlew :services:intl-service:test --tests "*CucumberIT*"
```

## Smoke

```bash
curl -s localhost:8087/actuator/health
# abrir conversa → perguntar (requer JWT de WRKS com permissão intl.copilot.use)
```
