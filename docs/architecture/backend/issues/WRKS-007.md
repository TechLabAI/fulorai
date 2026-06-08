# WRKS-007 -- Persistência JPA IAM (entities + repositories + adapters)

## Contexto
Camada de persistência do IAM em `journeyos_global`: entidades JPA, repositories Spring Data
e adapters implementando os `*RepositoryPort`.

## Spec de referencia
- SPEC-04-data-model-migrations
- SPEC-03-rbac-access-decision

## Escopo
- `infrastructure/persistence/entity`: entidades JPA para empresa, business_unit, team, usuario,
  usuario_team, papel, permissao, papel_permissao, usuario_empresa, modelo_acesso_versao, evento_auditoria.
- `repository`: Spring Data JPA. `adapter`: implementa `UsuarioRepositoryPort`, `PapelRepositoryPort`,
  `EmpresaRepositoryPort`, etc.
- Mapeamento para schema `journeyos_global`; `ddl-auto=validate`.

## Resultado esperado
Persistência funcional contra schema preparado pelo MIG; adapters convertem entity↔domain.

## Criterios de aceite
- [ ] `infrastructure.*` não depende de `api.*` (RULE-05).
- [ ] Controllers nunca retornam `@Entity` (sempre DTO record).
- [ ] Testes de integração (Testcontainers) CRUD passam.
- [ ] `@Transactional` ausente de repository/adapter (RULE-03).

## Dependencias
- WRKS-002 (precede), WRKS-008 (schema)

## Estimativa
L

## Prioridade
P3
