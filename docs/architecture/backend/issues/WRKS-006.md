# WRKS-006 -- ProvisionarEmpresaService (saga: PROVISIONANDO → MIG → ATIVA → evento)

## Contexto
Orquestração do provisionamento de tenant: WRKS é dono do ciclo de vida da empresa e dispara
o MIG para criar o schema `emp_<slug>`.

## Spec de referencia
- SPEC-02-identity-session
- SPEC-05-idempotency-concurrency

## Escopo
- `ProvisionarEmpresaService`: insere `empresa` (PROVISIONANDO) → `MigrationTriggerPort` →
  ao confirmar, ATIVA + publica `journey-os.empresa.provisionada`.
- Idempotência: re-trigger não duplica schema; slug duplicado → 409.
- CRUD de empresa (`EmpresaService`): create/read/update/list.

## Resultado esperado
Criar empresa inicia provisionamento; ATIVA só após confirmação do MIG; idempotente.

## Criterios de aceite
- [ ] Create → status PROVISIONANDO + MIG disparado.
- [ ] Confirmação MIG → ATIVA + evento publicado (exatamente uma vez).
- [ ] Slug duplicado → 409 `wrks.empresa.slug-duplicado`.
- [ ] Falha MIG → permanece PROVISIONANDO + 502 `wrks.empresa.provisionamento-falhou`.

## Dependencias
- WRKS-003 (precede), INT-WRKS-004 (MIG)

## Estimativa
M

## Prioridade
P2
