# LEAD-008 -- Flyway migrations (emp_<slug>): 12 tabelas do domínio LEAD

## Contexto
DDL schema-aware do LEAD para o schema operacional `emp_<slug>`, autorada em `contracts/data-model.md`
e centralizada em `journey-os-migrations`.

## Spec de referencia
- SPEC-04-data-model-migrations

## Escopo
- Gerar `V<N>__lead_*.sql` (`-- schema: empresa`) para: `lead`, `perfil_lead`, `atributo_perfil`,
  `survey`, `pergunta`, `resposta_survey`, `regra_qualificacao`, `condicao_regra`, `maturity_score`,
  `score_dimensao`, `segmento`, `lead_segmento`.
- Constraints/índices do data-model (UNIQUE `chave_natural`, partial unique `uq_regra_ativa`, CHECKs de enum/range).
- Roteado para `db/migration/empresa/`; ranges `V<N>` atribuídos por MIG (sem colisão cross-módulo).

## Resultado esperado
Schema `emp_<slug>` válido para `ddl-auto=validate` do LEAD.

## Criterios de aceite
- [ ] 12 tabelas criadas no schema do tenant com PK/FK/UNIQUE/CHECK do data-model.
- [ ] `:lead-service` sobe com `ddl-auto=validate` sem erro de validação.
- [ ] Migrations aplicáveis a qualquer `emp_<slug>` (sem schema hardcoded).

## Dependencias
- LEAD-002 (modelo)
- INT-LEAD (MIG provisiona schema)

## Estimativa
M

## Prioridade
P3
