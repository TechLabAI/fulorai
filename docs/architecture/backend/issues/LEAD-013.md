# LEAD-013 -- EmpresaContextHolder + cross-empresa guard (multi-tenancy)

## Contexto
Resolução do schema `emp_<slug>` por requisição/evento e garantia de que nenhum dado vaza entre empresas.

## Spec de referencia
- SPEC-06-security
- (ADR) ADR-004-multitenant-strategy

## Escopo
- `EmpresaContextHolder` resolve `empresa_id` do claim JWT (HTTP) e do header (consumo de evento).
- Roteamento de schema por tenant (`emp_<slug>`); `EmpresaContextHolder.require()` em `application.service`.
- `clear()` em `finally` no consumo assíncrono.
- Teste de cross-empresa guard (JWT da empresa A não lê dado da empresa B).

## Resultado esperado
Toda operação opera apenas no schema da empresa do contexto.

## Criterios de aceite
- [ ] Query/escrita escopadas ao `empresa_id` do contexto.
- [ ] JWT da empresa A não retorna dado da empresa B.
- [ ] Operação sem contexto resolvido é bloqueada.
- [ ] Contexto limpo após consumo de evento (sem vazamento entre mensagens).

## Dependencias
- LEAD-012 (JWT)

## Estimativa
M

## Prioridade
P5
