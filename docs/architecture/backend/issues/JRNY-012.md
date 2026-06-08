# JRNY-012 -- Security: JWT + AccessDecision (jrny.*) + EmpresaContextHolder (HTTP + Kafka) + MDC

## Contexto
Autenticação/autorização do JRNY: valida JWT (JWKS de WRKS), resolve permissões `jrny.*` via
`AccessDecision`, e fixa o tenant tanto no caminho HTTP quanto no consumo de eventos Kafka.

## Spec de referencia
- SPEC-06-security
- hub-integration.md

## Escopo
- Resource server OAuth2 (RS256, JWKS de WRKS); endpoints sem rota anônima.
- Filtro de segurança popula `EmpresaContextHolder.require()` a partir do claim `empresa_id` (HTTP)
  e do header `empresaId` do envelope (consumer Kafka); `clear()` em `finally`.
- Enforcement de permissões `jrny.<recurso>.<acao>` via `AccessDecisionPort` (cache curto).
- MDC com `correlationId` + `empresaId` (+ `leadId` no caminho de roteamento).
- Cross-empresa guard: nenhuma operação/leitura cruza schema.

## Resultado esperado
401/403 corretos; tenant sempre fixado antes de qualquer side effect; isolamento por empresa garantido em HTTP e mensageria.

## Criterios de aceite
- [ ] JWT ausente/inválido → 401 `jrny.auth.token-invalido`.
- [ ] Falta de permissão → 403 `jrny.acesso.permissao-negada`.
- [ ] Consumer fixa `EmpresaContextHolder` do envelope antes de processar e limpa no `finally`.
- [ ] Requisição/evento da empresa A nunca acessa dados da empresa B.

## Dependencias
- JRNY-003 (API)
- INT-JRNY-002 (AccessEvaluateClient)

## Estimativa
M

## Prioridade
P5
