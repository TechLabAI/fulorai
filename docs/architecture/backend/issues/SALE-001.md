# SALE-001 — Scaffold base do sale-service

## Contexto
Gerar o esqueleto hexagonal executável do `sale-service` (pacote `com.journeyos.sale`, porta 8086)
via `be-module-generator.py` a partir do `generator-config.yml`.

## Spec de referencia
- SPEC-01, SPEC-04, `sale-service-spec.md`

## Escopo
Estrutura de pacotes api/application/domain/infrastructure, `build.gradle.kts`, `application.yml`
(+ perfis), `ArchitectureTest` (RULE-01..09), BaseIntegrationTest singleton, registro em
`settings.gradle.kts`.

## Resultado esperado
Serviço compila e `architectureCheck` passa (skeleton vazio).

## Criterios de aceite
- [ ] `backend/services/sale-service/` gerado com layout hexagonal
- [ ] pacote base `com.journeyos.sale` (RULE-09)
- [ ] `architectureCheck` PASS (quando houver toolchain)
- [ ] registrado em `backend/settings.gradle.kts`

## Dependencias
- (nenhuma)

## Estimativa
M

## Prioridade
P1
