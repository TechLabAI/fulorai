# INTL-007 -- Persistência JPA (7 tabelas emp_<slug>)

## Contexto
Mapear o modelo relacional de INTL e os adapters de repositório.

## Spec de referência
- SPEC-04, `contracts/data-model.md`

## Escopo
Entities JPA + repositories + adapters para `base_conhecimento`, `fonte_conhecimento`,
`no_conhecimento` (coluna `embedding` vector nullable), `conversa_copiloto`, `mensagem_copiloto`,
`citacao`, `evento_indexado`. `ddl-auto=validate`. Mapear enums via `@Enumerated(STRING)` + CHECK.

## Resultado esperado
Boot valida o schema migrado por MIG; CRUD persiste no `emp_<slug>` resolvido.

## Critérios de aceite
- [ ] 7 tabelas mapeadas; FKs e UNIQUE (`conversa_id`,`ordem`) respeitados
- [ ] `embedding` mapeado como coluna nullable (refinado p/ vector no implement)
- [ ] Nenhum `@Entity` retornado por controller (sempre DTO)
- [ ] `@Transactional` apenas em application.service

## Dependências
- INTL-001, INTL-008 (schema)

## Estimativa
L

## Prioridade
P3
