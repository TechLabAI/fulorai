# Plano -- MIG (journey-os-migrations)

## Status das prioridades
> Baseline (B1) executado em 2026-06-05 — score **28 (Inicial)**, 0/5 prioridades concluídas.
> Estado real consolidado no README operacional do serviço (`backend/services/journey-os-migrations/README.md`).
- P1 -- pendente
- P2 -- pendente
- P3 -- pendente
- P5 -- pendente
- P7 -- pendente

> P4 (integrações externas REST), P6 (messaging), P8 (BDD), P9 (hardening) **não se
> aplicam** a MIG: sem Feign, sem Artemis/Kafka, sem domínio BDD. Ver issues_map-MIG.md.

## 0. Leitura executiva

### Papel do serviço (de 01-architectural-vision.md)
Fonte única e versionada de **todo** o schema do Journey OS (schema global + schema por
tenant `empresa`). Nenhum microserviço de negócio possui DDL; todos sobem com
`ddl-auto=validate` contra um schema que MIG já preparou.

### MVP scope (de 01)
Runner Flyway centralizado; schema `journeyos_global`; conjunto por tenant; migrações
versionadas schema-aware; `pgvector` provisionado no global; baseline para banco novo.

### Diagnóstico inicial (gaps de 06)
- **G1** — fonte autoritativa da lista de tenants (registry do WRKS) ainda não existe →
  MVP usa `MIG_TENANT_SCHEMAS` (config). Tratado em MIG-005.
- **G2** — gatilho de provisionamento de novo tenant indefinido (fora do MVP).
- **G3** — política de rollback: forward-only (ADR-005).

## 1. Estratégia geral

### Objetivo macro
Entregar um runner Flyway centralizado, não-destrutivo, idempotente e observável, que
prepara o schema global (com extensões) e os schemas de tenant, e falha rápido em drift.

### Ordem das prioridades

| P | Título | Motivo |
|---|--------|--------|
| P1 | Base + Flyway config + bootstrap de extensões + conectividade | Sem isto nada migra; pgvector é pré-condição de outros módulos |
| P2 | Layout schema-aware + orquestração + enumeração de tenants | Núcleo funcional: aplicar global + fan-out por tenant |
| P3 | Idempotência/concorrência + validação de extensões | Segurança de re-execução e diagnóstico |
| P5 | Security (credenciais env, papel de migração, clean off) | Hardening de privilégio elevado |
| P7 | Observability (logs runId + actuator readiness) | Sinal de prontidão para orquestradores |

## 2. Plano por prioridade

### Prioridade 1 -- Base, Flyway config e bootstrap
Status: pendente
#### Objetivo / Resultado esperado
Esqueleto compilando + ArchUnit ok; Flyway não-destrutivo; V1 habilita extensões no
global; conexão Postgres com retry/fail-fast.
#### Issues vinculadas
- MIG-001, MIG-002, INT-MIG-001
#### Specs cobertas
- SPEC-01, SPEC-04, SPEC-06
#### Sequência de execução
- Fase 1: MIG-001 (scaffold + FlywayConfig)
- Fase 2: INT-MIG-001 (DataSource + retry)
- Fase 3: MIG-002 (V1 extensões)
#### Critérios de aceite
- compileJava + architectureCheck passam; V1 aplicada; `clean` desabilitado.
#### Riscos
- Extensões exigirem allow-list no RDS/Aurora (ver INT-MIG-002 em P3).
#### Instrução para implementador
Gerar via scaffold (type=standard, domínio vazio). Não adicionar entidades JPA. Conferir
que `be-migration-generator.py` produziu o V1 a partir de data-model.md §0.

### Prioridade 2 -- Layout schema-aware, runner e tenants
Status: pendente
#### Objetivo / Resultado esperado
Aplicar `global/V*` no global e `empresa/V*` em cada tenant, em ordem, fail-fast.
#### Issues vinculadas
- MIG-003, MIG-004, MIG-005
#### Specs cobertas
- SPEC-04, SPEC-05
#### Sequência de execução
- Fase 1: MIG-003 (locations global/empresa)
- Fase 2: MIG-005 (enumerator de tenants)
- Fase 3: MIG-004 (MigrationRunner: global → fan-out)
#### Critérios de aceite
- Migração não aplica no schema errado; fan-out ordenado; lista vazia → só global.
#### Riscos
- Custo do fan-out cresce com nº de tenants (R1).
#### Instrução para implementador
`@Transactional` apenas em application.service (RULE-03). Runner em
`application/service`; enumerator e Flyway em `infrastructure`.

### Prioridade 3 -- Idempotência/concorrência + validação de extensões
Status: pendente
#### Objetivo / Resultado esperado
Re-run seguro; concorrência serializada por lock; drift falha; extensões validadas.
#### Issues vinculadas
- MIG-006, INT-MIG-002
#### Specs cobertas
- SPEC-05, SPEC-04
#### Critérios de aceite
- Exatamente-uma-vez por schema; checksum mismatch falha; 5 extensões validadas em teste.
#### Riscos
- Lock preso após crash (mitigado: liberado no drop de conexão).
#### Instrução para implementador
Confiar no schema-history e lock do Flyway; não reimplementar.

### Prioridade 5 -- Security
Status: pendente
#### Objetivo / Resultado esperado
Credenciais via env; papel de migração distinto; `clean` off; actuator interno.
#### Issues vinculadas
- MIG-007
#### Specs cobertas
- SPEC-06
#### Critérios de aceite
- Sem segredo no repo; credencial ausente → fail-fast; clean desabilitado.
#### Instrução para implementador
Usar `${VAR_NAME}` em application.yml; nunca defaults de segredo.

### Prioridade 7 -- Observability
Status: pendente
#### Objetivo / Resultado esperado
Logs estruturados com runId; actuator health/info/flyway; readiness pós-sucesso.
#### Issues vinculadas
- MIG-008
#### Specs cobertas
- SPEC-07
#### Critérios de aceite
- Logs de início/aplicação/falha; readiness `UP` só após sucesso; sem `System.out`.
#### Instrução para implementador
`@Slf4j` (Lombok) + MDC `runId`. Expor `health,info,flyway`.

## 3. Dependências externas
- PostgreSQL 15+ (RDS/Aurora) com papel de migração (DDL + CREATE EXTENSION).
- `pgvector` disponível no cluster.
- (Futuro) registry de tenants do WRKS — Gap G1.

## 4. Restrições arquiteturais
- ArchUnit RULE-01..09 (CLAUDE.md) — `architectureCheck` bloqueante.
- Camadas hexagonais: api / application / domain / infrastructure.
- `@Transactional` somente em application.service.
- `domain.*` sem Spring/JPA.
- Nunca `ddl-auto: create|update`; serviços de negócio = `validate`.
- Nunca `clean` do Flyway habilitado.

## 5. Referências
- docs/architecture/backend/services/journey-os-migrations/01..06 + adr/
- .../journey-os-migrations/contracts/{api-contract,data-model,event-contracts,hub-integration,integration-contracts}.md
- .../journey-os-migrations/spec/backend/SPEC-01,04,05,06,07
- .../journey-os-migrations/generator-config.yml
- docs/architecture/backend/issues/MIG-001..008, INT-MIG-001..002, issues_map-MIG.md
