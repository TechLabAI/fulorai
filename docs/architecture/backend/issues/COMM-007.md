# COMM-007 -- Persistência JPA + adapters (emp_<slug>)

## Contexto
Entidades JPA + repositórios + adapters implementando os ports `out` de repositório, no schema
do tenant `emp_<slug>` (`ddl-auto=validate`).

## Spec de referencia
- SPEC-04-data-model-migrations
- SPEC-02-message-dispatch-lifecycle

## Escopo
- Entities JPA: `TemplateMensagemEntity`, `MensagemEntity`, `EventoEntregaEntity`, `RegraRoteamentoEntity`, `ConfigCanalEntity`.
- Spring Data repositories + adapters (`TemplateRepositoryPort`, `MensagemRepositoryPort`, `RoteamentoRepositoryPort`, `ConfigCanalRepositoryPort`).
- Mapeamento entity↔domínio (MapStruct opcional); JSONB para `variaveis`/`condicoes`/`destinatario`/`conteudo_renderizado`/`provedor_payload`.
- `MultiTenantConnectionProvider` fixa `search_path` no `emp_<slug>`.

## Resultado esperado
Domínio persiste/recupera no schema do tenant via ports; sem `empresa_id` nas tabelas.

## Criterios de aceite
- [ ] CRUD persiste no `emp_<slug>` corrente (teste Testcontainers).
- [ ] `@Entity` nunca retornada por controller (sempre DTO).
- [ ] `chave_idempotencia` UNIQUE respeitada no banco.

## Dependencias
- COMM-002 (precede)

## Estimativa
M

## Prioridade
P3
