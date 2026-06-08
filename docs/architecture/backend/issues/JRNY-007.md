# JRNY-007 -- Migrations Flyway (5 tabelas em db/migration/empresa) via journey-os-migrations

## Contexto
DDL da fonte da verdade do JRNY no schema operacional `emp_<slug>`. Migrations centralizadas em
`journey-os-migrations` (MIG), naming `V<N>__jrny_*.sql` em `db/migration/empresa/`.

## Spec de referencia
- SPEC-04-data-model-migrations

## Escopo
- Extrair os 5 blocos ```sql``` de `contracts/data-model.md` (jornada, estagio, regra_roteamento,
  inscricao_jornada, decisao_roteamento) preservando ordem e constraints.
- Garantir: PK uuid (`gen_random_uuid()`), FKs, CHECKs de enum, `UNIQUE (jornada_id, ordem)`,
  índice parcial `UNIQUE (lead_id, jornada_id) WHERE estado='ATIVA'`, CHECK
  `resultado=ROTEADO ⇒ estagio_alvo_id NOT NULL`.
- `empresa_id` presente como guarda em todas as tabelas (schema isola; validado nos adapters).
- Sem novas extensões Postgres (usa `pgcrypto` provido por MIG).

## Resultado esperado
`ddl-auto=validate` do `jrny-service` passa contra o schema migrado por MIG.

## Criterios de aceite
- [ ] `:journey-os-migrations:bootRun` aplica `V__jrny_*` em `db/migration/empresa/`.
- [ ] `validate` do JRNY não acusa divergência de schema.
- [ ] Índice parcial e CHECKs presentes no banco.

## Dependencias
- JRNY-002 (modelo definido)

## Estimativa
M

## Prioridade
P3
