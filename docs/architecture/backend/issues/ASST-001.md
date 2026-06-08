# ASST-001 -- Bootstrap asst-service (Spring Boot MVC + Eureka client + Actuator + ArchUnit)

## Contexto
Esqueleto executável do Asset Hub. App Spring Boot MVC, pacote base `com.journeyos.asst`,
registro no Eureka (REG), Actuator e harness ArchUnit (RULE-01..09).

## Spec de referencia
- SPEC-01-api-surface
- SPEC-07-observability-health

## Escopo
- App Spring Boot 3.5.x MVC (não reativo), pacote `com.journeyos.asst`.
- Dependências: web, data-jpa, eureka-client, actuator, validation.
- `application.yml` com `${VAR}` (porta 8083, `ASST_DB_*`, `EUREKA_SERVICE_URL`); perfis dev/prod.
- `ddl-auto=validate`, `open-in-view=false` (RULE-08). `spring.application.name=asst-service`.
- `ArchitectureTest.java` (@AnalyzeClasses "com.journeyos.asst") com RULE-01..09.

## Resultado esperado
Serviço sobe, registra no Eureka e responde Actuator; sem lógica de negócio ainda.

## Criterios de aceite
- [ ] `./gradlew :services:asst-service:build` PASS.
- [ ] `GET /actuator/health` → 200.
- [ ] `:asst-service:architectureCheck` PASS.
- [ ] Nenhum segredo hardcoded (config via `${VAR}`).

## Dependencias
- INT-ASST-001 (Eureka discovery)

## Estimativa
S

## Prioridade
P1
