# LEAD-016 -- Kafka consumers: empresa.provisionada (seed) + modelo.acesso.alterado (cache)

## Contexto
Consumo idempotente dos eventos de WRKS: seed de regras/segmentos default por tenant e invalidação
do cache de AccessDecision.

## Spec de referencia
- SPEC-09-messaging-architecture
- SPEC-05-idempotency-concurrency

## Escopo
- `EmpresaProvisionadaConsumer`: ao receber `journey-os.empresa.provisionada`, faz seed idempotente
  da `regra_qualificacao` default + `segmento`s default no novo `emp_<slug>`.
- `ModeloAcessoAlteradoConsumer`: ao receber `journey-os.modelo.acesso.alterado`, invalida entradas
  de cache de `AccessDecision` afetadas.
- `EmpresaContextHolder` setado do header `empresaId` e `clear()` em `finally`.
- Idempotência por `(correlationId, evento)`.

## Resultado esperado
Novo tenant nasce com regra/segmentos default; mudanças de RBAC propagam invalidação de cache.

## Criterios de aceite
- [ ] `empresa.provisionada` → seed idempotente (reprocessar não duplica).
- [ ] `modelo.acesso.alterado` → cache de AccessDecision invalidado.
- [ ] Reprocessar evento já visto é no-op (idempotente).
- [ ] Contexto de empresa limpo após cada mensagem.

## Dependencias
- LEAD-008 (schema/seed)
- INT-LEAD-004 (cache)

## Estimativa
M

## Prioridade
P6
