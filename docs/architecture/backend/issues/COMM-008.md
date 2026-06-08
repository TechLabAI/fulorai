# COMM-008 -- Migrations Flyway (5 tabelas) via data-model

## Contexto
DDL das tabelas de comunicação no schema `emp_<slug>`, gerado a partir de `contracts/data-model.md`
e aplicado pelo `journey-os-migrations` (centralizado).

## Spec de referencia
- SPEC-04-data-model-migrations

## Escopo
- `V<N>__comm_*.sql` em `db/migration/empresa/`: `template_mensagem`, `mensagem`, `evento_entrega`, `regra_roteamento`, `config_canal` + índices + CHECK/UNIQUE.
- Extração via `be-migration-generator.py` (blocos ```sql``` em ordem).
- `outbox_event`/`processed_events` referenciados da migration compartilhada (não redefinir).

## Resultado esperado
Schema `emp_<slug>` valida contra as entities JPA (`ddl-auto=validate` passa).

## Criterios de aceite
- [ ] Migration cria as 5 tabelas + índices + constraints.
- [ ] `ddl-auto=validate` sobe sem erro contra o schema migrado.
- [ ] `UNIQUE (chave_idempotencia)` e `UNIQUE (canal, provedor)` presentes.

## Dependencias
- COMM-007 (precede)

## Estimativa
M

## Prioridade
P3
