# WRKS-013 -- Guardas de segurança: anti-escalonamento + cross-empresa + RULE-07

## Contexto
Defesas críticas do domínio de acesso: impedir escalonamento de papel e vazamento cross-empresa,
com enforcement do contexto de tenant.

## Spec de referencia
- SPEC-06-security
- SPEC-02-identity-session

## Escopo
- Domain service `AntiEscalationPolicy`: bloqueia atribuir/editar papel de `nivel` acima do
  papel do chamador (INV-1).
- Cross-empresa guard: nenhuma resposta retorna dado de `empresa_id` diferente do JWT.
- `EmpresaContextHolder.require()` no início de todo application service que toca dado de empresa (RULE-07).

## Resultado esperado
Escalonamento bloqueado; isolamento cross-empresa garantido; contexto sempre exigido.

## Criterios de aceite
- [ ] Atribuir papel acima do próprio → 403 `wrks.papel.escalonamento`.
- [ ] Atribuir papel igual/abaixo → permitido + evento `usuario.empresa.associado`.
- [ ] Listagens só retornam dados da empresa do JWT (BDD cross-empresa passa).
- [ ] ArchUnit RULE-07: todo application service chama `require()`.

## Dependencias
- WRKS-004, WRKS-011 (precedem)

## Estimativa
M

## Prioridade
P5
