# ASST-013 -- Idempotência (Idempotency-Key + publish) + concorrência otimista

## Contexto
Garantir composição/publicação idempotentes e consistência sob transições concorrentes.

## Spec de referencia
- SPEC-05-idempotency-concurrency
- SPEC-03-asset-studio-composition

## Escopo
- `Idempotency-Key` no Asset Studio: replay retorna a versão original, sem nova chamada à IA.
- Publish idempotente (republicação = no-op, sem evento duplicado).
- Concorrência otimista (`@Version`/checagem de estado) nas transições.

## Resultado esperado
Replays e concorrência não duplicam versões/eventos nem corrompem estado.

## Criterios de aceite
- [ ] Mesma `Idempotency-Key` → 1 versão, IA chamada 1 vez.
- [ ] Republicar versão já publicada → no-op, sem evento duplicado.
- [ ] 2 transições concorrentes → 1 aplica, a outra recebe 409.

## Dependencias
- ASST-006 (precede); ASST-009

## Estimativa
M

## Prioridade
P5
