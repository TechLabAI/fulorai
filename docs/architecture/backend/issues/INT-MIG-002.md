# INT-MIG-002 -- Extension availability validation (pgvector et al.)

## Contexto
As extensões exigidas (`vector`, `uuid-ossp`, `pgcrypto`, `pg_trgm`, `unaccent`) devem
existir/instalar no cluster. Em ambientes gerenciados (RDS/Aurora) algumas exigem
allow-list; a ausência deve ser detectada cedo.

## Spec de referencia
- contracts/integration-contracts.md
- SPEC-04 (Data model & migrations)
- contracts/data-model.md §0

## Escopo
- Migração de bootstrap (MIG-002) cria extensões via `CREATE EXTENSION IF NOT EXISTS`.
- Teste de integração valida que as 5 extensões ficam disponíveis no schema global após
  a execução.
- Mensagem de erro clara se uma extensão não puder ser criada (privilégio/allow-list).

## Resultado esperado
Após MIG rodar, todas as extensões requeridas estão presentes; falha de provisionamento
é diagnosticável.

## Criterios de aceite
- [ ] Teste de integração confirma as 5 extensões no schema global.
- [ ] Falha ao criar extensão → erro claro apontando a extensão e a causa provável.

## Dependencias
- MIG-002 (precede)
- INT-MIG-001 (precede)

## Estimativa
S

## Prioridade
P3
