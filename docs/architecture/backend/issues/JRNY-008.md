# JRNY-008 -- Persistência JPA (entities/repositories/adapters) + isolamento de schema

## Contexto
Adapters de persistência (`infrastructure/persistence`) para as 5 tabelas, implementando os
RepositoryPorts do domínio. Mapeamento entity↔domain sem vazar `@Entity` para fora da infra.

## Spec de referencia
- SPEC-04-data-model-migrations
- SPEC-06-security

## Escopo
- `@Entity` JPA para as 5 tabelas; `@Repository` Spring Data; adapters implementando
  `JornadaRepositoryPort`, `InscricaoRepositoryPort`, `DecisaoRepositoryPort` (+ acesso a Estagio/Regra).
- Imutabilidade de `decisao_roteamento` no adapter (apenas insert/select; sem update/delete).
- Resolução de schema por `EmpresaContextHolder` (search_path) + validação de `empresa_id` nas queries.
- Mapeamento `condicao`/`snapshot_entrada`/`config` jsonb ↔ value objects de domínio.

## Resultado esperado
Round-trip domínio↔banco via Testcontainers PostgreSQL com schema migrado; sem entity exposta na API.

## Criterios de aceite
- [ ] Salvar/recuperar Jornada com Estágios/Regras preserva ordem e versão.
- [ ] Inscrição respeita o índice parcial ATIVA (segunda inserção ATIVA falha).
- [ ] Decisão é insert-only (sem caminho de update no adapter).
- [ ] Nenhuma query retorna registro de outra empresa.

## Dependencias
- JRNY-007 (precede)

## Estimativa
L

## Prioridade
P3
