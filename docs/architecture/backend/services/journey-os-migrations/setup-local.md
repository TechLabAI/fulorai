# Setup Local · MIG (`journey-os-migrations`)

> MIG must run **first** in local dev — before any other service starts.

## HTTP port
- **8079** (actuator only; internal). Configurable via `SERVER_PORT`.
  > Convention: infra services occupy the 807x band (MIG 8079); business services 808x+.
  > Adjust if it collides with REG/GWY once their specs land.

## Local dependencies
- **PostgreSQL 15+** with the ability to create extensions (run locally via Docker).
- No Artemis, no Eureka, no other Journey OS service required to run MIG.

```bash
# Start local infra (Postgres)
docker compose -f docker/docker-compose.dev.yml up -d postgres
```

## Environment variables

| Var | Purpose | Example (local) |
|-----|---------|-----------------|
| `MIG_DB_URL` | JDBC URL to the cluster | `jdbc:postgresql://localhost:5432/journeyos` |
| `MIG_DB_USER` | Migration role user | `journeyos_migrator` |
| `MIG_DB_PASSWORD` | Migration role password | `*** (never commit)` |
| `MIG_GLOBAL_SCHEMA` | Global schema name | `journeyos_global` |
| `MIG_TENANT_SCHEMAS` | Comma list of tenant schemas (MVP, until WRKS registry) | `empresa_demo` |
| `SERVER_PORT` | Actuator port | `8079` |

## Commands

```bash
# Apply all migrations (global + per-tenant). RUN THIS FIRST.
./gradlew :journey-os-migrations:bootRun

# Build
./gradlew :journey-os-migrations:build

# ArchUnit (blocking before commit)
./gradlew :journey-os-migrations:architectureCheck
```

## Verify
- `GET http://localhost:8079/actuator/flyway` → lists applied/pending migrations.
- `GET http://localhost:8079/actuator/health` → `UP` after a successful run.
- Then start business services with `spring.jpa.hibernate.ddl-auto=validate`.
