# LEAD-009 -- JPA entities + repositories + persistence adapters

## Contexto
Camada de persistência: entidades JPA, repositórios Spring Data e adapters que implementam as
portas out de repositório, no schema `emp_<slug>`.

## Spec de referencia
- SPEC-04-data-model-migrations
- SPEC-05-idempotency-concurrency

## Escopo
- `infrastructure.persistence.entity`: `@Entity` para as 12 tabelas (mapeando o data-model).
- `infrastructure.persistence.repository`: Spring Data JPA.
- `infrastructure.persistence.adapter`: implementam `LeadRepositoryPort`, `SurveyRepositoryPort`,
  `RegraQualificacaoRepositoryPort`, `SegmentoRepositoryPort` (mapeiam entity ↔ domain model).
- Upsert por `chave_natural`; um `maturity_score` corrente por lead.

## Resultado esperado
Domínio persiste/recupera via portas; nenhuma entidade JPA vaza para `api`/`domain`.

## Criterios de aceite
- [ ] Adapters implementam as portas out de repositório; mapeiam entity↔model.
- [ ] `@Transactional` ausente em adapters (apenas `application.service`, RULE-03).
- [ ] Teste de integração (Testcontainers, singleton) CRUD do `lead` PASS.
- [ ] `open-in-view=false` respeitado (RULE-08).

## Dependencias
- LEAD-008 (schema)

## Estimativa
M

## Prioridade
P3
