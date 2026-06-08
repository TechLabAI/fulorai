# INTL-001 -- Scaffold hexagonal + build + ArchUnit (intl-service)

## Contexto
INTL ainda não tem esqueleto executável. Gerar o microserviço `intl-service` (pacote
`com.journeyos.intl`, porta 8087) com a estrutura hexagonal canônica e ArchUnit bloqueante.

## Spec de referência
- SPEC-01, `generator-config.yml`, `setup-local.md`

## Escopo
Esqueleto Spring Boot via `be-module-generator.py`: camadas api/application/domain/infrastructure,
`build.gradle.kts`, `application.yml` (+ perfis), `DomainServiceConfig`, ArchitectureTest
(`@AnalyzeClasses com.journeyos.intl`), registro em `backend/settings.gradle.kts`.

## Resultado esperado
Serviço compila e `architectureCheck` passa (quando a toolchain Gradle existir).

## Critérios de aceite
- [ ] Estrutura hexagonal com base package `com.journeyos.intl` (RULE-09)
- [ ] `architectureCheck` cobre RULE-01..08
- [ ] `spring.jpa.open-in-view=false` (RULE-08)
- [ ] Registrado em `backend/settings.gradle.kts`

## Dependências
- (nenhuma)

## Estimativa
M

## Prioridade
P1
