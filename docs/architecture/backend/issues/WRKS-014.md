# WRKS-014 -- Administração RBAC (papéis/permissões) + org structure + session policy

## Contexto
Endpoints administrativos do modelo de acesso e da estrutura organizacional, com bump de versão
e publicação de evento ao mudar bundles.

## Spec de referencia
- SPEC-03-rbac-access-decision
- SPEC-01-api-surface

## Escopo
- `PapelService`: `GET /papeis`, `GET/PUT /papeis/{codigo}/permissoes` — ao mudar bundle, bump
  `modelo_acesso_versao` (mesma transação) + publica `journey-os.modelo.acesso.alterado`.
- Validação: permissão referenciada deve constar no catálogo canônico.
- `BusinessUnitService` + `TeamService`: CRUD escopado à empresa do JWT.
- `UsuarioService.associar`: associação usuário↔empresa (papel + data_scope).
- Session policy config-driven por papel (`application.yml`).

## Resultado esperado
Admin gerencia papéis/permissões/org; mudança de RBAC propaga em segundos.

## Criterios de aceite
- [ ] Mudança de bundle → versão incrementada (mesma tx) + evento publicado.
- [ ] Permissão fora do catálogo → 422 `wrks.papel.permissao-desconhecida`.
- [ ] CRUD de business-unit/team isolado por empresa.
- [ ] Email duplicado em criar usuário → 409 `wrks.usuario.duplicado`.

## Dependencias
- WRKS-007 (persistência), WRKS-012 (cache/versão), WRKS-015 (publish)

## Estimativa
L

## Prioridade
P5
