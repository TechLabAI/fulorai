# Setup Local — journey-os-service-registry (REG)

## HTTP port

| Service | Port | In-cluster address |
|---|---|---|
| `journey-os-service-registry` | **8761** | `http://journey-os-service-registry:8761/eureka/` |

## Dependencies

**None.** REG has no PostgreSQL, Artemis/Kafka, or Hub-service dependency. It must be
started **first** (before business services) so clients can register on boot.

## Environment variables

| Variable | Default | Purpose |
|---|---|---|
| `SERVER_PORT` | `8761` | HTTP port |
| `SPRING_PROFILES_ACTIVE` | `local` | Active profile (`local` \| `prod`) |
| `EUREKA_SERVER_ENABLE_SELF_PRESERVATION` | `false` (local) / unset → default `true` (prod) | Self-preservation mode (ADR-005) |
| `EUREKA_INSTANCE_HOSTNAME` | `localhost` (local) / `journey-os-service-registry` (cluster) | Advertised hostname |

> No secrets. All config via `${VAR}` per the no-hardcoded-secret rule.

## Run

```bash
# From backend/
./gradlew :services:journey-os-service-registry:bootRun

# Or via the built jar
./gradlew :services:journey-os-service-registry:build
java -jar services/journey-os-service-registry/build/libs/journey-os-service-registry-*.jar
```

## Verify

```bash
# Dashboard (HTML)
curl -s http://localhost:8761/ | head

# Health probe — expect {"status":"UP"}
curl -s http://localhost:8761/actuator/health

# Registry (JSON) — empty until clients register
curl -s -H "Accept: application/json" http://localhost:8761/eureka/apps
```

## Clients (other services) point here

```yaml
# any business service application.yml
eureka:
  client:
    service-url:
      defaultZone: ${EUREKA_URL:http://localhost:8761/eureka/}
```

For local dev without the registry, a client may set `eureka.client.enabled=false`
and use explicit Feign URLs (see `platform-patterns.md` §7.2).
