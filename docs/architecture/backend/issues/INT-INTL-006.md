# INT-INTL-006 -- Seed por tenant (empresa.provisionada)

## Contexto
Provisionar a Base de Conhecimento e o registro de índices ao criar uma `empresa`.

## Spec de referência
- SPEC-03, `contracts/event-contracts.md §2`, `contracts/hub-integration.md §1`

## Escopo
`EmpresaProvisionadaConsumer` cria `base_conhecimento` da `empresa` (idempotente) e registra os
índices da plataforma para o tenant (governança via config). Trata reentrega como no-op.

## Resultado esperado
Tenant pronto para curadoria/copilot logo após o provisionamento.

## Critérios de aceite
- [ ] `empresa.provisionada` cria exatamente uma `base_conhecimento`
- [ ] Reentrega → no-op
- [ ] Registro de índices do tenant aplicado

## Dependências
- INTL-007, INTL-013

## Estimativa
S

## Prioridade
P6
