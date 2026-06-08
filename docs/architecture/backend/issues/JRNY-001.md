# JRNY-001 -- Bootstrap jrny-service (Spring Boot MVC + Eureka client + Actuator + ArchUnit)

## Contexto
Esqueleto executável do Journey & Routing. App Spring Boot MVC, pacote base `com.journeyos.jrny`,
registro no Eureka (REG), Actuator e harness ArchUnit (RULE-01..09).

## Spec de referencia
- SPEC-01-api-surface
- SPEC-07-observability-health

## Escopo
- App Spring Boot 3.5.x MVC (não reativo), pacote `com.journeyos.jrny`.
- Dependências: web, data-jpa, eureka-client, actuator, validation.
- `application.yml` com `${VAR}` (porta 8084, `JRNY_DB_*`, `EUREKA_SERVICE_URL`); perfis dev/prod.
- `ddl-auto=validate`, `open-in-view=false` (RULE-08). `spring.application.name=jrny-service`.
- `ArchitectureTest.java` (@AnalyzeClasses "com.journeyos.jrny") com RULE-01..09.

## Resultado esperado
Serviço sobe, registra no Eureka e responde Actuator; sem lógica de negócio ainda.

## Criterios de aceite
- [ ] `./gradlew :services:jrny-service:build` PASS.
- [ ] `GET /actuator/health` → 200.
- [ ] `:jrny-service:architectureCheck` PASS.
- [ ] Nenhum segredo hardcoded (config via `${VAR}`).

## Dependencias
- INT-JRNY-001 (Eureka discovery)

## Estimativa
S

## Prioridade
P1
