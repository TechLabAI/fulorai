# WRKS-010 -- Cliente Feign MIG (MigrationTriggerPort) para provisionamento

## Contexto
Adapter que dispara o MIG para criar o schema `emp_<slug>` ao provisionar uma empresa.

## Spec de referencia
- SPEC-10-integrations
- hub-integration.md

## Escopo
- `MigrationTriggerClient` (`@FeignClient(name="journey-os-migrations")`, url_prop `journey-os.mig.url`)
  implementando `MigrationTriggerPort`.
- Resilience4j: timeout 30s, retry 3 (backoff), circuit-breaker.
- Confirmação de provisionamento via evento `journey-os.empresa.provisionada` (assíncrono).

## Resultado esperado
Provisionamento dispara MIG com resiliência; idempotente em re-trigger.

## Criterios de aceite
- [ ] Trigger cria schema `emp_<slug>` (stub MIG).
- [ ] Falha/timeout MIG → empresa permanece PROVISIONANDO; retriable.
- [ ] `@FeignClient` apenas em `infrastructure.clients` (RULE-06).

## Dependencias
- WRKS-006 (consumidor), INT-WRKS-004

## Estimativa
S

## Prioridade
P4
