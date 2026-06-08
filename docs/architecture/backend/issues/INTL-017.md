# INTL-017 -- Hardening (SLAs, resiliência, runbook)

## Contexto
Endurecer INTL para operação: SLAs de latência do copiloto, tuning de circuit breaker/retry,
limites de custo por `empresa`, runbook de DLQ/replay.

## Spec de referência
- SPEC-07, SPEC-10, `06-risks-gaps-assumptions.md`

## Escopo
Ajustar timeouts/CB/retries (TechLab AI/Elastic); quota de custo de tokens por `empresa`
(soft-limit + métrica); runbook de inspeção/reprocessamento da DLQ; revisão de ILM dos índices
próprios.

## Resultado esperado
Operação previsível sob falha e custo controlado.

## Critérios de aceite
- [ ] SLA de latência do copiloto definido e medido
- [ ] Soft-limit de custo por `empresa` com alerta
- [ ] Runbook de DLQ/replay documentado
- [ ] ILM dos índices próprios revisado

## Dependências
- INTL-009, INTL-010, INTL-014, INTL-015 (precedem)

## Estimativa
M

## Prioridade
P9
