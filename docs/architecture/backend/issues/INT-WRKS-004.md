# INT-WRKS-004 -- Integração MIG (provisionamento de schema emp_<slug>)

## Contexto
Disparo do `journey-os-migrations` para criar o schema operacional ao provisionar uma empresa.

## Spec de referencia
- integration-contracts.md §5
- hub-integration.md §2

## Escopo
- Cliente HTTP/Feign para MIG (`journey-os.mig.url`), timeout 30s, retry 3 (backoff), circuit-breaker.
- Confirmação assíncrona via `journey-os.empresa.provisionada`.

## Resultado esperado
Provisionamento confiável e idempotente; resiliente a falhas transitórias do MIG.

## Criterios de aceite
- [ ] Trigger cria schema `emp_<slug>` (stub MIG / Testcontainers).
- [ ] Timeout/erro → empresa permanece PROVISIONANDO; retriable; sem schema duplicado.

## Dependencias
- WRKS-006, WRKS-010

## Estimativa
M

## Prioridade
P4
