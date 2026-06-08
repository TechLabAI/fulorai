# SALE-013 — Security (JWT resource server + sale.* + multi-tenancy)

## Contexto
Resource server JWT (WRKS JWKS), autorização por permissões `sale.*` e isolamento por
`EmpresaContextHolder`.

## Spec de referencia
- SPEC-06, ADR-004

## Escopo
`infrastructure.security`: filtro JWT, `EmpresaContextHolder` (resolve `emp_<slug>` do claim),
guarda cross-empresa, MDC sem PII. Ingestão de compra exige service token (não anônimo).

## Resultado esperado
Acesso autenticado, autorizado e isolado por tenant.

## Criterios de aceite
- [ ] sem JWT válido → 401; sem permissão → 403 problem+json
- [ ] tenant resolvido só do claim `empresa_id` (X-Empresa-Id ignorado p/ authz)
- [ ] nenhuma leitura cross-empresa
- [ ] `POST /compras` exige service token

## Dependencias
- SALE-011 (precede)

## Estimativa
M

## Prioridade
P5
