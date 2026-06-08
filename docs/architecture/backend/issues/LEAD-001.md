# LEAD-001 -- Bootstrap lead-service (Spring Boot MVC + Eureka client + Actuator + ArchUnit)

## Contexto
Esqueleto executável do serviço de inteligência de leads. App Spring Boot MVC, pacote base
`com.journeyos.lead`, registro no Eureka (REG), Actuator e harness ArchUnit (RULE-01..09).

## Spec de referencia
- SPEC-01-api-surface
- SPEC-07-observability-health

## Escopo
- App Spring Boot 3.5.x MVC, pacote `com.journeyos.lead`.
- Dependências: web, data-jpa, eureka-client, actuator, validation.
- `application.yml` com `${VAR}` (porta 8082, `LEAD_DB_*`, `EUREKA_SERVICE_URL`); perfis dev/prod.
- `ddl-auto=validate`, `open-in-view=false` (RULE-08). `spring.application.name=lead-service`.
- `ArchitectureTest.java` (@AnalyzeClasses "com.journeyos.lead") com RULE-01..09.

## Resultado esperado
Serviço sobe, registra no Eureka e responde Actuator; sem lógica de negócio ainda.

## Criterios de aceite
- [ ] `./gradlew :services:lead-service:build` PASS.
- [ ] `GET /actuator/health` → 200.
- [ ] `:lead-service:architectureCheck` PASS.
- [ ] Nenhum segredo hardcoded (config via `${VAR}`).

## Dependencias
- INT-LEAD-001 (Eureka discovery)

## Estimativa
S

## Prioridade
P1
